from flask import Flask, request
import requests
import os
import cv2
import numpy as np

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")

@app.route("/")
def home():
    return "Mangosteen AI Bot Running"

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json()
    
    events = body.get("events", [])
    
    for event in events:
        if event["type"] == "message":
            reply_token = event["replyToken"]

            # =====================
            # กรณีเป็นข้อความ
            # =====================
            if event["message"]["type"] == "text":
                user_message = event["message"]["text"]

                if "วิเคราะห์" in user_message:
                    reply_text(reply_token, "กรุณาส่งภาพมังคุดเพื่อตรวจสอบรอยช้ำ")
                else:
                    reply_text(reply_token, "พิมพ์คำว่า 'วิเคราะห์' เพื่อเริ่มต้น")

            # =====================
            # กรณีเป็นรูปภาพ
            # =====================
            elif event["message"]["type"] == "image":
                message_id = event["message"]["id"]

                image_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"

                headers = {
                    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
                }

                response = requests.get(image_url, headers=headers)

                image_path = "image.jpg"
                with open(image_path, "wb") as f:
                    f.write(response.content)

                # วิเคราะห์ภาพ
                result = analyze_image(image_path)

                reply_text(reply_token, result)

    return "OK"


# =====================
# ฟังก์ชันวิเคราะห์ภาพ (Simulation NIR)
# =====================
def analyze_image(path):
    img = cv2.imread(path)

    if img is None:
        return "ไม่สามารถอ่านภาพได้ กรุณาลองใหม่อีกครั้ง"

    # แปลงเป็น grayscale (จำลองการวิเคราะห์ความเข้มแสง)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # เพิ่ม contrast เล็กน้อย
    gray = cv2.equalizeHist(gray)

    mean_intensity = np.mean(gray)

    # ตั้ง threshold จำลองการตรวจรอยช้ำ
    if mean_intensity < 95:
        status = "ตรวจพบแนวโน้มรอยช้ำ"
    else:
        status = "ไม่พบรอยช้ำที่ชัดเจน"

    return f"""
ผลการวิเคราะห์มังคุด (Near-Infrared Simulation)

ค่าความเข้มเฉลี่ย: {round(mean_intensity, 2)}
สถานะ: {status}
"""


# =====================
# ฟังก์ชันตอบกลับ LINE
# =====================
def reply_text(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
    
    requests.post(url, headers=headers, json=data)
