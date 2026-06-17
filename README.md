markdown# VioSense — AI Traffic Enforcement Platform
### Gridlock Hackathon 2.0 | Theme 3: Computer Vision

An AI-powered traffic violation detection and enforcement platform that automatically identifies violations, generates evidence, and provides predictive analytics for law enforcement.

---

## Features

- Multi-Violation Detection (7 violation types)
- License Plate Recognition (Indian plates)
- Automated PDF Evidence Generation
- Repeat Offender Tracking
- City Safety Index
- Officer Deployment Planner
- Hotspot Prediction
- AI Weekly Summary Report

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Detection | YOLOv8n |
| Language | Python 3.10 |
| OCR | EasyOCR |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| AI Summary | Claude API |

---

## Performance Metrics

| Metric | Score |
|--------|-------|
| mAP50 | 60.5% |
| mAP50-95 | 44.5% |
| Precision | 63.8% |
| Recall | 53.6% |
| Inference Speed | 70.2ms |

---

## System Architecture
Traffic Image/Video

↓

Image Preprocessing

↓

YOLOv8 Detection

↓

Violation Classification

↓

License Plate OCR

↓

Evidence Generation (PDF)

↓

PostgreSQL Database

↓

Analytics Dashboard

↓

Hotspot Prediction

↓

Officer Deployment Planner

↓

AI Weekly Summary

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run analytics/dashboard.py
```

---

## Violations Detected

- No Helmet
- Triple Riding
- Wrong Side Driving
- Stop Line Violation
- Red Light Jump
- Illegal Parking
- No Seatbelt

---

## Project Structure
VioSense/

├── preprocessing/    # Image enhancement

├── detection/        # YOLO detection

├── ocr/              # Plate recognition

├── violation/        # Violation classifier

├── evidence/         # PDF generator

├── database/         # SQLite models

├── analytics/        # Dashboard + predictor

├── genai/            # AI summary

└── main_pipeline.py  # Main pipeline
---

Built for Gridlock Hackathon 2.0 — Flipkart & BTP
