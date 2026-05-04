from ultralytics import YOLO
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import POSE_MODEL_NAME

class PoseExtractor:
    def __init__(self):
        print(f"Loading Pose model: {POSE_MODEL_NAME}...")
        self.model = YOLO(POSE_MODEL_NAME)
        
    def extract(self, frame_crop):
        if frame_crop is None or frame_crop.size == 0:
            return None
            
        results = self.model.predict(frame_crop, verbose=False, conf=0.3)
        
        gaze_score = 0.5
        posture_score = 0.5
        head_down = False
        writing_posture = False
        
        if results and results[0].keypoints is not None:
            kpts = results[0].keypoints.data
            
            if kpts.shape[0] > 0 and kpts.shape[1] > 0:
                nose = kpts[0, 0]
                l_eye = kpts[0, 1]
                r_eye = kpts[0, 2]
                l_ear = kpts[0, 3]
                r_ear = kpts[0, 4]
                l_sh = kpts[0, 5]
                r_sh = kpts[0, 6]
                l_elbow = kpts[0, 7]
                r_elbow = kpts[0, 8]
                l_wrist = kpts[0, 9]
                r_wrist = kpts[0, 10]
                
                if nose[2] > 0.3:
                    crop_h = frame_crop.shape[0]
                    nose_y_ratio = float(nose[1]) / crop_h if crop_h > 0 else 0.5
                    
                    if nose_y_ratio > 0.45:
                        head_down = True
                
                if l_ear[2] > 0.5 and r_ear[2] > 0.5:
                    ear_width = abs(float(l_ear[0]) - float(r_ear[0]))
                    ear_center_x = (float(l_ear[0]) + float(r_ear[0])) / 2
                    nose_offset = abs(ear_center_x - float(nose[0]))
                    
                    if ear_width > 0:
                        yaw_ratio = nose_offset / ear_width
                        gaze_score = max(0.0, 1.0 - (yaw_ratio * 1.5))
                elif l_ear[2] > 0.3 or r_ear[2] > 0.3:
                    visible_ear = l_ear if l_ear[2] > r_ear[2] else r_ear
                    if nose[2] > 0.3 and visible_ear[2] > 0.3:
                        gaze_score = 0.55
                
                if head_down:
                    gaze_score = max(gaze_score, 0.7)
                
                wrist_near_desk = False
                elbow_visible = False
                
                if l_wrist[2] > 0.3 or r_wrist[2] > 0.3:
                    crop_h = frame_crop.shape[0]
                    for wrist in [l_wrist, r_wrist]:
                        if wrist[2] > 0.3:
                            wrist_y_ratio = float(wrist[1]) / crop_h if crop_h > 0 else 0
                            if wrist_y_ratio > 0.5:
                                wrist_near_desk = True
                
                if l_elbow[2] > 0.3 or r_elbow[2] > 0.3:
                    elbow_visible = True
                
                if head_down and wrist_near_desk:
                    writing_posture = True
                    gaze_score = max(gaze_score, 0.85)
                
                if l_sh[2] > 0.5 and r_sh[2] > 0.5:
                    shoulder_slope = abs(float(l_sh[1]) - float(r_sh[1]))
                    shoulder_width = abs(float(l_sh[0]) - float(r_sh[0])) + 1e-6
                    
                    rel_slope = shoulder_slope / shoulder_width
                    
                    if rel_slope < 0.15:
                        posture_score = 1.0
                    elif rel_slope < 0.25:
                        posture_score = 0.75
                    elif rel_slope < 0.35:
                        posture_score = 0.5
                    else:
                        posture_score = 0.3
                    
                    if writing_posture:
                        posture_score = max(posture_score, 0.85)
                    elif head_down and elbow_visible:
                        posture_score = max(posture_score, 0.7)
                elif head_down:
                    posture_score = 0.65

        return {
            "gaze_score": float(gaze_score),
            "posture_score": float(posture_score),
            "head_down": head_down,
            "writing_posture": writing_posture,
        }

    def close(self):
        pass
