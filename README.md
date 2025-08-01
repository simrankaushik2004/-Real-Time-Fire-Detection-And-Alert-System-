Real-Time Fire Detection & Alert System


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
pip install opencv-python pygame numpy gtts flask twilio ultralytics

The following image shows the real-time detection of fire using our YOLO-based model. Upon detection, the system triggers sirens, sends emergency alerts, and activates evacuation instructions.



 <img width="1008" height="717" alt="image" src="https://github.com/user-attachments/assets/7c693bd3-5f94-4702-89b2-36770e23d90a" />

🔥 If fire is detected - It will show in a rectangular block :

 <img width="381" height="296" alt="Screenshot 2025-04-28 205556" src="https://github.com/user-attachments/assets/40b5067e-907d-439e-a79b-cf28551f650e" />


🔥 If fire is detected - It will show in a rectangular block :
<img width="964" height="617" alt="Screenshot 2025-08-01 232428" src="https://github.com/user-attachments/assets/52265cbf-a915-444d-8b6c-b16d87e865a8" />



🚨 Local Alarm: Play a siren sound using Pygame:
<img width="947" height="287" alt="Screenshot 2025-04-28 202937" src="https://github.com/user-attachments/assets/870ec671-7c0f-4fd4-92c5-908679ae9ac7" />




📞📱✉🌐Remote Alert: Send SMS, calls, or app notifications to registered emergency contacts with the location:
![b1888c70-056e-4259-91d2-bd4da6b6c52c](https://github.com/user-attachments/assets/4a5e0230-45fb-4bee-a09b-b22fd2715823)












