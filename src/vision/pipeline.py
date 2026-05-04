import cv2
import pandas as pd
import numpy as np
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import OUTPUT_DIR, MAPPING_FRAMES_DIR
from vision.detector import StudentDetector
from vision.pose import PoseExtractor
from vision.motion import MotionAnalyzer
from vision.reid import AppearanceExtractor
from vision.gallery import StudentGallery


class VisionPipeline:
    def __init__(self, source=0, output_csv="engagement_log.csv", save_frames=True,
                 frame_save_tag="class", save_video=True, enable_reid=True,
                 gallery_path=None):
        self.detector = StudentDetector()
        self.pose_extractor = PoseExtractor()
        self.motion_analyzers = {}
        self.save_frames = save_frames
        self.frame_save_tag = frame_save_tag
        self.save_video = save_video
        self.saved_frame_paths = []
        self.engagement_history = {}
        self.smoothing_window = 8

        self.enable_reid = enable_reid
        self.appearance_extractor = None
        self.gallery = None
        if enable_reid:
            self.appearance_extractor = AppearanceExtractor()
            self.gallery = StudentGallery(
                min_similarity=0.72,
                ema_alpha=0.25,
                max_inactive_frames=600,
            )
            if gallery_path and Path(gallery_path).exists():
                self.gallery.load(gallery_path)
        self.gallery_path = gallery_path
        self.reid_events = []

        if source == 0 or source == "0":
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            print(f"Error: Could not open source {source}. Trying webcam.")
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.output_csv = OUTPUT_DIR / output_csv
        self.logs = []

    def _smooth_engagement(self, track_id, raw_score):
        if track_id not in self.engagement_history:
            self.engagement_history[track_id] = []
        self.engagement_history[track_id].append(raw_score)
        if len(self.engagement_history[track_id]) > self.smoothing_window:
            self.engagement_history[track_id] = self.engagement_history[track_id][-self.smoothing_window:]
        history = self.engagement_history[track_id]
        if len(history) >= 3:
            weights = np.linspace(0.5, 1.0, len(history))
            return float(np.average(history, weights=weights))
        return raw_score

    def _draw_premium_overlay(self, frame, detections_data):
        overlay = frame.copy()
        h, w = frame.shape[:2]

        bar_h = 40
        cv2.rectangle(overlay, (0, 0), (w, bar_h), (15, 15, 30), -1)
        cv2.putText(overlay, "EMERGENCE  |  Adaptive Classroom Intelligence",
                    (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 160, 255), 1, cv2.LINE_AA)

        n_students = len(detections_data)
        avg_eng = np.mean([d['engagement'] for d in detections_data]) if detections_data else 0
        reid_str = "ReID:ON" if self.enable_reid else "ReID:OFF"
        info = f"Students: {n_students}  |  Avg Eng: {avg_eng:.0%}  |  {reid_str}"
        (tw, _), _ = cv2.getTextSize(info, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(overlay, info, (w - tw - 12, 26), cv2.FONT_HERSHEY_SIMPLEX,
                    0.42, (180, 180, 180), 1, cv2.LINE_AA)

        for det in detections_data:
            x1, y1, x2, y2 = det['bbox']
            eng = det['engagement']
            local_id = det['track_id']
            global_id = det.get('global_id', local_id)
            gaze = det.get('gaze', 0)
            posture = det.get('posture', 0)
            activity = det.get('activity', '')
            reid_conf = det.get('reid_conf', 1.0)

            if activity == 'WRITING':
                color = (115, 213, 46)
                status = "WRITING"
            elif eng >= 0.65:
                color = (115, 213, 46)
                status = "ENGAGED"
            elif eng >= 0.5:
                color = (2, 165, 255)
                status = "ACTIVE"
            else:
                color = (87, 71, 255)
                status = "LOW"

            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)

            corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
            corner_len = 15
            for cx, cy in corners:
                dx = corner_len if cx == x1 else -corner_len
                dy = corner_len if cy == y1 else -corner_len
                cv2.line(overlay, (cx, cy), (cx + dx, cy), color, 3)
                cv2.line(overlay, (cx, cy), (cx, cy + dy), color, 3)

            label_h = 64
            label_y = max(y1 - label_h - 4, bar_h)
            label_bg = overlay.copy()
            cv2.rectangle(label_bg, (x1 - 1, label_y), (x1 + 185, label_y + label_h), (20, 20, 35), -1)
            cv2.addWeighted(label_bg, 0.85, overlay, 0.15, 0, overlay)

            id_line = f"G:{global_id}  L:{local_id}  {status}" if self.enable_reid else f"ID:{local_id}  {status}"
            cv2.putText(overlay, id_line, (x1 + 5, label_y + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)
            cv2.putText(overlay, f"Eng: {eng:.0%}", (x1 + 5, label_y + 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)
            cv2.putText(overlay, f"G:{gaze:.0%} P:{posture:.0%}", (x1 + 5, label_y + 46),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.33, (150, 150, 150), 1, cv2.LINE_AA)
            if self.enable_reid:
                conf_color = (115, 213, 46) if reid_conf >= 0.7 else (2, 165, 255) if reid_conf >= 0.55 else (100, 100, 200)
                cv2.putText(overlay, f"ReID: {reid_conf:.0%}", (x1 + 5, label_y + 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, conf_color, 1, cv2.LINE_AA)

            bar_x, bar_y = x1, y2 + 5
            bar_w = x2 - x1
            cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_w, bar_y + 5), (40, 40, 60), -1)
            cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + int(bar_w * min(eng, 1.0)), bar_y + 5), color, -1)

        return overlay

    def process(self, display=True, max_frames=None, process_every_n=3):
        print("Starting Vision Pipeline...")
        frame_idx = 0
        best_frame = None
        best_frame_detections = 0
        best_frame_det = []
        frames_dir = MAPPING_FRAMES_DIR / self.frame_save_tag
        frames_dir.mkdir(parents=True, exist_ok=True)

        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        fps_source = self.cap.get(cv2.CAP_PROP_FPS) or 30
        last_frame_det_data = []

        video_writer = None
        video_out_path = None
        if self.save_video:
            fps = fps_source
            w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if w > 0 and h > 0:
                codec_options = [
                    ('MJPG', OUTPUT_DIR / f"annotated_{self.frame_save_tag}.avi"),
                ]
                for codec_name, out_path in codec_options:
                    fourcc = cv2.VideoWriter_fourcc(*codec_name)
                    vw = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
                    if vw.isOpened():
                        video_writer = vw
                        video_out_path = out_path
                        print(f"Codec: {codec_name} | Output: {out_path}")
                        break
                    vw.release()
                if video_writer is None:
                    print("WARNING: Could not open any video writer.")
                else:
                    print(f"Total frames: {total_frames} | FPS: {fps_source:.1f} | Every {process_every_n} frames")

        proc_start = time.time()

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_idx += 1
            if max_frames and frame_idx > max_frames:
                break

            if frame_idx % 200 == 0:
                elapsed = time.time() - proc_start
                proc_fps = frame_idx / elapsed if elapsed > 0 else 0
                pct = (frame_idx / total_frames * 100) if total_frames > 0 else 0
                eta = (total_frames - frame_idx) / proc_fps if proc_fps > 0 and total_frames > 0 else 0
                print(f"  Frame {frame_idx}/{total_frames} ({pct:.1f}%) | {proc_fps:.1f} FPS | ETA: {eta:.0f}s")
                if self.gallery:
                    self.gallery.prune(frame_idx)

            run_detection = (frame_idx % process_every_n == 1)
            timestamp = time.time()

            if run_detection:
                detections = self.detector.detect(frame)
                detections = [d for d in detections if d['class_name'] == 'person']

                if len(detections) > best_frame_detections:
                    best_frame_detections = len(detections)
                    best_frame = frame.copy()
                    best_frame_det = list(detections)

                crops = []
                for det in detections:
                    x1, y1, x2, y2 = det['bbox']
                    fh, fw = frame.shape[:2]
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(fw, x2), min(fh, y2)
                    det['bbox'] = (x1, y1, x2, y2)
                    if x2 > x1 and y2 > y1:
                        crops.append(frame[y1:y2, x1:x2])
                    else:
                        crops.append(None)

                if self.enable_reid and self.appearance_extractor:
                    embeddings = self.appearance_extractor.extract_batch(crops)
                else:
                    embeddings = [None] * len(detections)

                frame_det_data = []

                local_ids  = [d['track_id'] for d in detections]
                bboxes_all = [d['bbox'] for d in detections]
                fh_fw      = (frame.shape[1], frame.shape[0])   # (width, height)

                if self.enable_reid and self.gallery:
                    reid_results = self.gallery.match_batch(
                        embeddings, local_ids, bboxes_all, frame_idx, frame_wh=fh_fw
                    )
                else:
                    reid_results = [(lid, 1.0) for lid in local_ids]

                for i, det in enumerate(detections):
                    x1, y1, x2, y2 = det['bbox']
                    if x2 <= x1 or y2 <= y1:
                        continue

                    track_id  = det['track_id']
                    crop      = crops[i]
                    global_id, reid_conf = reid_results[i]

                    pose_data = self.pose_extractor.extract(crop) if crop is not None else None

                    if track_id not in self.motion_analyzers:
                        self.motion_analyzers[track_id] = MotionAnalyzer()
                    motion_score = self.motion_analyzers[track_id].analyze(crop) if crop is not None else 0.0

                    gaze_s = pose_data['gaze_score'] if pose_data else 0.5
                    posture_s = pose_data['posture_score'] if pose_data else 0.5
                    head_down = pose_data.get('head_down', False) if pose_data else False
                    writing = pose_data.get('writing_posture', False) if pose_data else False

                    activity = ''
                    if writing:
                        engagement_score = min(1.0, 0.85 + (0.1 * posture_s) + (0.05 * (1.0 - motion_score)))
                        activity = 'WRITING'
                    elif head_down and motion_score < 0.3:
                        engagement_score = min(1.0, 0.75 + (0.15 * posture_s) + (0.1 * gaze_s))
                        activity = 'FOCUSED'
                    else:
                        engagement_score = (0.5 * gaze_s) + (0.3 * posture_s) + (0.2 * (1.0 - min(motion_score, 0.5) * 2))

                    cls_name = det['class_name']
                    if "raising_hand" in cls_name.lower():
                        engagement_score = min(1.0, engagement_score + 0.2)
                    if "sleeping" in cls_name.lower():
                        engagement_score = max(0.0, engagement_score - 0.3)

                    engagement_score = self._smooth_engagement(global_id, engagement_score)

                    self.logs.append({
                        "frame": frame_idx,
                        "timestamp": timestamp,
                        "local_track_id": track_id,
                        "global_student_id": global_id,
                        "reid_confidence": round(reid_conf, 3),
                        "class_name": cls_name,
                        "gaze_score": gaze_s,
                        "posture_score": posture_s,
                        "motion_score": motion_score,
                        "head_down": head_down,
                        "writing_posture": writing,
                        "activity": activity,
                        "engagement_score": engagement_score,
                    })

                    frame_det_data.append({
                        "bbox": (x1, y1, x2, y2),
                        "track_id": track_id,
                        "global_id": global_id,
                        "reid_conf": reid_conf,
                        "engagement": engagement_score,
                        "gaze": gaze_s,
                        "posture": posture_s,
                        "activity": activity,
                    })

                last_frame_det_data = frame_det_data
            else:
                frame_det_data = last_frame_det_data

            annotated_frame = self._draw_premium_overlay(frame, frame_det_data)

            if video_writer is not None:
                video_writer.write(annotated_frame)

            if self.save_frames and run_detection and frame_idx % 150 == 1 and last_frame_det_data:
                self._save_annotated_frame(annotated_frame, [
                    {"track_id": d["global_id"], "bbox": d["bbox"]} for d in last_frame_det_data
                ], frame_idx, frames_dir)

            if display:
                cv2.imshow("EMERGENCE Vision Layer", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        if self.save_frames and best_frame is not None and best_frame_det:
            best_annotated = self._draw_premium_overlay(best_frame, [
                {"bbox": d['bbox'], "track_id": d['track_id'], "global_id": d['track_id'],
                 "reid_conf": 1.0, "engagement": 0.5, "gaze": 0.5, "posture": 0.5, "activity": ""}
                for d in best_frame_det
            ])
            self._save_annotated_frame(best_annotated, [
                {"track_id": d["track_id"], "bbox": d["bbox"]} for d in best_frame_det
            ], "best", frames_dir)

        if video_writer is not None:
            video_writer.release()
            print(f"Annotated video saved to: {video_out_path}")

        elapsed_total = time.time() - proc_start
        print(f"Processed {frame_idx} frames in {elapsed_total:.1f}s ({frame_idx/elapsed_total:.1f} FPS)")

        if self.gallery:
            stats = self.gallery.get_stats()
            print(f"ReID Stats: {stats['total_global_ids']} unique students identified | "
                  f"{stats['active_global_ids']} currently active | "
                  f"{stats['local_id_mappings']} local→global mappings")
            if self.gallery_path:
                self.gallery.save(self.gallery_path)

        self.cleanup()

    def _save_annotated_frame(self, frame, detections, frame_label, save_dir):
        annotated = frame.copy()
        for det in detections:
            track_id = det['track_id']
            x1, y1, x2, y2 = det['bbox']
            h, w = annotated.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 2)
            label = f"G:{track_id}"
            font_scale = 0.7
            thickness = 2
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            cv2.rectangle(annotated, (x1, y1 - th - 10), (x1 + tw + 6, y1), (0, 255, 255), -1)
            cv2.putText(annotated, label, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, (0, 0, 0), thickness)
        save_path = save_dir / f"frame_{frame_label}.jpg"
        cv2.imwrite(str(save_path), annotated)
        self.saved_frame_paths.append(str(save_path))

    def process_batch(self, video_paths, output_csv="test_engagement_log.csv", display=False):
        print(f"Processing {len(video_paths)} videos in batch mode...")
        all_logs = []
        for i, video_path in enumerate(video_paths):
            print(f"\n  [{i+1}/{len(video_paths)}] Processing: {Path(video_path).name}")
            self.cap.release()
            self.cap = cv2.VideoCapture(str(video_path))
            if not self.cap.isOpened():
                print(f"    Error: Could not open {video_path}")
                continue
            self.logs = []
            self.motion_analyzers = {}
            self.engagement_history = {}
            self.detector = StudentDetector()
            self.frame_save_tag = f"test_{i}"
            self.process(display=display)
            all_logs.extend(self.logs)
            print(f"    Logged {len(self.logs)} entries")
        if all_logs:
            df = pd.DataFrame(all_logs)
            output_path = OUTPUT_DIR / output_csv
            df.to_csv(output_path, index=False)
            print(f"\nSaved combined test engagement log to {output_path}")
            return df
        return None

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.pose_extractor.close()
        if self.logs:
            df = pd.DataFrame(self.logs)
            df.to_csv(self.output_csv, index=False)
            print(f"Saved engagement logs to {self.output_csv}")
        else:
            print("No data logged.")


if __name__ == "__main__":
    pipeline = VisionPipeline(source=0, enable_reid=True)
    pipeline.process()
