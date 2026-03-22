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

# --- კონფიგურაცია ---
API_TOKEN = '8542244342:AAG6xFz93qGqlxw0qjkIug0dEhgm1wmbp_I'
GOOGLE_API_KEY = 'AIzaSyCDn8k5ESIR-BvPZZ-47bw--uZoJYkK5Xw'

# Gemini-ს გამართვა (ყველაზე სტაბილური მოდელით)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ვებ-სერვერი Render-ის "გასაღვიძებლად" ---
async def handle(request):
    return web.Response(text="Suno Music Bot is Live and Ready!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# --- ბოტის ფაზები (States) ---
class SongGenerator(StatesGroup):
    language = State()
    genre = State()
    topic = State()
    gender = State()

# პერსონების ინსტრუქციები ენების მიხედვით
LANGUAGE_PROMPTS = {
    "ka": "Expert Georgian Poet (Galaktion style). Use deep metaphors, perfect rhymes, and rhythmic flow.",
    "en": "Grammy-winning US Songwriter. Focus on catchy hooks, perfect meter, and clever wordplay.",
    "ru": "Master Russian Lyricist. Use 'Точные рифмы', deep emotional resonance, and classic structure.",
    "es": "Elite Spanish Composer. Passionate metaphors, 'Rimas consonantes', and rhythmic Latin style."
}

# --- ბოტის ფუნქციონალი ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🇬🇪 ქართული", callback_data="lang_ka"),
                types.InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"))
    builder.row(types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
                types.InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es"))
    
    await message.answer(
        "🎼 **კეთილი იყოს თქვენი მობრძანება პროფესიონალურ მუსიკალურ სტუდიაში!**\n\n"
        "მე შევქმნი უზუსტეს ტექსტებს Suno AI-სთვის.\n"
        "პირველ რიგში, **აირჩიეთ სიმღერის ენა:**", 
        reply_markup=builder.as_markup()
    )
    await state.set_state(SongGenerator.language)

@dp.callback_query(F.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    await state.update_data(lang=lang_code)
    await callback.message.edit_text("🎸 რა **ჟანრში** გსურთ სიმღერა?\n(მაგ: Cinematic Epic, Deep House, Georgian Polyphony, Heavy Metal):")
    await state.set_state(SongGenerator.genre)

@dp.message(SongGenerator.genre)
async def process_genre(message: types.Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await message.answer("📝 რა არის **სიმღერის თემა** ან მთავარი ისტორია?")
    await state.set_state(SongGenerator.topic)

@dp.message(SongGenerator.topic)
async def process_topic(message: types.Message, state: FSMContext):
    await state.update_data(topic=message.text)
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👨 კაცი (Male)", callback_data="gen_Male"),
                types.InlineKeyboardButton(text="👩 ქალი (Female)", callback_data="gen_Female"))
    builder.row(types.InlineKeyboardButton(text="👥 დუეტი (Duo)", callback_data="gen_Duo"))
    
    await message.answer("🎤 აირჩიეთ **ვოკალის ტიპი**:", reply_markup=builder.as_markup())
    await state.set_state(SongGenerator.gender)

@dp.callback_query(F.data.startswith("gen_"))
async def generate_final(callback: types.CallbackQuery, state: FSMContext):
    gender = callback.data.split("_")[1]
    user_data = await state.get_data()
    lang = user_data['lang']
    genre = user_data['genre']
    topic = user_data['topic']
    
    await callback.message.edit_text("⏳ **ვქმნი პროფესიონალურ პაკეტს...**\nვიყენებ Gemini Pro-ს მაქსიმალური ხარისხისთვის.")

    prompt = f"""
    ROLE: {LANGUAGE_PROMPTS[lang]}
    TASK: Write a full, top-tier song for Suno AI.
    
    CONTEXT:
    - Topic: {topic}
    - Genre/Style: {genre}
    - Vocal: {gender}
    - Language: {lang}

    STRICT REQUIREMENTS:
    1. STYLE PROMPT: Create a detailed 'Style of Music' prompt for Suno in English (BPM, instruments, mood).
    2. LYRICS: Full structure [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Bridge], [Outro].
    3. RHYME: Every verse must have a flawless, professional rhyme scheme.
    4. YOUTUBE PROMPT: Provide 1 viral, cinematic 16:9 image prompt for a YouTube Thumbnail.

    OUTPUT FORMAT:
    🎯 **SUNO STYLE PROMPT:** (English tags)
    ---
    📝 **LYRICS:** (The full song)
    ---
    🖼 **YOUTUBE THUMBNAIL PROMPT:** (16:9 prompt)
    """

    try:
        response = model.generate_content(prompt)
        content = response.text
        await callback.message.answer(f"✅ **თქვენი შედევრი მზად არის!**\n\n{content}")
    except Exception as e:
        await callback.message.answer(f"❌ შეცდომა გენერაციისას: {str(e)}")
    
    await state.clear()

# --- გაშვება ---
async def main():
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
