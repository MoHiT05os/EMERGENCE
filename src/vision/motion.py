import cv2
import numpy as np

class MotionAnalyzer:
    def __init__(self):
        self.prev_gray = None
    
    def analyze(self, frame_crop):
        if frame_crop is None or frame_crop.size == 0:
            return 0.0
            
        gray = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2GRAY)
        
        if self.prev_gray is None:
            self.prev_gray = gray
            return 0.0
        
        if gray.shape != self.prev_gray.shape:
            self.prev_gray = cv2.resize(self.prev_gray, (gray.shape[1], gray.shape[0]))
            
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray, None, 
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        avg_motion = np.mean(mag)
        
        self.prev_gray = gray
        
        motion_score = min(avg_motion / 5.0, 1.0)
        
        return motion_score

    def reset(self):
        self.prev_gray = None
