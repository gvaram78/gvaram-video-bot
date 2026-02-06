import telebot

TOKEN = '8542244342:AAG6xFz93qGqlxw0qjkIug0dEhgm1wmbp_I'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "გამარჯობა! მე ვარ @gvaram_video_bot. მომწერე თემა ინგლისურად და გიპოვი მასალებს.")

@bot.message_handler(func=lambda message: True)
def search(message):
    query = message.text
    chat_id = message.chat.id
    yt_link = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    px_link = f"https://www.pexels.com/search/video/{query}/"
    pb_link = f"https://pixabay.com/images/search/{query}/"
    response = f"✅ მასალა თემაზე: {query}\n\n📺 YouTube: {yt_link}\n\n🎬 Pexels: {px_link}\n\n🖼 Pixabay: {pb_link}"
    bot.send_message(chat_id, response)

bot.polling()