import telebot
import instaloader
from io import BytesIO
import requests
import time

# Initialize bot with your token
bot = telebot.TeleBot("YOUR_BOT_TOKEN")

# Initialize instaloader
L = instaloader.Instaloader()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me an Instagram post link to download.")

@bot.message_handler(func=lambda message: True)
def process_post(message):
    try:
        # Get post shortcode from URL
        url = message.text
        if "instagram.com" not in url:
            bot.reply_to(message, "Please send a valid Instagram link")
            return
            
        shortcode = url.split("/")[-2]
        
        # Get post information
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # For videos
        if post.is_video:
            # Get video URL
            video_url = post.video_url
            
            # Stream video without saving locally
            video_content = requests.get(video_url).content
            video_io = BytesIO(video_content)
            video_io.name = f"{shortcode}.mp4"
            
            try:
                bot.send_video(message.chat.id, video_io, timeout=60)
            except Exception as e:
                # Wait and retry with longer timeout
                time.sleep(5)
                video_io.seek(0)  # Reset file pointer
                try:
                    bot.send_video(message.chat.id, video_io, timeout=120)
                except Exception as e2:
                    bot.reply_to(message, f"Failed to send video after retry: {str(e2)}")
                    return
            
        # For photos
        else:
            # Get photo URL
            photo_url = post.url
            
            # Stream photo without saving locally
            photo_content = requests.get(photo_url).content
            photo_io = BytesIO(photo_content)
            photo_io.name = f"{shortcode}.jpg"
            
            try:
                bot.send_photo(message.chat.id, photo_io, timeout=30)
            except Exception as e:
                # Wait and retry
                time.sleep(5)
                photo_io.seek(0)  # Reset file pointer
                try:
                    bot.send_photo(message.chat.id, photo_io, timeout=60)
                except Exception as e2:
                    bot.reply_to(message, f"Failed to send photo after retry: {str(e2)}")
                    return
            
        bot.reply_to(message, "Media sent successfully!")
    except Exception as e:
        bot.reply_to(message, f"Error processing your request: {str(e)}")

# Start the bot
print("Bot is running...")
bot.polling(none_stop=True)
