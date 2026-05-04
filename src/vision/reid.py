import torch
import torchvision.transforms as T
import numpy as np
import cv2
from pathlib import Path
from vision.osnet import osnet_x1_0


class AppearanceExtractor:
    def __init__(self, device=None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading OSNet ReID backbone on {self.device}...")

        # Initialize OSNet architecture
        self.model = osnet_x1_0(num_classes=1000, pretrained=False)
        
        # Load weights specifically trained for Person ReID (Market-1501)
        weights_path = Path(__file__).resolve().parent.parent.parent / "data" / "models" / "osnet_x1_0_market1501.pth"
        if not weights_path.exists():
            print(f"WARNING: OSNet weights not found at {weights_path}. Feature extraction will be weak!")
        else:
            state_dict = torch.load(weights_path, map_location=self.device)
            
            # The pretrained weights might have a different number of classes in the classifier layer
            # We don't use the classifier layer for feature extraction, so we can ignore any size mismatches
            model_dict = self.model.state_dict()
            new_state_dict = {}
            for k, v in state_dict.items():
                if k.startswith('module.'):
                    k = k[7:]
                if k in model_dict and model_dict[k].size() == v.size():
                    new_state_dict[k] = v
            model_dict.update(new_state_dict)
            self.model.load_state_dict(model_dict)
            print("Successfully loaded OSNet Market-1501 pretrained weights.")

        self.model.eval()
        self.model.to(self.device)

        # OSNet standard spatial resolution
        self.transform = T.Compose([
            T.ToPILImage(),
            T.Resize((256, 128)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]),
        ])

        self._min_crop_size = 20

    def _color_histogram(self, crop_bgr):
        h, w = crop_bgr.shape[:2]
        # Focus mainly on the torso for clothing color, ignoring the head/background
        torso = crop_bgr[int(h * 0.2):int(h * 0.8), int(w * 0.1):int(w * 0.9)]
        if torso.size == 0:
            torso = crop_bgr

        hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
        h_hist = cv2.calcHist([hsv], [0], None, [32], [0, 180]).flatten()
        s_hist = cv2.calcHist([hsv], [1], None, [32], [0, 256]).flatten()
        v_hist = cv2.calcHist([hsv], [2], None, [16], [0, 256]).flatten()

        hist = np.concatenate([h_hist, s_hist, v_hist])
        norm = np.linalg.norm(hist)
        if norm > 0:
            hist = hist / norm
        return hist.astype(np.float32)

    @torch.no_grad()
    def _osnet_features(self, crop_bgr):
        crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        tensor = self.transform(crop_rgb).unsqueeze(0).to(self.device)
        # return_featuremaps=False returns the 512-dim embedding before the classifier
        features = self.model(tensor, return_featuremaps=False).squeeze().cpu().numpy().flatten()
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        return features.astype(np.float32)

    def extract(self, crop_bgr):
        if crop_bgr is None or crop_bgr.size == 0:
            return None
        h, w = crop_bgr.shape[:2]
        if h < self._min_crop_size or w < self._min_crop_size:
            return None
            
        try:
            # 85% OSNet Deep Features (highly trained for human ReID) + 15% Strict Color Region
            cnn_feat = self._osnet_features(crop_bgr)
            col_feat = self._color_histogram(crop_bgr)

            combined = np.concatenate([cnn_feat * 0.85, col_feat * 0.15])
            norm = np.linalg.norm(combined)
            if norm > 0:
                combined = combined / norm
            return combined.astype(np.float32)
            
        except Exception as e:
            print(f"Exception during extraction: {e}")
            return None

    @torch.no_grad()
    def extract_batch(self, crops_bgr):
        # We can implement a proper batch mechanism here if speed is needed
        # For simplicity and robust fallback, just loop over them
        return [self.extract(crop) for crop in crops_bgr]
