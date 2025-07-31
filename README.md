This project is a real-time fire detection and alerting system built using YOLO (You Only Look Once) for object detection, Flask for location integration, and Twilio for emergency SMS and call alerts. It also features camera tampering detection, severity classification, and bilingual evacuation alerts using Google Text-to-Speech (Hindi + English).

🚀 Features
✅ Real-time fire detection using YOLOv8

📊 Severity classification: LOW, MEDIUM, HIGH

🔁 Frame skipping and optimization for fast detection

🔉 Siren and bilingual evacuation announcements (Hindi & English)

📱 Twilio-based emergency SMS alerts and voice calls

📷 Camera tampering detection (black screen, frozen, unplugged)

🌐 Location-based alert with OpenStreetMap link

🧠 Flickering brightness logic to avoid false positives

🖥️ Tech Stack
Computer Vision: OpenCV, YOLOv8 (ultralytics)

Audio Alerts: gTTS, pygame

Backend: Flask

Communication: Twilio SMS & Voice API

Language Support: Hindi 🇮🇳 and English 🇺🇸

Deployment: Python script (can be integrated with GUI/web interface)

📦 Requirements
Install dependencies using pip:

bash
Copy
Edit
pip install opencv-python pygame numpy gtts flask twilio ultralytics
