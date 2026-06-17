import urllib.request
import os

os.makedirs("models", exist_ok=True)

print("Downloading helmet detection model...")

# Public YOLO helmet detection model
url = "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.pt"

urllib.request.urlretrieve(
    url,
    "models/yolov8n.pt",
    reporthook=lambda b, bs, ts: print(
        f"Progress: {min(100, int(b*bs*100/ts))}%",
        end='\r'
    )
)

print("\nDownload complete!")

# Test it
from ultralytics import YOLO
model = YOLO("models/yolov8n.pt")
print(f"Classes available: {len(model.names)}")
print("Model ready!")