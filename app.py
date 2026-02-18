from flask import Flask, request
import requests
import os

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "FvyB1UuyAsuFQVYgU2Pq3tUydKhQBJbs7G63FY+nbwDZVt/tnbsgyOIZZ8SugtRDi0sDm+3fvQj3Ko6xCfnHfFzCVxRE/JmsxVbHawMnCHlgIJnf1NBOoP7q5pLBB0QXcXfr7uZxPuae92K1UaJ8ygdB04t89/1O/w1cDnyilFU="

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
            
            if event["message"]["type"] == "text":
                user_message = event["message"]["text"]
                
                if "วิเคราะห์" in user_message:
                    reply_text(reply_token, "กรุณาส่งภาพมังคุดเพื่อตรวจสอบรอยช้ำ")
                else:
                    reply_text(reply_token, "พิมพ์คำว่า 'วิเคราะห์' เพื่อเริ่มต้น")
    
    return "OK"

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
