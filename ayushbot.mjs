import makeWASocket, { 
    useMultiFileAuthState, 
    DisconnectReason, 
    delay, 
    fetchLatestBaileysVersion, 
    Browsers, 
    downloadMediaMessage,
    downloadContentFromMessage
} from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import pino from 'pino';
import fs from 'fs';
import readline from 'readline';
import gtts from 'node-gtts';
import { exec } from 'child_process';
import util from 'util';
import NodeCache from 'node-cache';

// ========== CACHE FOR BETTER PERFORMANCE ==========
const msgRetryCounterCache = new NodeCache();

// ========== FONT STYLES FOR NC ATTACK ==========
const fontStyles = {
    double: {
        name: '𝔻𝕠𝕦𝕓𝕝𝕖 𝕊𝕥𝕣𝕚𝕜𝕖',
        map: {
            'A': '𝔸', 'B': '𝔹', 'C': 'ℂ', 'D': '𝔻', 'E': '𝔼', 'F': '𝔽', 'G': '𝔾',
            'H': 'ℍ', 'I': '𝕀', 'J': '𝕁', 'K': '𝕂', 'L': '𝕃', 'M': '𝕄', 'N': 'ℕ',
            'O': '𝕆', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'S': '𝕊', 'T': '𝕋', 'U': '𝕌',
            'V': '𝕍', 'W': '𝕎', 'X': '𝕏', 'Y': '𝕐', 'Z': 'ℤ',
            'a': '𝕒', 'b': '𝕓', 'c': '𝕔', 'd': '𝕕', 'e': '𝕖', 'f': '𝕗', 'g': '𝕘',
            'h': '𝕙', 'i': '𝕚', 'j': '𝕛', 'k': '𝕜', 'l': '𝕝', 'm': '𝕞', 'n': '𝕟',
            'o': '𝕠', 'p': '𝕡', 'q': '𝕢', 'r': '𝕣', 's': '𝕤', 't': '𝕥', 'u': '𝕦',
            'v': '𝕧', 'w': '𝕨', 'x': '𝕩', 'y': '𝕪', 'z': '𝕫'
        }
    },
    mono: {
        name: '𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎',
        map: {
            'A': '𝙰', 'B': '𝙱', 'C': '𝙲', 'D': '𝙳', 'E': '𝙴', 'F': '𝙵', 'G': '𝙶',
            'H': '𝙷', 'I': '𝙸', 'J': '𝙹', 'K': '𝙺', 'L': '𝙻', 'M': '𝙼', 'N': '𝙽',
            'O': '𝙾', 'P': '𝙿', 'Q': '𝚀', 'R': '𝚁', 'S': '𝚂', 'T': '𝚃', 'U': '𝚄',
            'V': '𝚅', 'W': '𝚆', 'X': '𝚇', 'Y': '𝚈', 'Z': '𝚉',
            'a': '𝚊', 'b': '𝚋', 'c': '𝚌', 'd': '𝚍', 'e': '𝚎', 'f': '𝚏', 'g': '𝚐',
            'h': '𝚑', 'i': '𝚒', 'j': '𝚓', 'k': '𝚔', 'l': '𝚕', 'm': '𝚖', 'n': '𝚗',
            'o': '𝚘', 'p': '𝚙', 'q': '𝚚', 'r': '𝚛', 's': '𝚜', 't': '𝚝', 'u': '𝚞',
            'v': '𝚟', 'w': '𝚠', 'x': '𝚡', 'y': '𝚢', 'z': '𝚣'
        }
    },
    script: {
        name: '𝒮𝒸𝓇𝒾𝓅𝓉',
        map: {
            'A': '𝒜', 'B': 'ℬ', 'C': '𝒞', 'D': '𝒟', 'E': 'ℰ', 'F': 'ℱ', 'G': '𝒢',
            'H': 'ℋ', 'I': 'ℐ', 'J': '𝒥', 'K': '𝒦', 'L': 'ℒ', 'M': 'ℳ', 'N': '𝒩',
            'O': '𝒪', 'P': '𝒫', 'Q': '𝒬', 'R': 'ℛ', 'S': '𝒮', 'T': '𝒯', 'U': '𝒰',
            'V': '𝒱', 'W': '𝒲', 'X': '𝒳', 'Y': '𝒴', 'Z': '𝒵',
            'a': '𝒶', 'b': '𝒷', 'c': '𝒸', 'd': '𝒹', 'e': 'ℯ', 'f': '𝒻', 'g': 'ℊ',
            'h': '𝒽', 'i': '𝒾', 'j': '𝒿', 'k': '𝓀', 'l': '𝓁', 'm': '𝓂', 'n': '𝓃',
            'o': 'ℴ', 'p': '𝓅', 'q': '𝓆', 'r': '𝓇', 's': '𝓈', 't': '𝓉', 'u': '𝓊',
            'v': '𝓋', 'w': '𝓌', 'x': '𝓍', 'y': '𝓎', 'z': '𝓏'
        }
    },
    boldscript: {
        name: '𝓑𝓸𝓵𝓭 𝓢𝓬𝓻𝓲𝓹𝓽',
        map: {
            'A': '𝓐', 'B': '𝓑', 'C': '𝓒', 'D': '𝓓', 'E': '𝓔', 'F': '𝓕', 'G': '𝓖',
            'H': '𝓗', 'I': '𝓘', 'J': '𝓙', 'K': '𝓚', 'L': '𝓛', 'M': '𝓜', 'N': '𝓝',
            'O': '𝓞', 'P': '𝓟', 'Q': '𝓠', 'R': '𝓡', 'S': '𝓢', 'T': '𝓣', 'U': '𝓤',
            'V': '𝓥', 'W': '𝓦', 'X': '𝓧', 'Y': '𝓨', 'Z': '𝓩',
            'a': '𝓪', 'b': '𝓫', 'c': '𝓬', 'd': '𝓭', 'e': '𝓮', 'f': '𝓯', 'g': '𝓰',
            'h': '𝓱', 'i': '𝓲', 'j': '𝓳', 'k': '𝓴', 'l': '𝓵', 'm': '𝓶', 'n': '𝓷',
            'o': '𝓸', 'p': '𝓹', 'q': '𝓺', 'r': '𝓻', 's': '𝓼', 't': '𝓽', 'u': '𝓾',
            'v': '𝓿', 'w': '𝔀', 'x': '𝔁', 'y': '𝔂', 'z': '𝔃'
        }
    },
    gothic: {
        name: '𝔊𝔬𝔱𝔥𝔦𝔠',
        map: {
            'A': '𝔄', 'B': '𝔅', 'C': 'ℭ', 'D': '𝔇', 'E': '𝔈', 'F': '𝔉', 'G': '𝔊',
            'H': 'ℌ', 'I': 'ℑ', 'J': '𝔍', 'K': '𝔎', 'L': '𝔏', 'M': '𝔐', 'N': '𝔑',
            'O': '𝔒', 'P': '𝔓', 'Q': '𝔔', 'R': 'ℜ', 'S': '𝔖', 'T': '𝔗', 'U': '𝔘',
            'V': '𝔙', 'W': '𝔚', 'X': '𝔛', 'Y': '𝔜', 'Z': 'ℨ',
            'a': '𝔞', 'b': '𝔟', 'c': '𝔠', 'd': '𝔡', 'e': '𝔢', 'f': '𝔣', 'g': '𝔤',
            'h': '𝔥', 'i': '𝔦', 'j': '𝔧', 'k': '𝔨', 'l': '𝔩', 'm': '𝔪', 'n': '𝔫',
            'o': '𝔬', 'p': '𝔭', 'q': '𝔮', 'r': '𝔯', 's': '𝔰', 't': '𝔱', 'u': '𝔲',
            'v': '𝔳', 'w': '𝔴', 'x': '𝔵', 'y': '𝔶', 'z': '𝔷'
        }
    },
    boldgothic: {
        name: '𝕭𝖔𝖑𝖉 𝕲𝖔𝖙𝖍𝖎𝖈',
        map: {
            'A': '𝕬', 'B': '𝕭', 'C': '𝕮', 'D': '𝕯', 'E': '𝕰', 'F': '𝕱', 'G': '𝕲',
            'H': '𝕳', 'I': '𝕴', 'J': '𝕵', 'K': '𝕶', 'L': '𝕷', 'M': '𝕸', 'N': '𝕹',
            'O': '𝕺', 'P': '𝕻', 'Q': '𝕼', 'R': '𝕽', 'S': '𝕾', 'T': '𝕿', 'U': '𝖀',
            'V': '𝖁', 'W': '𝖂', 'X': '𝖃', 'Y': '𝖄', 'Z': '𝖅',
            'a': '𝖆', 'b': '𝖇', 'c': '𝖈', 'd': '𝖉', 'e': '𝖊', 'f': '𝖋', 'g': '𝖌',
            'h': '𝖍', 'i': '𝖎', 'j': '𝖏', 'k': '𝖐', 'l': '𝖑', 'm': '𝖒', 'n': '𝖓',
            'o': '𝖔', 'p': '𝖕', 'q': '𝖖', 'r': '𝖗', 's': '𝖘', 't': '𝖙', 'u': '𝖚',
            'v': '𝖛', 'w': '𝖜', 'x': '𝖝', 'y': '𝖞', 'z': '𝖟'
        }
    },
    square: {
        name: 'Ｓｑｕａｒｅ',
        map: {
            'A': 'Ａ', 'B': 'Ｂ', 'C': 'Ｃ', 'D': 'Ｄ', 'E': 'Ｅ', 'F': 'Ｆ', 'G': 'Ｇ',
            'H': 'Ｈ', 'I': 'Ｉ', 'J': 'Ｊ', 'K': 'Ｋ', 'L': 'Ｌ', 'M': 'Ｍ', 'N': 'Ｎ',
            'O': 'Ｏ', 'P': 'Ｐ', 'Q': 'Ｑ', 'R': 'Ｒ', 'S': 'Ｓ', 'T': 'Ｔ', 'U': 'Ｕ',
            'V': 'Ｖ', 'W': 'Ｗ', 'X': 'Ｘ', 'Y': 'Ｙ', 'Z': 'Ｚ',
            'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ', 'f': 'ｆ', 'g': 'ｇ',
            'h': 'ｈ', 'i': 'ｉ', 'j': 'ｊ', 'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ',
            'o': 'ｏ', 'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 's': 'ｓ', 't': 'ｔ', 'u': 'ｕ',
            'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ', 'z': 'ｚ'
        }
    },
    circled: {
        name: 'Ⓒⓘⓡⓒⓛⓔⓓ',
        map: {
            'A': 'Ⓐ', 'B': 'Ⓑ', 'C': 'Ⓒ', 'D': 'Ⓓ', 'E': 'Ⓔ', 'F': 'Ⓕ', 'G': 'Ⓖ',
            'H': 'Ⓗ', 'I': 'Ⓘ', 'J': 'Ⓙ', 'K': 'Ⓚ', 'L': 'Ⓛ', 'M': 'Ⓜ', 'N': 'Ⓝ',
            'O': 'Ⓞ', 'P': 'Ⓟ', 'Q': 'Ⓠ', 'R': 'Ⓡ', 'S': 'Ⓢ', 'T': 'Ⓣ', 'U': 'Ⓤ',
            'V': 'Ⓥ', 'W': 'Ⓦ', 'X': 'Ⓧ', 'Y': 'Ⓨ', 'Z': 'Ⓩ',
            'a': 'ⓐ', 'b': 'ⓑ', 'c': 'ⓒ', 'd': 'ⓓ', 'e': 'ⓔ', 'f': 'ⓕ', 'g': 'ⓖ',
            'h': 'ⓗ', 'i': 'ⓘ', 'j': 'ⓙ', 'k': 'ⓚ', 'l': 'ⓛ', 'm': 'ⓜ', 'n': 'ⓝ',
            'o': 'ⓞ', 'p': 'ⓟ', 'q': 'ⓠ', 'r': 'ⓡ', 's': 'ⓢ', 't': 'ⓣ', 'u': 'ⓤ',
            'v': 'ⓥ', 'w': 'ⓦ', 'x': 'ⓧ', 'y': 'ⓨ', 'z': 'ⓩ'
        }
    }
};

async function generateTTS(text, lang = 'en') {
    return new Promise((resolve, reject) => {
        const tts = gtts(lang);
        const chunks = [];
        
        tts.stream(text).on('data', (chunk) => {
            chunks.push(chunk);
        }).on('end', () => {
            resolve(Buffer.concat(chunks));
        }).on('error', (err) => {
            reject(err);
        });
    });
}

// ========== WEBP TO MP4 CONVERSION FOR STICKER SPAM ==========
async function webpToMp4(webpBuffer) {
    return new Promise((resolve, reject) => {
        const inputPath = `./temp/sticker_${Date.now()}.webp`;
        const outputPath = `./temp/sticker_${Date.now()}.mp4`;
        
        if (!fs.existsSync('./temp')) fs.mkdirSync('./temp', { recursive: true });
        
        fs.writeFileSync(inputPath, webpBuffer);
        
        exec(`ffmpeg -i ${inputPath} -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -preset ultrafast -t 1 ${outputPath} -y`, (error) => {
            if (error) {
                reject(error);
                return;
            }
            
            if (fs.existsSync(outputPath)) {
                const mp4Buffer = fs.readFileSync(outputPath);
                try {
                    fs.unlinkSync(inputPath);
                    fs.unlinkSync(outputPath);
                } catch (e) {}
                resolve(mp4Buffer);
            } else {
                reject(new Error('Conversion failed'));
            }
        });
    });
}

const ROLES_FILE = './data/roles.json';
const BOTS_FILE = './data/bots.json';
const DELAYS_FILE = './data/delays.json';
const WORDS_FILE = './data/words.json';
const PREFIX_FILE = './data/prefix.json';

const defaultRoles = {
    owner: null,
    admins: [],
    subAdmins: {}
};

const defaultDelays = {
    nc1: 20, nc2: 20, nc3: 20, nc4: 20, nc5: 20, nc6: 20, nc7: 20,
    nc8: 20, nc9: 20, nc10: 20, nc11: 20, nc12: 20, nc13: 20, nc14: 20,
    nc15: 20, nc16: 20, nc17: 20, nc18: 20, nc19: 20, nc20: 20, nc21: 20,
    nc22: 20, nc23: 20, nc24: 20, nc25: 20, nc26: 20, nc27: 20, nc28: 20,
    nc29: 20, nc30: 20, nc31: 20, nc32: 20, nc33: 20, nc34: 20, nc35: 20,
    nc36: 20, nc37: 20, nc38: 20, nc39: 20, nc40: 20, nc41: 20, nc42: 20,
    nc43: 20, nc44: 20, nc45: 20, nc46: 20, nc47: 20, nc48: 20, nc49: 20,
    nc50: 20, nc51: 20, nc52: 20, nc53: 20, nc54: 20, nc55: 20, nc56: 20,
    nc57: 20, nc58: 20, nc59: 20, nc60: 20, nc61: 20, nc62: 20, nc63: 20,
    nc64: 20, nc65: 20, nc66: 20, nc67: 20, nc68: 20, nc69: 20, nc70: 20,
    nc71: 20, nc72: 20, nc73: 20, nc74: 20, nc75: 20, nc76: 20, nc77: 20,
    nc78: 20, nc79: 20, nc80: 20, nc81: 20, nc82: 20, nc83: 20, nc84: 20,
    nc85: 20, nc86: 20, nc87: 20, nc88: 20, nc89: 20, nc90: 20, nc91: 20,
    nc92: 20, nc93: 20, nc94: 20, nc95: 20, nc96: 20, nc97: 20, nc98: 20,
    nc99: 20, nc100: 20,
    triple1: 20, triple2: 20, triple3: 20, triple4: 20, triple5: 20,
    triple6: 20, triple7: 20, triple8: 20, triple9: 20, triple10: 20,
    triple11: 20, triple12: 20, triple13: 20, triple14: 20, triple15: 20,
    triple16: 20, triple17: 20, triple18: 20, triple19: 20, triple20: 20,
    triple21: 20, triple22: 20, triple23: 20, triple24: 20, triple25: 20,
    triple26: 20, triple27: 20, triple28: 20, triple29: 20, triple30: 20,
    triple31: 20, triple32: 20, triple33: 20, triple34: 20, triple35: 20,
    grpfp: 2000,
    speedup: 20
};

const defaultPrefix = '!';

const CONSTANT_WORDS = [
    '(𓀐𓂸)- ​ᴀYUSH',
    '🚀 ᴀYUSH ᴄʜᴜᴛ🚀', 
    'ᴀYUSH 𝗪𝗔𝗟𝗘🥀',
    'ɱ~ų~ɬ~ɦ ᴀYUSH 𝐊i🦐',
    '◤ᴀYUSH OP◥✕🚬🍸',
    '(🜏)- ​ᴀYUSH',
    '🍌 ᴀYUSH ᴄʜᴜᴛ🍌',
    'ᴀYUSH 𝗞𝗢 𝗕𝗛𝗨𝗟 𝗠𝗔𝗧 🥀',
    '◤ᴀYUSH POWER◥✕🚬🍸',
    'Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? BOT 🥶',
    '(𖤐)- ​ᴀYUSH',
    '♨️ ᴀYUSH ᴄʜᴜᴛ♨️',
    'ᴀYUSH 𝗟𝗔 🤙🏿',
    '🕷️ ᴀYUSH KING 👑',
    '🔥 ᴀYUSH ATTACK 🔥',
    '💀 ᴀYUSH MODE 💀',
    '⚡ AYUSH SPEED ⚡',
    '💫 ᴀYUSH POWER 💫',
    '👑 AYUSH OWNER 👑',
    '🤖 ᴀYUSH BOT 🤖',
    '🎯 ᴀYISH TARGET 🎯',
    '💥 ᴀYUSH ULTIMATE 💥'
];

// ========== ALL EMOJI SECTIONS (100 NC TYPES) ==========
const emojiArrays = {
    nc1: ['🤢','😩','😣','😖','😫','🥶','🫩','🤥','🤓','😇','😎','🤯'],
    nc2: ['💖','💘','💕','🩶','💞','💙','💗','🩷','❤️‍🩹','🤍','💜','💚'],
    nc3: ['🌙','🌑','🌘','🌗','🌖','🌕','🌔','🌓','🌒','🌑','🌚','🌛'],
    nc4: ['🌷','🌺','🥀','🍂','🪷','🪻','🌻','🏵️','💐','🌼','🌸','🌹'],
    nc5: ['🌩️','⭐','✨','⚜️','🌟','🪔','💫','⚡','💡','🏮','🔦','🕯️'],
    nc6: ['🏞️','🪺','❄️','🌋','💧','🪵','🪹','🪨','🌬️','🫧','🌀','🌊'],
    nc7: ['🇦🇪','🇦🇩','🇦🇪','🇦🇫','🇦🇬','🇦🇮','🇦🇱','🇦🇲','🇦🇴','🇦🇶','🇦🇷','🇦🇸'],
    nc8: ['🖋️','🖊️','🖍️','🖌️','📐','📏','✂️','🖇️','✏️','✒️','🔏','📝'],
    nc9: ['🪽','🐼','🦎','🦇','🦭','🐦‍🔥','🦘','🦆','🦑','🐚','🦜','🦢'],
    nc10: ['🟥','🟧','🟨','🟩','♂️','🟦','🟪','🟫','⬛','⬜','🔴','🟢'],
    nc11: ['💠','🔷','🔹','💠','🔷','🔹','💠','🔷','🔹','💠','🔶','🔸'],
    nc12: ['🦚','🪱','🦠','🦋','🐣','🦔','🦨','🦒','🫏','🐍','🐸','🦥'],
    nc13: ['🌀','🫧','💧','🌀','🫧','💧','🌀','🫧','💧','🌀','🌪️','💨'],
    nc14: ['🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍈','🍒','🍑'],
    nc15: ['🥕','🌽','🌶️','🫑','🥒','🥦','🥬','🧄','🧅','🍄','🥜','🫘'],
    nc16: ['🍔','🍟','🍕','🌭','🥪','🌮','🌯','🥗','🥘','🍝','🍜','🍲'],
    nc17: ['☕','🍵','🧃','🥤','🧋','🍶','🍺','🍻','🥂','🍷','🥃','🍸'],
    nc18: ['⚽','🏀','🏈','⚾','🥎','🎾','🏐','🏉','🥏','🎱','🏓','🏸'],
    nc19: ['🚗','🚕','🚙','🚌','🚎','🏎️','🚓','🚑','🚒','🚐','🛻','🚚'],
    nc20: ['⌚','📱','💻','🖥️','🖨️','📷','📹','🎥','📺','📻','🎙️','🎚️'],
    nc21: ['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐨','🐸','🐧','🐦'],
    nc22: ['🐔','🐤','🐣','🐥','🦆','🦅','🦉','🦇','🐺','🐗','🐴','🦄'],
    nc23: ['🐝','🐛','🦋','🐌','🐞','🐜','🦟','🦗','🕷️','🕸️','🦂','🦠'],
    nc24: ['🐟','🐠','🐡','🦈','🐙','🦑','🦐','🦞','🦀','🐳','🐋','🐬'],
    nc25: ['🐪','🐫','🦙','🦒','🐘','🦏','🦛','🐭','🐁','🐀','🐹','🐰'],
    nc26: ['🦔','🦝','🐿️','🦫','🦡','🐾','🦨','🦦','🦥','🐨','🦘','🦃'],
    nc27: ['🦜','🕊️','🦩','🦢','🦚','🦤','🦃','🐓','🐈','🐕','🦮','🐕‍🦺'],
    nc28: ['🐩','🐕','🐈‍⬛','🐈','🐆','🦌','🦬','🐃','🐂','🐄','🐎','🦓'],
    nc29: ['🦍','🦧','🐒','🦣','🐘','🦛','🦏','🐪','🐫','🦙','🦒','🐅'],
    nc30: ['🐊','🐍','🦎','🐢','🐉','🦕','🦖','🐋','🐬','🐟','🐠','🐡'],
    nc31: ['🏁','🚩','🎌','🏴','🏳️','🏳️‍🌈','🏴‍☠️','🇦🇫','🇦🇽','🇦🇱','🇩🇿','🇦🇸'],
    nc32: ['🇦🇩','🇦🇴','🇦🇮','🇦🇶','🇦🇬','🇦🇷','🇦🇲','🇦🇼','🇦🇺','🇦🇹','🇦🇿','🇧🇸'],
    nc33: ['🇧🇭','🇧🇩','🇧🇧','🇧🇾','🇧🇪','🇧🇿','🇧🇯','🇧🇲','🇧🇹','🇧🇴','🇧🇦','🇧🇼'],
    nc34: ['🇧🇷','🇻🇬','🇧🇳','🇧🇬','🇧🇫','🇧🇮','🇰🇭','🇨🇲','🇨🇦','🇮🇨','🇨🇻','🇧🇶'],
    nc35: ['🇰🇾','🇨🇫','🇹🇩','🇨🇱','🇨🇳','🇨🇽','🇨🇨','🇨🇴','🇰🇲','🇨🇬','🇨🇩','🇨🇰'],
    nc36: ['🇨🇷','🇨🇮','🇭🇷','🇨🇺','🇨🇼','🇨🇾','🇨🇿','🇩🇰','🇩🇯','🇩🇲','🇩🇴','🇪🇨'],
    nc37: ['🇪🇬','🇸🇻','🇬🇶','🇪🇷','🇪🇪','🇪🇹','🇪🇺','🇫🇰','🇫🇴','🇫🇯','🇫🇮','🇫🇷'],
    nc38: ['🇬🇫','🇵🇫','🇹🇫','🇬🇦','🇬🇲','🇬🇪','🇩🇪','🇬🇭','🇬🇮','🇬🇷','🇬🇱','🇬🇩'],
    nc39: ['🇬🇵','🇬🇺','🇬🇹','🇬🇬','🇬🇳','🇬🇼','🇬🇾','🇭🇹','🇭🇳','🇭🇰','🇭🇺','🇮🇸'],
    nc40: ['🇮🇳','🇮🇩','🇮🇷','🇮🇶','🇮🇪','🇮🇲','🇮🇱','🇮🇹','🇯🇲','🇯🇵','🇯🇪','🇯🇴'],
    nc41: ['⚽','🏀','🏈','⚾','🥎','🎾','🏐','🏉','🥏','🎱','🏓','🏸'],
    nc42: ['🏒','🏑','🏏','🥍','🏹','🎣','🥊','🥋','⛸️','🛷','⛷️','🏂'],
    nc43: ['🏋️','🤸','🤼','🤽','🤾','🤺','🏌️','🏇','🧘','🏄','🚣','🏊'],
    nc44: ['🚴','🚵','🎯','🎳','🎰','🎲','♠️','♥️','♦️','♣️','🃏','🀄'],
    nc45: ['🎴','🎭','🎨','🎪','🎤','🎧','🎼','🎹','🥁','🎷','🎺','🎸'],
    nc46: ['🎻','🪕','🎬','🎮','👾','🎯','🎲','🧩','♟️','🎖️','🏆','🏅'],
    nc47: ['🥇','🥈','🥉','⚽','🏀','🏈','⚾','🎾','🏐','🏉','🎱','🏓'],
    nc48: ['🏸','🥍','🏑','🏒','🏏','⛳','🥌','🎣','🤿','🥊','🥋','🎽'],
    nc49: ['🛹','🛼','🛸','🤹','🧗','🧭','🧱','🪢','🧶','🧵','🪡','🪤'],
    nc50: ['🪣','🪥','🪦','🪫','🔋','💡','🔦','🪔','🕯️','🪩','🪆','🎎'],
    nc51: ['🍏','🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍈','🍒'],
    nc52: ['🍑','🥭','🍍','🥥','🥝','🍅','🍆','🥑','🥦','🥬','🥒','🌶️'],
    nc53: ['🫑','🌽','🥕','🧄','🧅','🥔','🍠','🥐','🥯','🍞','🥖','🥨'],
    nc54: ['🧀','🥚','🍳','🧈','🥞','🧇','🥓','🥩','🍗','🍖','🦴','🌭'],
    nc55: ['🍔','🍟','🍕','🥪','🥙','🧆','🌮','🌯','🥗','🥘','🫔','🍝'],
    nc56: ['🍜','🍲','🍛','🍣','🍱','🥟','🦪','🍤','🍙','🍚','🍘','🍥'],
    nc57: ['🥠','🥮','🍡','🍢','🍧','🍨','🍦','🥧','🧁','🍰','🎂','🍮'],
    nc58: ['🍭','🍬','🍫','🍿','🍩','🍪','🌰','🥜','🫘','🍯','🥛','🧃'],
    nc59: ['🧋','🧉','🍵','🍶','🍾','🍷','🍸','🍹','🍺','🍻','🥂','🥃'],
    nc60: ['🧊','🥤','🧂','🥄','🍴','🥢','🍽️','🔪','🏺','🎀','🎁','💝'],
    nc61: ['🌲','🌳','🌴','🌵','🌾','🌿','☘️','🍀','🍁','🍂','🍃','🪹'],
    nc62: ['🪺','🍄','🌰','🦀','🦞','🦐','🦑','🐚','🪸','🐠','🐟','🐡'],
    nc63: ['🐬','🐳','🐋','🦈','🐊','🐅','🐆','🦓','🦍','🦧','🦣','🐘'],
    nc64: ['🦛','🦏','🐪','🐫','🦒','🦘','🦬','🐃','🐂','🐄','🐎','🐖'],
    nc65: ['🐏','🐑','🦙','🐐','🦌','🐕','🐩','🐈','🐓','🦃','🦤','🦚'],
    nc66: ['🦜','🦢','🦩','🕊️','🐇','🦝','🦨','🦡','🦫','🦦','🦥','🐿️'],
    nc67: ['🐀','🐁','🐭','🐹','🐰','🦊','🐻','🐻‍❄️','🐨','🐼','🐸','🐒'],
    nc68: ['🦎','🐍','🐢','🐉','🦕','🦖','🐙','🦑','🦐','🦞','🦀','🐡'],
    nc69: ['🐠','🐟','🐬','🐳','🐋','🦈','🐊','🐅','🐆','🦓','🦍','🦧'],
    nc70: ['🌋','🗻','🏔️','⛰️','🏕️','🏖️','🏜️','🏝️','🏞️','🏟️','🏛️','🏗️'],
    nc71: ['⌚','📱','💻','🖥️','🖨️','📷','📹','🎥','📺','📻','🎙️','🎚️'],
    nc72: ['🎛️','🧭','⏱️','⏲️','⏰','🕰️','⌛','⏳','📡','🔋','🪫','💡'],
    nc73: ['🔦','🪔','🕯️','🪩','🪆','🎎','🎐','🎑','🧧','🎀','🎁','🎗️'],
    nc74: ['🎟️','🎫','🎖️','🏆','🏅','🥇','🥈','🥉','⚽','🏀','🏈','⚾'],
    nc75: ['🥎','🎾','🏐','🏉','🥏','🎱','🏓','🏸','🏒','🏑','🏏','🥍'],
    nc76: ['🏹','🎣','🤿','🥊','🥋','🎽','🛹','🛼','🛷','⛸️','🥌','🎿'],
    nc77: ['⛷️','🏂','🏋️','🤸','🤼','🤽','🤾','🤺','🏌️','🏇','🧘','🏄'],
    nc78: ['🚣','🏊','⛹️','🏋️','🚴','🚵','🏎️','🏍️','🛵','🛺','🚲','🛴'],
    nc79: ['🚀','🛸','🛰️','🪐','🌠','🌌','🌃','🏙️','🌇','🌅','🌄','🌈'],
    nc80: ['☁️','⛅','⛈️','🌤️','🌥️','🌦️','🌧️','🌨️','🌩️','🌪️','🌫️','🌬️'],
    nc81: ['❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❤️‍🔥','❤️‍🩹'],
    nc82: ['💕','💞','💓','💗','💖','💘','💝','💟','☮️','✝️','☪️','🕉️'],
    nc83: ['☸️','✡️','🔯','🕎','☯️','☦️','🛐','⛎','♈','♉','♊','♋'],
    nc84: ['♌','♍','♎','♏','♐','♑','♒','♓','🆔','⚛️','🉑','☢️'],
    nc85: ['☣️','📴','📳','🈶','🈚','🈸','🈺','🈷️','✴️','🆚','💮','🉐'],
    nc86: ['㊙️','㊗️','🈴','🈵','🈹','🈲','🅰️','🅱️','🆎','🆑','🅾️','🆘'],
    nc87: ['🆚','🈁','🈂️','🚻','🚹','🚺','🚼','🚾','⚠️','🚸','⛔','🚫'],
    nc88: ['🚳','🚭','🚯','🚱','🚷','📵','🔞','☢️','☣️','⬆️','↗️','➡️'],
    nc89: ['↘️','⬇️','↙️','⬅️','↖️','↕️','↔️','↩️','↪️','⤴️','⤵️','🔃'],
    nc90: ['🔄','🔙','🔚','🔛','🔜','🔝','🛐','⚛️','🕉️','✡️','☸️','☯️'],
    nc91: ['😀','😃','😄','😁','😆','😅','🤣','😂','🙂','🙃','🫠','😉'],
    nc92: ['😊','😇','🥰','😍','🤩','😘','😗','☺️','😚','😙','🥲','😋'],
    nc93: ['😛','😜','🤪','😝','🤑','🤗','🤭','🫢','🫣','🤫','🤔','🪄'],
    nc94: ['😐','😑','😶','🫥','😏','😒','🙄','😬','🤥','😌','😔','😪'],
    nc95: ['🤤','😴','💤','😷','🤒','🤕','🤢','🤮','🤧','🥵','🥶','🥴'],
    nc96: ['😵','🤯','🤠','🥳','🥸','😎','🤓','🧐','😕','🫤','😟','🙁'],
    nc97: ['☹️','😮','😯','😲','😳','🥺','🥹','😦','😧','😨','😰','😥'],
    nc98: ['😢','😭','😱','😖','😣','😞','😓','😩','😫','🥱','😤','😡'],
    nc99: ['😠','🤬','😈','👿','💀','☠️','💩','🤡','👹','👺','👻','👽'],
    nc100: ['👾','🤖','🎃','😺','😸','😹','😻','😼','😽','🙀','😿','😾']
};

// ========== TRIPLE ATTACK DEFINITIONS (35 TRIPLES) ==========
const tripleNcCombos = {
    triple1: ['nc1', 'nc2', 'nc3'],
    triple2: ['nc4', 'nc5', 'nc6'],
    triple3: ['nc7', 'nc8', 'nc9'],
    triple4: ['nc10', 'nc11', 'nc12'],
    triple5: ['nc13', 'nc14', 'nc15'],
    triple6: ['nc16', 'nc17', 'nc18'],
    triple7: ['nc19', 'nc20', 'nc21'],
    triple8: ['nc22', 'nc23', 'nc24'],
    triple9: ['nc25', 'nc26', 'nc27'],
    triple10: ['nc28', 'nc29', 'nc30'],
    triple11: ['nc31', 'nc32', 'nc33'],
    triple12: ['nc34', 'nc35', 'nc36'],
    triple13: ['nc37', 'nc38', 'nc39'],
    triple14: ['nc40', 'nc41', 'nc42'],
    triple15: ['nc43', 'nc44', 'nc45'],
    triple16: ['nc46', 'nc47', 'nc48'],
    triple17: ['nc49', 'nc50', 'nc51'],
    triple18: ['nc52', 'nc53', 'nc54'],
    triple19: ['nc55', 'nc56', 'nc57'],
    triple20: ['nc58', 'nc59', 'nc60'],
    triple21: ['nc61', 'nc62', 'nc63'],
    triple22: ['nc64', 'nc65', 'nc66'],
    triple23: ['nc67', 'nc68', 'nc69'],
    triple24: ['nc70', 'nc71', 'nc72'],
    triple25: ['nc73', 'nc74', 'nc75'],
    triple26: ['nc76', 'nc77', 'nc78'],
    triple27: ['nc79', 'nc80', 'nc81'],
    triple28: ['nc82', 'nc83', 'nc84'],
    triple29: ['nc85', 'nc86', 'nc87'],
    triple30: ['nc88', 'nc89', 'nc90'],
    triple31: ['nc91', 'nc92', 'nc93'],
    triple32: ['nc94', 'nc95', 'nc96'],
    triple33: ['nc97', 'nc98', 'nc99'],
    triple34: ['nc100', 'nc1', 'nc2'],
    triple35: ['nc3', 'nc4', 'nc5']
};

// ========== CUSTOM FONT CONVERSION ==========
const customFontMap = {
    'T': 'ᴛ', 'ʀ': 'ʀ', 'ɪ': 'ɪ', 'ᴘ': 'ᴘ', 'ʟ': 'ʟ', 'ᴇ': 'ᴇ',
    'ɴ': 'ɴ', 'ᴄ': 'ᴄ', 's': 's', 'ᴛ': 'ᴛ', 'ᴀ': 'ᴀ', 'ʀ': 'ʀ',
    'ᴅ': 'ᴅ', 'ǫ': 'ǫ', 'ᴡ': 'ᴡ', 'ᴇ': 'ᴇ', 'ʀ': 'ʀ', 'ᴛ': 'ᴛ',
    'ʏ': 'ʏ', 'ᴜ': 'ᴜ', 'ɪ': 'ɪ', 'ᴏ': 'ᴏ', 'ᴘ': 'ᴘ', 'ʟ': 'ʟ',
    'ᴋ': 'ᴋ', 'ᴊ': 'ᴊ', 'ʜ': 'ʜ', 'ɢ': 'ɢ', 'ғ': 'ғ', 'ᴅ': 'ᴅ',
    's': 's', 'ᴀ': 'ᴀ', 'ᴢ': 'ᴢ', 'x': 'x', 'ᴄ': 'ᴄ', 'ᴠ': 'ᴠ',
    'ʙ': 'ʙ', 'ɴ': 'ɴ', 'ᴍ': 'ᴍ',
    
    'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ', 'G': 'ɢ',
    'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
    'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ',
    'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
    
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', 
    '6': '6', '7': '7', '8': '8', '9': '9',
    
    ' ': ' ', '.': '.', ',': ',', '!': '!', '?': '?', ':': ':', 
    ';': ';', '(': '(', ')': ')', '[': '[', ']': ']', '{': '{', 
    '}': '}', '@': '@', '#': '#', '$': '$', '%': '%', '^': '^', 
    '&': '&', '*': '*', '-': '-', '_': '_', '=': '=', '+': '+', 
    '|': '|', '\\': '\\', '/': '/', '<': '<', '>': '>', '"': '"', 
    "'": "'", '`': '`', '~': '~'
};

function convertToCustomFont(text) {
    return text.split('').map(char => customFontMap[char] || char).join('');
}

function applyFont(text, fontName) {
    const font = fontStyles[fontName];
    if (!font) return text;
    
    return text.split('').map(char => {
        if (font.map[char]) return font.map[char];
        if (font.map[char.toUpperCase()]) {
            return font.map[char.toUpperCase()];
        }
        return char;
    }).join('');
}

// ========== ALL REPLY MESSAGES ==========
const replyMessages = {
    ᴀYUSHBot: '🕷️ 𝑨YUSH 🕷️',
    tripleNcStarted: '🔥 ᴀYUSH ULTRA FAST triple nc started (10x)',
    ncStarted: 'ᴀYUSH nc started',
    csStarted: 'ᴀYUSH cs nc started',
    ncStopped: 'ᴀYUSH nc stopped',
    csStopped: 'ᴀYUSH cs attack stopped',
    tripleDelaySet: 'ᴀYUSH triple delay set to',
    ncDelaySet: 'ᴀYUSH nc delay set to',
    youAreNowOwner: '👑 𝙰𝙱 𝚃𝚄 𝙱𝙾𝚃 𝙺𝙰 𝙼𝙰𝙻𝙸𝙺 𝙱𝙰𝙽 𝙲𝙷𝚄𝙺𝙰 𝙷𝙰𝙸',
    youAreAlreadyOwner: '👑 𝚈𝙾𝚄 𝙰𝚁𝙴 𝙰𝙻𝚁𝙴𝙰𝙳𝚈 𝚃𝙷𝙴 𝙱𝙾𝚃 𝙾𝚆𝙽𝙴𝚁',
    ownerAlreadyExists: '👑 𝙱𝙾𝚃 𝙾𝚆𝙽𝙴𝚁 𝙰𝙻𝚁𝙴𝙰𝙳𝚈 𝙴𝚇𝙸𝚂𝚃𝚂',
    youAreNoLongerOwner: '👑 𝚈𝙾𝚄 𝙰𝚁𝙴 𝙽𝙾 𝙻𝙾𝙽𝙶𝙴𝚁 𝚃𝙷𝙴 𝙱𝙾𝚃 𝙾𝚆𝙽𝙴𝚁',
    youAreNotOwner: '👑 𝚈𝙾𝚄 𝙰𝚁𝙴 𝙽𝙾𝚃 𝚃𝙷𝙴 𝙱𝙾𝚃 𝙾𝚆𝙽𝙴𝚁',
    botAdminAdded: '✅ 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝙰𝙳𝙳𝙴𝙳',
    alreadyBotAdmin: '⚠️ 𝙰𝙻𝚁𝙴𝙰𝙳𝚈 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽',
    botAdminRemoved: '✅ 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝚁𝙴𝙼𝙾𝚅𝙴𝙳',
    notBotAdmin: '❌ 𝙽𝙾𝚃 𝙰 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽',
    subAdminAdded: '✅ 𝙱𝙾𝚃 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽 𝙰𝙳𝙳𝙴𝙳',
    alreadySubAdmin: '⚠️ 𝙰𝙻𝚁𝙴𝙰𝙳𝚈 𝙱𝙾𝚃 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽',
    subAdminRemoved: '✅ 𝙱𝙾𝚃 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽 𝚁𝙴𝙼𝙾𝚅𝙴𝙳',
    notSubAdmin: '❌ 𝙽𝙾𝚃 𝙰 𝙱𝙾𝚃 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽',
    replyToSomeone: '⚠️ 𝚁𝙴𝙿𝙻𝚈 𝚃𝙾 𝚂𝙾𝙼𝙴𝙾𝙽𝙴',
    invalidPhone: '❌ 𝙸𝙽𝚅𝙰𝙻𝙸𝙳 𝙿𝙷𝙾𝙽𝙴 𝙽𝚄𝙼𝙱𝙴𝚁',
    useInGroup: '⚠️ 𝚄𝚂𝙴 𝙸𝙽 𝙶𝚁𝙾𝚄𝙿',
    delayTooLow: '⚠️ 𝙳𝙴𝙻𝙰𝚈 𝙼𝚄𝚂𝚃 𝙱𝙴 >= 100𝙼𝚂',
    invalidNcNumber: '❌ 𝙸𝙽𝚅𝙰𝙻𝙸𝙳 𝙽𝙲 𝙽𝚄𝙼𝙱𝙴𝚁 𝚄𝚂𝙴 𝙽𝙲1 𝚃𝙾 𝙽𝙲100',
    usage: '📝 𝚄𝚂𝙰𝙶𝙴',
    activeBots: '🤖 𝙰𝙲𝚃𝙸𝚅𝙴 𝙱𝙾𝚃𝚂',
    ᴀYUSHStatus: '📊 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚂𝚃𝙰𝚃𝚄𝚂',
    individualNc: '𝚒𝚗𝚍𝚒𝚟𝚒𝚍𝚞𝚊𝚕 𝚗𝚌',
    constantText: '𝚌𝚘𝚗𝚜𝚝𝚊𝚗𝚝 𝚝𝚎𝚡𝚝',
    tripleAttacks: '𝚝𝚛𝚒𝚙𝚕𝚎 𝚊𝚝𝚝𝚊𝚌𝚔𝚜',
    constantTexts: '𝚌𝚘𝚗𝚜𝚝𝚊𝚗𝚝 𝚝𝚎𝚡𝚝𝚜',
    AYUSHPing: '🏓 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝙿𝙸𝙽𝙶',
    activeBotsCount: '𝚊𝚌𝚝𝚒𝚟𝚎 𝚋𝚘𝚝𝚜',
    connected: '✅ 𝙲𝙾𝙽𝙽𝙴𝙲𝚃𝙴𝙳',
    pairingCode: '🔑 𝙿𝙰𝙸𝚁𝙸𝙽𝙶 𝙲𝙾𝙳𝙴',
    number: '📱 𝙽𝚄𝙼𝙱𝙴𝚁',
    total: '📊 𝚃𝙾𝚃𝙰𝙻',
    pinging: '🏓 𝙿𝙸𝙽𝙶𝙸𝙽𝙶...',
    latency: '📶 𝙻𝙰𝚃𝙴𝙽𝙲𝚈',
    botCreated: '✅ 𝙱𝙾𝚃 𝙲𝚁𝙴𝙰𝚃𝙴𝙳',
    realTripleAttack: '🔥 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚄𝙻𝚃𝚁𝙰 𝙵𝙰𝚂𝚃 𝚃𝚁𝙸𝙿𝙻𝙴 𝙰𝚃𝚃𝙰𝙲𝙺 𝚂𝚃𝙰𝚁𝚃𝙴𝙳 (10𝚇)',
    slideAttackStarted: '𝚜𝚕𝚒𝚍𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    slideAttackStopped: '𝚜𝚕𝚒𝚍𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    textAttackStarted: '𝚝𝚎𝚡𝚝 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    textAttackStopped: '𝚝𝚎𝚡𝚝 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    ttsAttackStarted: '𝚝𝚝𝚜 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    ttsAttackStopped: '𝚝𝚝𝚜 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    picAttackStarted: '𝚙𝚒𝚌𝚝𝚞𝚛𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    picAttackStopped: '𝚙𝚒𝚌𝚝𝚞𝚛𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    videoSpamStarted: '𝚟𝚒𝚍𝚎𝚘 𝚜𝚙𝚊𝚖 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    videoSpamStopped: '𝚟𝚒𝚍𝚎𝚘 𝚜𝚙𝚊𝚖 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    allStopped: '𝚊𝚕𝚕 𝚊𝚝𝚝𝚊𝚌𝚔𝚜 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    rageStarted: '🔥 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚛𝚊𝚐𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    rageStopped: '🔥 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚛𝚊𝚐𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    grpfpStarted: '𝚐𝚛𝚘𝚞𝚙 𝚍𝚙 𝚌𝚑𝚊𝚗𝚐𝚎 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    grpfpStopped: '𝚐𝚛𝚘𝚞𝚙 𝚍𝚙 𝚌𝚑𝚊𝚗𝚐𝚎 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    reactEmojiSet: '𝚛𝚎𝚊𝚌𝚝 𝚎𝚖𝚘𝚓𝚒 𝚜𝚎𝚝 𝚝𝚘',
    reactStopped: '𝚊𝚞𝚝𝚘 𝚛𝚎𝚊𝚌𝚝 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    onlyOwner: '👑 𝙾𝙽𝙻𝚈 𝙱𝙾𝚃 𝙾𝚆𝙽𝙴𝚁 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂',
    onlyBotAdmin: '👑 𝙾𝙽𝙻𝚈 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝙲𝙰𝙽 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂',
    grpstkStarted: '𝚜𝚝𝚒𝚌𝚔𝚎𝚛 𝚜𝚕𝚒𝚍𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    grpstkStopped: '𝚜𝚝𝚒𝚌𝚔𝚎𝚛 𝚜𝚕𝚒𝚍𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    gifSpamStarted: '𝚐𝚒𝚏 𝚜𝚙𝚊𝚖 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    gifSpamStopped: '𝚐𝚒𝚏 𝚜𝚙𝚊𝚖 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    stickerSpamStarted: '𝚜𝚝𝚒𝚌𝚔𝚎𝚛 𝚜𝚙𝚊𝚖 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    stickerSpamStopped: '𝚜𝚝𝚒𝚌𝚔𝚎𝚛 𝚜𝚙𝚊𝚖 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    kickStarted: '👢 𝚔𝚒𝚌𝚔𝚒𝚗𝚐 𝚊𝚕𝚕 𝚖𝚎𝚖𝚋𝚎𝚛𝚜...',
    kickDone: '✅ 𝚔𝚒𝚌𝚔 𝚌𝚘𝚖𝚙𝚕𝚎𝚝𝚎𝚍',
    botNotAdmin: '❌ 𝙱𝙾𝚃 𝙸𝚂 𝙽𝙾𝚃 𝙰𝙽 𝙰𝙳𝙼𝙸𝙽',
    checkingAdmin: '🔍 𝚌𝚑𝚎𝚌𝚔𝚒𝚗𝚐 𝚊𝚍𝚖𝚒𝚗 𝚜𝚝𝚊𝚝𝚞𝚜...',
    reconnectMsg: '🔄 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚊𝚞𝚝𝚘 𝚛𝚎𝚌𝚘𝚗𝚗𝚎𝚌𝚝𝚒𝚗𝚐...',
    disconnected: '⚠️ Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚍𝚒𝚜𝚌𝚘𝚗𝚗𝚎𝚌𝚝𝚎𝚍, 𝚛𝚎𝚌𝚘𝚗𝚗𝚎𝚌𝚝𝚒𝚗𝚐 𝚒𝚗 5𝚜',
    badMacError: '⚠️ 𝚜𝚎𝚜𝚜𝚒𝚘𝚗 𝚎𝚛𝚛𝚘𝚛, Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚛𝚎𝚌𝚘𝚗𝚗𝚎𝚌𝚝𝚒𝚗𝚐...',
    vnStarted: '🎤 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚟𝚘𝚒𝚌𝚎 𝚗𝚘𝚝𝚎 𝚜𝚙𝚊𝚖 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    vnStopped: '🎤 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚟𝚘𝚒𝚌𝚎 𝚗𝚘𝚝𝚎 𝚜𝚙𝚊𝚖 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    attackStarted: '💥 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚄𝙻𝚃𝙸𝙼𝙰𝚃𝙴 𝙰𝚃𝚃𝙰𝙲𝙺 𝚂𝚃𝙰𝚁𝚃𝙴𝙳 (100 𝙽𝙲 𝚂𝙸𝙼𝚄𝙻𝚃𝙰𝙽𝙴𝙾𝚄𝚂𝙻𝚈)',
    attackStopped: '💥 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚞𝚕𝚝𝚒𝚖𝚊𝚝𝚎 𝚊𝚝𝚝𝚊𝚌𝚔 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    wordAdded: '✅ 𝚠𝚘𝚛𝚍 𝚊𝚍𝚍𝚎𝚍 𝚝𝚘 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚕𝚒𝚜𝚝',
    wordRemoved: '✅ 𝚠𝚘𝚛𝚍 𝚛𝚎𝚖𝚘𝚟𝚎𝚍 𝚏𝚛𝚘𝚖 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚕𝚒𝚜𝚝',
    wordsCleared: '🧹 𝚊ll Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚠𝚘𝚛𝚍𝚜 𝚌𝚕𝚎𝚊𝚛𝚎𝚍',
    wordList: '📋 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚠𝚘𝚛𝚍 𝚕𝚒𝚜𝚝',
    noWords: '❌ 𝚗𝚘 𝚠𝚘𝚛𝚍𝚜 𝚒𝚗 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚕𝚒𝚜𝚝',
    useWordsStarted: '📝 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚠𝚘𝚛𝚍 𝚗𝚌 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    useWordsStopped: '📝 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚠𝚘𝚛𝚍 𝚗𝚌 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    coverGCStarted: '🔥 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝙲𝙾𝚅𝙴𝚁 𝙶𝙲 𝚂𝚃𝙰𝚁𝚃𝙴𝙳 (𝙼𝙰𝚇 𝚂𝙿𝙴𝙴𝙳)',
    coverGCStopped: '🔥 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚌𝚘𝚟𝚎𝚛 𝚐𝚌 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    speedUpSet: '⚡ Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚜𝚙𝚎𝚎𝚍 𝚞𝚙 𝚜𝚎𝚝 𝚝𝚘',
    rageModeStarted: '😤 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚁𝙰𝙶𝙴 𝙼𝙾𝙳𝙴 𝚂𝚃𝙰𝚁𝚃𝙴𝙳 (𝙷𝚈𝙿𝙴𝚁 𝙳𝙴𝙽𝚂𝙸𝚃𝚈)',
    rageModeStopped: '😤 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚛𝚊𝚐𝚎 𝚖𝚘𝚍𝚎 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    timeNCStarted: '⏱️ Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚝𝚒𝚖𝚎 𝚗𝚌 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    timeNCStopped: '⏱️ Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚝𝚒𝚖𝚎 𝚗𝚌 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    ncLoopStarted: '🔄 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚗𝚌 𝚕𝚘𝚘𝚙 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    ncLoopStopped: '🔄 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚗𝚌 𝚕𝚘𝚘𝚙 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    heartLoopStarted: '💞 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚑𝚎𝚊𝚛𝚝 𝚕𝚘𝚘𝚙 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    heartLoopStopped: '💞 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚑𝚎𝚊𝚛𝚝 𝚕𝚘𝚘𝚙 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    ncSpamStarted: '🌊 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚗𝚌 𝚜𝚙𝚊𝚖 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    ncSpamStopped: '🌊 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚗𝚌 𝚜𝚙𝚊𝚖 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    targetStarted: '🎯 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚝𝚊𝚛𝚐𝚎𝚝 𝚜𝚕𝚒𝚍𝚎 𝚜𝚝𝚊𝚛𝚝𝚎𝚍',
    targetStopped: '🎯 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚝𝚊𝚛𝚐𝚎𝚝 𝚜𝚕𝚒𝚍𝚎 𝚜𝚝𝚘𝚙𝚙𝚎𝚍',
    tagAll: '🔔 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚝𝚊𝚐 𝚊𝚕𝚕',
    promoted: '👑 𝙿𝚁𝙾𝙼𝙾𝚃𝙴𝙳 𝚃𝙾 𝚆𝙷𝙰𝚃𝚂𝙰𝙿𝙿 𝙰𝙳𝙼𝙸𝙽',
    demoted: '⬇️ 𝙳𝙴𝙼𝙾𝚃𝙴𝙳 𝙵𝚁𝙾𝙼 𝚆𝙷𝙰𝚃𝚂𝙰𝙿𝙿 𝙰𝙳𝙼𝙸𝙽',
    blocked: '🚫 𝚄𝚂𝙴𝚁 𝙱𝙻𝙾𝙲𝙺𝙴𝙳',
    unblocked: '🔓 𝚄𝚂𝙴𝚁 𝚄𝙽𝙱𝙻𝙾𝙲𝙺𝙴𝙳',
    joined: '🔗 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚓𝚘𝚒𝚗𝚎𝚍 𝚐𝚛𝚘𝚞𝚙',
    left: '🚪 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚕𝚎𝚏𝚝 𝚐𝚛𝚘𝚞𝚙',
    groupLink: '🔗 𝙶𝚁𝙾𝚄𝙿 𝙻𝙸𝙽𝙺',
    multiGC: '📋 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚖𝚞𝚕𝚝𝚒 𝚐𝚌 𝚕𝚒𝚜𝚝',
    botDisabled: '🔴 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚋𝚘𝚝 𝚍𝚒𝚜𝚊𝚋𝚕𝚎𝚍',
    botEnabled: '🟢 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚋𝚘𝚝 𝚎𝚗𝚊𝚋𝚕𝚎𝚍',
    prefixChanged: '🧡 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚙𝚛𝚎𝚏𝚒𝚡 𝚌𝚑𝚊𝚗𝚐𝚎𝚍 𝚝𝚘',
    cacheCleared: '🧹 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚌𝚊𝚌𝚑𝚎 𝚌𝚕𝚎𝚊𝚛𝚎𝚍',
    fontsMenu: '🎨 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚏𝚘𝚗𝚝 𝚐𝚊𝚕𝚕𝚎𝚛𝚢',
    delaysInfo: '⏱️ Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚌𝚞𝚛𝚛𝚎𝚗𝚝 𝚍𝚎𝚕𝚊𝚢𝚜',
    triplesInfo: '😶‍🌫️ Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? 𝚝𝚛𝚒𝚙𝚕𝚎𝚜 𝚒𝚗𝚏𝚘'
};

// ========== MENU ==========
const AyushMenu = `╔═══❖•ೋ° °ೋ•❖═══╗
      🕷️ GOD AYUSH BOT 🕷️
╚═══❖•ೋ° °ೋ•❖═══╝
◎ ══════ ❈ ══════ ◎
👑 𝘽𝙊𝙏 𝙊𝙒𝙉𝙀𝙍 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 (Database)
◎ ══════ ❈ ══════ ◎
👑!owner - Claim Bot Ownership (DM Only • First Claim)
🔓!removeowner - Remove Yourself As Owner (DM Only)
➕!addadmin - Add Bot Admin (Owner Only • DM • Reply)
🗑️!removeadmin - Remove Bot Admin (Owner/Admin • DM • Reply)
📋!listadmins - List All Bot Admins

◎ ══════ ❈ ══════ ◎
👥 𝘽𝙊𝙏 𝙎𝙐𝘽-𝘼𝘿𝙈𝙄𝙉 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 (Per Group)
◎ ══════ ❈ ══════ ◎
👥!sub - Add Bot Sub-Admin (Owner/Admin • Group • Reply)
🚫!removesub - Remove Bot Sub-Admin (Owner/Admin • Group • Reply)
📋!listsub - List Sub-Admins In Current Group

◎ ══════ ❈ ══════ ◎
👥 𝙒𝙃𝘼𝙏𝙎𝘼𝙋𝙋 𝙂𝙍𝙊𝙐𝙋 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 (WhatsApp)
◎ ══════ ❈ ══════ ◎
👑!wadmin - Promote To WhatsApp Group Admin
⬇️!wremoveadmin - Demote From WhatsApp Group Admin
📋!wadmins - List WhatsApp Group Admins

◎ ══════ ❈ ══════ ◎ 
🤖 𝘽𝙊𝙏 𝙈𝘼𝙉𝘼𝙂𝙀𝙈𝙀𝙉𝙏
◎ ══════ ❈ ══════ ◎
💥!add [No] - Add New Sessions
👾!bots - Shows All Bots
🎐!ping - Bot Ping Ms

╔══════════════════════════╗
║  🎨 𝙁𝙊𝙉𝙏 𝙉𝘾 𝘼𝙏𝙏𝘼𝘾𝙆 🎨    ║
╚══════════════════════════╝
🔷 double - 𝔸𝔹ℂ𝔻𝔼  (Double Strike)
🟫 mono - 𝙰𝙱𝙲𝙳𝙴  (Monospace)
✨ script - 𝒜𝐵𝒞𝒟𝐸  (Script/Cursive)
💫 boldscript - 𝓐𝓑𝓒𝓓𝓔  (Bold Script)
🖤 gothic - 𝔄𝔅ℭ𝔇𝔈  (Gothic)
⚔️ boldgothic - 𝕬𝕭𝕮𝕯𝕰  (Bold Gothic)
🟦 square - ＡＢＣＤＥ  (Fullwidth)
🔵 circled - ⒶⒷⒸⒹⒺ  (Circled)
🎀 !tne [font] [nc#] [text] [delay] - Font NC Attack

◎ ══════ ❈ ══════ ◎ 
☠️ 𝙉𝘾!𝙏𝙍𝙄𝙋𝙇𝙀 𝘼𝙏𝙏𝘼𝘾𝙆 ☠️
◎ ══════ ❈ ══════ ◎
✨!nc1 to !nc100 [text] - Simple Nc Attack
🔁!ncloop [nc#] [text] [rounds] - Loops NC Getting Faster Each Round
🛑!stopncloop - Stops NC Loop
💞!loopheart [text] [delay] - NC With Looping Hearts Wrapping Text
🛑!stoploopheart - Stops Heart Loop
📝!addwords [word1] [word2]... - Save Words For NC Use
📋!mywords - View All Saved Words
🗑️!removeword [#] - Remove A Word By Number
🧹!clearwords - Wipe All Saved Words
🔤!usewords [nc#] [delay] - NC Using All Your Saved Words
🛑!stopusewords - Stops Word NC
🔥!covergc [text] - MAX Speed NC — All 100 Sets Zero Delay
🛑!stopcovergc - Stops CoverGC
⚡!speedup [ms] - Sets ALL Delays To 0ms (Max Speed) Or Custom ms
😤!rage [nc#] [text] - RAGE MODE — Hyper Density NC Storm (5x threads, 0ms)
🛑!stoprage - Stops Rage Mode
🌴!dnc - Stops Nc Attack
⏱️!timenc [nc#] [text] - NC With Live Clock In Group Name
🔥!triple1 to !triple35 [text] - 3 Nc Forms At Once
🌊!ncspam [nc#] [text] [delay] - After 10 Nc It Spams Once
💗+Smash - Nc+Text+Slide Works All At Once

◎ ══════ ❈ ══════ ◎ 
   🍀 𝙑𝙊𝙄𝘾𝙀 𝘼𝙏𝙏𝘼𝘾𝙆 🍀
◎ ══════ ❈ ══════ ◎
🩸!tts [text] - Sends A Single Voice Note
💤!ttsatk [text] [delay] - Spams Voice Note
❤️!stopttsatk - Stops Sending Vns

◎ ══════ ❈ ══════ ◎
      🩵𝙋𝙄𝘾-𝙂𝘾🩵
◎ ══════ ❈ ══════ ◎
💧!pic [delay] - Spams Picture (Reply To Image)
💋!stoppic - Stops Pic Spamming 
🎬!videospam [delay] - Spams Video (Reply To A Video)
⏹️!stopvideospam - Stops Video Spam
🌞!grpfp [delay] - Changes Group Profile Picture 
🤣!stopgrpfp - Stops Group Profile Change

◎ ══════ ❈ ══════ ◎ 
     🥂 𝘼𝙐𝙏𝙊 𝙍𝙀𝘼𝘾𝙏 🥂
◎ ══════ ❈ ══════ ◎
🌠!react [emoji] - Reacts To All Messages
☄️!stopreact - Stops Reacting 

◎ ══════ ❈ ══════ ◎
      🛑 𝙎𝙏𝙊𝙋𝙎 𝘼𝙇𝙇 🛑
◎ ══════ ❈ ══════ ◎
👽!stopall - Stops Everything 

◎ ══════ ❈ ══════ ◎
     📢 𝙂𝙍𝙊𝙐𝙋 𝙏𝙊𝙊𝙇𝙎 📢
◎ ══════ ❈ ══════ ◎
🔔!tagall [msg] - Tags Everyone In The Group
🚫!block - Blocks The Replied Member (Or DM Contact)
🔓!unblock [number] - Unblocks The Replied Member Or By Number
🔗!join [group link] - Bot Joins The Group Via Invite Link
📋!multigc - List All GCs & Start NC In Any Of Them
🚪!leave - Bot Leaves The Current Group Chat
🔗!grplink - Gets The Invite Link Of The Group
🎯!target [text] [delay] - Auto-Slides Every Time Replied Person Sends A Msg
🛑!stoptarget - Stops The Target Slide
🗣️!s [text] [delay] - Constant Slides At A Person
💨!txt [text] [delay] - Spams Text
🌝!stops - Stops Constant Slide Spam
🤩!stoptxt - Stops Text Spamming

◎ ══════ ❈ ══════ ◎
  🌙 𝙄𝙉𝙁𝙊𝙍𝙈𝘼𝙏𝙄𝙊𝙉 🌙
◎ ══════ ❈ ══════ ◎
🪾!menu - Shows The Whole Menu
💃!status - Active Attacks
☃️!delays - Shows Current Delays
😶‍🌫️!triples - All The Triples Emojies / Delays
🎨 !fonts - Full Font Gallery · 8 styles with live samples
👑!start - Starts Up / Reconnects All Bot Sessions
🔴!disable [BOT#] - Turns Off A Specific Bot Session
🟢!enable [BOT#] - Turns A Disabled Bot Back On
🧡!prefix [prefix/emoji] - Changes The Prefix Of The Commands
🧹!clearcatch - Clears All Cached/Processed Messages

◎ ══════ ❈ ══════ ◎ 
    💸 𝐀𝐘𝐔𝐒𝐇 𝙋𝙊𝙒𝙀𝙍 𝘽𝙊𝙏 💸
◎ ══════ ❈ ══════ ◎

📍 ᏀᴏD 𝐀𝐘𝐔𝐒𝐇 BOT - 𝙔𝙤𝙪𝙧 𝙐𝙡𝙩𝙞𝙢𝙖𝙩𝙚 𝙒𝙝𝙖𝙩𝙨𝘼𝙥𝙥 𝘽𝙤𝙩`;

function loadRoles() {
    try {
        if (fs.existsSync(ROLES_FILE)) {
            const data = fs.readFileSync(ROLES_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (err) {
        console.log('[ROLES] Using defaults');
    }
    return { ...defaultRoles };
}

function saveRoles(roles) {
    try {
        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });
        fs.writeFileSync(ROLES_FILE, JSON.stringify(roles, null, 2));
    } catch (err) {
        console.error('[ROLES] Error:', err.message);
    }
}

function loadDelays() {
    try {
        if (fs.existsSync(DELAYS_FILE)) {
            const data = fs.readFileSync(DELAYS_FILE, 'utf8');
            return { ...defaultDelays, ...JSON.parse(data) };
        }
    } catch (err) {
        console.log('[DELAYS] Using defaults');
    }
    return { ...defaultDelays };
}

function saveDelays(delays) {
    try {
        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });
        fs.writeFileSync(DELAYS_FILE, JSON.stringify(delays, null, 2));
    } catch (err) {
        console.error('[DELAYS] Error:', err.message);
    }
}

function loadWords() {
    try {
        if (fs.existsSync(WORDS_FILE)) {
            const data = fs.readFileSync(WORDS_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (err) {
        console.log('[WORDS] Using defaults');
    }
    return [];
}

function saveWords(words) {
    try {
        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });
        fs.writeFileSync(WORDS_FILE, JSON.stringify(words, null, 2));
    } catch (err) {
        console.error('[WORDS] Error:', err.message);
    }
}

function loadPrefix() {
    try {
        if (fs.existsSync(PREFIX_FILE)) {
            const data = fs.readFileSync(PREFIX_FILE, 'utf8');
            return JSON.parse(data).prefix || defaultPrefix;
        }
    } catch (err) {
        console.log('[PREFIX] Using default');
    }
    return defaultPrefix;
}

function savePrefix(prefix) {
    try {
        if (!fs.existsSync('./data')) fs.mkdirSync('./data', { recursive: true });
        fs.writeFileSync(PREFIX_FILE, JSON.stringify({ prefix }, null, 2));
    } catch (err) {
        console.error('[PREFIX] Error:', err.message);
    }
}

let roles = loadRoles();
let ncDelays = loadDelays();
let savedWords = loadWords();
let commandPrefix = loadPrefix();

function isOwner(jid) {
    return roles.owner === jid;
}

function isAdmin(jid) {
    return roles.admins.includes(jid);
}

function isSubAdmin(jid, groupJid) {
    return roles.subAdmins[groupJid]?.includes(jid) || false;
}

function hasPermission(jid, groupJid, botNumber = null) {
    return isOwner(jid) || isAdmin(jid) || isSubAdmin(jid, groupJid) || jid === botNumber;
}

function setOwner(jid) {
    if (!roles.owner) {
        roles.owner = jid;
        saveRoles(roles);
        return true;
    }
    return false;
}

function removeOwner() {
    roles.owner = null;
    saveRoles(roles);
    return true;
}

function addAdmin(jid) {
    if (!roles.admins.includes(jid)) {
        roles.admins.push(jid);
        saveRoles(roles);
        return true;
    }
    return false;
}

function removeAdmin(jid) {
    const index = roles.admins.indexOf(jid);
    if (index > -1) {
        roles.admins.splice(index, 1);
        saveRoles(roles);
        return true;
    }
    return false;
}

function addSubAdmin(jid, groupJid) {
    if (!roles.subAdmins[groupJid]) {
        roles.subAdmins[groupJid] = [];
    }
    if (!roles.subAdmins[groupJid].includes(jid)) {
        roles.subAdmins[groupJid].push(jid);
        saveRoles(roles);
        return true;
    }
    return false;
}

function removeSubAdmin(jid, groupJid) {
    if (roles.subAdmins[groupJid]) {
        const index = roles.subAdmins[groupJid].indexOf(jid);
        if (index > -1) {
            roles.subAdmins[groupJid].splice(index, 1);
            saveRoles(roles);
            return true;
        }
    }
    return false;
}

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const question = (text) => new Promise((resolve) => rl.question(text, resolve));

class CommandBus {
    constructor() {
        this.botSessions = new Map();
        this.processedMessages = new Map();
    }

    registerBot(botId, session) {
        this.botSessions.set(botId, session);
    }

    unregisterBot(botId) {
        this.botSessions.delete(botId);
    }

    shouldProcessMessage(msgId) {
        if (this.processedMessages.has(msgId)) return false;
        this.processedMessages.set(msgId, Date.now());
        return true;
    }

    async broadcastCommand(commandType, data, originBotId, sendConfirmation = true) {
        const bots = Array.from(this.botSessions.values()).filter(b => b.connected && !b.disabled);
        
        for (const bot of bots) {
            try {
                const isOrigin = bot.botId === originBotId;
                await bot.executeCommand(commandType, data, isOrigin && sendConfirmation);
            } catch (err) {
                console.error(`[${bot.botId}] Error:`, err.message);
            }
        }
    }

    getAllBots() {
        return Array.from(this.botSessions.values());
    }

    getConnectedBots() {
        return Array.from(this.botSessions.values()).filter(b => b.connected);
    }

    getLeaderBot() {
        const connected = this.getConnectedBots();
        return connected.length > 0 ? connected[0] : null;
    }
}

class BotSession {
    constructor(botId, phoneNumber, botManager, requestingJid = null) {
        this.botId = botId;
        this.phoneNumber = phoneNumber;
        this.botManager = botManager;
        this.requestingJid = requestingJid;
        this.sock = null;
        this.connected = false;
        this.botNumber = null;
        this.botNumberJid = null;
        this.botNumberSimple = null;
        this.authPath = `./auth/${botId}`;
        this.pairingCodeRequested = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 100;
        this.reconnecting = false;
        this.disabled = false;
        
        this.activeNameChanges = new Map();
        this.activeTripleNc = new Map();
        this.activeConstantAttacks = new Map();
        this.activeSlides = new Map();
        this.activeTargetSlides = new Map();
        this.activeTxtSenders = new Map();
        this.activeTTSSenders = new Map();
        this.activePicSenders = new Map();
        this.activeVideoSenders = new Map();
        this.activeGroupDpChanges = new Map();
        this.autoReactEmojis = new Map();
        this.rageSettings = new Map();
        this.activeNcLoop = null;
        this.activeHeartLoop = null;
        this.activeUseWords = null;
        this.activeCoverGC = null;
        this.activeTimeNC = null;
        this.activeRageMode = null;
        this.activeNcSpam = null;
        
        this.activeStickerSlides = new Map();
        this.activeGifSpam = new Map();
        this.activeStickerSpam = new Map();
        this.activeVnSpam = new Map();
        
        this.activeAttack = false;
        this.attackThreads = [];
    }

    async connect() {
        try {
            if (this.reconnecting || this.disabled) return;
            this.reconnecting = true;

            if (!fs.existsSync(this.authPath)) {
                fs.mkdirSync(this.authPath, { recursive: true });
            }

            const { state, saveCreds } = await useMultiFileAuthState(this.authPath);
            const { version } = await fetchLatestBaileysVersion();
            
            const needsPairing = !state.creds.registered;

            this.sock = makeWASocket({
                auth: state,
                logger: pino({ level: 'silent' }),
                browser: Browsers.macOS('Chrome'),
                version,
                printQRInTerminal: true,
                connectTimeoutMs: 60000,
                defaultQueryTimeoutMs: 0,
                keepAliveIntervalMs: 30000,
                generateHighQualityLinkPreview: false,
                syncFullHistory: false,
                markOnlineOnConnect: true,
                msgRetryCounterCache,
                shouldIgnoreJid: (jid) => {
                    return jid === 'status@broadcast';
                }
            });

            this.sock.ev.on('connection.update', async (update) => {
                const { connection, lastDisconnect, qr } = update;

                if (qr) {
                    console.log(`[${this.botId}] QR Code received`);
                }

                if (needsPairing && this.phoneNumber && !this.pairingCodeRequested && !state.creds.registered) {
                    this.pairingCodeRequested = true;
                    await delay(2000);
                    try {
                        const code = await this.sock.requestPairingCode(this.phoneNumber);
                        console.log(`[${this.botId}] Pairing code: ${code}`);
                        
                        if (this.requestingJid) {
                            const connectedBots = this.botManager.commandBus.getConnectedBots();
                            if (connectedBots.length > 0) {
                                const firstBot = connectedBots[0];
                                await firstBot.sock.sendMessage(this.requestingJid, {
                                    text: `${replyMessages.AYUSHBot}\n\n${replyMessages.pairingCode} ${code}\n\n${replyMessages.number} ${this.phoneNumber}`
                                });
                            }
                        } else {
                            console.log(`\n${replyMessages.ᴀYUSHBot}`);
                            console.log(`${replyMessages.pairingCode} ${code}`);
                            console.log(`${replyMessages.number} ${this.phoneNumber}\n`);
                        }
                    } catch (err) {
                        console.error(`[${this.botId}] Error getting pairing code:`, err.message);
                        this.pairingCodeRequested = false;
                    }
                }

                if (connection === 'close') {
                    const statusCode = (lastDisconnect?.error instanceof Boom)
                        ? lastDisconnect.error.output.statusCode
                        : 500;

                    console.log(`[${this.botId}] Connection closed. Status: ${statusCode}`);
                    this.connected = false;
                    this.reconnecting = false;

                    const isLoggedOut = statusCode === DisconnectReason.loggedOut;
                    
                    if (isLoggedOut) {
                        console.log(`[${this.botId}] Logged out. Removing session...`);
                        try {
                            fs.rmSync(this.authPath, { recursive: true, force: true });
                        } catch (e) {}
                        this.botManager.removeBot(this.botId);
                    } else if (!this.disabled) {
                        this.reconnectAttempts++;
                        console.log(`[${this.botId}] ${replyMessages.disconnected} (Attempt ${this.reconnectAttempts})`);
                        
                        const reconnectDelay = Math.min(5000 * Math.pow(1.2, this.reconnectAttempts - 1), 30000);
                        await delay(reconnectDelay);
                        
                        console.log(`[${this.botId}] ${replyMessages.reconnectMsg}`);
                        this.connect();
                    }
                } else if (connection === 'open') {
                    console.log(`[${this.botId}] ✅ ${replyMessages.connected}`);
                    this.connected = true;
                    this.reconnectAttempts = 0;
                    this.reconnecting = false;
                    
                    try {
                        const userJid = this.sock.user.id;
                        this.botNumberJid = userJid;
                        this.botNumber = userJid.split(':')[0];
                        this.botNumberSimple = this.botNumber.split('@')[0];
                        
                        console.log(`[${this.botId}] Bot Number: ${this.botNumberSimple}`);
                    } catch (err) {
                        console.error(`[${this.botId}] Error parsing bot number:`, err.message);
                    }
                }
            });

            this.sock.ev.on('creds.update', saveCreds);
            
            this.sock.ev.on('messages.upsert', async (m) => {
                try {
                    await this.handleMessage(m);
                } catch (err) {
                    if (err.message && err.message.includes('Bad MAC')) {
                        // Silent ignore
                    } else {
                        console.error(`[${this.botId}] Message error:`, err.message);
                    }
                }
            });

        } catch (err) {
            console.error(`[${this.botId}] Connection error:`, err.message);
            this.reconnecting = false;
            if (!this.disabled) {
                await delay(5000);
                this.connect();
            }
        }
    }

    async handleMessage({ messages, type }) {
        try {
            if (type !== 'notify') return;
            
            const msg = messages[0];
            if (!msg.message) return;
            if (msg.key.fromMe) return;
            
            const from = msg.key.remoteJid;
            const isGroup = from.endsWith('@g.us');
            
            let sender = null;
            try {
                if (isGroup) {
                    sender = msg.key.participant || from;
                } else {
                    sender = from;
                }
                
                if (!sender) return;
            } catch (err) {
                return;
            }
            
            const msgId = msg.key.id;
            const isLeader = this.botManager.commandBus.getLeaderBot()?.botId === this.botId;
            
            if (!isLeader && !this.botManager.commandBus.shouldProcessMessage(msgId)) return;
            if (isLeader && !this.botManager.commandBus.shouldProcessMessage(msgId)) return;
            
            let text = '';
            try {
                if (msg.message.conversation) {
                    text = msg.message.conversation;
                } else if (msg.message.extendedTextMessage?.text) {
                    text = msg.message.extendedTextMessage.text;
                } else if (msg.message.imageMessage?.caption) {
                    text = msg.message.imageMessage.caption;
                } else if (msg.message.videoMessage?.caption) {
                    text = msg.message.videoMessage.caption;
                }
            } catch (err) {
                return;
            }

            if (!text.startsWith(commandPrefix)) return;
            
            const originalText = text;
            const args = text.slice(commandPrefix.length).trim().split(/ +/);
            const command = args.shift().toLowerCase();
            const fullArgs = args.join(' ');

            const isDM = !isGroup;
            
            let senderNumber = '';
            let senderSimple = '';
            let botSimple = this.botNumberSimple || '';
            
            try {
                if (sender && typeof sender === 'string') {
                    senderNumber = sender.includes('@') ? sender.split('@')[0] : sender;
                    senderSimple = senderNumber.replace(/[^0-9]/g, '');
                }
            } catch (err) {}
            
            let senderIsBotNumber = false;
            try {
                senderIsBotNumber = 
                    (sender && this.botNumberJid && sender === this.botNumberJid) || 
                    (sender && this.botNumber && sender === this.botNumber) ||
                    (senderNumber && this.botNumber && senderNumber === this.botNumber) ||
                    (senderSimple && botSimple && senderSimple === botSimple);
            } catch (err) {}
            
            const senderIsOwner = isOwner(sender);
            const senderIsAdmin = isAdmin(sender);
            const senderIsSubAdmin = isGroup ? isSubAdmin(sender, from) : false;
            
            const senderHasPermission = senderIsOwner || senderIsAdmin || senderIsSubAdmin || senderIsBotNumber;

            // AUTO REACT SYSTEM
            const reactEmoji = this.autoReactEmojis.get(from);
            if (reactEmoji && !text.startsWith(commandPrefix)) {
                try {
                    await this.sock.sendMessage(from, {
                        react: {
                            text: reactEmoji,
                            key: msg.key
                        }
                    });
                } catch (err) {}
            }

            // TARGET SLIDE AUTO REPLY - FIXED VERSION
            if (this.activeTargetSlides) {
                for (const [taskId, target] of this.activeTargetSlides.entries()) {
                    if (target && target.groupJid === from && target.active && sender === target.targetJid && !msg.key.fromMe) {
                        setTimeout(async () => {
                            try {
                                await this.sock.sendMessage(from, { 
                                    text: target.text 
                                }, { 
                                    quoted: msg 
                                });
                            } catch (err) {
                                console.error(`[${this.botId}] Target reply error:`, err.message);
                            }
                        }, target.delay);
                        break;
                    }
                }
            }

            // ========== OWNER COMMANDS (DM Only) ==========
            if (command === 'owner' && isDM) {
                if (!roles.owner) {
                    if (setOwner(sender)) {
                        await this.sendMessage(from, replyMessages.youAreNowOwner);
                    }
                } else if (senderIsOwner) {
                    await this.sendMessage(from, replyMessages.youAreAlreadyOwner);
                } else {
                    await this.sendMessage(from, replyMessages.ownerAlreadyExists);
                }
                return;
            }

            if (command === 'removeowner' && isDM) {
                if (senderIsOwner) {
                    removeOwner();
                    await this.sendMessage(from, replyMessages.youAreNoLongerOwner);
                } else {
                    await this.sendMessage(from, replyMessages.youAreNotOwner);
                }
                return;
            }

            // ========== BOT ADMIN COMMANDS (Database, NOT WhatsApp) ==========
            
            // !addadmin - Add bot admin (Database only)
            if (command === 'addadmin' && isDM && senderIsOwner) {
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    await this.sendMessage(from, replyMessages.replyToSomeone);
                    return;
                }
                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                if (addAdmin(targetJid)) {
                    await this.sendMessage(from, `✅ @${targetJid.split('@')[0]} 𝙰𝙱 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝙱𝙰𝙽 𝙶𝙰𝙴 🦾`, [targetJid]);
                } else {
                    await this.sendMessage(from, `⚠️ @${targetJid.split('@')[0]} 𝙿𝙷𝙻𝙴 𝚂𝙴 𝙷𝙸 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝙷𝙰𝙸 👑`, [targetJid]);
                }
                return;
            }

            // !removeadmin - Remove bot admin (Database only)
            if (command === 'removeadmin' && isDM) {
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    if (senderIsAdmin) {
                        if (removeAdmin(sender)) {
                            await this.sendMessage(from, `✅ 𝙰𝙿𝙽𝙴 𝙺𝙾 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝚂𝙴 𝙷𝚃𝙰𝚈𝙰 𝙶𝙰𝚈𝙰 🗑️`);
                        }
                    }
                    return;
                }
                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                if (senderIsOwner || (senderIsAdmin && targetJid === sender)) {
                    if (removeAdmin(targetJid)) {
                        await this.sendMessage(from, `✅ @${targetJid.split('@')[0]} 𝙰𝙱 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝙽𝙰𝙷𝙸 𝚁𝙰𝙷𝙴 🚫`, [targetJid]);
                    } else {
                        await this.sendMessage(from, `❌ @${targetJid.split('@')[0]} 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝚃𝙷𝙰 𝙷𝙸 𝙽𝙰𝙷𝙸 🫠`, [targetJid]);
                    }
                } else {
                    await this.sendMessage(from, replyMessages.onlyOwner);
                }
                return;
            }

            // !listadmins - List all bot admins
            if (command === 'listadmins' && senderHasPermission) {
                let msg = `👑 *𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽𝚂*\n\n`;
                msg += `𝙾𝚆𝙽𝙴𝚁: @${roles.owner?.split('@')[0] || '𝙽𝙾𝙽𝙴'}\n\n`;
                msg += `𝙰𝙳𝙼𝙸𝙽𝚂:\n`;
                if (roles.admins.length === 0) {
                    msg += `𝙺𝙾𝙸 𝙽𝙰𝙷𝙸 🥲\n`;
                } else {
                    roles.admins.forEach((admin, i) => {
                        msg += `${i+1}. @${admin.split('@')[0]}\n`;
                    });
                }
                await this.sendMessage(from, msg, [roles.owner, ...roles.admins].filter(Boolean));
                return;
            }

            // ========== BOT SUB-ADMIN COMMANDS (Per Group) ==========
            
            // !sub - Add bot sub-admin (Per group)
            if (command === 'sub' && isGroup) {
                if (!senderIsOwner && !senderIsAdmin) {
                    await this.sendMessage(from, `👑 𝚂𝙸𝚁𝙵 𝙱𝙾𝚃 𝙾𝚆𝙽𝙴𝚁 𝚈𝙰 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝚈𝙴𝙷 𝙲𝙷𝙻𝙰 𝚂𝙺𝚃𝙴 𝙷𝙰𝙸`);
                    return;
                }
                
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    await this.sendMessage(from, replyMessages.replyToSomeone);
                    return;
                }
                
                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                
                if (addSubAdmin(targetJid, from)) {
                    await this.sendMessage(from, `✅ @${targetJid.split('@')[0]} 𝙰𝙱 𝙸𝚂 𝙶𝚁𝙾𝚄𝙿 𝙼𝙴 𝙱𝙾𝚃 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽 𝙱𝙰𝙽 𝙶𝙰𝚈𝙰 🔥`, [targetJid]);
                } else {
                    await this.sendMessage(from, `⚠️ @${targetJid.split('@')[0]} 𝙿𝙷𝙻𝙴 𝚂𝙴 𝙷𝙸 𝙱𝙾𝚃 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽 𝙷𝙰𝙸 🥂`, [targetJid]);
                }
                return;
            }

            // !removesub - Remove bot sub-admin (Per group)
            if (command === 'removesub' && isGroup) {
                if (!senderIsOwner && !senderIsAdmin) {
                    await this.sendMessage(from, `👑 𝚂𝙸𝚁𝙵 𝙱𝙾𝚃 𝙾𝚆𝙽𝙴𝚁 𝚈𝙰 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝚈𝙴𝙷 𝙲𝙷𝙻𝙰 𝚂𝙺𝚃𝙴 𝙷𝙰𝙸`);
                    return;
                }
                
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    await this.sendMessage(from, replyMessages.replyToSomeone);
                    return;
                }
                
                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                
                if (removeSubAdmin(targetJid, from)) {
                    await this.sendMessage(from, `✅ @${targetJid.split('@')[0]} 𝙰𝙱 𝙱𝙾𝚃 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽 𝙽𝙰𝙷𝙸 𝚁𝙰𝙷𝙴 🥀`, [targetJid]);
                } else {
                    await this.sendMessage(from, `❌ @${targetJid.split('@')[0]} 𝙱𝙾𝚃 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽 𝚃𝙷𝙰 𝙷𝙸 𝙽𝙰𝙷𝙸 🫠`, [targetJid]);
                }
                return;
            }

            // !listsub - List sub-admins in current group
            if (command === 'listsub' && isGroup && senderHasPermission) {
                const groupSubs = roles.subAdmins[from] || [];
                let msg = `👥 *𝙶𝚁𝙾𝚄𝙿 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽𝚂*\n\n`;
                if (groupSubs.length === 0) {
                    msg += `𝙸𝚂 𝙶𝚁𝙾𝚄𝙿 𝙼𝙴 𝙺𝙾𝙸 𝚂𝚄𝙱-𝙰𝙳𝙼𝙸𝙽 𝙽𝙰𝙷𝙸 🫤`;
                } else {
                    groupSubs.forEach((sub, i) => {
                        msg += `${i+1}. @${sub.split('@')[0]}\n`;
                    });
                }
                await this.sendMessage(from, msg, groupSubs);
                return;
            }

            // ========== WHATSAPP GROUP ADMIN COMMANDS (Separate) ==========

            // !wadmin - Promote to WhatsApp group admin (NOT bot admin)
            if (command === 'wadmin' && isGroup) {
                if (!senderIsOwner && !senderIsAdmin) {
                    await this.sendMessage(from, `👑 𝚂𝙸𝚁𝙵 𝙱𝙾𝚃 𝙾𝚆𝙽𝙴𝚁 𝚈𝙰 𝙱𝙾𝚃 𝙰𝙳𝙼𝙸𝙽 𝚈𝙴𝙷 𝙲𝙷𝙻𝙰 𝚂𝙺𝚃𝙴 𝙷𝙰𝙸`);
                    return;
                }
                
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    await this.sendMessage(from, replyMessages.replyToSomeone);
                    return;
                }
                
                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                
                try {
                    await this.sock.groupParticipantsUpdate(from, [targetJid], 'promote');
                    await this.sendMessage(from, `👑 @${targetJid.split('@')[0]} 𝙰𝙱 𝚆𝙷𝙰𝚃𝚂𝙰𝙿𝙿 𝙶𝚁𝙾𝚄𝙿 𝙰𝙳𝙼𝙸𝙽 𝙱𝙰𝙽 𝙶𝙰𝙴 🥂🔥`, [targetJid]);
                } catch (err) {
                    console.error(`[${this.botId}] Promote error:`, err.message);
                    
                    if (err.message.includes('not admin')) {
                        await this.sendMessage(from, `❌ 𝙱𝙾𝚃 𝙺𝙾 𝙿𝙷𝙻𝙴 𝙶𝚁𝙾𝚄𝙿 𝙰𝙳𝙼𝙸𝙽 𝙱𝙰𝙽𝙰𝙾 🥲`);
                    } else {
                        await this.sendMessage(from, `❌ 𝙵𝙰𝙸𝙻𝙴𝙳: ${err.message.substring(0, 50)}`);
                    }
                }
                return;
            }

            // !wremoveadmin - Demote from WhatsApp group admin
            if (command === 'wremoveadmin' && isGroup) {
                if (!senderIsOwner && !senderIsAdmin) {
                    await this.sendMessage(from, `👑 ᴬᴰᴵ ᴮᴬᴬᴾ ᴷᴬ ᴮᴼᵀ ᶜᴴᴬᴸᴬᴺᴱ ᴷᴵ ᴬᵁᴷᴬᵀ ᴮᴬᴺᴬ ᴿᴬᴺᴰᴵᴷᴱ`);
                    return;
                }
                
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    await this.sendMessage(from, replyMessages.replyToSomeone);
                    return;
                }
                
                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                
                try {
                    await this.sock.groupParticipantsUpdate(from, [targetJid], 'demote');
                    await this.sendMessage(from, `⬇️ @${targetJid.split('@')[0]} 𝙰𝙱 𝚆𝙷𝙰𝚃𝚂𝙰𝙿𝙿 𝙶𝚁𝙾𝚄𝙿 𝙰𝙳𝙼𝙸𝙽 𝙽𝙰𝙷𝙸 𝚁𝙰𝙷𝙴 🚫`, [targetJid]);
                } catch (err) {
                    await this.sendMessage(from, `❌ 𝙵𝙰𝙸𝙻𝙴𝙳`);
                }
                return;
            }

            // !wadmins - List all WhatsApp group admins
            if (command === 'wadmins' && isGroup) {
                try {
                    const groupMetadata = await this.sock.groupMetadata(from);
                    const admins = groupMetadata.participants.filter(p => p.admin);
                    
                    let msg = `👑 *𝚆𝙷𝙰𝚃𝚂𝙰𝙿𝙿 𝙶𝚁𝙾𝚄𝙿 𝙰𝙳𝙼𝙸𝙽𝚂*\n\n`;
                    admins.forEach((admin, i) => {
                        const adminType = admin.admin === 'superadmin' ? '🦅' : '👮';
                        msg += `${i+1}. ${adminType} @${admin.id.split('@')[0]}\n`;
                    });
                    
                    await this.sendMessage(from, msg, admins.map(a => a.id));
                } catch (err) {
                    await this.sendMessage(from, `❌ 𝙴𝚁𝚁𝙾𝚁`);
                }
                return;
            }

            // ========== BOT MANAGEMENT ==========
            if (command === 'add' && senderIsOwner) {
                const number = fullArgs.replace(/[^0-9]/g, '');
                if (number.length < 10) {
                    await this.sendMessage(from, replyMessages.invalidPhone);
                    return;
                }
                
                const result = await this.botManager.addBot(number, from);
                await this.sendMessage(from, result);
                return;
            }

            if (command === 'bots' && senderHasPermission) {
                const bots = this.botManager.commandBus.getAllBots();
                let msg = `${replyMessages.activeBots}\n\n`;
                msg += `${replyMessages.total} ${bots.length}\n\n`;
                
                bots.forEach(bot => {
                    const status = bot.connected ? '✅' : (bot.disabled ? '🔴' : '⚠️');
                    msg += `${bot.botId}: ${status}\n`;
                });
                
                await this.sendMessage(from, msg);
                return;
            }

            if (command === 'ping' && senderHasPermission) {
                const startTime = Date.now();
                await this.sendMessage(from, `${replyMessages.pinging}`);
                const latency = Date.now() - startTime;
                await this.sendMessage(from, `${replyMessages.ᴀYUSHPing}\n\n${replyMessages.latency} ${latency}ms`);
                return;
            }

            // ========== FONT NC ATTACK ==========
            if (command === 'tne' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 4) {
                    await this.sendMessage(from, `${replyMessages.usage} !tne [font] [nc#] [text] [delay]`);
                    return;
                }

                const fontName = parts[0].toLowerCase();
                const ncKey = parts[1].toLowerCase();
                const delayTime = parseInt(parts[parts.length - 1]);
                const userText = parts.slice(2, parts.length - 1).join(' ');

                if (!fontStyles[fontName]) {
                    await this.sendMessage(from, `invalid font. available: double, mono, script, boldscript, gothic, boldgothic, square, circled`);
                    return;
                }

                if (!emojiArrays[ncKey]) {
                    await this.sendMessage(from, replyMessages.invalidNcNumber);
                    return;
                }

                if (isNaN(delayTime) || delayTime < 100) {
                    await this.sendMessage(from, replyMessages.delayTooLow);
                    return;
                }

                const styledText = applyFont(userText, fontName);
                await this.botManager.commandBus.broadcastCommand('start_cs', { 
                    from, 
                    userText: styledText, 
                    csDelay: delayTime, 
                    ncKey 
                }, this.botId);
                return;
            }

            // ========== SIMPLE NC ATTACK ==========
            if (command.startsWith('nc') && isGroup && senderHasPermission) {
                const ncNumber = command.slice(2);
                const ncKey = `nc${ncNumber}`;
                
                if (!emojiArrays[ncKey]) {
                    await this.sendMessage(from, replyMessages.invalidNcNumber);
                    return;
                }

                if (!fullArgs) {
                    await this.sendMessage(from, `${replyMessages.usage} !${command} [text]`);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_nc', { 
                    from, 
                    nameText: fullArgs, 
                    ncKey 
                }, this.botId);
                return;
            }

            // ========== TRIPLE ATTACK ==========
            if (command.startsWith('triple') && isGroup && senderHasPermission) {
                const tripleNumber = command.slice(6);
                const tripleKey = `triple${tripleNumber}`;
                
                if (!tripleNcCombos[tripleKey]) {
                    await this.sendMessage(from, `invalid triple number. use triple1 to triple35`);
                    return;
                }

                if (!fullArgs) {
                    await this.sendMessage(from, `${replyMessages.usage} !${command} [text]`);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_triple_nc', { 
                    from, 
                    nameText: fullArgs, 
                    tripleKey 
                }, this.botId);
                return;
            }

            // ========== NC LOOP ==========
            if (command === 'ncloop' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 3) {
                    await this.sendMessage(from, `${replyMessages.usage} !ncloop [nc#] [text] [rounds]`);
                    return;
                }

                const ncKey = parts[0].toLowerCase();
                const rounds = parseInt(parts[parts.length - 1]);
                const userText = parts.slice(1, parts.length - 1).join(' ');

                if (!emojiArrays[ncKey]) {
                    await this.sendMessage(from, replyMessages.invalidNcNumber);
                    return;
                }

                if (isNaN(rounds) || rounds < 1) {
                    await this.sendMessage(from, `rounds must be >= 1`);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_nc_loop', { 
                    from, 
                    nameText: userText, 
                    ncKey,
                    rounds
                }, this.botId);
                return;
            }

            if (command === 'stopncloop' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_nc_loop', { from }, this.botId);
                return;
            }

            // ========== HEART LOOP ==========
            if (command === 'loopheart' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 2) {
                    await this.sendMessage(from, `${replyMessages.usage} !loopheart [text] [delay]`);
                    return;
                }

                const delayTime = parseInt(parts[parts.length - 1]);
                const userText = parts.slice(0, parts.length - 1).join(' ');

                if (isNaN(delayTime) || delayTime < 100) {
                    await this.sendMessage(from, replyMessages.delayTooLow);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_heart_loop', { 
                    from, 
                    userText,
                    delay: delayTime
                }, this.botId);
                return;
            }

            if (command === 'stoploopheart' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_heart_loop', { from }, this.botId);
                return;
            }

            // ========== WORD MANAGEMENT ==========
            if (command === 'addwords' && senderHasPermission) {
                const words = fullArgs.split(' ').filter(w => w.trim());
                if (words.length === 0) {
                    await this.sendMessage(from, `${replyMessages.usage} !addwords [word1] [word2] ...`);
                    return;
                }

                savedWords.push(...words);
                saveWords(savedWords);
                await this.sendMessage(from, `${replyMessages.wordAdded}\ntotal: ${savedWords.length}`);
                return;
            }

            if (command === 'mywords' && senderHasPermission) {
                if (savedWords.length === 0) {
                    await this.sendMessage(from, replyMessages.noWords);
                    return;
                }

                let wordList = `${replyMessages.wordList}\n\n`;
                savedWords.forEach((word, i) => {
                    wordList += `${i + 1}. ${word}\n`;
                });
                await this.sendMessage(from, wordList);
                return;
            }

            if (command === 'removeword' && senderHasPermission) {
                const index = parseInt(fullArgs) - 1;
                if (isNaN(index) || index < 0 || index >= savedWords.length) {
                    await this.sendMessage(from, `invalid word number`);
                    return;
                }

                const removed = savedWords.splice(index, 1);
                saveWords(savedWords);
                await this.sendMessage(from, `${replyMessages.wordRemoved}\n${removed[0]}`);
                return;
            }

            if (command === 'clearwords' && senderHasPermission) {
                savedWords = [];
                saveWords(savedWords);
                await this.sendMessage(from, replyMessages.wordsCleared);
                return;
            }

            if (command === 'usewords' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 2) {
                    await this.sendMessage(from, `${replyMessages.usage} !usewords [nc#] [delay]`);
                    return;
                }

                const ncKey = parts[0].toLowerCase();
                const delayTime = parseInt(parts[1]);

                if (!emojiArrays[ncKey]) {
                    await this.sendMessage(from, replyMessages.invalidNcNumber);
                    return;
                }

                if (savedWords.length === 0) {
                    await this.sendMessage(from, replyMessages.noWords);
                    return;
                }

                if (isNaN(delayTime) || delayTime < 100) {
                    await this.sendMessage(from, replyMessages.delayTooLow);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_use_words', { 
                    from, 
                    ncKey,
                    delay: delayTime,
                    words: [...savedWords]
                }, this.botId);
                return;
            }

            if (command === 'stopusewords' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_use_words', { from }, this.botId);
                return;
            }

            // ========== COVER GC ==========
            if (command === 'covergc' && isGroup && senderHasPermission) {
                if (!fullArgs) {
                    await this.sendMessage(from, `${replyMessages.usage} !covergc [text]`);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_cover_gc', { 
                    from, 
                    text: fullArgs
                }, this.botId);
                return;
            }

            if (command === 'stopcovergc' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_cover_gc', { from }, this.botId);
                return;
            }

            // ========== SPEED UP ==========
            if (command === 'speedup' && senderHasPermission) {
                const ms = parseInt(fullArgs);
                if (isNaN(ms) || ms < 0) {
                    await this.sendMessage(from, `invalid delay value`);
                    return;
                }

                ncDelays.speedup = ms;
                saveDelays(ncDelays);
                await this.sendMessage(from, `${replyMessages.speedUpSet} ${ms}ms`);
                return;
            }

            // ========== RAGE MODE ==========
            if (command === 'rage' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 2) {
                    await this.sendMessage(from, `${replyMessages.usage} !rage [nc#] [text]`);
                    return;
                }

                const ncKey = parts[0].toLowerCase();
                const userText = parts.slice(1).join(' ');

                if (!emojiArrays[ncKey]) {
                    await this.sendMessage(from, replyMessages.invalidNcNumber);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_rage_mode', { 
                    from, 
                    ncKey,
                    text: userText
                }, this.botId);
                return;
            }

            if (command === 'stoprage' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_rage_mode', { from }, this.botId);
                return;
            }

            // ========== DNC (STOP NC) ==========
            if (command === 'dnc' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_nc', { from }, this.botId);
                await this.botManager.commandBus.broadcastCommand('stop_triple_nc', { from }, this.botId);
                return;
            }

            // ========== TIME NC ==========
            if (command === 'timenc' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 2) {
                    await this.sendMessage(from, `${replyMessages.usage} !timenc [nc#] [text]`);
                    return;
                }

                const ncKey = parts[0].toLowerCase();
                const userText = parts.slice(1).join(' ');

                if (!emojiArrays[ncKey]) {
                    await this.sendMessage(from, replyMessages.invalidNcNumber);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_time_nc', { 
                    from, 
                    ncKey,
                    text: userText
                }, this.botId);
                return;
            }

            // ========== NC SPAM ==========
            if (command === 'ncspam' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 3) {
                    await this.sendMessage(from, `${replyMessages.usage} !ncspam [nc#] [text] [delay]`);
                    return;
                }

                const ncKey = parts[0].toLowerCase();
                const delayTime = parseInt(parts[parts.length - 1]);
                const userText = parts.slice(1, parts.length - 1).join(' ');

                if (!emojiArrays[ncKey]) {
                    await this.sendMessage(from, replyMessages.invalidNcNumber);
                    return;
                }

                if (isNaN(delayTime) || delayTime < 100) {
                    await this.sendMessage(from, replyMessages.delayTooLow);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_nc_spam', { 
                    from, 
                    ncKey,
                    text: userText,
                    delay: delayTime
                }, this.botId);
                return;
            }

            if (command === 'stopncspam' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_nc_spam', { from }, this.botId);
                return;
            }

            // ========== VOICE ATTACK ==========
            if (command === 'tts' && senderHasPermission) {
                if (!fullArgs) {
                    await this.sendMessage(from, `${replyMessages.usage} !tts [text]`);
                    return;
                }

                try {
                    const audioBuffer = await generateTTS(fullArgs);
                    await this.sock.sendMessage(from, {
                        audio: audioBuffer,
                        mimetype: 'audio/ogg; codecs=opus',
                        ptt: true
                    });
                } catch (err) {
                    await this.sendMessage(from, `tts error`);
                }
                return;
            }

            if (command === 'ttsatk' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 2) {
                    await this.sendMessage(from, `${replyMessages.usage} !ttsatk [text] [delay]`);
                    return;
                }

                const ttsDelay = parseInt(parts[parts.length - 1]);
                const ttsText = parts.slice(0, parts.length - 1).join(' ');

                if (isNaN(ttsDelay) || ttsDelay < 1000) {
                    await this.sendMessage(from, `delay must be >= 1000ms`);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_tts', { from, ttsText, ttsDelay }, this.botId);
                return;
            }

            if (command === 'stopttsatk' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_tts', { from }, this.botId);
                return;
            }

            // ========== PICTURE ATTACK ==========
            if (command === 'pic' && isGroup && senderHasPermission) {
                if (!msg.message.extendedTextMessage?.contextInfo?.quotedMessage?.imageMessage) {
                    await this.sendMessage(from, `${replyMessages.usage} !pic [delay]`);
                    return;
                }

                const picDelay = parseInt(fullArgs);
                if (isNaN(picDelay) || picDelay < 100) {
                    await this.sendMessage(from, `delay must be >= 100ms`);
                    return;
                }

                const quotedMsg = {
                    key: {
                        remoteJid: from,
                        fromMe: false,
                        id: msg.message.extendedTextMessage.contextInfo.stanzaId,
                        participant: msg.message.extendedTextMessage.contextInfo.participant
                    },
                    message: msg.message.extendedTextMessage.contextInfo.quotedMessage
                };

                try {
                    const imageBuffer = await downloadMediaMessage(quotedMsg, 'buffer', {});
                    const imageMessage = msg.message.extendedTextMessage.contextInfo.quotedMessage.imageMessage;
                    
                    await this.botManager.commandBus.broadcastCommand('start_pic', { 
                        from, 
                        picDelay, 
                        imageBuffer: imageBuffer.toString('base64'),
                        mimetype: imageMessage.mimetype || 'image/jpeg'
                    }, this.botId);
                } catch (err) {
                    await this.sendMessage(from, `error downloading image`);
                }
                return;
            }

            if (command === 'stoppic' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_pic', { from }, this.botId);
                return;
            }

            // ========== VIDEO SPAM ==========
            if (command === 'videospam' && isGroup && senderHasPermission) {
                if (!msg.message.extendedTextMessage?.contextInfo?.quotedMessage?.videoMessage) {
                    await this.sendMessage(from, `${replyMessages.usage} !videospam [delay]`);
                    return;
                }

                const videoDelay = parseInt(fullArgs);
                if (isNaN(videoDelay) || videoDelay < 100) {
                    await this.sendMessage(from, `delay must be >= 100ms`);
                    return;
                }

                const quotedMsg = {
                    key: {
                        remoteJid: from,
                        fromMe: false,
                        id: msg.message.extendedTextMessage.contextInfo.stanzaId,
                        participant: msg.message.extendedTextMessage.contextInfo.participant
                    },
                    message: msg.message.extendedTextMessage.contextInfo.quotedMessage
                };

                try {
                    const videoBuffer = await downloadMediaMessage(quotedMsg, 'buffer', {});
                    const videoMessage = msg.message.extendedTextMessage.contextInfo.quotedMessage.videoMessage;
                    
                    await this.botManager.commandBus.broadcastCommand('start_video', { 
                        from, 
                        videoDelay, 
                        videoBuffer: videoBuffer.toString('base64'),
                        mimetype: videoMessage.mimetype || 'video/mp4'
                    }, this.botId);
                } catch (err) {
                    await this.sendMessage(from, `error downloading video`);
                }
                return;
            }

            if (command === 'stopvideospam' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_video', { from }, this.botId);
                return;
            }

            // ========== GROUP DP CHANGE ==========
            if (command === 'grpfp' && isGroup && senderHasPermission) {
                if (!msg.message.extendedTextMessage?.contextInfo?.quotedMessage?.imageMessage) {
                    await this.sendMessage(from, `${replyMessages.usage} !grpfp [delay]`);
                    return;
                }

                const grpfpDelay = parseInt(fullArgs) || 2000;

                const quotedMsg = {
                    key: {
                        remoteJid: from,
                        fromMe: false,
                        id: msg.message.extendedTextMessage.contextInfo.stanzaId,
                        participant: msg.message.extendedTextMessage.contextInfo.participant
                    },
                    message: msg.message.extendedTextMessage.contextInfo.quotedMessage
                };

                try {
                    const imageBuffer = await downloadMediaMessage(quotedMsg, 'buffer', {});
                    
                    await this.botManager.commandBus.broadcastCommand('start_grpfp', { 
                        from, 
                        imageBuffer: imageBuffer.toString('base64'),
                        grpfpDelay
                    }, this.botId);
                } catch (err) {
                    await this.sendMessage(from, `error downloading image`);
                }
                return;
            }

            if (command === 'stopgrpfp' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_grpfp', { from }, this.botId);
                return;
            }

            // ========== AUTO REACT ==========
            if (command === 'react' && senderHasPermission) {
                const emoji = fullArgs.trim();
                if (!emoji) {
                    await this.sendMessage(from, `${replyMessages.usage} !react [emoji]`);
                    return;
                }

                this.autoReactEmojis.set(from, emoji);
                await this.sendMessage(from, `${replyMessages.reactEmojiSet} ${emoji}`);
                return;
            }

            if (command === 'stopreact' && senderHasPermission) {
                if (this.autoReactEmojis.has(from)) {
                    this.autoReactEmojis.delete(from);
                    await this.sendMessage(from, replyMessages.reactStopped);
                }
                return;
            }

            // ========== STOP ALL ==========
            if (command === 'stopall' && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_all', { from }, this.botId);
                return;
            }

            // ========== GROUP TOOLS ==========
            if (command === 'tagall' && isGroup && senderHasPermission) {
                const groupMetadata = await this.sock.groupMetadata(from);
                const participants = groupMetadata.participants;
                const mentions = participants.map(p => p.id);
                
                let msg = `${replyMessages.tagAll}\n\n`;
                if (fullArgs) msg += `${fullArgs}\n\n`;
                participants.forEach(p => {
                    msg += `@${p.id.split('@')[0]}\n`;
                });
                
                await this.sendMessage(from, msg, mentions);
                return;
            }

            if (command === 'join' && senderHasPermission) {
                const link = fullArgs.trim();
                if (!link) {
                    await this.sendMessage(from, `${replyMessages.usage} !join [group link]`);
                    return;
                }

                try {
                    const result = await this.sock.groupAcceptInvite(link.split('/').pop());
                    await this.sendMessage(from, `${replyMessages.joined}\n${result}`);
                } catch (err) {
                    await this.sendMessage(from, `error joining group`);
                }
                return;
            }

            if (command === 'multigc' && senderHasPermission) {
                const groups = await this.sock.groupFetchAllParticipating();
                let msg = `${replyMessages.multiGC}\n\n`;
                
                let i = 1;
                for (const [id, group] of Object.entries(groups)) {
                    msg += `${i}. ${group.subject}\n${id}\n\n`;
                    i++;
                    if (i > 20) break;
                }
                
                await this.sendMessage(from, msg);
                return;
            }

            if (command === 'leave' && isGroup && senderHasPermission) {
                await this.sendMessage(from, replyMessages.left);
                await delay(1000);
                await this.sock.groupLeave(from);
                return;
            }

            if (command === 'grplink' && isGroup && senderHasPermission) {
                try {
                    const code = await this.sock.groupInviteCode(from);
                    const link = `https://chat.whatsapp.com/${code}`;
                    await this.sendMessage(from, `${replyMessages.groupLink}\n${link}`);
                } catch (err) {
                    await this.sendMessage(from, `error getting group link`);
                }
                return;
            }

            // ========== TARGET COMMAND (FIXED) ==========
            if (command === 'target' && isGroup && senderHasPermission) {
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    await this.sendMessage(from, replyMessages.replyToSomeone);
                    return;
                }

                const parts = fullArgs.split(' ');
                if (parts.length < 2) {
                    await this.sendMessage(from, `${replyMessages.usage} !target [text] [delay]`);
                    return;
                }

                const delayTime = parseInt(parts[parts.length - 1]);
                const targetText = parts.slice(0, parts.length - 1).join(' ');

                if (isNaN(delayTime) || delayTime < 100) {
                    await this.sendMessage(from, replyMessages.delayTooLow);
                    return;
                }

                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                
                await this.botManager.commandBus.broadcastCommand('start_target', {
                    from,
                    targetJid,
                    text: targetText,
                    delay: delayTime
                }, this.botId);
                return;
            }

            if (command === 'stoptarget' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_target', { from }, this.botId);
                return;
            }

            if (command === 's' && isGroup && senderHasPermission) {
                if (!msg.message.extendedTextMessage?.contextInfo?.quotedMessage) {
                    await this.sendMessage(from, `${replyMessages.usage} !s [text] [delay]`);
                    return;
                }

                const parts = fullArgs.split(' ');
                if (parts.length < 2) {
                    await this.sendMessage(from, `${replyMessages.usage} !s [text] [delay]`);
                    return;
                }

                const slideDelay = parseInt(parts[parts.length - 1]);
                const slideText = parts.slice(0, parts.length - 1).join(' ');

                if (isNaN(slideDelay) || slideDelay < 100) {
                    await this.sendMessage(from, replyMessages.delayTooLow);
                    return;
                }

                const quotedParticipant = msg.message.extendedTextMessage.contextInfo.participant || from;
                const quotedMsgId = msg.message.extendedTextMessage.contextInfo.stanzaId;
                const quotedMessage = msg.message.extendedTextMessage.contextInfo.quotedMessage;

                await this.botManager.commandBus.broadcastCommand('start_slide', {
                    from,
                    slideText,
                    slideDelay,
                    quotedParticipant,
                    quotedMsgId,
                    quotedMessage
                }, this.botId);
                return;
            }

            if (command === 'txt' && isGroup && senderHasPermission) {
                const parts = fullArgs.split(' ');
                if (parts.length < 2) {
                    await this.sendMessage(from, `${replyMessages.usage} !txt [text] [delay]`);
                    return;
                }

                const txtDelay = parseInt(parts[parts.length - 1]);
                const txtText = parts.slice(0, parts.length - 1).join(' ');

                if (isNaN(txtDelay) || txtDelay < 100) {
                    await this.sendMessage(from, replyMessages.delayTooLow);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_txt', { from, txtText, txtDelay }, this.botId);
                return;
            }

            if (command === 'stops' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_slide', { from }, this.botId);
                return;
            }

            if (command === 'stoptxt' && isGroup && senderHasPermission) {
                await this.botManager.commandBus.broadcastCommand('stop_txt', { from }, this.botId);
                return;
            }

            // ========== INFORMATION ==========
            if (command === 'menu' && senderHasPermission) {
                await this.sendMessage(from, AyushMenu);
                return;
            }

            if (command === 'status' && senderHasPermission) {
                const allBots = this.botManager.commandBus.getAllBots();
                let totalName = 0, totalTriple = 0, totalConstant = 0, totalSlides = 0, totalTarget = 0, totalTxt = 0, totalTts = 0, totalPic = 0, totalVideo = 0, totalDp = 0, totalStickerSlides = 0, totalGif = 0, totalSticker = 0, totalVn = 0;
                
                allBots.forEach(bot => {
                    totalName += bot.activeNameChanges.size;
                    totalTriple += bot.activeTripleNc.size;
                    totalConstant += bot.activeConstantAttacks.size;
                    totalSlides += bot.activeSlides.size;
                    totalTarget += bot.activeTargetSlides ? bot.activeTargetSlides.size : 0;
                    totalTxt += bot.activeTxtSenders.size;
                    totalTts += bot.activeTTSSenders.size;
                    totalPic += bot.activePicSenders.size;
                    totalVideo += bot.activeVideoSenders ? bot.activeVideoSenders.size : 0;
                    totalDp += bot.activeGroupDpChanges.size;
                    totalStickerSlides += bot.activeStickerSlides.size;
                    totalGif += bot.activeGifSpam.size;
                    totalSticker += bot.activeStickerSpam.size;
                    totalVn += bot.activeVnSpam ? bot.activeVnSpam.size : 0;
                });
                
                const statusMsg = `${replyMessages.ᴀYUSHStatus}\n\n` +
                                `${replyMessages.individualNc} ${totalName}\n` +
                                `triple nc: ${totalTriple}\n` +
                                `${replyMessages.constantText} ${totalConstant}\n` +
                                `slide attacks: ${totalSlides}\n` +
                                `target slides: ${totalTarget}\n` +
                                `text attacks: ${totalTxt}\n` +
                                `tts attacks: ${totalTts}\n` +
                                `pic attacks: ${totalPic}\n` +
                                `video spam: ${totalVideo}\n` +
                                `dp changes: ${totalDp}\n` +
                                `sticker slides: ${totalStickerSlides}\n` +
                                `gif spam: ${totalGif}\n` +
                                `sticker spam: ${totalSticker}\n` +
                                `voice note spam: ${totalVn}\n` +
                                `${replyMessages.activeBotsCount} ${allBots.filter(b => b.connected).length}/${allBots.length}`;
                
                await this.sendMessage(from, statusMsg);
                return;
            }

            if (command === 'delays' && senderHasPermission) {
                let msg = `${replyMessages.delaysInfo}\n\n`;
                msg += `speed up: ${ncDelays.speedup}ms\n`;
                msg += `grpfp: ${ncDelays.grpfp}ms\n\n`;
                msg += `triple delays:\n`;
                for (let i = 1; i <= 4; i++) {
                    msg += `triple${i}: ${ncDelays[`triple${i}`]}ms\n`;
                }
                await this.sendMessage(from, msg);
                return;
            }

            if (command === 'triples' && senderHasPermission) {
                let msg = `${replyMessages.triplesInfo}\n\n`;
                for (let i = 1; i <= 35; i++) {
                    const triple = tripleNcCombos[`triple${i}`];
                    if (triple) {
                        msg += `triple${i}: ${triple.join(' + ')}\n`;
                    }
                }
                await this.sendMessage(from, msg);
                return;
            }

            if (command === 'fonts' && senderHasPermission) {
                let msg = `${replyMessages.fontsMenu}\n\n`;
                for (const [key, style] of Object.entries(fontStyles)) {
                    msg += `${key}: ${applyFont('AYUSH Bot', key)}\n`;
                }
                await this.sendMessage(from, msg);
                return;
            }

            if (command === 'start' && senderIsOwner) {
                await this.sendMessage(from, `restarting all ᴀYUSH bots...`);
                process.exit(0);
                return;
            }

            if (command === 'disable' && senderIsOwner) {
                const botNum = fullArgs.trim();
                const bots = this.botManager.commandBus.getAllBots();
                const bot = bots.find(b => b.botId === `BOT${botNum}`);
                
                if (bot) {
                    bot.disabled = true;
                    if (bot.sock) bot.sock.end();
                    await this.sendMessage(from, `${replyMessages.botDisabled} BOT${botNum}`);
                } else {
                    await this.sendMessage(from, `bot not found`);
                }
                return;
            }

            if (command === 'enable' && senderIsOwner) {
                const botNum = fullArgs.trim();
                const bots = this.botManager.commandBus.getAllBots();
                const bot = bots.find(b => b.botId === `BOT${botNum}`);
                
                if (bot) {
                    bot.disabled = false;
                    bot.connect();
                    await this.sendMessage(from, `${replyMessages.botEnabled} BOT${botNum}`);
                } else {
                    await this.sendMessage(from, `bot not found`);
                }
                return;
            }

            if (command === 'prefix' && senderIsOwner) {
                const newPrefix = fullArgs.trim();
                if (!newPrefix) {
                    await this.sendMessage(from, `${replyMessages.usage} !prefix [new prefix]`);
                    return;
                }

                commandPrefix = newPrefix;
                savePrefix(newPrefix);
                await this.sendMessage(from, `${replyMessages.prefixChanged} ${newPrefix}`);
                return;
            }

            if (command === 'clearcatch' && senderIsOwner) {
                this.botManager.commandBus.processedMessages.clear();
                await this.sendMessage(from, replyMessages.cacheCleared);
                return;
            }

        } catch (err) {
            console.error(`[${this.botId}] Error in handleMessage:`, err);
        }
    }

    async executeCommand(commandType, data, sendConfirmation = true) {
        try {
            // CONSTANT TEXT ATTACK
            if (commandType === 'start_cs') {
                const { from, userText, csDelay, ncKey } = data;
                
                const taskId = `${from}_cs`;
                
                if (this.activeConstantAttacks.has(taskId)) {
                    this.activeConstantAttacks.get(taskId).active = false;
                    await delay(100);
                }

                const csTask = { 
                    active: true,
                    userText: userText,
                    constantIndex: 0
                };
                this.activeConstantAttacks.set(taskId, csTask);

                const runCS = async () => {
                    while (csTask.active) {
                        try {
                            const constantWord = CONSTANT_WORDS[csTask.constantIndex % CONSTANT_WORDS.length];
                            const finalText = `${userText} ${constantWord}`;
                            await this.sock.groupUpdateSubject(from, finalText);
                            csTask.constantIndex++;
                            await delay(csDelay);
                        } catch (err) {
                            await delay(csDelay);
                        }
                    }
                };

                runCS();

                if (sendConfirmation) {
                    await this.sendMessage(from, replyMessages.csStarted);
                }
            }
            
            // STOP CONSTANT TEXT ATTACK
            else if (commandType === 'stop_cs') {
                const { from } = data;
                let stopped = 0;
                
                this.activeConstantAttacks.forEach((task, taskId) => {
                    if (taskId.startsWith(from)) {
                        task.active = false;
                        this.activeConstantAttacks.delete(taskId);
                        stopped++;
                    }
                });

                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, replyMessages.csStopped);
                }
            }
            
            // INDIVIDUAL NC ATTACK
            else if (commandType === 'start_nc') {
                const { from, nameText, ncKey } = data;
                const emojis = emojiArrays[ncKey] || ['❓'];
                const nameDelay = ncDelays.speedup > 0 ? ncDelays.speedup : (ncDelays[ncKey] || 20);
                
                for (let i = 0; i < 5; i++) {
                    const taskId = `${from}_${ncKey}_${i}`;
                    if (this.activeNameChanges.has(taskId)) {
                        this.activeNameChanges.delete(taskId);
                        await delay(100);
                    }

                    let emojiIndex = i * Math.floor(emojis.length / 5);
                    
                    const runLoop = async () => {
                        this.activeNameChanges.set(taskId, true);
                        await delay(i * 20);
                        while (this.activeNameChanges.get(taskId)) {
                            try {
                                const emoji = emojis[Math.floor(emojiIndex) % emojis.length];
                                const newName = `${nameText} ${emoji}`;
                                await this.sock.groupUpdateSubject(from, newName);
                                emojiIndex++;
                                await delay(nameDelay);
                            } catch (err) {
                                await delay(nameDelay);
                            }
                        }
                    };

                    runLoop();
                }

                if (sendConfirmation) {
                    await this.sendMessage(from, replyMessages.ncStarted);
                }
            }
            
            // TRIPLE NC ATTACK
            else if (commandType === 'start_triple_nc') {
                const { from, nameText, tripleKey } = data;
                const comboNames = tripleNcCombos[tripleKey] || ['nc1', 'nc2', 'nc3'];
                const tripleDelay = ncDelays.speedup > 0 ? ncDelays.speedup : (ncDelays[tripleKey] || 20);
                
                const tripleTaskId = `${from}_${tripleKey}`;
                const tripleTask = { 
                    active: true, 
                    ncKeys: comboNames,
                    threads: []
                };
                this.activeTripleNc.set(tripleTaskId, tripleTask);
                
                comboNames.forEach((ncKey, sectionIndex) => {
                    const emojis = emojiArrays[ncKey] || ['❓'];
                    const individualDelay = tripleDelay;
                    
                    for (let threadIndex = 0; threadIndex < 5; threadIndex++) {
                        const threadId = `${from}_${tripleKey}_${ncKey}_${threadIndex}`;
                        
                        if (this.activeNameChanges.has(threadId)) {
                            this.activeNameChanges.delete(threadId);
                        }

                        let emojiIndex = threadIndex * Math.floor(emojis.length / 5);
                        
                        const runTripleThread = async () => {
                            this.activeNameChanges.set(threadId, true);
                            await delay(threadIndex * 5);
                            
                            while (this.activeNameChanges.get(threadId) && tripleTask.active) {
                                try {
                                    const emoji = emojis[Math.floor(emojiIndex) % emojis.length];
                                    const newName = `${nameText} ${emoji}`;
                                    await this.sock.groupUpdateSubject(from, newName);
                                    emojiIndex++;
                                    await delay(individualDelay);
                                } catch (err) {
                                    await delay(individualDelay);
                                }
                            }
                            this.activeNameChanges.delete(threadId);
                        };

                        tripleTask.threads.push(threadId);
                        runTripleThread();
                    }
                });

                if (sendConfirmation) {
                    const comboNames = tripleNcCombos[tripleKey];
                    const firstEmoji = emojiArrays[comboNames[0]]?.[0] || '❓';
                    const secondEmoji = emojiArrays[comboNames[1]]?.[0] || '❓';
                    const thirdEmoji = emojiArrays[comboNames[2]]?.[0] || '❓';
                    
                    const confirmationMsg = `${replyMessages.realTripleAttack}\n\n` +
                                          `running: ${comboNames.join(' + ')}\n` +
                                          `emojis: ${firstEmoji} ${secondEmoji} ${thirdEmoji}\n` +
                                          `delay: ${tripleDelay}ms 🔥`;
                    
                    await this.sendMessage(from, confirmationMsg);
                }
            }
            
            // STOP INDIVIDUAL NC
            else if (commandType === 'stop_nc') {
                const { from } = data;
                let stopped = 0;
                
                this.activeNameChanges.forEach((value, taskId) => {
                    if (taskId.startsWith(from) && !taskId.includes('_triple')) {
                        this.activeNameChanges.set(taskId, false);
                        this.activeNameChanges.delete(taskId);
                        stopped++;
                    }
                });

                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, replyMessages.ncStopped);
                }
            }
            
            // STOP TRIPLE NC
            else if (commandType === 'stop_triple_nc') {
                const { from } = data;
                let stoppedCombos = 0;
                
                this.activeTripleNc.forEach((task, taskId) => {
                    if (taskId.startsWith(from)) {
                        task.active = false;
                        
                        task.threads?.forEach(threadId => {
                            if (this.activeNameChanges.has(threadId)) {
                                this.activeNameChanges.delete(threadId);
                            }
                        });
                        
                        task.ncKeys?.forEach(ncKey => {
                            for (let i = 0; i < 5; i++) {
                                const threadId = `${from}_${taskId.split('_')[1]}_${ncKey}_${i}`;
                                if (this.activeNameChanges.has(threadId)) {
                                    this.activeNameChanges.delete(threadId);
                                }
                            }
                        });
                        
                        this.activeTripleNc.delete(taskId);
                        stoppedCombos++;
                    }
                });

                if (stoppedCombos > 0 && sendConfirmation) {
                    await this.sendMessage(from, replyMessages.ncStopped);
                }
            }

            // ULTIMATE ATTACK - 100 NC SIMULTANEOUSLY
            else if (commandType === 'start_attack') {
                const { from, nameText } = data;
                
                if (this.activeAttack) {
                    this.activeAttack = false;
                    this.attackThreads.forEach(threadId => {
                        if (this.activeNameChanges.has(threadId)) {
                            this.activeNameChanges.delete(threadId);
                        }
                    });
                    this.attackThreads = [];
                    await delay(500);
                }

                this.activeAttack = true;
                const attackThreads = [];

                for (let t = 1; t <= 35; t++) {
                    const tripleKey = `triple${t}`;
                    const comboNames = tripleNcCombos[tripleKey] || ['nc1', 'nc2', 'nc3'];
                    
                    comboNames.forEach((ncKey, sectionIndex) => {
                        const emojis = emojiArrays[ncKey] || ['❓'];
                        const individualDelay = 20;
                        
                        for (let threadIndex = 0; threadIndex < 3; threadIndex++) {
                            const threadId = `${from}_attack_${tripleKey}_${ncKey}_${threadIndex}`;
                            
                            if (this.activeNameChanges.has(threadId)) {
                                this.activeNameChanges.delete(threadId);
                            }

                            let emojiIndex = threadIndex * Math.floor(emojis.length / 3);
                            
                            const runAttackThread = async () => {
                                this.activeNameChanges.set(threadId, true);
                                await delay((sectionIndex * 5) + (threadIndex * 3) + (t * 5));
                                
                                while (this.activeNameChanges.get(threadId) && this.activeAttack) {
                                    try {
                                        const emoji = emojis[Math.floor(emojiIndex) % emojis.length];
                                        const newName = `${nameText} ${emoji}`;
                                        await this.sock.groupUpdateSubject(from, newName);
                                        emojiIndex++;
                                        await delay(individualDelay);
                                    } catch (err) {
                                        await delay(individualDelay);
                                    }
                                }
                                this.activeNameChanges.delete(threadId);
                            };

                            attackThreads.push(threadId);
                            runAttackThread();
                        }
                    });
                }

                this.attackThreads = attackThreads;

                if (sendConfirmation) {
                    const confirmationMsg = `${replyMessages.attackStarted}\n\n` +
                                          `running: ALL 100 NC TYPES\n` +
                                          `delay: 20ms (ULTRA FAST!)\n` +
                                          `threads: 105 PARALLEL THREADS 🔥`;
                    
                    await this.sendMessage(from, confirmationMsg);
                }
            }
            
            // STOP ULTIMATE ATTACK
            else if (commandType === 'stop_attack') {
                const { from } = data;
                if (this.activeAttack) {
                    this.activeAttack = false;
                    this.attackThreads.forEach(threadId => {
                        if (this.activeNameChanges.has(threadId)) {
                            this.activeNameChanges.delete(threadId);
                        }
                    });
                    this.attackThreads = [];
                    
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.attackStopped);
                    }
                }
            }

            // NC LOOP
            else if (commandType === 'start_nc_loop') {
                const { from, nameText, ncKey, rounds } = data;
                
                this.activeNcLoop = {
                    active: true,
                    ncKey,
                    text: nameText,
                    round: 0,
                    maxRounds: rounds,
                    baseDelay: 100
                };

                const runNcLoop = async () => {
                    const emojis = emojiArrays[ncKey] || ['❓'];
                    let emojiIndex = 0;
                    
                    while (this.activeNcLoop && this.activeNcLoop.active && this.activeNcLoop.round < this.activeNcLoop.maxRounds) {
                        const currentDelay = Math.max(20, this.activeNcLoop.baseDelay - (this.activeNcLoop.round * 10));
                        
                        for (let i = 0; i < 10; i++) {
                            if (!this.activeNcLoop || !this.activeNcLoop.active) break;
                            
                            try {
                                const emoji = emojis[emojiIndex % emojis.length];
                                const newName = `${nameText} ${emoji}`;
                                await this.sock.groupUpdateSubject(from, newName);
                                emojiIndex++;
                                await delay(currentDelay);
                            } catch (err) {
                                await delay(currentDelay);
                            }
                        }
                        
                        this.activeNcLoop.round++;
                    }
                    
                    if (sendConfirmation) {
                        await this.sendMessage(from, `${replyMessages.ncLoopStopped}`);
                    }
                    this.activeNcLoop = null;
                };

                runNcLoop();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.ncLoopStarted}\n\nrounds: ${rounds}`);
                }
            }
            
            else if (commandType === 'stop_nc_loop') {
                if (this.activeNcLoop) {
                    this.activeNcLoop.active = false;
                    this.activeNcLoop = null;
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.ncLoopStopped);
                    }
                }
            }

            // HEART LOOP
            else if (commandType === 'start_heart_loop') {
                const { from, userText, delay } = data;
                
                this.activeHeartLoop = {
                    active: true,
                    text: userText,
                    delay
                };

                const hearts = ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔'];
                let heartIndex = 0;

                const runHeartLoop = async () => {
                    while (this.activeHeartLoop && this.activeHeartLoop.active) {
                        try {
                            const heart = hearts[heartIndex % hearts.length];
                            const wrappedText = `${heart} ${userText} ${heart}`;
                            await this.sock.groupUpdateSubject(from, wrappedText);
                            heartIndex++;
                            await delay(this.activeHeartLoop.delay);
                        } catch (err) {
                            await delay(this.activeHeartLoop.delay);
                        }
                    }
                };

                runHeartLoop();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.heartLoopStarted}\n\ndelay: ${delay}ms`);
                }
            }
            
            else if (commandType === 'stop_heart_loop') {
                if (this.activeHeartLoop) {
                    this.activeHeartLoop.active = false;
                    this.activeHeartLoop = null;
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.heartLoopStopped);
                    }
                }
            }

            // USE WORDS
            else if (commandType === 'start_use_words') {
                const { from, ncKey, delay, words } = data;
                
                this.activeUseWords = {
                    active: true,
                    ncKey,
                    words,
                    delay,
                    wordIndex: 0
                };

                const emojis = emojiArrays[ncKey] || ['❓'];
                let emojiIndex = 0;

                const runUseWords = async () => {
                    while (this.activeUseWords && this.activeUseWords.active) {
                        try {
                            const word = this.activeUseWords.words[this.activeUseWords.wordIndex % this.activeUseWords.words.length];
                            const emoji = emojis[emojiIndex % emojis.length];
                            const newName = `${word} ${emoji}`;
                            await this.sock.groupUpdateSubject(from, newName);
                            
                            emojiIndex++;
                            this.activeUseWords.wordIndex++;
                            await delay(this.activeUseWords.delay);
                        } catch (err) {
                            await delay(this.activeUseWords.delay);
                        }
                    }
                };

                runUseWords();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.useWordsStarted}\n\nwords: ${words.length}`);
                }
            }
            
            else if (commandType === 'stop_use_words') {
                if (this.activeUseWords) {
                    this.activeUseWords.active = false;
                    this.activeUseWords = null;
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.useWordsStopped);
                    }
                }
            }

            // COVER GC
            else if (commandType === 'start_cover_gc') {
                const { from, text } = data;
                
                this.activeCoverGC = {
                    active: true,
                    text
                };

                const runCoverGC = async () => {
                    const allNcKeys = Object.keys(emojiArrays);
                    let ncIndex = 0;
                    
                    while (this.activeCoverGC && this.activeCoverGC.active) {
                        for (let i = 0; i < 10; i++) {
                            if (!this.activeCoverGC || !this.activeCoverGC.active) break;
                            
                            try {
                                const ncKey = allNcKeys[ncIndex % allNcKeys.length];
                                const emojis = emojiArrays[ncKey];
                                const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                                const newName = `${text} ${emoji}`;
                                await this.sock.groupUpdateSubject(from, newName);
                                ncIndex++;
                                await delay(10);
                            } catch (err) {
                                await delay(10);
                            }
                        }
                    }
                };

                runCoverGC();

                if (sendConfirmation) {
                    await this.sendMessage(from, replyMessages.coverGCStarted);
                }
            }
            
            else if (commandType === 'stop_cover_gc') {
                if (this.activeCoverGC) {
                    this.activeCoverGC.active = false;
                    this.activeCoverGC = null;
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.coverGCStopped);
                    }
                }
            }

            // RAGE MODE
            else if (commandType === 'start_rage_mode') {
                const { from, ncKey, text } = data;
                
                this.activeRageMode = {
                    active: true,
                    ncKey,
                    text
                };

                const emojis = emojiArrays[ncKey] || ['❓'];

                const runRageMode = async () => {
                    for (let t = 0; t < 10; t++) {
                        if (!this.activeRageMode || !this.activeRageMode.active) break;
                        
                        const runRageThread = async (threadId) => {
                            let emojiIndex = threadId * 10;
                            while (this.activeRageMode && this.activeRageMode.active) {
                                try {
                                    const emoji = emojis[emojiIndex % emojis.length];
                                    const newName = `${text} ${emoji}`;
                                    await this.sock.groupUpdateSubject(from, newName);
                                    emojiIndex++;
                                    await delay(5);
                                } catch (err) {
                                    await delay(5);
                                }
                            }
                        };

                        runRageThread(t);
                        await delay(2);
                    }
                };

                runRageMode();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.rageModeStarted}\n\nnc: ${ncKey}`);
                }
            }
            
            else if (commandType === 'stop_rage_mode') {
                if (this.activeRageMode) {
                    this.activeRageMode.active = false;
                    this.activeRageMode = null;
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.rageModeStopped);
                    }
                }
            }

            // TIME NC
            else if (commandType === 'start_time_nc') {
                const { from, ncKey, text } = data;
                
                this.activeTimeNC = {
                    active: true,
                    ncKey,
                    text
                };

                const emojis = emojiArrays[ncKey] || ['❓'];

                const runTimeNC = async () => {
                    let emojiIndex = 0;
                    while (this.activeTimeNC && this.activeTimeNC.active) {
                        try {
                            const now = new Date();
                            const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
                            const emoji = emojis[emojiIndex % emojis.length];
                            const newName = `${text} ${emoji} [${timeStr}]`;
                            await this.sock.groupUpdateSubject(from, newName);
                            emojiIndex++;
                            await delay(1000);
                        } catch (err) {
                            await delay(1000);
                        }
                    }
                };

                runTimeNC();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.timeNCStarted}\n\nnc: ${ncKey}`);
                }
            }

            // NC SPAM
            else if (commandType === 'start_nc_spam') {
                const { from, ncKey, text, delay } = data;
                
                this.activeNcSpam = {
                    active: true,
                    ncKey,
                    text,
                    delay,
                    count: 0
                };

                const emojis = emojiArrays[ncKey] || ['❓'];

                const runNcSpam = async () => {
                    let emojiIndex = 0;
                    while (this.activeNcSpam && this.activeNcSpam.active) {
                        try {
                            const emoji = emojis[emojiIndex % emojis.length];
                            const newName = `${text} ${emoji}`;
                            await this.sock.groupUpdateSubject(from, newName);
                            emojiIndex++;
                            this.activeNcSpam.count++;
                            
                            if (this.activeNcSpam.count % 10 === 0) {
                                await this.sock.sendMessage(from, { text: text });
                            }
                            
                            await delay(this.activeNcSpam.delay);
                        } catch (err) {
                            await delay(this.activeNcSpam.delay);
                        }
                    }
                };

                runNcSpam();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.ncSpamStarted}\n\ndelay: ${delay}ms`);
                }
            }
            
            else if (commandType === 'stop_nc_spam') {
                if (this.activeNcSpam) {
                    this.activeNcSpam.active = false;
                    this.activeNcSpam = null;
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.ncSpamStopped);
                    }
                }
            }

            // SLIDE ATTACK
            else if (commandType === 'start_slide') {
                const { from, slideText, slideDelay, quotedParticipant, quotedMsgId, quotedMessage } = data;
                
                const taskId = `${from}_${quotedParticipant}`;
                
                if (this.activeSlides.has(taskId)) {
                    this.activeSlides.get(taskId).active = false;
                    await delay(200);
                }

                const slideTask = {
                    targetJid: quotedParticipant,
                    text: slideText,
                    groupJid: from,
                    latestMsg: {
                        key: {
                            remoteJid: from,
                            fromMe: false,
                            id: quotedMsgId,
                            participant: quotedParticipant
                        },
                        message: quotedMessage
                    },
                    active: true
                };

                this.activeSlides.set(taskId, slideTask);

                const runSlide = async () => {
                    while (slideTask.active) {
                        try {
                            await this.sock.sendMessage(from, { 
                                text: slideText 
                            }, { 
                                quoted: slideTask.latestMsg
                            });
                        } catch (err) {}
                        await delay(slideDelay);
                    }
                };

                runSlide();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.slideAttackStarted}\n\n${slideText}\ndelay: ${slideDelay}ms`);
                }
            }
            else if (commandType === 'stop_slide') {
                const { from } = data;
                let stopped = 0;
                this.activeSlides.forEach((task, taskId) => {
                    if (task.groupJid === from) {
                        task.active = false;
                        this.activeSlides.delete(taskId);
                        stopped++;
                    }
                });

                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, replyMessages.slideAttackStopped);
                }
            }

            // TARGET SLIDE
            else if (commandType === 'start_target') {
                const { from, targetJid, text, delay } = data;
                
                if (!this.activeTargetSlides) this.activeTargetSlides = new Map();
                
                const taskId = `${from}_target`;
                
                if (this.activeTargetSlides.has(taskId)) {
                    this.activeTargetSlides.get(taskId).active = false;
                    await delay(200);
                }

                const targetTask = {
                    targetJid,
                    text,
                    groupJid: from,
                    delay,
                    active: true
                };

                this.activeTargetSlides.set(taskId, targetTask);

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.targetStarted}\n\n${text}\ndelay: ${delay}ms`, [targetJid]);
                }
            }
            else if (commandType === 'stop_target') {
                const { from } = data;
                let stopped = 0;
                if (this.activeTargetSlides) {
                    this.activeTargetSlides.forEach((task, taskId) => {
                        if (task.groupJid === from) {
                            task.active = false;
                            this.activeTargetSlides.delete(taskId);
                            stopped++;
                        }
                    });
                }

                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, replyMessages.targetStopped);
                }
            }

            // TEXT ATTACK
            else if (commandType === 'start_txt') {
                const { from, txtText, txtDelay } = data;
                
                const taskId = `${from}_txt`;
                
                if (this.activeTxtSenders.has(taskId)) {
                    this.activeTxtSenders.get(taskId).active = false;
                    await delay(200);
                }

                const txtTask = { active: true };
                this.activeTxtSenders.set(taskId, txtTask);

                const runTxt = async () => {
                    while (txtTask.active) {
                        try {
                            await this.sock.sendMessage(from, { text: txtText });
                        } catch (err) {}
                        await delay(txtDelay);
                    }
                };

                runTxt();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.textAttackStarted}\n\n${txtText}\ndelay: ${txtDelay}ms`);
                }
            }
            else if (commandType === 'stop_txt') {
                const { from } = data;
                const taskId = `${from}_txt`;
                if (this.activeTxtSenders.has(taskId)) {
                    this.activeTxtSenders.get(taskId).active = false;
                    this.activeTxtSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.textAttackStopped);
                    }
                }
            }

            // TTS ATTACK
            else if (commandType === 'start_tts') {
                const { from, ttsText, ttsDelay } = data;
                
                const taskId = `${from}_tts`;
                
                if (this.activeTTSSenders.has(taskId)) {
                    this.activeTTSSenders.get(taskId).active = false;
                    await delay(200);
                }

                const ttsTask = { active: true };
                this.activeTTSSenders.set(taskId, ttsTask);

                const runTTS = async () => {
                    while (ttsTask.active) {
                        try {
                            const audioBuffer = await generateTTS(ttsText);
                            await this.sock.sendMessage(from, {
                                audio: audioBuffer,
                                mimetype: 'audio/ogg; codecs=opus',
                                ptt: true
                            });
                        } catch (err) {}
                        await delay(ttsDelay);
                    }
                };

                runTTS();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.ttsAttackStarted}\n\n${ttsText}\ndelay: ${ttsDelay}ms`);
                }
            }
            else if (commandType === 'stop_tts') {
                const { from } = data;
                const taskId = `${from}_tts`;
                if (this.activeTTSSenders.has(taskId)) {
                    this.activeTTSSenders.get(taskId).active = false;
                    this.activeTTSSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.ttsAttackStopped);
                    }
                }
            }

            // PICTURE ATTACK
            else if (commandType === 'start_pic') {
                const { from, picDelay, imageBuffer, mimetype } = data;
                
                const taskId = `${from}_pic`;
                
                if (this.activePicSenders.has(taskId)) {
                    this.activePicSenders.get(taskId).active = false;
                    await delay(200);
                }

                const picTask = { active: true, buffer: Buffer.from(imageBuffer, 'base64'), mimetype };
                this.activePicSenders.set(taskId, picTask);

                const runPic = async () => {
                    while (picTask.active) {
                        try {
                            await this.sock.sendMessage(from, {
                                image: picTask.buffer,
                                mimetype: picTask.mimetype
                            });
                        } catch (err) {}
                        await delay(picDelay);
                    }
                };

                runPic();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.picAttackStarted}\n\ndelay: ${picDelay}ms`);
                }
            }
            else if (commandType === 'stop_pic') {
                const { from } = data;
                const taskId = `${from}_pic`;
                if (this.activePicSenders.has(taskId)) {
                    this.activePicSenders.get(taskId).active = false;
                    this.activePicSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.picAttackStopped);
                    }
                }
            }

            // VIDEO SPAM
            else if (commandType === 'start_video') {
                const { from, videoDelay, videoBuffer, mimetype } = data;
                
                const taskId = `${from}_video`;
                
                if (!this.activeVideoSenders) this.activeVideoSenders = new Map();
                
                if (this.activeVideoSenders.has(taskId)) {
                    this.activeVideoSenders.get(taskId).active = false;
                    await delay(200);
                }

                const videoTask = { active: true, buffer: Buffer.from(videoBuffer, 'base64'), mimetype };
                this.activeVideoSenders.set(taskId, videoTask);

                const runVideo = async () => {
                    while (videoTask.active) {
                        try {
                            await this.sock.sendMessage(from, {
                                video: videoTask.buffer,
                                mimetype: videoTask.mimetype
                            });
                        } catch (err) {}
                        await delay(videoDelay);
                    }
                };

                runVideo();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.videoSpamStarted}\n\ndelay: ${videoDelay}ms`);
                }
            }
            else if (commandType === 'stop_video') {
                const { from } = data;
                if (this.activeVideoSenders) {
                    const taskId = `${from}_video`;
                    if (this.activeVideoSenders.has(taskId)) {
                        this.activeVideoSenders.get(taskId).active = false;
                        this.activeVideoSenders.delete(taskId);
                        if (sendConfirmation) {
                            await this.sendMessage(from, replyMessages.videoSpamStopped);
                        }
                    }
                }
            }

            // GROUP DP CHANGE
            else if (commandType === 'start_grpfp') {
                const { from, imageBuffer, grpfpDelay } = data;
                
                const taskId = `${from}_dp`;
                
                if (this.activeGroupDpChanges.has(taskId)) {
                    this.activeGroupDpChanges.get(taskId).active = false;
                    await delay(200);
                }

                const dpTask = { 
                    active: true,
                    buffer: Buffer.from(imageBuffer, 'base64')
                };
                this.activeGroupDpChanges.set(taskId, dpTask);

                const runDpLoop = async () => {
                    while (dpTask.active) {
                        try {
                            await this.sock.updateProfilePicture(from, dpTask.buffer);
                            await delay(grpfpDelay);
                        } catch (err) {
                            await delay(grpfpDelay);
                        }
                    }
                };
                
                runDpLoop();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.grpfpStarted}\ndelay: ${grpfpDelay}ms`);
                }
            }
            else if (commandType === 'stop_grpfp') {
                const { from } = data;
                const taskId = `${from}_dp`;
                if (this.activeGroupDpChanges.has(taskId)) {
                    this.activeGroupDpChanges.get(taskId).active = false;
                    this.activeGroupDpChanges.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.grpfpStopped);
                    }
                }
            }

            // STICKER SLIDE
            else if (commandType === 'start_grpstk') {
                const { from, quotedParticipant, quotedMsgId, quotedMessage, stickerDelay, stickerBuffer, mimetype } = data;
                
                const taskId = `${from}_sticker_${quotedParticipant}`;
                
                if (this.activeStickerSlides.has(taskId)) {
                    this.activeStickerSlides.get(taskId).active = false;
                    await delay(200);
                }

                const stickerSlideTask = {
                    targetJid: quotedParticipant,
                    groupJid: from,
                    latestMsg: {
                        key: {
                            remoteJid: from,
                            fromMe: false,
                            id: quotedMsgId,
                            participant: quotedParticipant
                        },
                        message: quotedMessage
                    },
                    active: true,
                    stickerBuffer: Buffer.from(stickerBuffer, 'base64'),
                    mimetype
                };

                this.activeStickerSlides.set(taskId, stickerSlideTask);

                const runStickerSlide = async () => {
                    while (stickerSlideTask.active) {
                        try {
                            const messageOptions = {};
                            
                            if (stickerSlideTask.mimetype.includes('video')) {
                                messageOptions.video = stickerSlideTask.stickerBuffer;
                                messageOptions.mimetype = stickerSlideTask.mimetype;
                                messageOptions.gifPlayback = true;
                            } else {
                                messageOptions.sticker = stickerSlideTask.stickerBuffer;
                                messageOptions.mimetype = stickerSlideTask.mimetype;
                            }
                            
                            await this.sock.sendMessage(from, messageOptions, { 
                                quoted: stickerSlideTask.latestMsg
                            });
                        } catch (err) {}
                        await delay(stickerDelay);
                    }
                };

                runStickerSlide();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.grpstkStarted}\n\ndelay: ${stickerDelay}ms`);
                }
            }
            else if (commandType === 'stop_grpstk') {
                const { from } = data;
                let stopped = 0;
                this.activeStickerSlides.forEach((task, taskId) => {
                    if (task.groupJid === from) {
                        task.active = false;
                        this.activeStickerSlides.delete(taskId);
                        stopped++;
                    }
                });

                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, replyMessages.grpstkStopped);
                }
            }

            // GIF SPAM
            else if (commandType === 'start_gif') {
                const { from, gifDelay, videoBuffer, mimetype } = data;
                
                const taskId = `${from}_gif`;
                
                if (this.activeGifSpam.has(taskId)) {
                    this.activeGifSpam.get(taskId).active = false;
                    await delay(200);
                }

                const gifTask = { 
                    active: true, 
                    buffer: Buffer.from(videoBuffer, 'base64'), 
                    mimetype 
                };
                this.activeGifSpam.set(taskId, gifTask);

                const runGif = async () => {
                    while (gifTask.active) {
                        try {
                            await this.sock.sendMessage(from, {
                                video: gifTask.buffer,
                                mimetype: gifTask.mimetype,
                                gifPlayback: true
                            });
                        } catch (err) {}
                        await delay(gifDelay);
                    }
                };

                runGif();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.gifSpamStarted}\n\ndelay: ${gifDelay}ms`);
                }
            }
            else if (commandType === 'stop_gif') {
                const { from } = data;
                const taskId = `${from}_gif`;
                if (this.activeGifSpam.has(taskId)) {
                    this.activeGifSpam.get(taskId).active = false;
                    this.activeGifSpam.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.gifSpamStopped);
                    }
                }
            }

            // STICKER SPAM
            else if (commandType === 'start_stk') {
                const { from, stkDelay, stickerBuffer, mimetype } = data;
                
                const taskId = `${from}_stk`;
                
                if (this.activeStickerSpam.has(taskId)) {
                    this.activeStickerSpam.get(taskId).active = false;
                    await delay(200);
                }

                const stkTask = { 
                    active: true, 
                    buffer: Buffer.from(stickerBuffer, 'base64'), 
                    mimetype 
                };
                this.activeStickerSpam.set(taskId, stkTask);

                const runStk = async () => {
                    while (stkTask.active) {
                        try {
                            const messageOptions = {};
                            
                            if (stkTask.mimetype.includes('video')) {
                                messageOptions.video = stkTask.buffer;
                                messageOptions.mimetype = stkTask.mimetype;
                                messageOptions.gifPlayback = true;
                            } else {
                                messageOptions.sticker = stkTask.buffer;
                                messageOptions.mimetype = stkTask.mimetype;
                            }
                            
                            await this.sock.sendMessage(from, messageOptions);
                        } catch (err) {}
                        await delay(stkDelay);
                    }
                };

                runStk();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.stickerSpamStarted}\n\ndelay: ${stkDelay}ms`);
                }
            }
            else if (commandType === 'stop_stk') {
                const { from } = data;
                const taskId = `${from}_stk`;
                if (this.activeStickerSpam.has(taskId)) {
                    this.activeStickerSpam.get(taskId).active = false;
                    this.activeStickerSpam.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.stickerSpamStopped);
                    }
                }
            }

            // VOICE NOTE SPAM
            else if (commandType === 'start_vn') {
                const { from, vnDelay, audioBuffer, mimetype, seconds, ptt } = data;
                
                const taskId = `${from}_vn`;
                
                if (this.activeVnSpam.has(taskId)) {
                    this.activeVnSpam.get(taskId).active = false;
                    await delay(200);
                }

                const vnTask = { 
                    active: true, 
                    buffer: Buffer.from(audioBuffer, 'base64'), 
                    mimetype,
                    seconds,
                    ptt
                };
                
                this.activeVnSpam.set(taskId, vnTask);

                const runVn = async () => {
                    while (vnTask.active) {
                        try {
                            await this.sock.sendMessage(from, {
                                audio: vnTask.buffer,
                                mimetype: vnTask.mimetype,
                                ptt: vnTask.ptt,
                                seconds: vnTask.seconds
                            });
                        } catch (err) {}
                        await delay(vnDelay);
                    }
                };

                runVn();

                if (sendConfirmation) {
                    await this.sendMessage(from, `${replyMessages.vnStarted}\n\ndelay: ${vnDelay}ms`);
                }
            }
            else if (commandType === 'stop_vn') {
                const { from } = data;
                const taskId = `${from}_vn`;
                if (this.activeVnSpam.has(taskId)) {
                    this.activeVnSpam.get(taskId).active = false;
                    this.activeVnSpam.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, replyMessages.vnStopped);
                    }
                }
            }

            // STOP ALL
            else if (commandType === 'stop_all') {
                const { from } = data;
                let stopped = 0;
                
                this.activeNameChanges.forEach((value, taskId) => {
                    if (taskId.startsWith(from)) {
                        this.activeNameChanges.set(taskId, false);
                        this.activeNameChanges.delete(taskId);
                        stopped++;
                    }
                });
                
                this.activeTripleNc.forEach((task, taskId) => {
                    if (taskId.startsWith(from)) {
                        task.active = false;
                        this.activeTripleNc.delete(taskId);
                        stopped++;
                    }
                });
                
                if (this.activeAttack) {
                    this.activeAttack = false;
                    this.attackThreads.forEach(threadId => {
                        if (this.activeNameChanges.has(threadId)) {
                            this.activeNameChanges.delete(threadId);
                        }
                    });
                    this.attackThreads = [];
                    stopped++;
                }
                
                if (this.activeNcLoop) {
                    this.activeNcLoop.active = false;
                    this.activeNcLoop = null;
                    stopped++;
                }
                
                if (this.activeHeartLoop) {
                    this.activeHeartLoop.active = false;
                    this.activeHeartLoop = null;
                    stopped++;
                }
                
                if (this.activeUseWords) {
                    this.activeUseWords.active = false;
                    this.activeUseWords = null;
                    stopped++;
                }
                
                if (this.activeCoverGC) {
                    this.activeCoverGC.active = false;
                    this.activeCoverGC = null;
                    stopped++;
                }
                
                if (this.activeRageMode) {
                    this.activeRageMode.active = false;
                    this.activeRageMode = null;
                    stopped++;
                }
                
                if (this.activeTimeNC) {
                    this.activeTimeNC.active = false;
                    this.activeTimeNC = null;
                    stopped++;
                }
                
                if (this.activeNcSpam) {
                    this.activeNcSpam.active = false;
                    this.activeNcSpam = null;
                    stopped++;
                }
                
                this.activeConstantAttacks.forEach((task, taskId) => {
                    if (taskId.startsWith(from)) {
                        task.active = false;
                        this.activeConstantAttacks.delete(taskId);
                        stopped++;
                    }
                });
                
                this.activeSlides.forEach((task, taskId) => {
                    if (task.groupJid === from) {
                        task.active = false;
                        this.activeSlides.delete(taskId);
                        stopped++;
                    }
                });
                
                if (this.activeTargetSlides) {
                    this.activeTargetSlides.forEach((task, taskId) => {
                        if (task.groupJid === from) {
                            task.active = false;
                            this.activeTargetSlides.delete(taskId);
                            stopped++;
                        }
                    });
                }
                
                if (this.rageSettings && this.rageSettings.has(from)) {
                    this.rageSettings.get(from).active = false;
                    this.rageSettings.delete(from);
                    stopped++;
                }
                
                const dpTaskId = `${from}_dp`;
                if (this.activeGroupDpChanges.has(dpTaskId)) {
                    this.activeGroupDpChanges.get(dpTaskId).active = false;
                    this.activeGroupDpChanges.delete(dpTaskId);
                    stopped++;
                }
                
                const txtTaskId = `${from}_txt`;
                if (this.activeTxtSenders.has(txtTaskId)) {
                    this.activeTxtSenders.get(txtTaskId).active = false;
                    this.activeTxtSenders.delete(txtTaskId);
                    stopped++;
                }

                const ttsTaskId = `${from}_tts`;
                if (this.activeTTSSenders.has(ttsTaskId)) {
                    this.activeTTSSenders.get(ttsTaskId).active = false;
                    this.activeTTSSenders.delete(ttsTaskId);
                    stopped++;
                }

                const picTaskId = `${from}_pic`;
                if (this.activePicSenders.has(picTaskId)) {
                    this.activePicSenders.get(picTaskId).active = false;
                    this.activePicSenders.delete(picTaskId);
                    stopped++;
                }

                if (this.activeVideoSenders) {
                    const videoTaskId = `${from}_video`;
                    if (this.activeVideoSenders.has(videoTaskId)) {
                        this.activeVideoSenders.get(videoTaskId).active = false;
                        this.activeVideoSenders.delete(videoTaskId);
                        stopped++;
                    }
                }

                this.activeStickerSlides.forEach((task, taskId) => {
                    if (task.groupJid === from) {
                        task.active = false;
                        this.activeStickerSlides.delete(taskId);
                        stopped++;
                    }
                });
                
                const gifTaskId = `${from}_gif`;
                if (this.activeGifSpam.has(gifTaskId)) {
                    this.activeGifSpam.get(gifTaskId).active = false;
                    this.activeGifSpam.delete(gifTaskId);
                    stopped++;
                }
                
                const stkTaskId = `${from}_stk`;
                if (this.activeStickerSpam.has(stkTaskId)) {
                    this.activeStickerSpam.get(stkTaskId).active = false;
                    this.activeStickerSpam.delete(stkTaskId);
                    stopped++;
                }
                
                const vnTaskId = `${from}_vn`;
                if (this.activeVnSpam && this.activeVnSpam.has(vnTaskId)) {
                    this.activeVnSpam.get(vnTaskId).active = false;
                    this.activeVnSpam.delete(vnTaskId);
                    stopped++;
                }
                
                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, `stopped ${stopped} attacks`);
                }
            }
            
        } catch (err) {
            console.error(`[${this.botId}] executeCommand error:`, err);
        }
    }

    async sendMessage(jid, text, mentions = []) {
        if (!this.sock || !this.connected) return;
        try {
            const message = { text };
            if (mentions.length > 0) {
                message.mentions = mentions;
            }
            await this.sock.sendMessage(jid, message);
        } catch (err) {}
    }
}

class BotManager {
    constructor() {
        this.bots = new Map();
        this.commandBus = new CommandBus();
        this.botCounter = 0;
        this.loadedData = this.loadBots();
    }

    loadBots() {
        try {
            if (fs.existsSync(BOTS_FILE)) {
                const data = fs.readFileSync(BOTS_FILE, 'utf8');
                const savedBots = JSON.parse(data);
                this.botCounter = savedBots.counter || 0;
                console.log(`[MANAGER] Found ${savedBots.bots?.length || 0} saved bot(s)`);
                return savedBots;
            }
        } catch (err) {
            console.log('[MANAGER] No saved bots found, starting fresh');
        }
        return { counter: 0, bots: [] };
    }

    saveBots() {
        try {
            if (!fs.existsSync('./data')) {
                fs.mkdirSync('./data', { recursive: true });
            }
            const data = {
                counter: this.botCounter,
                bots: Array.from(this.bots.entries()).map(([id, bot]) => ({
                    id,
                    phoneNumber: bot.phoneNumber,
                    connected: bot.connected,
                    disabled: bot.disabled
                }))
            };
            fs.writeFileSync(BOTS_FILE, JSON.stringify(data, null, 2));
        } catch (err) {
            console.error('[MANAGER] Error saving bots:', err.message);
        }
    }

    async restoreSavedBots() {
        if (this.loadedData.bots && this.loadedData.bots.length > 0) {
            console.log(`[MANAGER] Restoring ${this.loadedData.bots.length} bot session(s)...`);
            
            for (const botData of this.loadedData.bots) {
                const authPath = `./auth/${botData.id}`;
                const hasAuth = fs.existsSync(authPath) && fs.readdirSync(authPath).length > 0;
                
                let phoneNumber = botData.phoneNumber;
                
                if (!hasAuth && !phoneNumber) {
                    console.log(`\n[MANAGER] ${botData.id} has no credentials and no phone number.`);
                    phoneNumber = await question(`Enter phone number for ${botData.id} (e.g. 
917983133773): `);
                    phoneNumber = phoneNumber.replace(/[^0-9]/g, '');
                    
                    if (!phoneNumber || phoneNumber.length < 10) {
                        console.log(`[MANAGER] Invalid number. Removing ${botData.id}...`);
                        continue;
                    }
                }
                
                const session = new BotSession(botData.id, phoneNumber, this, null);
                session.disabled = botData.disabled || false;
                this.bots.set(botData.id, session);
                this.commandBus.registerBot(botData.id, session);
                
                if (!session.disabled) {
                    console.log(`[MANAGER] Reconnecting ${botData.id}...`);
                    await session.connect();
                } else {
                    console.log(`[MANAGER] ${botData.id} is disabled`);
                }
                await delay(2000);
            }
            
            this.saveBots();
        } else {
            console.log('[MANAGER] No saved sessions. Waiting for first bot via !add command...');
            
            const phoneNumber = await question('Enter phone number for BOT1 (or press Enter to skip): ');
            if (phoneNumber && phoneNumber.trim()) {
                const cleanNumber = phoneNumber.replace(/[^0-9]/g, '');
                if (cleanNumber.length >= 10) {
                    await this.addBot(cleanNumber, null);
                }
            } else {
                console.log('[MANAGER] Skipped. Use !add command in WhatsApp to add bots.\n');
            }
        }
    }

    async addBot(phoneNumber, requestingJid = null) {
        this.botCounter++;
        const botId = `BOT${this.botCounter}`;
        
        const session = new BotSession(botId, phoneNumber, this, requestingJid);
        this.bots.set(botId, session);
        this.commandBus.registerBot(botId, session);
        
        await session.connect();
        this.saveBots();
        
        return `${replyMessages.botCreated}\n\n✅ ᴀYUSH bot session created\n📱 number: ${phoneNumber}\n\n⏳ waiting for pairing code`;
    }

    removeBot(botId) {
        if (this.bots.has(botId)) {
            this.commandBus.unregisterBot(botId);
            this.bots.delete(botId);
            this.saveBots();
            console.log(`[MANAGER] Removed ${botId}`);
        }
    }
}

// ========== STARTUP ==========
console.log(`
╔═══❖•ೋ° °ೋ•❖═══╗
 Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟? BOT 🕷️
╚═══❖•ೋ° °ೋ•❖═══╝
◎ ══════ ❈ ══════ ◎
Ꮐᴏ֟፝ᴅ 𝐀𝐘𝐔𝐒𝐇𓆩⃟?bot system

🔥 𝙁𝙄𝙓𝙀𝘿 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎:
━━━━━━━━━━━━━━━━━━
👑 !addadmin - Add bot admin (DM only, Owner only)
🗑️ !removeadmin - Remove bot admin (DM only)
👥 !sub - Add bot sub-admin (Group, Owner/Admin)
🚫 !removesub - Remove bot sub-admin (Group)
📋 !listadmins - List all bot admins
📋 !listsub - List sub-admins in current group

👥 𝙒𝙃𝘼𝙏𝙎𝘼𝙋𝙋 𝘼𝘿𝙈𝙄𝙉 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎:
━━━━━━━━━━━━━━━━━━━━━━━━━
👑 !wadmin - Promote to WhatsApp group admin
⬇️ !wremoveadmin - Demote from WhatsApp group admin
📋 !wadmins - List WhatsApp group admins

🎯 !target - Auto-reply to specific user (FIXED)

other features:
• constant text attack 🌀
• real triple attacks (10x FAST!) 🔥
• ULTIMATE ATTACK (100 NC SIMULTANEOUSLY) 💥
• 100 nc types with expanded emojis ⚔️
• rage mode (hyper density) 😤
• group dp changer with stop 🎨
• sticker slide attack 🏷️
• gif spam 🎞️
• sticker spam 📍
• voice note spam 🎵
• AUTO RECONNECT SYSTEM 🔄
• Bad Mac Error FIXED ✅
• bot status checker 🤖
• auto react system 💖
• fast pairing system ⚡

ULTIMATE ATTACK (100 NC):
• !attack [text] → ALL 100 NC TYPES SIMULTANEOUSLY 💥

triple attacks (10x FAST!):
• !triple1 to !triple35 → 3 NC at once 🎭

minimum delay: 20ms (10x FASTER!)
send !menu to see commands
`);

const botManager = new BotManager();
await botManager.restoreSavedBots();
rl.close();

console.log(`\n✅ connected`);
console.log(`!owner in dm to become AYUSH owner 👑`);
console.log(`!add [number] to add new ᴀYUSH bots 🤖`);
console.log(`!menu to see all commands 📋`);
console.log(`enjoy the power of ᴀYUSH BOT !♡ ⚡\n`);
