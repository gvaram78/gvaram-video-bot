import telebot
import os
from flask import Flask
from threading import Thread

# Render-ისთვის საჭირო "ტყუილი" ვებ-სერვერი
app = Flask('')

@app.route('/')
def home():
    return "ბოტი ჩართულია!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ტელეგრამ ბოტის ნაწილი
TOKEN = '8542244342:AAG6xFz93qGqlxw0qjkIug0dEhgm1wmbp_I'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "გამარჯობა! მე ვარ @gvaram_video_bot. მომწერე თემა ინგლისურად და გიპოვი მასალებს.")

@bot.message_handler(func=lambda m: True)
def search(m):
    q = m.text.replace(' ', '+')
    res = f"✅ მასალა: {m.text}\n\n📺 YouTube: https://www.youtube.com/results?search_query={q}\n🎬 Pexels: https://www.pexels.com/search/video/{q}/"
    bot.reply_to(m, res)

# ორივეს ერთად გაშვება
if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("ბოტი გაშვებულია...")
    bot.polling(none_stop=True)
