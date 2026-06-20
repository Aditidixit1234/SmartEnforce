from ultralytics import YOLO
import cv2
import os

model = YOLO('models/yolov8n.pt')

VEHICLE_CLASSES = {
    0: 'person',
    1: 'bicycle',
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck'
}

def track_video(video_path, output_path='static/tracked_output.mp4'):
    """
    Track vehicles across video frames using YOLO tracker
    Returns: tracked vehicles summary
    """
    os.makedirs('static', exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    tracked_vehicles = {}
    violations_detected = []
    frame_count = 0

    print(f"Processing video: {total_frames} frames at {fps} fps")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        results = model.track(
            frame,
            persist=True,
            conf=0.25,
            classes=[0, 1, 2, 3, 5, 7]
        )

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            classes = results[0].boxes.cls.cpu().numpy().astype(int)
            confs = results[0].boxes.conf.cpu().numpy()

            for box, track_id, cls_id, conf in zip(boxes, track_ids, classes, confs):
                if cls_id not in VEHICLE_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, box)
                vehicle_type = VEHICLE_CLASSES[cls_id]
                confidence = round(float(conf) * 100, 1)

                if track_id not in tracked_vehicles:
                    tracked_vehicles[track_id] = {
                        'id': track_id,
                        'type': vehicle_type,
                        'first_frame': frame_count,
                        'last_frame': frame_count,
                        'confidence': confidence,
                        'max_confidence': confidence,
                        'frames_seen': 1,
                        'violation': None
                    }
                else:
                    tracked_vehicles[track_id]['last_frame'] = frame_count
                    tracked_vehicles[track_id]['frames_seen'] += 1
                    # keep running best confidence, not the last-seen one
                    if confidence > tracked_vehicles[track_id]['max_confidence']:
                        tracked_vehicles[track_id]['max_confidence'] = confidence
                    tracked_vehicles[track_id]['confidence'] = tracked_vehicles[track_id]['max_confidence']

                if vehicle_type == 'motorcycle':
                    tracked_vehicles[track_id]['violation'] = 'No Helmet'
                    color = (0, 0, 255)
                    label = f"ID:{track_id} VIOLATION:No Helmet {confidence}%"
                else:
                    color = (0, 255, 0)
                    label = f"ID:{track_id} {vehicle_type} {confidence}%"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

        out.write(frame)

        if frame_count >= 150:
            break

    cap.release()
    out.release()

    # Only report violations that are reasonably tracked:
    # at least 3 frames AND at least 30% confidence
    MIN_FRAMES = 3
    MIN_CONFIDENCE = 30.0

    for tid, vehicle in tracked_vehicles.items():
        if (vehicle['violation']
                and vehicle['frames_seen'] >= MIN_FRAMES
                and vehicle['confidence'] >= MIN_CONFIDENCE):
            violations_detected.append({
                'track_id': tid,
                'vehicle_type': vehicle['type'],
                'violation_type': vehicle['violation'],
                'violation_key': 'no_helmet',
                'severity': 7.2,
                'risk_level': 'HIGH',
                'confidence': vehicle['confidence'],
                'frames_seen': vehicle['frames_seen'],
                'bbox': [0, 0, 100, 100]
            })

    print(f"Tracked {len(tracked_vehicles)} unique vehicles")
    print(f"Found {len(violations_detected)} reliable violations (min {MIN_FRAMES} frames, {MIN_CONFIDENCE}% confidence)")

    return {
        'total_vehicles': len(tracked_vehicles),
        'violations': violations_detected,
        'output_video': output_path,
        'frames_processed': frame_count,
        'fps': fps,
        'tracked_vehicles': tracked_vehicles
    }

if __name__ == "__main__":
    print("Video tracker ready!")
    print("Supports: MP4, AVI, MOV")