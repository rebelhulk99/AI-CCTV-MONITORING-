from ultralytics import YOLO
import cv2
import telebot
from telebot import types
# Load YOLOv8 model
model = YOLO('yolov8n.pt')  # 'n' is nano version

# Telegram Bot Setup
TOKEN = '8135316387:AAFhkOAt20mc1jBbPS_C2W1sa8EqQAolzPU'
CHAT_ID = '7797455582'
bot = telebot.TeleBot(TOKEN)

def send_telegram_alert(image_path):
    with open(image_path, 'rb') as photo:
        bot.send_photo(CHAT_ID, photo, caption="⚠️ Suspicious Activity Detected!")

# Initialize video capture
# For CCTV RTSP stream: replace with your RTSP URL
cap = cv2.VideoCapture("rtsp://admin:admin%40123@192.168.0.103:554/cam/realmonitor?channel=2&subtype=0", cv2.CAP_FFMPEG)

#cap = cv2.VideoCapture(0)  # For webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    pocket_y = None  # Initialize pocket_y to handle scope

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])  # Class index
            label = model.names[cls]  # Converts class index to label

            if label == 'person':
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

                # Define pocket region (lower quarter of person box)
                pocket_y = y2 - ((y2 - y1) // 4)
                cv2.rectangle(frame, (x1, pocket_y), (x2, y2), (255,0,0), 2)

            elif label == 'hand' and pocket_y is not None:
                hx1, hy1, hx2, hy2 = map(int, box.xyxy[0])
                hand_center_y = (hy1 + hy2) // 2

                if hand_center_y > pocket_y:
                    print("Hand near pocket detected!")

                    snapshot_path = 'suspicious_activity.jpg'
                    cv2.imwrite(snapshot_path, frame)
                    send_telegram_alert(snapshot_path)

    cv2.imshow('AI CCTV Monitoring', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


