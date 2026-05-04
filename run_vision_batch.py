import sys
from pathlib import Path

# Add root to sys path
sys.path.append(str(Path(__file__).resolve().parent))
from src.vision.pipeline import VisionPipeline

print("Processing Video 4 for Computer Core...")
pipeline1 = VisionPipeline(
    source="data/input/Test_video/CLASS_RECORDINGS/Video_4.mp4",
    output_csv="engagement_log_Computer_Core.csv",
    frame_save_tag="Computer_Core"
)
pipeline1.process(display=False)

print("Processing Video 3 for Data Structures...")
pipeline2 = VisionPipeline(
    source="data/input/Test_video/CLASS_RECORDINGS/Video_3.mp4",
    output_csv="engagement_log_Data_Structures.csv",
    frame_save_tag="Data_Structures"
)
pipeline2.process(display=False)
