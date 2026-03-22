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

# --- SMART MODEL SELECTOR ---
def get_best_model():
    try:
        models = list(genai.list_models())
        # ვეძებთ სპეციალურად flash ან pro ვერსიებს
        for m in models:
            if "generateContent" in m.supported_generation_methods:
                if "flash" in m.name.lower() or "pro" in m.name.lower():
                    logging.info(f"✅ ავტომატურად აირჩა მოდელი: {m.name}")
                    return genai.GenerativeModel(m.name)
                    
    except Exception as e:
        logging.error(f"❌ Model detection failed: {e}")

    # Fallback ვარიანტი (თუ რამე აირია სიაში)
    logging.info("⚠️ ვიყენებთ სტანდარტულ gemini-pro-ს")
    return genai.GenerativeModel("gemini-pro")

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
    "Cinematic Epic", "Pop
