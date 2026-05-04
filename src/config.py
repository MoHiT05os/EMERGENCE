import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
PROFILES_DIR = DATA_DIR / "profiles"
MAPPING_FRAMES_DIR = OUTPUT_DIR / "mapping_frames"
TEST_VIDEO_DIR = INPUT_DIR / "test_video"

TEST_SCORES_PATH = INPUT_DIR / "normalized_student_data.xlsx"
STUDENT_MAPPING_PATH = PROFILES_DIR / "student_mapping.csv"

TEST1_MAX_MARKS = 20
TEST2_MAX_MARKS = 20
TOTAL_MAX_MARKS = TEST1_MAX_MARKS + TEST2_MAX_MARKS

for d in [DATA_DIR, MODELS_DIR, INPUT_DIR, OUTPUT_DIR, PROFILES_DIR, MAPPING_FRAMES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

DEFAULT_MODEL_NAME = "yolo26m.pt"
POSE_MODEL_NAME = "yolo11n-pose.pt"

YOLO_MODEL_PATH = DEFAULT_MODEL_NAME

CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45
