import os
import telebot
import requests
import base64

# Variables (Railway Settings > Variables में ये नाम होने चाहिए)
TOKEN = "8095048825:AAEEoiluSycrAg-GTuzDMq2m7r3MhXihd9I"
API_KEY = "AIzaSyBrTfjQwMlStAlk2F856qYD3tG_tyH3BKI"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "फ़ोटो मिल गई है, AI इसे प्रोसेस कर रहा है...")
        
        # 1. टेलीग्राम से फ़ोटो का पाथ निकालना
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        # 2. फ़ोटो को डाउनलोड करके Base64 में बदलना
        img_response = requests.get(file_url)
        if img_response.status_code == 200:
            img_data = img_response.content
            base64_image = base64.b64encode(img_data).decode('utf-8')
        else:
            bot.reply_to(message, "फ़ोटो डाउनलोड करने में समस्या आई।")
            return

        # 3. Google Gemini API (v1beta) को सीधा कॉल करना
        # यह URL सबसे स्टेबल है और 404 नहीं देता
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Analyze the provided image and recreate it with the following changes: Replace the location text at [approximate location], [Lat 30.065122, Long 75.532133] with '[New Location]'. Update the date to '[New Date]' and time to '[New Time]'. Ensure the rest of the image remains identical."},
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

        # 4. रिजल्ट चेक करना
        if "candidates" in res_json:
            answer = res_json['candidates'][0]['content']['parts'][0]['text']
            bot.reply_to(message, answer)
        else:
            error_msg = res_json.get('error', {}).get('message', 'API Response Error')
            bot.reply_to(message, f"AI Error: {error_msg}")

    except Exception as e:
        bot.reply_to(message, f"सिस्टम एरर: {str(e)}")

print("Bot is active on Online Server...")
bot.infinity_polling()
