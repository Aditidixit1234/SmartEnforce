# VioSense Model Performance Metrics
# Evaluated on COCO128 dataset

METRICS = {
    'model': 'YOLOv8n',
    'dataset': 'COCO128',
    'image_size': 640,
    'mAP50': 0.6054,
    'mAP50_95': 0.4454,
    'precision': 0.6385,
    'recall': 0.5361,
    'inference_speed': '70.2ms per image',
    'device': 'CPU'
}

def print_metrics():
    print("="*50)
    print("VIOSENSE MODEL PERFORMANCE REPORT")
    print("="*50)
    print(f"Model        : {METRICS['model']}")
    print(f"mAP50        : {METRICS['mAP50']*100:.1f}%")
    print(f"mAP50-95     : {METRICS['mAP50_95']*100:.1f}%")
    print(f"Precision    : {METRICS['precision']*100:.1f}%")
    print(f"Recall       : {METRICS['recall']*100:.1f}%")
    print(f"Speed        : {METRICS['inference_speed']}")
    print("="*50)

if __name__ == "__main__":
    print_metrics()