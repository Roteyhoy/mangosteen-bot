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

                user_message = event["message"]["text"].strip()

                if user_message == "เมนู":
                    reply_text(reply_token,
                        "📋 เมนูการใช้งาน\n\n"
                        "1️⃣ พิมพ์ 'วิเคราะห์' เพื่อตรวจรอยช้ำ\n"
                        "2️⃣ พิมพ์ 'วิธีใช้'\n"
                        "3️⃣ พิมพ์ 'เกี่ยวกับระบบ'"
                    )

                elif user_message == "วิธีใช้":
                    reply_text(reply_token,
                        "📸 วิธีใช้งาน\n\n"
                        "1. พิมพ์ 'วิเคราะห์'\n"
                        "2. ส่งภาพมังคุด\n"
                        "3. รอผลการวิเคราะห์"
                    )

                elif user_message == "เกี่ยวกับระบบ":
                    reply_text(reply_token,
                        "🤖 Mangosteen AI Bot\n"
                        "ระบบวิเคราะห์รอยช้ำมังคุดด้วย OpenCV"
                    )

                elif "วิเคราะห์" in user_message:
                    reply_text(reply_token,
                        "กรุณาส่งภาพมังคุดเพื่อตรวจสอบรอยช้ำ"
                    )

                else:
                    reply_text(reply_token,
                        "ไม่เข้าใจคำสั่ง\nพิมพ์ 'เมนู' เพื่อดูคำสั่ง"
                    )

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

                result = analyze_image(image_path)
                reply_text(reply_token, result)

    return "OK"
# =====================
# ฟังก์ชันวิเคราะห์ภาพ (Improved Version)
# =====================
def analyze_image(path):
    img = cv2.imread(path)

    if img is None:
        return "ไม่สามารถอ่านภาพได้ กรุณาลองใหม่อีกครั้ง"

    # ลดขนาดภาพให้ประมวลผลเร็วขึ้น
    img = cv2.resize(img, (600, 600))

    # แปลงเป็น HSV เพื่อตัดพื้นหลัง
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # ช่วงสีของมังคุด (ปรับได้ตามภาพจริง)
    lower = np.array([20, 40, 40])
    upper = np.array([160, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)

    # ทำความสะอาด mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # เอาเฉพาะส่วนที่เป็นผล
    fruit = cv2.bitwise_and(img, img, mask=mask)

    # แปลงเป็น grayscale
    gray = cv2.cvtColor(fruit, cv2.COLOR_BGR2GRAY)

    # เพิ่ม contrast
    gray = cv2.equalizeHist(gray)

    # ใช้ adaptive threshold หา area มืด
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21,
        5
    )

    total_pixels = cv2.countNonZero(mask)
    bruise_pixels = cv2.countNonZero(thresh)

    if total_pixels == 0:
        return "ไม่สามารถตรวจจับผลมังคุดได้ กรุณาถ่ายภาพให้ชัดขึ้น"

    bruise_percent = (bruise_pixels / total_pixels) * 100

    if bruise_percent < 8:
        status = "ปกติ ไม่พบรอยช้ำ"
    elif bruise_percent < 18:
        status = "อาจมีรอยช้ำเล็กน้อย"
    else:
        status = "พบแนวโน้มรอยช้ำชัดเจน"

    return f"""
ผลการวิเคราะห์มังคุด (Improved Analysis)

พื้นที่รอยช้ำประมาณ: {bruise_percent:.2f}%
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
