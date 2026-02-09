import telebot
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

TOKEN = '8542244342:AAG6xFz93qGqlxw0qjkIug0dEhgm1wmbp_I'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🇬🇪 გამარჯობა! მომწერე თემა და გიპოვი სამეცნიერო მასალებს, ისტორიულ კადრებს და AI პრომტებს.")

@bot.message_handler(func=lambda m: True)
def handle_all(m):
    q = m.text.replace(' ', '+')
    
    # AI პრომტების გენერაცია
    image_prompt = f"Cinematic, 8k, hyper-realistic, historical setting, {m.text}, golden hour lighting, detailed texture."
    video_prompt = f"Slow motion cinematic drone shot, ancient landscape, {m.text}, realistic movement, 4k, National Geographic style."
    
    res = (
        f"🔍 **მასალები თემაზე:** {m.text}\n\n"
        f"📺 **YouTube (დოკუმენტური):** https://www.youtube.com/results?search_query={q}+documentary\n"
        f"🏛 **Wikimedia (ისტორიული ფოტო/ვიდეო):** https://commons.wikimedia.org/w/index.php?search={q}\n"
        f"🔬 **Google Scholar (სამეცნიერო ნაშრომები):** https://scholar.google.com/scholar?q={q}\n"
        f"🌍 **World History Encyclopedia:** https://www.worldhistory.org/search/?q={q}\n\n"
        f"🎨 **AI Image Prompt:**\n`{image_prompt}`\n\n"
        f"🎬 **AI Video Prompt (Runway/Luma):**\n`{video_prompt}`"
    )
    bot.reply_to(m, res)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.polling(none_stop=True)
