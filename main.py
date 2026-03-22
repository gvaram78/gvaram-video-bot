import logging
import asyncio
import os
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- CONFIG ---
API_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- MODEL SELECTOR (IMPROVED) ---
def get_best_model():
    try:
        models = list(genai.list_models())

        # პრიორიტეტი
        priority = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]

        for p in priority:
            for m in models:
                if p in m.name and "generateContent" in m.supported_generation_methods:
                    logging.info(f"✅ Selected model: {m.name}")
                    return genai.GenerativeModel(m.name)

    except Exception as e:
        logging.error(f"Model detection failed: {e}")

    logging.info("⚠️ Fallback → gemini-1.0-pro")
    return genai.GenerativeModel("gemini-1.0-pro")


model = get_best_model()

# --- WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is alive")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    app.router.add_get("/health", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# --- STATES ---
class SongGenerator(StatesGroup):
    language = State()
    genre = State()
    topic = State()
    gender = State()

# --- HELPERS ---
def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

LANGUAGE_PROMPTS = {
    "ka": "Elite Georgian Poet. Deep metaphors, powerful emotion.",
    "en": "Top Billboard songwriter. Viral hooks and modern structure.",
    "ru": "Master Russian lyricist with perfect rhyme.",
    "es": "Latin hitmaker with rhythm and passion."
}

GENRES = [
    "Cinematic Epic", "Pop", "Hip Hop", "Rock",
    "Deep House", "Techno", "Georgian Folk",
    "Country Pop", "R&B"
]

# --- START ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🇬🇪 ქართული", callback_data="lang_ka"),
        types.InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
    )
    builder.row(
        types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")
    )

    await message.answer("🎼 აირჩიე ენა:", reply_markup=builder.as_markup())
    await state.set_state(SongGenerator.language)

# --- LANGUAGE ---
@dp.callback_query(F.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)

    builder = InlineKeyboardBuilder()
    for g in GENRES:
        builder.row(types.InlineKeyboardButton(text=g, callback_data=f"genre_{g}"))

    await callback.message.edit_text("🎸 აირჩიე ჟანრი:")
    await callback.message.answer("👇", reply_markup=builder.as_markup())

    await state.set_state(SongGenerator.genre)

# --- GENRE ---
@dp.callback_query(F.data.startswith("genre_"))
async def process_genre(callback: types.CallbackQuery, state: FSMContext):
    genre = callback.data.replace("genre_", "")
    await state.update_data(genre=genre)

    await callback.message.answer("📝 დაწერე თემა:")
    await state.set_state(SongGenerator.topic)

# --- TOPIC ---
@dp.message(SongGenerator.topic)
async def process_topic(message: types.Message, state: FSMContext):
    await state.update_data(topic=message.text)

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="👨 Male", callback_data="gen_Male"),
        types.InlineKeyboardButton(text="👩 Female", callback_data="gen_Female"),
        types.InlineKeyboardButton(text="👥 Duo", callback_data="gen_Duo")
    )

    await message.answer("🎤 აირჩიე ვოკალი:", reply_markup=builder.as_markup())
    await state.set_state(SongGenerator.gender)

# --- GENERATION ---
async def generate_song(data):
    global model

    prompt = f"""
Create a viral hit song.

Topic: {data['topic']}
Genre: {data['genre']}
Vocal: {data['gender']}

- Viral chorus
- Emotional
- Modern structure

OUTPUT:
STYLE PROMPT
---
LYRICS
---
THUMBNAIL PROMPT
"""

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            logging.error(f"Attempt {attempt+1}: {e}")

            # fallback switch
            model = genai.GenerativeModel("gemini-1.0-pro")

            await asyncio.sleep(1)

    return "❌ გენერაცია ვერ მოხერხდა."

# --- FINAL ---
@dp.callback_query(F.data.startswith("gen_"))
async def generate_final(callback: types.CallbackQuery, state: FSMContext):
    gender = callback.data.split("_")[1]
    data = await state.get_data()
    data["gender"] = gender

    await callback.message.edit_text("⏳ ვქმნი ჰიტს...")

    content = await generate_song(data)

    for part in split_message(content):
        await callback.message.answer(part)

    await state.clear()

# --- MAIN ---
async def main():
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
