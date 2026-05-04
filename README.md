# 🧠 EMERGENCE: Intelligent Classroom Learning System

An AI-powered system that transforms traditional classrooms into adaptive, student-centric learning environments using **Computer Vision**, **Unsupervised Machine Learning**, and **Generative AI**.

## Architecture

```
Vision Layer (Perception) → Reasoning Layer (Analysis) → Generative Layer (Adaptation)
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Vision** | YOLO + MediaPipe + OpenCV | Detect students, estimate pose/gaze, compute motion energy |
| **Reasoning** | Pandas + K-Means (Scikit-learn) | Cluster students into engagement profiles |
| **Generation** | Google Gemini Pro | Create personalized learning modules & micro-tests |

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

### 3. Run the Full Pipeline (CLI)
```bash
# With webcam
python main.py --source 0 --topic "Photosynthesis"

# With video file
python main.py --source data/input/iNPUT.mp4 --topic "General Science"

# Skip vision (use existing logs)
python main.py --skip-vision --topic "General Science"
```

### 4. Run the Dashboard
```bash
streamlit run app.py
```

## Project Structure
```
EMERGENCE/
├── main.py                 # CLI entry point
├── app.py                  # Streamlit dashboard
├── src/
│   ├── config.py           # Global configuration
│   ├── vision/
│   │   ├── detector.py     # YOLO student detection & tracking
│   │   ├── pose.py         # Pose & gaze estimation
│   │   ├── motion.py       # Optical flow motion analysis
│   │   └── pipeline.py     # Vision pipeline orchestrator
│   ├── reasoning/
│   │   ├── analytics.py    # K-Means clustering & profiling
│   │   └── assessment.py   # Micro-test generation (Gemini)
│   └── generation/
│       ├── curriculum.py   # Personalized module generation (Gemini)
│       └── renderer.py     # Content file renderer
├── data/
│   ├── input/              # Input videos
│   ├── output/             # Engagement logs & generated modules
│   └── profiles/           # Student cluster profiles
└── requirements.txt
```

## Output
- `data/output/engagement_log.csv` — Frame-by-frame engagement metrics
- `data/profiles/student_profiles.csv` — Clustered student profiles
- `data/output/module_*.md` — Personalized learning modules per student
