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
model = genai.GenerativeModel('gemini-1.5-pro')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_get('/health', handle)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
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
    "ka": "Elite Georgian Poet. Deep metaphors, perfect rhythm, emotional depth.",
    "en": "Top Billboard Songwriter. Viral hooks, modern structure, catchy phrasing.",
    "ru": "Master Russian Lyricist. Precise rhymes, strong emotional storytelling.",
    "es": "Latin Hitmaker. Passion, rhythm, memorable choruses."
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

    await message.answer(
        "🎼 აირჩიე სიმღერის ენა:",
        reply_markup=builder.as_markup()
    )
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
    await callback.message.answer("👇 აირჩიე:", reply_markup=builder.as_markup())

    await state.set_state(SongGenerator.genre)

# --- GENRE ---
@dp.callback_query(F.data.startswith("genre_"))
async def process_genre(callback: types.CallbackQuery, state: FSMContext):
    genre = callback.data.replace("genre_", "")
    await state.update_data(genre=genre)

    await callback.message.answer("📝 დაწერე სიმღერის თემა:")
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
    prompt = f"""
ROLE: {LANGUAGE_PROMPTS[data['lang']]}

TASK: Create a HIT SONG for Suno AI

CONTEXT:
- Topic: {data['topic']}
- Genre: {data['genre']}
- Vocal: {data['gender']}

REQUIREMENTS:
1. SUPER VIRAL CHORUS (TikTok ready, repeatable)
2. Modern structure
3. Strong emotional impact
4. Perfect rhyme and rhythm
5. Memorable phrases

OUTPUT:

🎯 STYLE PROMPT (English, detailed, BPM, instruments)
---
📝 LYRICS:
[Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Bridge]
[Outro]
---
🖼 THUMBNAIL PROMPT (cinematic 16:9)
"""

    for _ in range(2):  # retry ერთხელ
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Retry error: {e}")
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

    # split message
    for part in split_message(content):
        await callback.message.answer(part)

    # regenerate button
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔄 თავიდან გენერაცია", callback_data="regen"))

    await callback.message.answer("👇", reply_markup=builder.as_markup())

    await state.clear()

# --- REGENERATE ---
@dp.callback_query(F.data == "regen")
async def regenerate(callback: types.CallbackQuery, state: FSMContext):
    await start_cmd(callback.message, state)

# --- MAIN ---
async def main():
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
