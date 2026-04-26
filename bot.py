import os
import telebot
import requests
import base64

# Variables
TOKEN = "8095048825:AAEEoiluSycrAg-GTuzDMq2m7r3MhXihd9I"
API_KEY = "AIzaSyBrTfjQwMlStAlk2F856qYD3tG_tyH3BKI"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "फ़ोटो प्रोसेस हो रही है...")
        
        # 1. Telegram से फोटो डाउनलोड करना
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        img_data = requests.get(file_url).content
        base64_image = base64.b64encode(img_data).decode('utf-8')

        # 2. Google Gemini API को सीधा (Direct) कॉल करना
        # यहाँ हम v1 (Stable) का उपयोग कर रहे हैं, जिससे 404 नहीं आएगा
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Analyze this image and describe the location, date, and time."},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }]
        }

        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()

        # 3. जवाब भेजना
        if "candidates" in res_json:
            answer = res_json['candidates'][0]['content']['parts'][0]['text']
            bot.reply_to(message, answer)
        else:
            bot.reply_to(message, f"API Error: {res_json.get('error', {}).get('message', 'Unknown Error')}")

    except Exception as e:
        bot.reply_to(message, f"System Error: {str(e)}")

print("Bot is alive...")
bot.infinity_polling()
