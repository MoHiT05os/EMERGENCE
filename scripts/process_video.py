import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vision.pipeline import VisionPipeline

INPUT_VIDEO = Path(r"C:\Users\TheRealMohitYadav\Documents\EMERGENCE\data\input\Test_video\Main_Test.mp4")

if not INPUT_VIDEO.exists():
    print(f"ERROR: Video not found at {INPUT_VIDEO}")
    sys.exit(1)

print(f"Processing video: {INPUT_VIDEO}")
print(f"File size: {INPUT_VIDEO.stat().st_size / (1024*1024):.1f} MB")

pipeline = VisionPipeline(
    source=str(INPUT_VIDEO),
    output_csv="engagement_log_Main_Test.csv",
    save_frames=True,
    frame_save_tag="Main_Test",
    save_video=True,
)

pipeline.process(display=False)

print("\nDone! Check data/output/ for:")
print("  - annotated_Main_Test.mp4  (annotated video with bounding boxes & student IDs)")
print("  - engagement_log_Main_Test.csv  (per-frame engagement data)")
