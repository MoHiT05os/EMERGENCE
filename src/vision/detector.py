from ultralytics import YOLO
import cv2
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import YOLO_MODEL_PATH, CONFIDENCE_THRESHOLD

TRACKER_CONFIG = Path(__file__).resolve().parent / "tracker_config.yaml"

class StudentDetector:
    def __init__(self, model_path=None):
        self.model_path = model_path if model_path else YOLO_MODEL_PATH
        print(f"Loading YOLO model from: {self.model_path}")
        self.model = YOLO(self.model_path)
        self.tracker_cfg = "botsort.yaml"
        print(f"Using tracker config: {self.tracker_cfg}")

    def detect(self, frame):
        results = self.model.track(
            frame,
            persist=True,
            verbose=False,
            conf=CONFIDENCE_THRESHOLD,
            tracker=self.tracker_cfg,
            iou=0.5,
        )

        detections = []
        if results and len(results) > 0:
            result = results[0]
            if result.boxes:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    cls_id = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())

                    track_id = -1
                    if box.id is not None:
                        track_id = int(box.id[0].cpu().numpy())

                    class_name = self.model.names[cls_id]

                    detections.append({
                        "bbox": (int(x1), int(y1), int(x2), int(y2)),
                        "class_id": cls_id,
                        "class_name": class_name,
                        "conf": conf,
                        "track_id": track_id
                    })

        return detections

if __name__ == "__main__":
    detector = StudentDetector()
    print("Model loaded successfully.")
