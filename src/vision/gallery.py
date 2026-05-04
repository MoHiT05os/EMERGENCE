import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity


class StudentGallery:
    def __init__(self,
                 min_similarity=0.68,   # Slightly relaxed to accommodate rotations
                 ema_alpha=0.20,
                 max_inactive_frames=600,
                 spatial_weight=0.25,
                 spatial_frame_window=30,       # CRITICAL FIX: Clamped down to 30 frames to block ID hijacking across severe camera rotations
                 max_bank_size=5):      # MULTI-VIEW FEATURE BANKING
                 
        self._gallery = {}
        self._next_global_id = 1
        self._local_to_global = {}

        self.min_similarity = min_similarity
        self.ema_alpha = ema_alpha
        self.max_inactive_frames = max_inactive_frames
        self.spatial_weight = spatial_weight
        self.spatial_frame_window = spatial_frame_window
        self.max_bank_size = max_bank_size

    @property
    def size(self):
        return len(self._gallery)

    def match_batch(self, embeddings, local_track_ids, bboxes, frame_idx, frame_wh=None):
        """
        Match a batch of detections exclusively using Multi-View Feature Banking.
        """
        n = len(embeddings)
        results = [None] * n

        if not self._gallery:
            for i, (emb, lid, bbox) in enumerate(zip(embeddings, local_track_ids, bboxes)):
                gid = self._create_new(emb, lid, frame_idx, bbox, frame_wh)
                results[i] = (gid, 1.0)
            return results

        gallery_ids = list(self._gallery.keys())
        
        # Build flattened gallery matrix for multi-view comparison
        flattened_gallery_embs = []
        embedding_to_gid_idx = []
        for j, gid in enumerate(gallery_ids):
            for emb in self._gallery[gid]['bank']:
                flattened_gallery_embs.append(emb)
                embedding_to_gid_idx.append(j)
                
        flattened_gallery_embs = np.stack(flattened_gallery_embs)

        valid_indices = [i for i, e in enumerate(embeddings) if e is not None]
        sim_matrix = np.zeros((n, len(gallery_ids)))

        if valid_indices:
            valid_embs = np.stack([embeddings[i] for i in valid_indices])
            raw_sims = cosine_similarity(valid_embs, flattened_gallery_embs)
            
            # Collapse the multi-view matches by max similarity per Global ID
            for vi, i in enumerate(valid_indices):
                for flat_idx, sim in enumerate(raw_sims[vi]):
                    gid_j = embedding_to_gid_idx[flat_idx]
                    if sim > sim_matrix[i, gid_j]:
                        sim_matrix[i, gid_j] = sim

        # Apply Spatial Physics Bonus (Only boosting, never penalizing)
        if frame_wh is not None:
            fw, fh = frame_wh
            for i, bbox in enumerate(bboxes):
                if bbox is None:
                    continue
                x1, y1, x2, y2 = bbox
                cx = (x1 + x2) / 2 / fw
                cy = (y1 + y2) / 2 / fh
                for j, gid in enumerate(gallery_ids):
                    last_pos = self._gallery[gid].get('last_pos')
                    last_seen = self._gallery[gid].get('last_seen', 0)
                    if last_pos is not None and (frame_idx - last_seen) < self.spatial_frame_window:
                        dist = np.sqrt((cx - last_pos[0]) ** 2 + (cy - last_pos[1]) ** 2)
                        if dist < 0.2:
                            spatial_bonus = 0.15 * (1.0 - (dist / 0.2))
                            sim_matrix[i, j] = min(1.0, sim_matrix[i, j] + spatial_bonus)

        taken_gallery = set()
        best_raw = sim_matrix.max(axis=1) if len(gallery_ids) > 0 else np.zeros(n)
        order = np.argsort(-best_raw)

        for i in order:
            lid = local_track_ids[i]
            emb = embeddings[i]
            bbox = bboxes[i]

            # Cache verification
            if lid in self._local_to_global:
                cached_gid = self._local_to_global[lid]
                if cached_gid in self._gallery and cached_gid not in taken_gallery:
                    cached_j = gallery_ids.index(cached_gid)
                    cached_sim = float(sim_matrix[i, cached_j])

                    if emb is not None and cached_sim >= (self.min_similarity - 0.15):
                        taken_gallery.add(cached_gid)
                        self._update(cached_gid, emb, frame_idx, bbox, frame_wh)
                        results[i] = (cached_gid, cached_sim)
                        continue
                    elif emb is None:
                        taken_gallery.add(cached_gid)
                        self._gallery[cached_gid]['last_seen'] = frame_idx
                        results[i] = (cached_gid, 0.5)
                        continue
                    else:
                        del self._local_to_global[lid]

            avail_sims = sim_matrix[i].copy()
            for j, gid in enumerate(gallery_ids):
                if gid in taken_gallery:
                    avail_sims[j] = -1.0

            best_j = int(np.argmax(avail_sims))
            best_sim = float(avail_sims[best_j])

            if best_sim >= self.min_similarity:
                matched_gid = gallery_ids[best_j]
                taken_gallery.add(matched_gid)
                self._local_to_global[lid] = matched_gid
                self._gallery[matched_gid]['local_ids'].add(lid)
                self._update(matched_gid, emb, frame_idx, bbox, frame_wh)
                print(f"  [ReID] Local {lid} → Global G:{matched_gid}  (sim={best_sim:.2f})")
                results[i] = (matched_gid, best_sim)
            else:
                new_gid = self._create_new(emb, lid, frame_idx, bbox, frame_wh)
                taken_gallery.add(new_gid)
                results[i] = (new_gid, 1.0)

        return results

    def _create_new(self, embedding, local_track_id, frame_idx, bbox=None, frame_wh=None):
        gid = self._next_global_id
        self._next_global_id += 1

        last_pos = None
        if bbox is not None and frame_wh is not None:
            fw, fh = frame_wh
            x1, y1, x2, y2 = bbox
            last_pos = ((x1 + x2) / 2 / fw, (y1 + y2) / 2 / fh)

        emb_matrix = embedding if embedding is not None else np.zeros(592, dtype=np.float32)
        
        self._gallery[gid] = {
            'bank': [emb_matrix],
            'last_seen': frame_idx,
            'last_pos': last_pos,
            'local_ids': {local_track_id},
        }
        self._local_to_global[local_track_id] = gid
        print(f"  [ReID] New Global ID G:{gid} assigned to Local {local_track_id}")
        return gid

    def _update(self, gid, embedding, frame_idx, bbox, frame_wh):
        if embedding is not None:
            bank = self._gallery[gid]['bank']
            
            # Find which view in the bank is the closest match
            bank_matrix = np.stack(bank)
            sims = cosine_similarity([embedding], bank_matrix)[0]
            best_idx = int(np.argmax(sims))
            best_sim = sims[best_idx]
            
            if best_sim >= 0.85:
                # We have seen this angle before. Gently update this specific view.
                old = bank[best_idx]
                updated = (1 - self.ema_alpha) * old + self.ema_alpha * embedding
                norm = np.linalg.norm(updated)
                if norm > 0:
                    updated = updated / norm
                self._gallery[gid]['bank'][best_idx] = updated
            else:
                # The student shifted dynamically! This is a radically new view. Append to bank!
                self._gallery[gid]['bank'].append(embedding)
                if len(self._gallery[gid]['bank']) > self.max_bank_size:
                    self._gallery[gid]['bank'].pop(0) # Remove oldest view

        self._gallery[gid]['last_seen'] = frame_idx

        if bbox is not None and frame_wh is not None:
            fw, fh = frame_wh
            x1, y1, x2, y2 = bbox
            self._gallery[gid]['last_pos'] = ((x1 + x2) / 2 / fw, (y1 + y2) / 2 / fh)

    def prune(self, current_frame):
        stale = [gid for gid, info in self._gallery.items()
                 if (current_frame - info['last_seen']) > self.max_inactive_frames]
        for gid in stale:
            self._gallery.pop(gid)
        stale_locals = [lid for lid, gid in self._local_to_global.items()
                        if gid not in self._gallery]
        for lid in stale_locals:
            self._local_to_global.pop(lid)

    def get_stats(self):
        return {
            'total_global_ids': self._next_global_id - 1,
            'active_global_ids': len(self._gallery),
            'local_id_mappings': len(self._local_to_global),
        }

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'gallery': self._gallery,
                'next_id': self._next_global_id,
                'local_to_global': self._local_to_global,
            }, f)
        print(f"Gallery saved: {path} ({len(self._gallery)} students)")

    def load(self, path):
        path = Path(path)
        if not path.exists():
            return False
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self._gallery = data['gallery']
        self._next_global_id = data['next_id']
        self._local_to_global = data['local_to_global']
        print(f"Gallery loaded: {path} ({len(self._gallery)} students)")
        return True
