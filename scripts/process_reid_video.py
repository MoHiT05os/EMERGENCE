import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vision.pipeline import VisionPipeline

INPUT_VIDEO = Path(r"C:\Users\TheRealMohitYadav\Documents\EMERGENCE\data\input\Test_video\rotate_one.mp4")
GALLERY_PATH = Path(r"C:\Users\TheRealMohitYadav\Documents\EMERGENCE\data\profiles\student_gallery.pkl")

if not INPUT_VIDEO.exists():
    print(f"ERROR: Video not found at {INPUT_VIDEO}")
    sys.exit(1)

print(f"Processing video: {INPUT_VIDEO}")
print(f"File size: {INPUT_VIDEO.stat().st_size / (1024*1024):.1f} MB")
print(f"ReID gallery path: {GALLERY_PATH}")
print("-" * 60)

pipeline = VisionPipeline(
    source=str(INPUT_VIDEO),
    output_csv="engagement_log_rotate_one.csv",
    save_frames=True,
    frame_save_tag="rotate_one",
    save_video=True,
    enable_reid=True,
    gallery_path=str(GALLERY_PATH),
)

pipeline.process(display=False, process_every_n=2)

print("\n" + "=" * 60)
print("DONE! Output files:")
print(f"  Video : data/output/annotated_rotate_one.avi")
print(f"  CSV   : data/output/engagement_log_rotate_one.csv")
print(f"  Gallery: {GALLERY_PATH}")
print("=" * 60)
print("\nIn the video look for:")
print("  G:1 = Global Student 1 (persistent across camera cuts)")
print("  L:X = Local ByteTrack ID (resets on camera change)")
print("  G-ID stays same even when L-ID changes = ReID working!")
