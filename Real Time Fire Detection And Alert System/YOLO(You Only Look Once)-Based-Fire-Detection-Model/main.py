import cv2
import time
import pygame
import numpy as np
import threading
from flask import Flask, request, jsonify
from ultralytics import YOLO
from gtts import gTTS
import io
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Flask app
app = Flask(__name__)

# Twilio configuration
#  make your own SID from twillio account this is not working 
ACCOUNT_SID = 'AC63a1d1c8a0204a404'
AUTH_TOKEN = 'a0decb196748f106'
TWILIO_PHONE_NUMBER = '+12392159779'
OWNER_PHONE = '+911234567892'
NEARBY_PHONES = ['+918287344433']
FIRE_STATION_PHONE = '+91833333333'
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms_alert(message, recipients):
    for number in recipients:
        try:
            message_obj = twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=number
            )
            print(f"✅ Message sent to {number}, SID: {message_obj.sid}")
        except Exception as e:
            print(f"❌ Failed to send to {number}: {e}")

def make_call_alert(to_number):
    try:
        response = VoiceResponse()
        response.say("Fire is detected at your location. Please evacuate immediately.", voice='alice', language='en-US')
        call = twilio_client.calls.create(
            twiml=response,
            to=to_number,
            from_=TWILIO_PHONE_NUMBER
        )
        print(f"✅ Call placed to {to_number}, SID: {call.sid}")
    except Exception as e:
        print(f"❌ Failed to call {to_number}: {e}")

pygame.mixer.init()
model = YOLO(r'C:\Users\simra\Desktop\Real Time Fire Detection And Alert System\YOLO(You Only Look Once)-Based-Fire-Detection-Model\fire.pt')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

fire_frame_count = 0
fire_threshold = 1  # Reduced threshold to detect fire on the first frame
prev_gray = None
siren_active = False

MOTION_PIXEL_CHANGE_THRESHOLD = 25
MOTION_AREA_RATIO_THRESHOLD = 0.1
MIN_FIRE_BOX_AREA = 100  # Reduced to detect smaller fire areas

tampering_active = False
previous_frame = None
previous_tampering_state = None

current_location = {"latitude": None, "longitude": None}
brightness_history = []
BRIGHTNESS_HISTORY_LEN = 10
FLICKER_STD_THRESHOLD = 7  # Slightly more sensitive

confidence_threshold = 0.7  # Increased confidence threshold for fire detection

def classify_fire_severity(fire_boxes):
    total_area = sum((x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in fire_boxes)
    if total_area > 60000:
        return "HIGH"
    elif total_area > 20000:
        return "MEDIUM"
    elif total_area > 0:
        return "LOW"
    else:
        return "NONE"

def evacuation_loop(severity):
    severity_hindi = {"LOW": "कम", "MEDIUM": "मध्यम", "HIGH": "उच्च"}
    severity_english = severity
    while siren_active:
        messages = [
            ('hi', f"आपकी सुरक्षा के लिए सूचना है कि भवन में {severity_hindi.get(severity, 'अज्ञात')} स्तर की आग का आसार मिला है। कृपया शांत रहें और निकासी द्वार की ओर बढ़ें।"),
            ('en', f"For your safety, a {severity_english} severity fire has been detected in the building. Please stay calm and proceed to the nearest exit.")
        ]
        for lang, text in messages:
            tts = gTTS(text=text, lang=lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.5)
            if not siren_active:
                break

def check_tampering(frame):
    global previous_frame, tampering_active, previous_tampering_state
    tampered = False
    reason = ""

    if frame is None:
        tampered = True
        reason = "Warning! Camera disconnected or not working."
    elif np.mean(frame) < 10:
        tampered = True
        reason = "Warning! Camera feed is blocked or covered."
    elif previous_frame is not None and np.array_equal(frame, previous_frame):
        tampered = True
        reason = "Warning! Camera feed is frozen."

    if tampered:
        print(f"🚨 {reason}")
        if not tampering_active:
            tampering_active = True
            threading.Thread(target=tampering_loop, args=(reason,)).start()
        previous_tampering_state = True

    if previous_tampering_state and not tampered:
        print("✅ Camera feed restored.")
        tampering_active = False
        previous_tampering_state = False
        tts = gTTS(text="Camera feed is restored.", lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

    previous_frame = frame

def tampering_loop(reason):
    while tampering_active:
        try:
            tts = gTTS(text=reason, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.5)
        except Exception as e:
            print(f"Error in tampering loop: {e}")
            break

def play_siren():
    siren_sound = pygame.mixer.Sound(r"C:\Users\simra\Downloads\sound-effect.mp3")
    pygame.mixer.Channel(1).play(siren_sound, loops=-1)
    print("🚨 Siren loop started.")

@app.route('/get-location', methods=['POST'])
def get_location():
    data = request.json
    lat = data.get("latitude")
    lon = data.get("longitude")
    if lat and lon:
        global current_location
        current_location = {"latitude": lat, "longitude": lon}
        print(f"✅ Location updated: {lat}, {lon}")
        return jsonify({
            "location": f"📍 {lat}, {lon}",
            "osm_link": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}"
        })
    else:
        return jsonify({"error": "GPS data not available"}), 400

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    try:
        check_tampering(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect fire using YOLO with the updated confidence threshold
        results = model.predict(frame, conf=confidence_threshold, vid_stride=1, show_labels=True, show_conf=False)
        fire_boxes = []

        for box, c in zip(results[0].boxes.xyxy, results[0].boxes.cls):
            if model.names[int(c)] == 'fire':
                coords = box.cpu().numpy().astype(int)
                x1, y1, x2, y2 = coords
                area = (x2 - x1) * (y2 - y1)
                if area >= MIN_FIRE_BOX_AREA:  # Only consider areas larger than the new minimum threshold
                    fire_boxes.append(coords)

        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        filtered_fire_boxes = []
        for box in fire_boxes:
            x1, y1, x2, y2 = box
            is_face_overlap = False
            for (fx, fy, fw, fh) in faces:
                if fx < x1 < fx+fw and fy < y1 < fy+fh:
                    is_face_overlap = True
                    break
            if not is_face_overlap:
                filtered_fire_boxes.append(box)

        flicker_detected = False
        for box in filtered_fire_boxes:
            x1, y1, x2, y2 = box
            fire_region = gray[y1:y2, x1:x2]
            if fire_region.size > 0:
                brightness = np.mean(fire_region)
                brightness_history.append(brightness)
                if len(brightness_history) > BRIGHTNESS_HISTORY_LEN:
                    brightness_history.pop(0)
                if np.std(brightness_history) > FLICKER_STD_THRESHOLD:
                    flicker_detected = True
                    break

        severity = classify_fire_severity(filtered_fire_boxes)
        if filtered_fire_boxes and flicker_detected:
            fire_frame_count = 1  # Fire is detected immediately upon meeting the threshold
        else:
            fire_frame_count = 0

        if fire_frame_count >= fire_threshold and not siren_active:
            print(f"🔥 REAL FIRE DETECTED! Severity: {severity}")
            siren_active = True
            threading.Thread(target=play_siren).start()
            threading.Thread(target=evacuation_loop, args=(severity,)).start()
            alert_message = f"🚨 Fire Alert: {severity} severity fire detected at your location. Evacuate immediately!"
            if severity in ["LOW", "MEDIUM"]:
                send_sms_alert(alert_message, [OWNER_PHONE] + NEARBY_PHONES)
            elif severity == "HIGH":
                send_sms_alert(alert_message, [OWNER_PHONE] + NEARBY_PHONES + [FIRE_STATION_PHONE])
                make_call_alert(FIRE_STATION_PHONE)
                make_call_alert(OWNER_PHONE)
            fire_frame_count = 0

        prev_gray = gray
        annotated_frame = results[0].plot()
        cv2.putText(annotated_frame, f"🔥 Fire Severity: {severity}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("🔥 Fire Detection", annotated_frame)

    except Exception as e:
        print(str(e))
        siren_active = False
        pygame.mixer.stop()
        continue

    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("🚩 Quitting and stopping alerts.")
        siren_active = False
        tampering_active = False
        pygame.mixer.stop()
        break

cap.release()
cv2.destroyAllWindows()
