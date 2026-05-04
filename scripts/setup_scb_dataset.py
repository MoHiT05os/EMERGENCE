import argparse
import os
import sys
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCB_DIR = DATA_DIR / "scb_dataset"
MODELS_DIR = DATA_DIR / "models"


def download_scb_dataset():
    print("=" * 60)
    print("SCB Dataset Download")
    print("=" * 60)
    
    try:
        from huggingface_hub import hf_hub_download, snapshot_download
    except ImportError:
        print("Installing huggingface_hub...")
        os.system(f"{sys.executable} -m pip install huggingface_hub")
        from huggingface_hub import hf_hub_download, snapshot_download
    
    SCB_DIR.mkdir(parents=True, exist_ok=True)
    
    repo_id = "wintonYF/SCB-Dataset"
    
    folders_to_download = [
        "SCB5-Handrise-Read-write-2024-9-17",
        "SCB5-Discuss-2024-9-17",
        "SCB_BowTurnHead_20250509",
    ]
    
    print("\n[1/2] Downloading behavior datasets...")
    for folder in folders_to_download:
        print(f"\n  Downloading: {folder}...")
        try:
            snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                allow_patterns=f"{folder}/*",
                local_dir=str(SCB_DIR),
            )
            print(f"  ✓ {folder} downloaded successfully")
        except Exception as e:
            print(f"  ✗ Error downloading {folder}: {e}")
    
    yolo_zip = SCB_DIR / "YOLO.zip"
    if not yolo_zip.exists():
        print("\n[2/2] Downloading pre-trained YOLO weights (5.33 GB)...")
        print("  This may take a while depending on your connection...")
        try:
            hf_hub_download(
                repo_id=repo_id,
                repo_type="dataset",
                filename="YOLO.zip",
                local_dir=str(SCB_DIR),
            )
            print("  ✓ YOLO.zip downloaded")
            
            print("  Extracting YOLO.zip...")
            with zipfile.ZipFile(yolo_zip, 'r') as zf:
                zf.extractall(SCB_DIR / "YOLO_pretrained")
            print("  ✓ Extracted to SCB_DIR/YOLO_pretrained/")
        except Exception as e:
            print(f"  ✗ Error downloading YOLO.zip: {e}")
            print("  You can manually download from:")
            print("  https://huggingface.co/datasets/wintonYF/SCB-Dataset/resolve/main/YOLO.zip")
    else:
        print("\n[2/2] YOLO.zip already exists, skipping download.")
    
    print("\n✓ Dataset download complete!")
    print(f"  Location: {SCB_DIR}")
    return True


def create_dataset_yaml():
    yaml_path = SCB_DIR / "scb_classroom.yaml"
    
    yaml_content = f"""path: {SCB_DIR}
train: images/train
val: images/val

names:
  0: hand_raising
  1: reading
  2: writing
  3: discussing
  4: turning_head
  5: bowing_head
  6: sleeping
  7: standing
"""
    
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    
    print(f"✓ Created dataset YAML: {yaml_path}")
    return yaml_path


def train_custom_yolo(epochs=50, imgsz=640, batch=8):
    print("=" * 60)
    print("Custom YOLO Training for Classroom Behaviors")
    print("=" * 60)
    
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Error: ultralytics not installed. Run: pip install ultralytics")
        return False
    
    yaml_path = create_dataset_yaml()
    
    base_model = "yolo11n.pt"
    print(f"\nBase model: {base_model}")
    print(f"Dataset: {yaml_path}")
    print(f"Epochs: {epochs}")
    print(f"Image size: {imgsz}")
    print(f"Batch size: {batch}")
    
    model = YOLO(base_model)
    
    print("\nStarting training...")
    results = model.train(
        data=str(yaml_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name="emergence_classroom",
        project=str(MODELS_DIR / "training"),
        exist_ok=True,
        patience=10,
        save_period=10,
        plots=True,
        verbose=True,
    )
    
    best_model_src = MODELS_DIR / "training" / "emergence_classroom" / "weights" / "best.pt"
    best_model_dst = MODELS_DIR / "emergence_classroom_best.pt"
    
    if best_model_src.exists():
        shutil.copy2(best_model_src, best_model_dst)
        print(f"\n✓ Best model saved to: {best_model_dst}")
    
    print("\n✓ Training complete!")
    return True


def main():
    parser = argparse.ArgumentParser(description="SCB Dataset & YOLO Training Setup")
    parser.add_argument("--download", action="store_true", help="Download SCB dataset")
    parser.add_argument("--train", action="store_true", help="Train custom YOLO model")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs (default: 50)")
    parser.add_argument("--batch", type=int, default=8, help="Batch size (default: 8)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size (default: 640)")
    
    args = parser.parse_args()
    
    if not args.download and not args.train:
        parser.print_help()
        print("\nPlease specify --download, --train, or both.")
        return
    
    if args.download:
        download_scb_dataset()
    
    if args.train:
        train_custom_yolo(
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
        )


if __name__ == "__main__":
    main()
