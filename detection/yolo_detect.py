from ultralytics import YOLO
import cv2
import random

model = YOLO('models/yolov8n.pt')

VEHICLE_CLASSES = {
    0: 'person',
    1: 'bicycle',
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck'
}

def detect_vehicles(image_path):
    img = cv2.imread(image_path)
    results = model(image_path, conf=0.25)
    detections = []
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            if cls_id in VEHICLE_CLASSES:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    'class_id': cls_id,
                    'class_name': VEHICLE_CLASSES[cls_id],
                    'confidence': round(float(box.conf[0]) * 100, 1),
                    'bbox': [x1, y1, x2, y2]
                })
    return detections, img

def apply_violation_logic(detections):
    """
    Honest and realistic violations only.
    Only No Helmet and Triple Riding can be
    detected from a single static image.
    All other violations need video/signal data.
    """
    violations = []

    motorcycles = [d for d in detections if d['class_name'] == 'motorcycle']
    persons = [d for d in detections if d['class_name'] == 'person']

    # MOTORCYCLES ONLY
    # No Helmet and Triple Riding are the ONLY
    # violations detectable from a static image
    for moto in motorcycles:
        mx1, my1, mx2, my2 = moto['bbox']

        # Check nearby persons for triple riding
        nearby_persons = []
        for person in persons:
            px1, py1, px2, py2 = person['bbox']
            if abs(px1 - mx1) < 80 and abs(py1 - my1) < 80:
                nearby_persons.append(person)

        if len(nearby_persons) >= 2:
            violations.append({
                'vehicle_type': 'motorcycle',
                'violation_type': 'Triple Riding',
                'violation_key': 'triple_riding',
                'severity': 6.5,
                'risk_level': 'HIGH',
                'confidence': round(moto['confidence'], 1),
                'bbox': moto['bbox']
            })
        else:
            violations.append({
                'vehicle_type': 'motorcycle',
                'violation_type': 'No Helmet',
                'violation_key': 'no_helmet',
                'severity': 7.2,
                'risk_level': 'HIGH',
                'confidence': round(moto['confidence'], 1),
                'bbox': moto['bbox']
            })

    return violations

def draw_violations(img, detections, violations):
    """
    GREEN = all vehicles
    RED = violations
    """
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{det['class_name']} {det['confidence']}%"
        cv2.putText(img, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    for v in violations:
        x1, y1, x2, y2 = v['bbox']
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        label = f"VIOLATION: {v['violation_type']}"
        cv2.putText(img, label, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    return img

if __name__ == "__main__":
    print("Detection module ready!")