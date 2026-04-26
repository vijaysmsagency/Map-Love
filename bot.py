import os
import telebot
import google.generativeai as genai
from PIL import Image
import io

# API Keys (Railway Environment Variables से आएंगी)
TELEGRAM_TOKEN = os.getenv("8095048825:AAEEoiluSycrAg-GTuzDMq2m7r3MhXihd9I")
GEMINI_API_KEY = os.getenv("AIzaSyA9OHh36vyIpTrawumw3xv3DI1obt1WXy8")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # या gemini-1.5-pro का उपयोग करें

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "प्रोसेसिंग शुरू हो रही है... कृपया प्रतीक्षा करें।")
        
        # फोटो डाउनलोड करना
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # इमेज को PIL फॉर्मेट में बदलना
        img = Image.open(io.BytesIO(downloaded_file))
        
        # आपका स्पेसिफिक प्रॉम्प्ट
        prompt = """Analyze the provided image and recreate it with the following changes: 
        Replace the location text at [approximate location], [Lat 30.065122, Long 75.532133] with '[New Location]'. 
        Update the date to '[New Date]' and time to '[New Time]'. 
        Change Longitude as requested. 
        Ensure the rest of the image, including the handwriting and background, remains identical. 
        Keep the text style, format, and color consistent."""

        # Gemini से इमेज जेनरेट/एडिट करवाना
        response = model.generate_content([prompt, img])
        
        # रिस्पांस भेजना (अगर टेक्स्ट है तो टेक्स्ट, अगर इमेज है तो इमेज)
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "AI ने इमेज प्रोसेस की है, लेकिन रिस्पांस में टेक्स्ट नहीं मिला।")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

print("Bot is running...")
bot.infinity_polling()
