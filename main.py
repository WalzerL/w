import os
import json
import random
import math
import logging
import re
import asyncio
import io
import qrcode
from datetime import datetime, timedelta
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# ================== Настройки логирования ==================
def setup_logging():
    """Настройка системы логирования"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "bot.log"), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    error_handler = logging.FileHandler(os.path.join(log_dir, "errors.log"), encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    logging.getLogger().addHandler(error_handler)
    
    return logging.getLogger(__name__)

logger = setup_logging()

# ================== Настройки бота ==================
TOKEN = "8611102281:AAGELNBTHu6xLLDYoD1ccmbCeshFjeqHV7M"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# Исходные карточки по редкости
CARDS = {
    "обычная": [
        {"id": "WR","name": "Безумный Волзер", "url": "https://ltdfoto.ru/images/2025/04/04/Crazy_DaWalzer.png"},
        {"id": "W1","name": "Волзер Огузок", "url": "https://ltdfoto.ru/images/2025/04/04/Oguzok_Walzer.png"},
        {"id": "WU","name": "Волзер-Пират", "url": "https://ltdfoto.ru/images/2025/04/04/PIrate_Walzer.png"},
        {"id": "WZ","name": "Волзер в пуховике", "url": "https://ltdfoto.ru/images/2025/04/04/Pukhovik_Walzer.png"},
        {"id": "WI","name": "Шакальный Волзер", "url": "https://ltdfoto.ru/images/2025/04/04/shakal_walzer.png"},
        {"id": "WW","name": "Волзер Волзер", "url": "https://ltdfoto.ru/images/2025/04/04/Walzer_Walzer.png"},
        {"id": "WWW","name": "ээ.. что?", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY148_20251026053800.png"},
        {"id": "WN","name": "Волзер, который шел на програмиста", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY152_20251026055218.png"},
        {"id": "WRR","name": "®", "url": "https://ltdfoto.ru/images/2025/11/13/r.png"},
        {"id": "WHEH","name": "ХП=КХАХЗХРАДХРЗДАЗХРЗХРЗХЩРЗП", "url": "https://s1.radikal.cloud/2025/12/16/BEZ-NAZVANIY21_20251216223541001564d55e16526c.png"},
        {"id": "WPR3","name": "Тайип Эрдозер", "url": "https://radika1.link/2025/12/16/BEZ-NAZVANIY18_20251216222851f6a84bbacba46c76.png"},
        {"id": "WPH","name": "SNOWser", "url": "https://radika1.link/2025/12/16/BEZ-NAZVANIY15_2025121622223978827a18ecd79b60.png"},
    ],
    "необычная": [
        {"id": "W9","name": "Горничная Волзер", "url": "https://ltdfoto.ru/images/2025/04/04/Clening_walzer.png"},
        {"id": "WL","name": "Волзер-Лягушонок", "url": "https://ltdfoto.ru/images/2025/04/04/Kermit_Walzer.png"},
        {"id": "WLZ","name": "СУПЕР СИГМА ВОЛЗЕР!!", "url": "https://ltdfoto.ru/images/2025/04/04/Mewing_Walzer.png"},
        {"id": "WM","name": "Волзер-Стейк", "url": "https://ltdfoto.ru/images/2025/04/04/Walzer_The_Steak.png"},
        {"id": "WX","name": "Пиксельный Волзер Маг", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY144_20251026054448.png"},
        {"id": "W09","name": "Шут", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY150_20251026054219.png"},
        {"id": "WMB","name": "Волзер из Китая", "url": "https://i.ibb.co/N6C5S1b5/156-20251028223706.png"},
        {"id": "WMD","name": " Гитарист Волзер ", "url": "https://i.ibb.co/fdNwwyFC/157-20251028223854.png"},
        {"id": "WJQ","name": "Бородатый Волзер", "url": "https://i.ibb.co/ccW3T3qs/172-20251101022845.png"},
        {"id": "WJ7","name": "как. ", "url": "https://i.ibb.co/xqMTPR6m/174-20251101024217.png"},
        {"id": "WI3","name": "Большояйцевый Волзер", "url": "https://s1.radikal.cloud/2025/12/16/BEZ-NAZVANIY16_202512162224304be71ef25599bc98.png"},
        {"id": "WL2","name": "Suomalainen tarkka-ampuja Walzer", "url": "https://s1.radikal.cloud/2025/12/16/BEZ-NAZVANIY9_2025121622050249d45f0066b3026f.png"}
    ],
    "редкая": [
        {"id": "WK","name": "Робо-Волзер", "url": "https://ltdfoto.ru/images/2025/04/04/Walzer_Bot.png"},
        {"id": "WO","name": "Волзер-Скуф", "url": "https://ltdfoto.ru/images/2025/04/04/Walzer_Ckyf.png"},
        {"id": "W040","name": "Повешенный Волзер", "url": "https://ltdfoto.ru/images/2025/05/19/BEZ-NAZVANIY550_20250519121616.png"},
        {"id": "WHI","name": "Ало,Это Майор Черновозяев.", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY142_20251022234600.png"},
        {"id": "WPI","name": "Пиксельный Волзер.", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY151_20251026054920.png"},
        {"id": "WNN","name": "Босс русской мафии Волзер", "url": "https://i.ibb.co/CKxGDfWR/171-20251101022647.png"},
        {"id": "WMN","name": "Конструктивный Волзер", "url": "https://s2.radikal.cloud/2025/12/16/BEZ-NAZVANIY19_202512162231195fd1667bd1a7983c.png"},
        {"id": "WXJ","name": "Русский Волзер", "url": "https://s2.radikal.cloud/2025/12/16/BEZ-NAZVANIY12_20251216221329dbd1c9f9ca77253d.png"},
        {"id": "W5L", "name": "Канадец Волзер", "url": "https://s1.radikal.cloud/2025/12/16/BEZ-NAZVANIY11_20251216221023398289d9db2fec0d.png"},
        {"id": "WKO","name": "Рядовой Волзер", "url": "https://s1.radikal.cloud/2025/12/16/BEZ-NAZVANIY5_202512162147246b5a9a70014740d6.png"}
    ],
    "эпическая": [
        {"id": "W6V","name": "Волзер Делитеусс", "url": "https://ltdfoto.ru/images/2025/04/04/Deleteys_Walzer.png"},
        {"id": "WNZ","name": "Темный Всадник Волзер", "url": "https://ltdfoto.ru/images/2025/04/04/Pumpkin_Walzer.png"},
        {"id": "WSAX","name": "Волзер с Саксофоном", "url": "https://ltdfoto.ru/images/2025/04/04/Saxophone_Walzer.png"},
        {"id": "WHE","name": "Троллфейс Волзер", "url": "https://ltdfoto.ru/images/2025/05/19/BEZ-NAZVANIY549_20250519115241.png"},
        {"id": "WD","name": "ОМЕГА-ВОЛЗЕР", "url": "https://ltdfoto.ru/images/2025/10/26/photo_2025-10-26_13-00-32.png"},
        {"id": "WDB","name": "Панк Волзер", "url": "https://i.ibb.co/nMQcHwFn/158-20251028224145.png"},
        {"id": "W6Е","name": "Кибер-Волзер", "url": "https://i.ibb.co/zH2HD7fs/165-20251101014612.png"},
        {"id": "WJY","name": "Йолебеели", "url": "https://s3.radikal.cloud/2025/12/16/BEZ-NAZVANIY20_2025121622340420d6b11d0deaab56.png"},
        {"id": "WZB","name": "Сельдзор", "url": "https://s3.radikal.cloud/2025/12/16/BEZ-NAZVANIY17_202512162227024422ff960fea0bfe.png"},
        {"id": "WTM", "name": "Шт'аммзер", "url": "https://s3.radikal.cloud/2025/12/16/BEZ-NAZVANIY6_2025121621520498bcbf5d959c8920.png"}
    ],
    "легендарная": [
        {"id": "WPR","name": "Волзер Прайм", "url": "https://ltdfoto.ru/images/2025/04/04/Prime_WAlzer.png"},
        {"id": "WGH","name": "Волзер Гигачад", "url": "https://ltdfoto.ru/images/2025/04/04/Strong_Walzer.png"},
        {"id": "WBD","name": "Волзер-Птаха", "url": "https://ltdfoto.ru/images/2025/04/04/Walzer_Bird.png"},
        {"id": "WSH","name": "Чумной Волзер", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY143_20251026052541.png"},
        {"id": "WSF","name": "Наваф аль-Волзер", "url": "https://i.ibb.co/Qjk8z1Kj/image.jpg"},
        {"id": "WP4","name": "Хеллоуинский Волзер", "url": "https://i.ibb.co/yBPPfNQ6/162-20251101024441.png"},
        {"id": "WSK", "name": "Бутыкла шапамансого", "url": "https://s3.radikal.cloud/2025/12/16/BEZ-NAZVANIY8fbf69ebc35446965.png"},
        {"id": "WWI", "name": "Walzer Intelligent (WI) ", "url": "https://radika1.link/2025/12/16/BEZ-NAZVANIY7_20251216215712cbb340b8e368f5d7.png"}
    ],
    "донатная": [
        {"id": "WGL","name": "Золотой Волзер", "url": "https://ltdfoto.ru/images/2025/04/13/IMG_0685.jpg"},
        {"id": "W2C","name": "Волзер Волмер и Бигмак", "url": "https://ltdfoto.ru/images/2025/04/13/IMG_0686.jpg"},
        {"id": "W7M","name": "Волзер Богач", "url": "https://ltdfoto.ru/images/2025/04/13/IMG_0687.jpg"},
        {"id": "W9L","name": "Волзер Фурри", "url": "https://i.ibb.co/mCD9mf3b/photo-2025-10-26-13-45-07.jpg"},
        {"id": "WAH","name": "Альфредус", "url": "https://ltdfoto.ru/images/2025/11/13/image_2025-11-13_15-52-37.png"},
        {"id": "WAV","name": "Неизветсный Витраж", "url": "https://s2.radikal.cloud/2025/12/16/BEZ-NAZVANIY4_20251216214333690f69aa07ee314b.png"}
    ],
    "экстра": [
        {"id": "W4L","name": "Египетский Волзер", "url": "https://ltdfoto.ru/images/2025/05/20/BEZ-NAZVANIY554_20250520172201.png"},
        {"id": "WNW","name": "Волзер с аккордеоном", "url": "https://ltdfoto.ru/images/2025/05/20/BEZ-NAZVANIY555_20250520172439.png"},
        {"id": "WB5","name": "Волзер с бас-гитарой", "url": "https://ltdfoto.ru/images/2025/05/20/BEZ-NAZVANIY556_20250520172709.png"},
        {"id": "WH7","name": "нет", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY147_20251026053502.png"},
        {"id": "WH8","name": "Волзер фрик семьи", "url": "https://i.ibb.co/TMQkB3C3/159-20251028224254.png"},
        {"id": "WBW7","name": "Красавец", "url": "https://ltdfoto.ru/images/2025/11/13/image92baaae8cc63730e.png"},
        {"id": "WM7","name": "im fine", "url": "https://radika1.link/2025/12/16/photo_2025-12-16_20-42-02961939e2dbfe7204.jpg"},
        {"id": "WK3","name": "Колядующий Волзер", "url": "https://radika1.link/2025/12/16/BEZ-NAZVANIY14_2025121622193016721d847224d86b.png"}
    ],
    "боссы": [
        {"id": "WGF","name": "ЭТО ЧТО ВООБЩЕ НАХУЙ", "url": "https://ltdfoto.ru/images/2025/05/19/BEZ-NAZVANIY552_20250519192945.png"},
        {"id": "WGA","name": "УЛЬТРА ГИГАЧАД ВОЛЗЕР", "url": "https://ltdfoto.ru/images/2025/05/19/BEZ-NAZVANIY551_20250519192317.png"},
        {"id": "WEND","name": "конец света.", "url": "https://ltdfoto.ru/images/2025/10/26/BEZ-NAZVANIY145_20251026053312.png"},
        {"id": "WKG","name": "Волзер Король", "url": "https://i.ibb.co/LD1nd7Hn/IMG-20251028-214949-897.png"},
        {"id": "WPG","name": "Diktator-Führer-Walzer", "url": "https://i.ibb.co/Kj7hQW6Z/173-20251101023524.png"},
        {"id": "WDS", "name": "Дед Склероз", "url": "https://radika1.link/2025/12/16/BEZ-NAZVANIY13_202512162216480f1ad211d9fbd2aa.png"},
        {"id": "IHS", "name": "Волзурочка", "url": "https://s3.radikal.cloud/2025/12/16/BEZ-NAZVANIY10_20251216220741e8a2e4d9eb8999d9.png"}
    ],
    "особенные": [
        {"id": "PAPWAL", "name": "Бумажный Воллер", "url": "https://i.ibb.co/sp6ThPPC/image.jpg"},
        {"id": "ROBMAX", "name": "Робеспьер Максимилиан)", "url": "https://i.ibb.co/NnStT1M9/image.png"},
        {"id": "MAAW", "name": "Мутант-аномалия арабский Волзер", "url": "https://i.ibb.co/B53chGrR/image.jpg"},
        {"id": "WBR", "name": "МОЗГИИИИИ!И1И1ИИ!И!№№№№", "url": "https://i.ibb.co/VYgRfDsz/168-20251101015753.png"}
    ],
    "погодные": [
        {"id": "WBS", "name": "Птице-паукоподобие", "url": "https://ltdfoto.ru/images/2025/11/12/photo_2025-11-12_17-08-20.jpg"},
        {"id": "WPPFS", "name": "рыцарь-пихтоващик-футболист-сантехник", "url": "https://ltdfoto.ru/images/2025/11/12/photo_1_2025-11-12_17-05-21.jpg"},
        {"id": "WAN", "name": "аномалия", "url": "https://ltdfoto.ru/images/2025/11/12/photo_2_2025-11-12_17-05-21.jpg"},
        {"id": "WDAN", "name": "дикий волзер", "url": "https://ltdfoto.ru/images/2025/11/12/photo_3_2025-11-12_17-05-21.jpg"},
        {"id": "WSTN", "name": "Волзерштейн", "url": "https://ltdfoto.ru/images/2025/11/13/photo_2025-11-13_16-46-40.jpg"},
        {"id": "WFT32", "name": "Санта-Клаус", "url": "https://ltdfoto.ru/images/2025/11/13/image5c1f9725bb7a49ba.png"},
        {"id": "WCODE", "name": "строки кода", "url": "https://ltdfoto.ru/images/2025/11/14/image37da5aeb9a0ba474.png"},
        {"id": "WWHAT", "name": "╔╦╩╠▒▓█▌▐░♪♫☼☻♥♦♣♠∞≈≠≤≥±÷×¤¦¦₧₯₮₱₲₴₵ℵℶℷ⌂⌐╬╫╪╨╥╤╢╖╓╙╘╛ФЖЩЮЯѦҨҪӜӁӇӉ҂҈҉ҌҍҎҏђѓѣѤѥѦѧѨѩѪѫѬѭѮѯѰѱѲѳѴѵѶѷѸѹѺѻѼѽѾѿҀҁ҂҃҄҅☀☁☂☃☄★☆☇☈☉☊☋☌☍☠☢☣☤☥☦☧♔♕♖♗♘♙♚♛♜♝♞♟♠♣♥♦⚀⚁⚂⚃⚄⚅☯☮☭✈✉✌✍✎✏✐✑✒✓✔✕✖✗✘┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╝╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬ȺȻȼȽȾɁɂɃɄɅɆɇɈɉɊɋɌɍɎɏɐɑɒɓɔɕɖɗɘəɚɛɜɝɞɟɠɡɢɣɤɥɦɧɨɩɪ", "url": "https://ltdfoto.ru/images/2025/11/13/image87862b04abab72ec.png"}
    ],
    "элементали": [
        {"id": "EL_CLOCK", "name": "Классический Волзер", "url": "https://placeholder.com/clock.png"},
        {"id": "EL_SNOW", "name": "Снежный Волзер", "url": "https://placeholder.com/snow.png"},
        {"id": "EL_TOY", "name": "Играшка", "url": "https://placeholder.com/toy.png"},
        {"id": "EL_VITRUVIUS", "name": "Витрувианский Волзер", "url": "https://placeholder.com/vitruvius.png"},
        {"id": "EL_HERB", "name": "Расцветший гербарий", "url": "https://placeholder.com/herb.png"},
        {"id": "EL_LATE", "name": "Запоздалыйтень", "url": "https://placeholder.com/late.png"},
        {"id": "EL_WALTER", "name": "Уолтер", "url": "https://placeholder.com/walter.png"},
        {"id": "EL_AUTUMN", "name": "Пиздаж Осени", "url": "https://placeholder.com/autumn.png"},
    ]
}

# Базовые шансы (сумма должна быть ~100)
RARITY_CHANCES = {
    "боссы": 0.5,
    "экстра": 2.0,
    "легендарная": 5.0,
    "эпическая": 10.0,
    "редкая": 15.0,
    "необычная": 30.0,
    "обычная": 37.5
}

CARD_REWARDS = {
    "боссы": 30,
    "экстра": 20,
    "легендарная": 7,
    "эпическая": 5,
    "редкая": 4,
    "необычная": 3,
    "обычная": 2,
    "погодные": 10,
    "элементали": 15
}

CARD_PRICES = {
    "обычная": 5,
    "необычная": 10,
    "редкая": 25,
    "эпическая": 45,
    "легендарная": 80,
    "экстра": 130,
    "боссы": 200,
    "донатная": 630
}

WEATHER_SYSTEM = {
    "ясная луна": {"emoji": "🌕", "duration": 4, "card_chance": 2.0},
    "грибная слякоть со снегом": {"emoji": "🍄❄️", "duration": 3, "card_chance": 3.0},
    "буря со мглой покрывающая небо": {"emoji": "🌪️🌫️", "duration": 3, "card_chance": 4.0},
    "торнадо небес": {"emoji": "🌪️", "duration": 2, "card_chance": 8.0},
    "мозговой штурм": {"emoji": "🧠⚡", "duration": 2, "card_chance": 9.0},
    "метеоритный дождь": {"emoji": "☄️", "duration": 2, "card_chance": 12.0},
    "Цунами из-поднутри": {"emoji": "🌊⬇️", "duration": 1, "card_chance": 16.0},
    "Ано-р-мальный туман": {"emoji": "🌫️❓", "duration": 1, "card_chance": 19.0},
    "Затмение Марса": {"emoji": "🔴🌑", "duration": 1, "card_chance": 27.0}
}

# ====================== ЭЛЕМЕНТАРИИ: ГЛОБАЛЬНЫЕ ДАННЫЕ ======================
ELEMENTALS = {
    "EL_CLOCK":     {"name": "Классический Волзер",     "emoji": "🕰", "elements": 1, "url": "https://ibb.co/r2TtzQLb"},
    "EL_SNOW":      {"name": "Снежный Волзер",          "emoji": "❄️", "elements": 1, "url": "https://ibb.co/1Yh4ysgf"},
    "EL_TOY":       {"name": "Играшка",                 "emoji": "🧦", "elements": 1, "url": "https://ibb.co/Kj8XzHFp"},
    "EL_VITRUVIUS": {"name": "Витрувианский Волзер",    "emoji": "📑", "elements": 1, "url": "https://ibb.co/HLHg33kY"},
    "EL_HERB":      {"name": "Расцветший гербарий",     "emoji": "🌱", "elements": 1, "url": "https://ibb.co/S71Z8R3y"},
    
    "EL_LATE":      {"name": "Запоздалыйтень",          "emoji": "🕰❄️", "elements": 1, "url": "https://ibb.co/Y7gqcdtj"},
    "EL_WALTER":    {"name": "Уолтер",                  "emoji": "🕰🧦",  "elements": 1, "url": "https://ibb.co/7dRG1g2B"},
    "EL_AUTUMN":    {"name": "Пиздаж Осени",            "emoji": "📑🌱",  "elements": 1, "url": "https://ibb.co/fzR46GFh"},
}

ELEMENTAL_ID_MAP = {k: v for k, v in ELEMENTALS.items()}

def normalize_elemental_id(elemental_id):
    """Преобразует короткий ID элементаля в полный"""
    short_to_full = {
        "EL": "EL_CLOCK",
        "SNOW": "EL_SNOW",
        "TOY": "EL_TOY",
        "VITRUVIUS": "EL_VITRUVIUS",
        "HERB": "EL_HERB",
        "LATE": "EL_LATE",
        "WALTER": "EL_WALTER",
        "AUTUMN": "EL_AUTUMN"
    }
    
    if elemental_id in short_to_full:
        return short_to_full[elemental_id]
    elif elemental_id in ELEMENTAL_ID_MAP:
        return elemental_id
    else:
        return elemental_id
        
        
ELEMENTAL_WISH_COST = 127

# Константы для элементалей
ELEMENTAL_PRICES = {
    1: 50,    # цена за элементаля с 1 элементом
    2: 100    # цена за элементаля с 2 элементами
}

SYNTHESIS_RECIPES = {
    ('EL_CLOCK', 'EL_SNOW'): ['EL_LATE'],
    ('EL_CLOCK', 'EL_TOY'): ['EL_WALTER'],
    ('EL_VITRUVIUS', 'EL_HERB'): ['EL_AUTUMN'],
}

# ================== LANGUAGES ==================
LANGUAGES = ['ru', 'en']

# Словарь переводов для карт
CARD_TRANSLATIONS = {
    'en': {
        # Обычные
        'Безумный Волзер': 'Crazy Walzer',
        'Волзер Огузок': 'Walzer chickn-butt',
        'Волзер-Пират': 'Pirate Walzer',
        'Волзер в пуховике': 'Walzer in Puffer Jacket',
        'Шакальный Волзер': 'Walzer recorded on a toaster',
        'Волзер Волзер': 'Walzer Walzer',
        'ээ.. что?': 'uh.. what?',
        'Волзер, который шел на програмиста': 'Walzer Who Went to Programmer',
        '®': '®',
        'ХП=КХАХЗХРАДХРЗДАЗХРЗХРЗХЩРЗП': 'HHAHAAHAHAHAHAHAHAAH',
        'Тайип Эрдозер': 'Tayyip Erdozer',
        'SNOWser': 'SNEJser',
        
        # Необычные
        'Горничная Волзер': 'Maid Walzer',
        'Волзер-Лягушонок': 'KermAfrog Walzer',
        'СУПЕР СИГМА ВОЛЗЕР!!': 'SUPER SIGMA WALZER!!',
        'Волзер-Стейк': 'Walzer the Steak',
        'Пиксельный Волзер Маг': 'Pixel Walzer Mage',
        'Шут': 'Jester',
        'Волзер из Китая': 'Walzer from China',
        'Гитарист Волзер': 'Guitarist Walzer',
        'Бородатый Волзер': 'Bearded Walzer',
        'как. ': 'how. ',
        'Большояйцевый Волзер': 'BigEgg Walzer',
        'Suomalainen tarkka-ampuja Walzer': 'Suomalainen tarkka-ampuja Walzer',
        
        # Редкие
        'Робо-Волзер': 'Robo-Walzer',
        'Волзер-Скуф': 'Walzer oldmaN',
        'Повешенный Волзер': 'Hanged Walzer',
        'Ало,Это Майор Черновозяев.': 'Hello, This is Major-Genelar.',
        'Пиксельный Волзер.': 'Pixeld Walzer.',
        'Босс русской мафии Волзер': 'Russian Mafia Boss Walzer',
        'Конструктивный Волзер': 'Constructive Walzer',
        'Русский Волзер': 'Russian Walzer',
        'Канадец Волзер': 'Canadian Walzer',
        'Рядовой Волзер': 'soldier Walzer',
        
        # Эпические
        'Волзер Делитеусс': 'Walzer Deleteusz',
        'Темный Всадник Волзер': 'DarkHorseman Walzer',
        'Волзер с Саксофоном': 'Walzer with Saxophone',
        'Троллфейс Волзер': 'Trollface Walzer',
        'ОМЕГА-ВОЛЗЕР': 'OMEGA-WALZER',
        'Панк Волзер': 'Punk Walzer',
        'Кибер-Волзер': 'Cyber Walzer',
        'Йолебеели': 'Yolebeeli',
        'Сельдзор': 'Seldzor',
        'Шт\'аммзер': 'St\'ammzer',
        
        # Легендарные
        'Волзер Прайм': 'Walzer Prime',
        'Волзер Гигачад': 'Walzer Gigachad',
        'Волзер-Птаха': 'Walzer Birdie',
        'Чумной Волзер': 'Plagui Walzer',
        'Наваф аль-Волзер': 'Nawaf al-Walzer',
        'Хеллоуинский Волзер': 'Halloween Walzer',
        'Бутыкла шапамансого': 'Shapamansogo Bottle',
        'Walzer Intelligent (WI) ': 'Walzer Intelligent (WI)',
        
        # Донатные
        'Золотой Волзер': 'Golden Walzer',
        'Волзер Волмер и Бигмак': 'Walzer Volmer and Big Mac',
        'Волзер Богач': 'Rich Walzer',
        'Волзер Фурри': 'Furry Walzer',
        'Альфредус': 'Alfredus',
        'Неизветсный Витраж': 'Unknown Stained-Glass',
        
        # Экстра
        'Египетский Волзер': 'Egyptian Walzer',
        'Волзер с аккордеоном': 'Walzer with Accordion',
        'Волзер с бас-гитарой': 'Walzer with Bass Guitar',
        'нет': 'no',
        'Волзер фрик семьи': 'Family-Freak Walzer',
        'Красавец': 'Handsome',
        'im fine': 'im fine',
        'Колядующий Волзер': 'Caroling Walzer',
        
        # Боссы
        'ЭТО ЧТО ВООБЩЕ НАХУЙ': 'WHAT THE FUCK IS THIS',
        'УЛЬТРА ГИГАЧАД ВОЛЗЕР': 'ULTRA GIGACHAD WALZER',
        'конец света.': 'end of the world.',
        'Волзер Король': 'King Walzer',
        'Diktator-Führer-Walzer': 'Diktator-Führer-Walzer',
        'Дед Склероз': 'Jolly Old Sclerosis',
        'Волзурочка': ' Walzurochka',
        
        # Особенные
        'Бумажный Воллер': 'Paper Waller',
        'Робеспьер Максимилиан)': 'Robespierre Maximilian)',
        'Мутант-аномалия арабский Волзер': 'Mutant-anomaly Arabian Walzer',
        'МОЗГИИИИИ!И1И1ИИ!И!№№№№': 'BRAAAAAINS!',
        
        # Погодные
        'Птице-паукоподобие': 'Bird-spider-like',
        'рыцарь-пихтоващик-футболист-сантехник': 'knight-lumberjack-footballer-plumber',
        'аномалия': 'anomaly',
        'дикий волзер': 'wild walzer',
        'Волзерштейн': 'Walzerstein',
        'Санта-Клаус': 'Santa Claus',
        'строки кода': 'lines of code',
        '╔╦╩╠▒▓█▌▐░♪♫☼☻♥♦♣♠∞≈≠≤≥±÷×¤¦¦₧₯₮₱₲₴₵ℵℶℷ⌂⌐╬╫╪╨╥╤╢╖╓╙╘╛ФЖЩЮЯѦҨҪӜӁӇӉ҂҈҉ҌҍҎҏђѓѣѤѥѦѧѨѩѪѫѬѭѮѯѰѱѲѳѴѵѶѷѸѹѺѻѼѽѾѿҀҁ҂҃҄҅☀☁☂☃☄★☆☇☈☉☊☋☌☍☠☢☣☤☥☦☧♔♕♖♗♘♙♚♛♜♝♞♟♠♣♥♦⚀⚁⚂⚃⚄⚅☯☮☭✈✉✌✍✎✏✐✑✒✓✔✕✖✗✘┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╝╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬ȺȻȼȽȾɁɂɃɄɅɆɇɈɉɊɋɌɍɎɏɐɑɒɓɔɕɖɗɘəɚɛɜɝɞɟɠɡɢɣɤɥɦɧɨɩɪ': '╔╦╩╠▒▓█▌▐░♪♫☼☻♥♦♣♠∞≈≠≤≥±÷×¤¦¦₧₯₮₱₲₴₵ℵℶℷ⌂⌐╬╫╪╨╥╤╢╖╓╙╘╛ФЖЩЮЯѦҨҪӜӁӇӉ҂҈҉ҌҍҎҏђѓѣѤѥѦѧѨѩѪѫѬѭѮѯѰѱѲѳѴѵѶѷѸѹѺѻѼѽѾѿҀҁ҂҃҄҅☀☁☂☃☄★☆☇☈☉☊☋☌☍☠☢☣☤☥☦☧♔♕♖♗♘♙♚♛♜♝♞♟♠♣♥♦⚀⚁⚂⚃⚄⚅☯☮☭✈✉✌✍✎✏✐✑✒✓✔✕✖✗✘┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╝╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬ȺȻȼȽȾɁɂɃɄɅɆɇɈɉɊɋɌɍɎɏɐɑɒɓɔɕɖɗɘəɚɛɜɝɞɟɠɡɢɣɤɥɦɧɨɩɪ',
        
        # Элементали
        'Классический Волзер': 'Classic Walzer',
        'Снежный Волзер': 'Snow Walzer',
        'Играшка': 'Toiy',
        'Витрувианский Волзер': 'Vitruvian Walzer',
        'Расцветший гербарий': 'Bloomed Herbarium',
        'Запоздалыйтень': 'BelatetShadow',
        'Уолтер': 'Walter',
        'Пиздаж Осени': 'Autumn Fuckery',
    }
}

# Основной словарь переводов
TRANSLATIONS = {
    'ru': {
        # Основное
        'yes': 'Да',
        'no': 'Нет',
        'cancel': 'Отмена',
        'back': 'Назад',
        'loading': '⏳ Загрузка...',
        'error': '❌ Ошибка',
        'success': '✅ Успешно',

        # Баланс
        'balance': '💰 Баланс: {count} {forms}',
        'wc_forms': ('Волзер-Коин', 'Волзер-Коина', 'Волзер-Коинов'),

        # Команды (для меню)
        'cmd_start': 'старт',
        'cmd_getcard': 'получить',
        'cmd_mycards': 'карты',
        'cmd_shop': 'магазин',
        'cmd_buy': 'купить',
        'cmd_sell': 'продать',
        'cmd_price': 'цена',
        'cmd_view': 'посмотреть',
        'cmd_shaman': 'шаман',
        'cmd_solitaire': 'пасьянс',
        'cmd_weather': 'погода',
        'cmd_top': 'топ',
        'cmd_lang': 'язык',
        'cmd_commands': 'команды',

        # Меню
        'menu_getcard': '🎴 Получить карту',
        'menu_mycards': '📇 Мои карты',
        'menu_shop': '🏪 Магазин',
        'menu_commands': '📋 Команды',
        'menu_prepodvalie': '👻 Преподвалье',
        'menu_shaman': '🔮 Шаман',
        'menu_solitaire': '🃏 Пасьянс',
        'menu_weather': '🌤 Погода',
        'menu_top': '🏆 Топ',
        'menu_lang': '🌐 Язык',

        # Редкости (отображаемые)
        'rarity_common': 'обычная',
        'rarity_uncommon': 'необычная',
        'rarity_rare': 'редкая',
        'rarity_epic': 'эпическая',
        'rarity_legendary': 'легендарная',
        'rarity_donor': 'донатная',
        'rarity_extra': 'экстра',
        'rarity_boss': 'боссы',
        'rarity_weather': 'погодная',
        'rarity_elemental': 'элементаль',

        # Карты
        'new_card': '🎉 НОВАЯ КАРТА!',
        'card_received': 'Ты получил: {name} ({rarity})\n+{reward} WC',
        'card_duplicate': 'Повторка: {name} ({rarity})\n+{reward} WC',
        'no_cards': '😢 У тебя нет карт. Получи первую через /{cmd}!',
        'cards_collection': '📇 Твоя коллекция карт:',
        'cards_total': 'Всего карт: {total}',
        'cards_unique': 'Уникальных: {unique}/{max}',

        # Погода
        'weather_current': '🌤 Текущая погода: **{name}** {emoji}',
        'weather_chance': '📊 Шанс погодной карты: {chance}%',
        'weather_changes_in': '⏱ Сменится через: {hours}ч {minutes}м',
        'weather_description': '📖 {desc}',

        # Шаман
        'shaman_title': '🔮 *ШАМАНСТВО*',
        'shaman_desc': 'Приноси жертвы духам и получай награды!',
        'shaman_victims': '👥 Жертв: {count}',
        'shaman_wish': '✨ Желание: {wish}',
        'shaman_no_wish': 'не выбрано',
        'shaman_select_victims': '🃏 Выбери жертвы:',
        'shaman_select_wish': '🎯 Выбери желание:',
        'shaman_start': '🔥 НАЧАТЬ РИТУАЛ',
        'shaman_cancel': '❌ Отмена',
        'shaman_success': '✨ РИТУАЛ УДАЛСЯ!',
        'shaman_fail': '💀 Провал... Жертвы сгорели зря',
        'shaman_troll': '😈 Шаман тебя наебал! Всё пропало',
        'shaman_cooldown': '⏳ Шаман отдыхает. Осталось: {minutes} мин',
        'shaman_result_card': 'Ты получил: {name}',
        'shaman_result_wc': 'Духи дали {count} WC',
        'shaman_result_elemental': '🌌 Появился элементаль: {name}',

        # Элементали
        'elementals_title': '🌌 ЭЛЕМЕНТАЛИ',
        'elementals_desc': 'Пассивный доход. Чем выше уровень, тем больше WC в час',
        'elementals_count': 'У тебя: {count}/{total}',
        'elementals_rate': 'Доход: +{rate} WC/час',
        'elementals_stored': 'Накоплено: {stored} WC',
        'elementals_collect': '💰 Собрать всё',
        'elementals_collected': 'Собрано {count} WC с элементалей!',
        'elementals_level_up': '⬆️ Уровень повышен до {level}!',
        'elementals_feed': '🍖 Кормить',

        # Пасьянс
        'solitaire_title': '🃏 *ПАСЬЯНС НА ЗИМБАБВИЙСКИЕ ДОЛЛАРЫ*',
        'solitaire_desc': 'Собирай карты и меняй на WC! 100 ZWD = 1 WC',
        'solitaire_score': '💰 Счет: {score} ZWD',
        'solitaire_wc': '💵 Можно получить: {wc} WC',
        'solitaire_draw': '📁 Взять карту',
        'solitaire_waste': '🃏 Отбой',
        'solitaire_new': '🔄 Новая игра',
        'solitaire_cashout': '💵 Забрать WC',
        'solitaire_victory': '🎉 ПОБЕДА! Ты бог пасьянса!',
        'solitaire_no_money': '😢 Нужно хотя бы 100 ZWD для обмена',

        # Магазин
        'shop_title': '🏪 МАГАЗИН КАРТ',
        'shop_buy': 'Купить: /{cmd} <ID> [кол-во]',
        'shop_sell': 'Продать: /{cmd} <ID> [кол-во|all]',
        'shop_price': 'Цена продажи: {price} WC ({half} WC при продаже)',
        'shop_not_enough_wc': '❌ Не хватает WC! Нужно {need}, у тебя {have}',
        'shop_not_enough_cards': '❌ У тебя нет столько карт',
        'shop_bought': '✅ Куплено {count} × {name} за {price} WC',
        'shop_sold': '💰 Продано {count} × {name} за {price} WC',
        'shop_cannot_sell': '❌ Эту карту нельзя продать!',

        # Топ
        'top_title': '🏆 *ТОП ИГРОКОВ*',
        'top_wc': '💰 По Волзер-Коинам',
        'top_cards': '🎴 По количеству карт',
        'top_unique': '🌟 По уникальным картам',

        # Админка
        'admin_only': '🚫 Только для админов',
        'admin_welcome': '🛠 Панель администратора',
        'admin_stats': '📊 Статистика',
        'admin_users': '👤 Пользователи',
        'admin_cards': '🎴 Карты',
        'admin_give': '🎁 Выдача',
        'admin_broadcast': '📢 Рассылка',

        # Стартовое сообщение
        'start_message': """здравствуй, это ВОлзер комбат. самый "Интересный" бот в ТГ.
это меню не испольузеся по нормальному, поэтому юзай /statr.
Гайды - /explanations.
 To change the language, type /lang .""",

        # Команды
        'commands_list': """📋 **ПОЛНЫЙ СПИСОК КОМАНД**

/getcard - /card , /получить , /карта
/mycards - /cards , /коллекция , /карты , /collection , /инвентарь , /inventory
/shop - /магазин , /store
/buy - /купить , /purchase
/sell - /продать , /sale
/price - /цена , /стоимость
/view - /посмотреть , /show , /info

/minigames - /игры , /games
/dice - /кубик , /кость , /кости
/casino - /казино , /рулетка

/weather - /погода
/shaman /шаман /шаманить
/next_weather - /следующая_погода , /nextweather
/chance - /шанс , /шансы , /chances

/statr - /старт , /статр

/commands_list - /commands , /команды
/solitaire /solitaire_cmd, /пасьянс , /косынка
/lang - /language , /язык
/give""",

        # Ошибки
        'error_unknown': '❌ Неизвестная ошибка',
        'error_no_card': '❌ Карта не найдена',
        'error_no_user': '❌ Пользователь не найден',
        'error_invalid_amount': '❌ Неверное количество',
        'error_cooldown': '⏳ Подожди {minutes}м {seconds}с',

        # Сленг
        'based': 'БАЗОВАНО',
        'cringe': 'КРИНЖ',
        'pog': 'ПОГЧАМПС',
        'rip': 'RIP',
        'lmao': 'LMAO',
        'kappa': 'Kappa',
        'copium': 'COPIUM',
        'hopium': 'HOPIUM',
        
        'rarity_обычная': 'обычная',
        'rarity_необычная': 'необычная', 
        'rarity_редкая': 'редкая',
        'rarity_эпическая': 'эпическая',
        'rarity_легендарная': 'легендарная',
        'rarity_донатная': 'донатная',
        'rarity_экстра': 'экстра',
        'rarity_боссы': 'боссы',
        'rarity_погодные': 'погодная',
        'rarity_элементали': 'элементаль',
        
        # Преподвалье
        'prepodvalie_welcome': 'Ты спустился в Преподвалье...\nТут темно. Тут воняет. Тут нет Волзеров.\nПиши !хелп — если не боишься.',
        'prepodvalie_back': 'Ты выбрался!\nСвет... Волзеры... WC...\nДобро пожаловать обратно в матрицу.',
        'prepodvalie_help': 'ПРЕПОДВАЛЬЕ — тут нет Волзеров, тут только хаос\n\n!хелп — это меню\n!скажи <текст> — я скажу это голосом\n!инфобот — кому это надо\n!переведи <язык> <текст> — переводчик из каменного века\n!юзер — инфа о тебе или о том, на кого ответишь\n!qrcode <текст> — QR-код из твоего бреда\n!преподвалье — спуститься сюда\n!комбат — выбраться к свету и Волзерам\n\nТут нет смысла. Только свобода.',
        'give_no_reply': '❌ Ошибка: Используй эту команду ОТВЕТОМ на сообщение игрока.',
        'give_no_args': '📝 Укажи название карты. Пример: `/give Безумный Волзер`',
        'give_self': '🤔 Ты не можешь подарить карту самому себе.',
        'give_not_found': "❓ Карта '{name}' не найдена.",
        'give_no_card': '🚫 У тебя нет карты «{name}».',
        'give_success': '🎁 Ты успешно передал карту «**{name}**» игроку {target}!',
    },

    'en': {
        # Basic
        'yes': 'Yes',
        'no': 'No',
        'cancel': 'Cancel',
        'back': 'Back',
        'loading': '⏳ Loading...',
        'error': '❌ Error',
        'success': '✅ Success',

        # Balance
        'balance': '💰 Balance: {count} {forms}',
        'wc_forms': ('Walzer-Coin', 'Walzer-Coins', 'Walzer-Coins'),

        # Commands
        'cmd_start': 'start',
        'cmd_getcard': 'card',
        'cmd_mycards': 'collection',
        'cmd_shop': 'shop',
        'cmd_buy': 'buy',
        'cmd_sell': 'sell',
        'cmd_price': 'price',
        'cmd_view': 'view',
        'cmd_shaman': 'shaman',
        'cmd_solitaire': 'solitaire',
        'cmd_weather': 'weather',
        'cmd_top': 'top',
        'cmd_lang': 'language',
        'cmd_commands': 'commands',

        # Menu
        'menu_getcard': '🎴 Get Card',
        'menu_mycards': '📇 My Cards',
        'menu_shop': '🏪 Shop',
        'menu_commands': '📋 Commands',
        'menu_prepodvalie': '👻 Basement',
        'menu_shaman': '🔮 Shaman',
        'menu_solitaire': '🃏 Solitaire',
        'menu_weather': '🌤 Weather',
        'menu_top': '🏆 Top',
        'menu_lang': '🌐 Language',

        # Rarities
        'rarity_common': 'Common',
        'rarity_uncommon': 'Uncommon',
        'rarity_rare': 'Rare',
        'rarity_epic': 'Epic',
        'rarity_legendary': 'Legendary',
        'rarity_donor': 'Donor',
        'rarity_extra': 'Extra',
        'rarity_boss': 'Boss',
        'rarity_weather': 'Weather',
        'rarity_elemental': 'Elemental',

        # Cards
        'new_card': '🎉 NEW CARD!',
        'card_received': 'You got: {name} ({rarity})\n+{reward} WC',
        'card_duplicate': 'Duplicate: {name} ({rarity})\n+{reward} WC',
        'no_cards': '😢 You have no cards. Get your first with /{cmd}!',
        'cards_collection': '📇 Your card collection:',
        'cards_total': 'Total cards: {total}',
        'cards_unique': 'Unique: {unique}/{max}',

        # Weather
        'weather_current': '🌤 Current weather: **{name}** {emoji}',
        'weather_chance': '📊 Weather card chance: {chance}%',
        'weather_changes_in': '⏱ Changes in: {hours}h {minutes}m',
        'weather_description': '📖 {desc}',

        # Shaman
        'shaman_title': '🔮 *SHAMANISM*',
        'shaman_desc': 'Sacrifice cards to the spirits and get rewards!',
        'shaman_victims': '👥 Victims: {count}',
        'shaman_wish': '✨ Wish: {wish}',
        'shaman_no_wish': 'not selected',
        'shaman_select_victims': '🃏 Choose victims:',
        'shaman_select_wish': '🎯 Choose your wish:',
        'shaman_start': '🔥 START RITUAL',
        'shaman_cancel': '❌ Cancel',
        'shaman_success': '✨ RITUAL SUCCESSFUL!',
        'shaman_fail': '💀 Failed... Victims burned for nothing',
        'shaman_troll': '😈 Shaman trolled you! Everything is lost',
        'shaman_cooldown': '⏳ Shaman is resting. Left: {minutes} min',
        'shaman_result_card': 'You got: {name}',
        'shaman_result_wc': 'Spirits gave {count} WC',
        'shaman_result_elemental': '🌌 Elemental appeared: {name}',

        # Elementals
        'elementals_title': '🌌 ELEMENTALS',
        'elementals_desc': 'Passive income. Higher level = more WC per hour',
        'elementals_count': 'You have: {count}/{total}',
        'elementals_rate': 'Income: +{rate} WC/hour',
        'elementals_stored': 'Stored: {stored} WC',
        'elementals_collect': '💰 Collect all',
        'elementals_collected': 'Collected {count} WC from elementals!',
        'elementals_level_up': '⬆️ Level up to {level}!',
        'elementals_feed': '🍖 Feed',

        # Solitaire
        'solitaire_title': '🃏 *ZIMBABWEAN DOLLAR SOLITAIRE*',
        'solitaire_desc': 'Collect cards and exchange for WC! 100 ZWD = 1 WC',
        'solitaire_score': '💰 Score: {score} ZWD',
        'solitaire_wc': '💵 Can cash out: {wc} WC',
        'solitaire_draw': '📁 Draw',
        'solitaire_waste': '🃏 Waste',
        'solitaire_new': '🔄 New Game',
        'solitaire_cashout': '💵 Cash Out',
        'solitaire_victory': '🎉 VICTORY! You\'re the solitaire god!',
        'solitaire_no_money': '😢 Need at least 100 ZWD to cash out',

        # Shop
        'shop_title': '🏪 CARD SHOP',
        'shop_buy': 'Buy: /{cmd} <ID> [amount]',
        'shop_sell': 'Sell: /{cmd} <ID> [amount|all]',
        'shop_price': 'Price: {price} WC ({half} WC when selling)',
        'shop_not_enough_wc': '❌ Not enough WC! Need {need}, you have {have}',
        'shop_not_enough_cards': '❌ You don\'t have that many cards',
        'shop_bought': '✅ Bought {count} × {name} for {price} WC',
        'shop_sold': '💰 Sold {count} × {name} for {price} WC',
        'shop_cannot_sell': '❌ This card cannot be sold!',

        # Top
        'top_title': '🏆 *PLAYER TOP*',
        'top_wc': '💰 By Walzer-Coins',
        'top_cards': '🎴 By card count',
        'top_unique': '🌟 By unique cards',

        # Admin
        'admin_only': '🚫 Admins only',
        'admin_welcome': '🛠 Admin Panel',
        'admin_stats': '📊 Statistics',
        'admin_users': '👤 Users',
        'admin_cards': '🎴 Cards',
        'admin_give': '🎁 Give',
        'admin_broadcast': '📢 Broadcast',
        
        'rarity_обычная': 'Common',
        'rarity_необычная': 'Uncommon',
        'rarity_редкая': 'Rare',
        'rarity_эпическая': 'Epic',
        'rarity_легендарная': 'Legendary',
        'rarity_донатная': 'Donat',
        'rarity_экстра': 'Extra',
        'rarity_боссы': 'Boss',
        'rarity_погодные': 'Weather',
            'rarity_элементали': 'Elemental',

        # Start message
        'start_message': """hello, this is Walzer combat. the most "Interesting" bot in TG.
this menu is not used normally, so use /statr.
Guides - /explanations.
чтобы сменить язык, напишите /lang""",

        # Commands list
        'commands_list': """📋 **FULL COMMANDS LIST**

/getcard - /card , /get
/mycards - /cards , /collection , /inventory
/shop - /store
/buy - /purchase
/sell - /sale
/price - /cost
/view - /show , /info

/minigames - /games
/dice
/casino

/weather
/shaman
/next_weather
/chance - /chances

/statr - /start

/commands_list - /commands
/solitaire
/lang - /language

/give""",

        # Errors
        'error_unknown': '❌ Unknown error',
        'error_no_card': '❌ Card not found',
        'error_no_user': '❌ User not found',
        'error_invalid_amount': '❌ Invalid amount',
        'error_cooldown': '⏳ Wait {minutes}m {seconds}s',

        # Slang (keep Russian vibe or translate with memes)
        'based': 'BASED',
        'cringe': 'CRINGE',
        'pog': 'POGGERS',
        'rip': 'RIP',
        'lmao': 'LMAO',
        'kappa': 'Kappa',
        'copium': 'COPIUM',
        'hopium': 'HOPIUM',
        
        # Prepodvalie
        'prepodvalie_welcome': 'You descended into the UNBasement...\nIt\'s dark. It stinks. There are no Walzers.\nType !help — if you\'re not afraid.',
        'prepodvalie_back': 'You got out!\nLight... Walzers... WC...\nWelcome back to the matrix.',
        'prepodvalie_help': 'UNBASEMENT — no Walzers here, only chaos\n\n!help — this menu\n!say <text> — I\'ll say it with voice\n!infobot — who needs this\n!translate <lang> <text> — stone age translator\n!user — info about you or replied user\n!qrcode <text> — QR code from your nonsense\n!basement — come here\n!combat — get back to light and Walzers\n\nThere\'s no meaning here. Only freedom.',
        'give_no_reply': '❌ Error: Use this command as a REPLY to someone\'s message.',
        'give_no_args': '📝 Specify the card name. Example: `/give Mad Walzer`',
        'give_self': '🤔 You cannot give a card to yourself.',
        'give_not_found': "❓ Card '{name}' not found.",
        'give_no_card': '🚫 You don\'t have the card "{name}".',
        'give_success': '🎁 You successfully gave the card "**{name}**" to {target}!',
    }
}

# ============ ФУНКЦИИ ДЛЯ ПЕРЕВОДА ============
def translate_card_name(name, lang='en'):
    """Переводит название карты на указанный язык"""
    if lang == 'ru':
        return name
    return CARD_TRANSLATIONS.get(lang, {}).get(name, name)

def get_translated_cards(lang='ru'):
    """Возвращает карты с переведенными названиями"""
    if lang == 'ru':
        return CARDS
    
    translated_cards = {}
    for rarity, card_list in CARDS.items():
        translated_cards[rarity] = []
        for card in card_list:
            translated_card = card.copy()
            translated_card['name'] = translate_card_name(card['name'], lang)
            translated_cards[rarity].append(translated_card)
    
    return translated_cards

def update_card_id_map_with_translation(lang='ru'):
    """Обновляет CARD_ID_MAP с переведенными названиями"""
    translated_cards = get_translated_cards(lang)
    
    for rarity, card_list in translated_cards.items():
        for card in card_list:
            card_id = card["id"]
            if card_id in CARD_ID_MAP:
                CARD_ID_MAP[card_id]["name"] = card["name"]
    
    return CARD_ID_MAP

# Класс для управления языком пользователя
class LanguageManager:
    def __init__(self):
        self.user_languages = {}  # {user_id: lang}
    
    def get_user_lang(self, user_id):
        """Получает язык пользователя"""
        return self.user_languages.get(str(user_id), 'ru')
    
    def set_user_lang(self, user_id, lang):
        """Устанавливает язык пользователя"""
        if lang in LANGUAGES:
            self.user_languages[str(user_id)] = lang
            return True
        return False
    
    def t(self, user_id, key, **kwargs):
        """Переводит ключ на язык пользователя"""
        lang = self.get_user_lang(user_id)
        translation = TRANSLATIONS[lang].get(key, TRANSLATIONS['ru'].get(key, key))
        
        # Форматирование с плюрализацией
        if isinstance(translation, tuple):
            if 'count' in kwargs:
                count = kwargs['count']
                form = pluralize(count, translation)
                translation = form
            else:
                translation = translation[0]
        
        # Подстановка переменных
        if kwargs:
            try:
                return translation.format(**kwargs)
            except:
                return translation
        
        return translation

# Создаем глобальный экземпляр менеджера языков
lang_manager = LanguageManager()

# Декоратор для добавления перевода в функции команд
def with_translation(func):
    """Декоратор для добавления t функции в context"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Добавляем t функцию в context
        context.t = lambda key, **kwargs: lang_manager.t(user_id, key, **kwargs)
        
        # Если язык английский, обновляем карты
        if lang_manager.get_user_lang(user_id) == 'en':
            update_card_id_map_with_translation('en')
        
        return await func(update, context, *args, **kwargs)
    return wrapper

# ============ Инициализация системы карт ============
CARD_ID_MAP = {}
RARITY_TO_IDS = {}

def initialize_card_system():
    """Инициализирует систему карт с фиксированными ID"""
    global CARD_ID_MAP, RARITY_TO_IDS
    
    CARD_ID_MAP.clear()
    RARITY_TO_IDS.clear()
    
    for rarity, card_list in CARDS.items():
        RARITY_TO_IDS[rarity] = []
        for card in card_list:
            card_id = card["id"]
            CARD_ID_MAP[card_id] = {
                "id": card_id,
                "name": card["name"],
                "url": card.get("url"),
                "rarity": rarity,
                "price": CARD_PRICES.get(rarity, 0)
            }
            RARITY_TO_IDS[rarity].append(card_id)
    
    logger.info(f"Инициализирована система карт: {len(CARD_ID_MAP)} карт, {len(RARITY_TO_IDS)} категорий")

initialize_card_system()

# ============ Данные (файл) ============


def update_user_data(user, data):
    """Обновляет имя и юзернейм пользователя в базе данных"""
    # Если load_data вернула None, превращаем в словарь, чтобы не было ошибки
    if data is None:
        data = {}
        
    u_id = str(user.id)
    if u_id not in data:
        # Создаем стандартный профиль для нового игрока
        data[u_id] = {
            "balance": 100, 
            "cards": {},
            "lang": "ru",
            "last_card_time": None
        }
    
    # Обновляем или добавляем поля имени и юзернейма
    # Если юзернейма нет, запишем None
    data[u_id]["username"] = f"@{user.username}" if user.username else None
    data[u_id]["first_name"] = user.first_name
    
    return data
    
    
data = {}

def load_data():
    """Загрузка данных с логированием"""
    global data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "users" not in data:
                data = {"users": data if isinstance(data, dict) else {}}
            
        if "pvp_queue" not in data:
            data["pvp_queue"] = []
        if "pvp_battles" not in data:
            data["pvp_battles"] = {}
            
        logger.info("Данные успешно загружены")
    except FileNotFoundError:
        logger.warning("Файл данных не найден, создается новый")
        data = {"users": {}, "pvp_queue": [], "pvp_battles": {}}
        save_data()
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        data = {"users": {}, "pvp_queue": [], "pvp_battles": {}}
        save_data()
    except Exception as e:
        logger.error(f"Неизвестная ошибка при загрузке данных: {e}")
        data = {"users": {}, "pvp_queue": [], "pvp_battles": {}}
        save_data()

def save_data():
    """Сохранение данных с логированием"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug("Данные успешно сохранены")
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")

def get_user(uid):
    """Получение пользователя с логированием"""
    uid = str(uid)
    if "users" not in data:
        data["users"] = {}
    if uid not in data["users"]:
        data["users"][uid] = {
            "cards": {},
            "wc": 0,
            "last_card_time": "2000-01-01T00:00:00",
            "chance_bonus": {"экстра": 0.0, "боссы": 0.0},
            "card_counter": 0,
            "banned_cards": {},
            "elementals": {},
            "active_craft": None
        }
        save_data()
        logger.info(f"Создан новый пользователь: {uid}")
    return data["users"][uid]

def pluralize(number, forms):
    number = abs(int(number))
    if number % 10 == 1 and number % 100 != 11:
        return forms[0]
    if 2 <= number % 10 <= 4 and not (12 <= number % 100 <= 14):
        return forms[1]
    return forms[2]

def main_menu():
    keyboard = [
        [KeyboardButton("/statr")], 
        [KeyboardButton("/getcard"), KeyboardButton("/mycards")],
        [KeyboardButton("/commands"), KeyboardButton("!преподвалье")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def notify_user(bot, user_id, message):
    """Отправляет уведомление пользователю"""
    try:
        await bot.send_message(chat_id=user_id, text=message)
        return True
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        return False 

def choose_card(user):
    """Выбор карты с учетом погодных условий"""
    try:
        uid = str([k for k, v in data["users"].items() if v == user][0]) if user in data["users"].values() else None
        
        user["card_counter"] = user.get("card_counter", 0) + 1
        logger.info(f"=== ВЫБОР КАРТЫ ДЛЯ {uid} ===")
        logger.info(f"Счетчик: {user['card_counter']}")

        current_weather = get_current_weather()
        weather_info = WEATHER_SYSTEM[current_weather]
        weather_chance = weather_info["card_chance"]
        weather_roll = random.random() * 100
        logger.info(f"Погода: {current_weather}, шанс погодной: {weather_chance}%, ролл: {weather_roll:.2f}")
        
        if weather_roll <= weather_chance:
            weather_cards = CARDS.get("погодные", [])
            if weather_cards:
                weather_card = random.choice(weather_cards)
                card = CARD_ID_MAP[weather_card["id"]].copy()
                card["rarity"] = "погодные"
                logger.info(f"✅ ВЫПАЛА ПОГОДНАЯ КАРТА: {card['name']}")
                return card
            else:
                logger.warning("Нет доступных погодных карт")

        logger.info("=== ЗАПУСК ОБЫЧНОЙ СИСТЕМЫ РЕДКОСТЕЙ ===")
        total_chances = RARITY_CHANCES.copy()
        bonus = user.get("chance_bonus", {"экстра": 0.0, "боссы": 0.0})
        total_chances["экстра"] = total_chances.get("экстра", 0) + bonus.get("экстра", 0.0)
        total_chances["боссы"] = total_chances.get("боссы", 0) + bonus.get("боссы", 0.0)

        logger.info(f"Шансы до нормализации: {total_chances}")
        total_sum = sum(total_chances.values())
        logger.info(f"Общая сумма шансов: {total_sum}")
        
        if total_sum <= 0:
            logger.error("Сумма шансов <= 0, использую резервный выбор")
            available_cards = RARITY_TO_IDS.get("обычная", [])
            if available_cards:
                cid = random.choice(available_cards)
                card = CARD_ID_MAP[cid].copy()
                card["rarity"] = "обычная"
                logger.info(f"🔄 РЕЗЕРВНЫЙ ВЫБОР: {card['name']} (обычная)")
                return card
            else:
                all_cards = list(CARD_ID_MAP.keys())
                cid = random.choice(all_cards)
                card = CARD_ID_MAP[cid].copy()
                logger.info(f"🚨 АВАРИЙНЫЙ ВЫБОР: {card['name']}")
                return card
        
        scale = 100.0 / total_sum
        normalized_chances = {}
        for k, v in total_chances.items():
            normalized_chances[k] = v * scale

        logger.info(f"Нормализованные шансы: {normalized_chances}")
        roll = random.uniform(0, 100)
        cumulative = 0.0
        logger.info(f"Ролл для выбора редкости: {roll:.2f}")
        
        for rarity, chance in normalized_chances.items():                
            cumulative += chance
            logger.info(f"Проверка {rarity}: шанс={chance:.2f}%, кумулятивно={cumulative:.2f}%")
            if roll <= cumulative:
                available_cards = RARITY_TO_IDS.get(rarity, [])
                filtered_cards = []
                for card_id in available_cards:
                    card_rarity = CARD_ID_MAP[card_id]["rarity"]
                    if card_rarity not in ["особенные", "донатная", "элементали"]:
                        filtered_cards.append(card_id)
                
                if filtered_cards:
                    cid = random.choice(filtered_cards)
                    card = CARD_ID_MAP[cid].copy()
                    card["rarity"] = rarity
                    logger.info(f"🎯 ВЫБРАНА КАРТА: {card['name']} ({rarity})")
                    return card
                else:
                    logger.warning(f"Нет доступных карт для редкости: {rarity}")
                    continue

        logger.warning("Ни одна редкость не выбрана, резервный выбор")
        available_cards = RARITY_TO_IDS.get("обычная", [])
        if available_cards:
            cid = random.choice(available_cards)
            card = CARD_ID_MAP[cid].copy()
            card["rarity"] = "обычная"
            logger.info(f"🔄 ФИНАЛЬНЫЙ РЕЗЕРВ: {card['name']} (обычная)")
            return card
        else:
            all_cards = list(CARD_ID_MAP.keys())
            cid = random.choice(all_cards)
            card = CARD_ID_MAP[cid].copy()
            logger.info(f"🚨 АВАРИЙНЫЙ ВЫБОР: {card['name']}")
            return card
    
    except Exception as e:
        logger.error(f"Ошибка при выборе карты: {e}")
        available_cards = RARITY_TO_IDS.get("обычная", [])
        if available_cards:
            cid = random.choice(available_cards)
            card = CARD_ID_MAP[cid].copy()
            card["rarity"] = "обычная"
            return card
        else:
            all_cards = list(CARD_ID_MAP.keys())
            cid = random.choice(all_cards)
            return CARD_ID_MAP[cid].copy()

# ====================== ФУНКЦИИ ДЛЯ ЭЛЕМЕНТАРИЕВ ======================
def calculate_production_for_one(elemental_id, elemental_data, now):
    level = elemental_data.get('level', 1)
    last_collect = datetime.fromisoformat(
        elemental_data.get('last_collect', '2000-01-01T00:00:00')
    )
    hours_passed = (now - last_collect).total_seconds() / 3600
    rate = level  # +level WC в час
    max_stored = level * 24  # лимит — сутки накопления
    produced = min(hours_passed * rate, max_stored - elemental_data.get('stored', 0))
    return produced

async def check_and_complete_craft(user_id, context, query=None):
    """Проверка и завершение крафта"""
    load_data()
    user = get_user(user_id)
    now = datetime.now().timestamp()
    craft = user.get('active_craft')
    if craft and craft['end_time'] <= now:
        eid = craft['result_id']
        add_elemental(user, eid)
        user['active_craft'] = None
        save_data()
        if query:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(context.t('elementals_collect') if hasattr(context, 't') else "Собрать", callback_data="elem_collect")],
                [InlineKeyboardButton("Синтезатор", callback_data="elem_synth")],
                [InlineKeyboardButton("Инкубатор", callback_data="elem_incub")],
                [InlineKeyboardButton("Пекарня", callback_data="elem_bakery")]
            ])
            await query.edit_message_text(
                f"✅ Готово! Получен {ELEMENTALS[eid]['name']}",
                reply_markup=keyboard
            )
        else:
            await notify_user(context.bot, user_id, f"Готово! Получен {ELEMENTALS[eid]['name']}")

def add_elemental(user, eid):
    """Добавляет элементаля пользователю или повышает уровень, если уже есть"""
    if eid not in user.get('elementals', {}):
        user['elementals'][eid] = {
            'level': 1,
            'stored': 0.0,
            'last_collect': datetime.now().isoformat()
        }
    else:
        user['elementals'][eid]['level'] += 1

async def collect_all_elementals(update, context):
    """Сбор ресурсов со всех элементалей"""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    
    load_data()
    user = get_user(user_id)
    now = datetime.now()
    total = 0
    
    for eid, edata in user.get('elementals', {}).items():
        produced = calculate_production_for_one(eid, edata, now)
        total += math.floor(produced)
        edata['stored'] = 0.0
        edata['last_collect'] = now.isoformat()
    
    user['wc'] += total
    save_data()
    
    # Получаем перевод
    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t('elementals_collect'), callback_data="elem_collect")],
        [InlineKeyboardButton("Синтезатор", callback_data="elem_synth")],
        [InlineKeyboardButton("Инкубатор", callback_data="elem_incub")],
        [InlineKeyboardButton("Пекарня", callback_data="elem_bakery")]
    ])
    
    await query.edit_message_text(
        t('elementals_collected', count=total),
        reply_markup=keyboard
    )

async def start_incubator(update, context):
    """Запуск инкубатора элементаля"""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    
    load_data()
    user = get_user(user_id)
    now = datetime.now()
    
    # Получаем перевод
    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    
    if user.get('active_craft'):
        remaining = user['active_craft']['end_time'] - now.timestamp()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t('elementals_collect'), callback_data="elem_collect")],
            [InlineKeyboardButton("Синтезатор", callback_data="elem_synth")],
            [InlineKeyboardButton("Инкубатор", callback_data="elem_incub")],
            [InlineKeyboardButton("Пекарня", callback_data="elem_bakery")]
        ])
        await query.edit_message_text(
            f"Уже идёт процесс! Осталось {int(remaining // 60)} мин",
            reply_markup=keyboard
        )
        return
    
    if user['wc'] < ELEMENTAL_WISH_COST:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t('elementals_collect'), callback_data="elem_collect")],
            [InlineKeyboardButton("Синтезатор", callback_data="elem_synth")],
            [InlineKeyboardButton("Инкубатор", callback_data="elem_incub")],
            [InlineKeyboardButton("Пекарня", callback_data="elem_bakery")]
        ])
        await query.edit_message_text(
            f"Нужно {ELEMENTAL_WISH_COST} WC!",
            reply_markup=keyboard
        )
        return
    
    user['wc'] -= ELEMENTAL_WISH_COST
    end_time = now + timedelta(minutes=30)
    user['active_craft'] = {
        'type': 'incubator',
        'end_time': end_time.timestamp(),
        'result_id': random.choice([k for k, v in ELEMENTALS.items() if v['elements'] == 1])
    }
    save_data()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t('elementals_collect'), callback_data="elem_collect")],
        [InlineKeyboardButton("Синтезатор", callback_data="elem_synth")],
        [InlineKeyboardButton("Инкубатор", callback_data="elem_incub")],
        [InlineKeyboardButton("Пекарня", callback_data="elem_bakery")]
    ])
    await query.edit_message_text(
        "Инкубация начата! Через 30 мин получишь элементаля.",
        reply_markup=keyboard
    )

async def start_synthesis(update, context, pair, result_id):
    """Запуск синтеза элементалей"""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    
    load_data()
    user = get_user(user_id)
    now = datetime.now()
    
    # Получаем перевод
    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    
    if user.get('active_craft'):
        remaining = user['active_craft']['end_time'] - now.timestamp()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t('elementals_collect'), callback_data="elem_collect")],
            [InlineKeyboardButton("Синтезатор", callback_data="elem_synth")],
            [InlineKeyboardButton("Инкубатор", callback_data="elem_incub")],
            [InlineKeyboardButton("Пекарня", callback_data="elem_bakery")]
        ])
        await query.edit_message_text(
            f"Уже идёт процесс! Осталось {int(remaining // 60)} мин",
            reply_markup=keyboard
        )
        return
    
    for eid in pair:
        if eid not in user.get('elementals', {}):
            await query.answer("У тебя нет одного из элементалей!", show_alert=True)
            return
    
    elements1 = ELEMENTALS[pair[0]]['elements']
    elements2 = ELEMENTALS[pair[1]]['elements']
    minutes = 30 if (elements1 == 1 and elements2 == 1) else 65
    
    end_time = now + timedelta(minutes=minutes)
    user['active_craft'] = {
        'type': 'synthesis',
        'end_time': end_time.timestamp(),
        'result_id': result_id
    }
    
    for eid in pair:
        del user['elementals'][eid]
    
    save_data()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t('elementals_collect'), callback_data="elem_collect")],
        [InlineKeyboardButton("Синтезатор", callback_data="elem_synth")],
        [InlineKeyboardButton("Инкубатор", callback_data="elem_incub")],
        [InlineKeyboardButton("Пекарня", callback_data="elem_bakery")]
    ])
    await query.edit_message_text(
        f"Синтез начат! Через {minutes} мин получишь {ELEMENTALS[result_id]['name']}.",
        reply_markup=keyboard
    )

async def feed_elemental(update, context, eid, levels_to_add=1):
    """Кормление элементаля для повышения уровня"""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    
    load_data()
    user = get_user(user_id)
    edata = user['elementals'].get(eid)
    if not edata:
        return "Элементаль не найден"
    
    # Получаем перевод
    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    
    current_level = edata.get('level', 1)
    if current_level >= 15:
        return t('error') or "Максимальный уровень достигнут!"
    
    total_portions = sum(range(current_level, current_level + levels_to_add))
    cost = total_portions * 15
    if user['wc'] < cost:
        return f"Не хватает WC! Нужно {cost}, а у тебя {user['wc']}"
    
    user['wc'] -= cost
    edata['level'] = current_level + levels_to_add
    save_data()
    
    return t('elementals_level_up', level=edata['level']) + f" Потрачено {cost} WC."

@with_translation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Команда /start от пользователя {user.id}")
    
    # 1. Загружаем данные (обязательно присваиваем переменной!)
    data = load_data()
    
    # 2. Обновляем данные пользователя (теперь не упадет из-за None)
    data = update_user_data(user, data)
    
    # 3. Сохраняем обновленный словарь обратно в файл
    save_data()
    
    # 4. Обновляем локальное состояние (твоя старая функция)
    get_user(user.id)
    
    t = context.t
    text = t('commands_list')
    
    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )

@with_translation
async def getcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /getcard"""
    user = update.effective_user
    logger.info(f"Команда /getcard от пользователя {user.id}")
    
    load_data()
    uid = str(user.id)
    user_data = get_user(uid)
    
    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)

    base_cooldown = 6.5
    cooldown = base_cooldown

    boosters = user_data.get("boosters", {})
    now = datetime.now()
    
    for booster_name, target_cooldown in [("картограф_i", 4), ("картограф_ii", 3), ("картограф_iii", 2)]:
        if booster_name in boosters:
            booster_end = datetime.fromisoformat(boosters[booster_name])
            if now <= booster_end:
                cooldown = target_cooldown
                logger.debug(f"Активен бустер {booster_name}, КД: {cooldown} мин")
            else:
                del boosters[booster_name]

    try:
        last_time = datetime.fromisoformat(user_data.get("last_card_time", "2000-01-01T00:00:00"))
    except Exception as e:
        logger.warning(f"Ошибка парсинга времени: {e}")
        last_time = datetime(2000,1,1)

    wait = timedelta(minutes=cooldown)
    if now - last_time < wait:
        remaining = wait - (now - last_time)
        total_seconds = int(remaining.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        logger.info(f"Пользователь {user.id} пытался получить карту раньше времени")
        
        # Используем перевод для сообщения о кулдауне
        await update.message.reply_text(
            t('error_cooldown', minutes=minutes, seconds=seconds),
            reply_markup=main_menu()
        )
        return

    card = choose_card(user_data)
    rarity = card.get("rarity", CARD_ID_MAP[card["id"]]["rarity"])
    cid = card["id"]

    # Переводим название карты
    if user_lang != 'ru':
        card['name'] = translate_card_name(card['name'], user_lang)

    is_weather_card = (rarity == "погодные")
    
    if not is_weather_card:
        user_data.setdefault("banned_cards", {})
        user_data["banned_cards"][cid] = 2
        logger.info(f"Карта {card['name']} забанена на 2 получения для пользователя {uid}")

        user_data.setdefault("chance_bonus", {"экстра": 0.0, "боссы": 0.0})
        user_data["chance_bonus"]["экстра"] = round(user_data["chance_bonus"].get("экстра", 0.0) + 0.03, 6)
        user_data["chance_bonus"]["боссы"] = round(user_data["chance_bonus"].get("боссы", 0.0) + 0.01, 6)
        
        if rarity in ("экстра", "боссы"):
            user_data["chance_bonus"][rarity] = 0.0
            logger.info(f"Сброс бонуса для {rarity} у пользователя {user.id}")

    reward = CARD_REWARDS.get(rarity, 0)
    
    if cid in user_data["cards"]:
        user_data["cards"][cid]["count"] += 1
        is_new_card = False
    else:
        user_data["cards"][cid] = {"name": card["name"], "rarity": rarity, "count": 1, "url": card.get("url")}
        is_new_card = True
    
    user_data["wc"] = user_data.get("wc", 0) + reward
    user_data["last_card_time"] = now.isoformat()

    save_data()

    if is_weather_card:
        current_weather = get_current_weather()
        weather_info = WEATHER_SYSTEM[current_weather]
        
        mystery_msg = await update.message.reply_text(
            "Пип. Пип. Пип... это же...",
            reply_markup=main_menu()
        )
        
        await asyncio.sleep(3)
        
        revelation_text = (
            f"...Погодная карта, которая выпала во время **{current_weather}** {weather_info['emoji']}\n\n"
            f" **{card['name']}**\n"
            f"️ Редкость: Погодная\n"
            f" удивлю, но шансы на эту карту - {weather_info['card_chance']}%\n\n"
            f" **Аномальная погода увеличила шанс на редкие карты! (наверное..) **"
        )
        
        await update.message.reply_photo(
            card.get("url"),
            caption=revelation_text,
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        
        try:
            await mystery_msg.delete()
        except:
            pass
            
        logger.info(f"Пользователь {user.id} получил погодную карту {card['name']} во время {current_weather}")
        
    else:
        card_counter = user_data.get("card_counter", 1)
        
        if is_new_card:
            caption = t('card_received', 
                name=card['name'], 
                rarity=t(f'rarity_{rarity}'), 
                reward=reward
        )
        else:
            caption = t('card_duplicate', 
                name=card['name'], 
                rarity=t(f'rarity_{rarity}'), 
                reward=reward
        )

        logger.info(f"Пользователь {user.id} получил карту {card['name']} ({rarity}) +{reward} WC, счетчик: {card_counter}")
        await update.message.reply_photo(
            card.get("url"),
            caption=caption,
            reply_markup=main_menu()
        )

@with_translation
async def mycards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /mycards с коллекцией карт и элементалей"""
    user = update.effective_user
    logger.info(f"Команда /mycards от пользователя {user.id}")
    
    load_data()
    uid = str(user.id)
    user_data = get_user(uid)
    
    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)
    
    wc = user_data.get("wc", 0)
    text = t('balance', count=wc, forms=t('wc_forms')) + "\n\n"

    if not user_data["cards"]:
        text += t('no_cards', cmd=t('cmd_getcard'))
        logger.info(f"Пользователь {user.id} просмотрел пустую коллекцию")
    else:
        text += t('cards_collection') + "\n"

        for i, (cid, info) in enumerate(user_data["cards"].items(), start=1):
            if cid in CARD_ID_MAP:
                # Переводим название карты
                card_name = info.get('name', CARD_ID_MAP[cid]['name'])
                if user_lang != 'ru':
                    card_name = translate_card_name(card_name, user_lang)
                card_rarity = info.get('rarity', CARD_ID_MAP[cid]['rarity'])
                rarity_text = t(f'rarity_{card_rarity}') if f'rarity_{card_rarity}' in TRANSLATIONS[user_lang] else card_rarity
            else:
                card_name = info.get('name', '???')
                rarity_text = info.get('rarity', '???')
                
            text += f"{i}) [{cid}] {card_name} ({rarity_text}) × {info.get('count', 0)}\n"

        text += f"\n В общем:\n"

        rarity_stats = {}
        special_cards = []
        
        total_cards_in_system = 0
        for rarity, card_list in CARDS.items():
            if rarity not in ["особенные", "элементали"]:
                total_cards_in_system += len(card_list)
        
        for cid, info in user_data["cards"].items():
            if cid in CARD_ID_MAP:
                card_rarity = info.get('rarity', CARD_ID_MAP[cid]['rarity'])
                card_name = info.get('name', CARD_ID_MAP[cid]['name'])
                count = info.get('count', 0)
                
                if card_rarity == "особенные":
                    special_cards.append((cid, card_name, count))
                else:
                    if card_rarity not in rarity_stats:
                        rarity_stats[card_rarity] = {"unique": 0, "total": 0}
                    rarity_stats[card_rarity]["unique"] += 1
                    rarity_stats[card_rarity]["total"] += count
        
        rarity_order = ["обычная", "необычная", "редкая", "эпическая", "легендарная", 
                       "донатная", "экстра", "боссы", "погодные", "элементали"]
        
        emoji_map = {
            "обычная": "⚪", "необычная": "🔵", "редкая": "🟢", 
            "эпическая": "🟣", "легендарная": "🟠", "донатная": "💎", 
            "экстра": "🔥", "боссы": "💀", "погодные": "🌪️",
            "элементали": "🌌"
        }
        
        for rarity in rarity_order:
            if rarity in rarity_stats:
                unique_user_cards = rarity_stats[rarity]["unique"]
                total_possible_cards = len(RARITY_TO_IDS.get(rarity, []))
                emoji = emoji_map.get(rarity, "🎴")
                rarity_text = t(f'rarity_{rarity}')
                
                text += f"{emoji} {rarity_text}: [{unique_user_cards}/{total_possible_cards}]\n"
        
        special_count = len(special_cards)
        if special_count > 0:
            total_special_cards = len(CARDS.get("особенные", []))
            text += f"🌟 {t('rarity_extra') if user_lang == 'ru' else 'Special'}: {special_count}\n"
        
        unique_user_cards_total = sum(stats["unique"] for stats in rarity_stats.values())
        
        total_user_cards_with_duplicates = 0
        for cid, info in user_data["cards"].items():
            if cid in CARD_ID_MAP and CARD_ID_MAP[cid]["rarity"] not in ["особенные", "элементали"]:
                total_user_cards_with_duplicates += info.get('count', 0)
        
        text += f"\n {t('cards_total', total=unique_user_cards_total)}/{total_cards_in_system}"
        if total_user_cards_with_duplicates != unique_user_cards_total:
            text += f" ({t('cards_total', total=total_user_cards_with_duplicates)} с повторками)"
        
        # ────────────────────────────── Элементали ──────────────────────────────
        text += "\n\n📊 **" + t('elementals_title') + "**\n"
        owned = user_data.get('elementals', {})
        total_possible = len(ELEMENTALS)
        unique_count = len(owned)

        text += t('elementals_count', count=unique_count, total=total_possible) + "\n"

        now = datetime.now()
        total_collected = 0
        total_rate = 0

        if owned:
            text += "Список:\n"
            for eid, edata in owned.items():
                level = edata.get('level', 1)
                produced = calculate_production_for_one(eid, edata, now)
                current_stored = edata.get('stored', 0.0) + produced

                total_collected += math.floor(current_stored)
                total_rate += level

                text += (
                    f"• {ELEMENTALS[eid]['emoji']} **{ELEMENTALS[eid]['name']}** "
                    f"ур. {level}   →   +{level}/ч   (≈{current_stored:.1f} WC)\n"
                )

                # обновляем время и сбрасываем накопленное
                edata['last_collect'] = now.isoformat()
                edata['stored'] = 0.0

            if total_collected > 0:
                user_data['wc'] = user_data.get('wc', 0) + total_collected
                text += f"\n**Автоматически собрано при просмотре: +{total_collected} WC**\n"

            text += f"\n{t('elementals_rate', rate=total_rate)}\n"
        else:
            text += t('no_cards', cmd=t('cmd_elemental')) if hasattr(t, 'no_cards_elemental') else "У тебя пока нет элементалей.\n"

        # ────────────────────────────── Клавиатура ──────────────────────────────
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t('elementals_collect'), callback_data="elem_collect")]
        ])

        logger.info(f"Пользователь {user.id} просмотрел коллекцию: {unique_user_cards_total} уникальных карт, {total_user_cards_with_duplicates} с повторками")

        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

@with_translation
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /shop"""
    user = update.effective_user
    logger.info(f"Команда /shop от пользователя {user.id}")
    
    load_data()
    uid = str(user.id)
    user_data = get_user(uid)

    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)

    text = t('shop_title') + "\n"
    emoji_map = {
        "обычная": "💠", "необычная": "💠", "редкая": "💠", 
        "эпическая": "💠", "легендарная": "💠", "донатная": "💎", 
        "экстра": "🔥", "боссы": "💀", "элементали": "🌌"
    }

    order = ["обычная", "необычная", "редкая", "эпическая", "легендарная", "донатная", "экстра", "боссы", "элементали"]

    for rarity in order:
        price = CARD_PRICES.get(rarity)
        if price is None:
            continue

        emoji = emoji_map.get(rarity, "💠")
        rarity_text = t(f'rarity_{rarity}')
        text += f"{emoji} {rarity_text} — {price} WC\n"

        for cid in RARITY_TO_IDS.get(rarity, []):
            card = CARD_ID_MAP[cid]
            card_name = translate_card_name(card['name'], user_lang) if user_lang != 'ru' else card['name']
            text += f"  [{cid}] {card_name}\n"
        text += "\n"

    text += t('shop_buy', cmd=t('cmd_buy')) + "\n"
    text += t('shop_sell', cmd=t('cmd_sell')) + "\n"
    text += "Пример: /buy W3 2, /sell W3 all."

    await update.message.reply_text(text, reply_markup=main_menu())

def parse_count_arg(arg, fallback=1):
    """Парсинг аргумента количества"""
    if arg is None:
        return fallback
    arg = str(arg).strip().lower()
    if arg == "all":
        return "all"
    try:
        n = int(arg)
        return n if n > 0 else None
    except Exception:
        return None

@with_translation
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /buy"""
    user = update.effective_user
    logger.info(f"Команда /buy от пользователя {user.id}: {context.args}")
    
    load_data()
    uid = str(user.id)
    user_data = get_user(uid)

    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)

    if not context.args:
        await update.message.reply_text(t('shop_buy', cmd=t('cmd_buy')), reply_markup=main_menu())
        return

    cid = context.args[0].upper()
    cid = normalize_elemental_id(cid)  # Нормализуем ID элементаля
    
    if cid not in CARD_ID_MAP:
        logger.warning(f"Пользователь {user.id} пытался купить несуществующую карту: {cid}")
        await update.message.reply_text(t('error_no_card'), reply_markup=main_menu())
        return

    count = parse_count_arg(context.args[1] if len(context.args) > 1 else None, fallback=1)
    if count is None:
        await update.message.reply_text(t('error_invalid_amount'), reply_markup=main_menu())
        return

    if count == "all":
        count = 1

    price_per = CARD_ID_MAP[cid]["price"]
    total_cost = price_per * count
    
    if user_data.get("wc",0) < total_cost:
        logger.warning(f"Пользователь {user.id} пытался купить без средств: нужно {total_cost}, есть {user_data.get('wc',0)}")
        await update.message.reply_text(
            t('shop_not_enough_wc', need=total_cost, have=user_data.get('wc',0)),
            reply_markup=main_menu()
        )
        return

    user_data["wc"] = user_data.get("wc", 0) - total_cost
    cards = user_data["cards"]
    
    card_name = CARD_ID_MAP[cid]["name"]
    if user_lang != 'ru':
        card_name = translate_card_name(card_name, user_lang)
    
    if cid in cards:
        cards[cid]["count"] += count
    else:
        cards[cid] = {
            "name": card_name, 
            "rarity": CARD_ID_MAP[cid]["rarity"], 
            "count": count, 
            "url": CARD_ID_MAP[cid].get("url")
        }
    
    save_data()

    logger.info(f"Пользователь {user.id} купил {count} × {CARD_ID_MAP[cid]['name']} за {total_cost} WC")
    
    await update.message.reply_photo(
        CARD_ID_MAP[cid].get("url"),
        caption=t('shop_bought', count=count, name=card_name, price=total_cost) + f"\n{t('balance', count=user_data['wc'], forms=t('wc_forms'))}",
        reply_markup=main_menu()
    )

@with_translation
async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /sell с защитой от продажи особенных и погодных карт"""
    user = update.effective_user
    logger.info(f"Команда /sell от пользователя {user.id}: {context.args}")
    
    load_data()
    uid = str(user.id)
    user_data = get_user(uid)

    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)

    if not context.args:
        await update.message.reply_text(t('shop_sell', cmd=t('cmd_sell')), reply_markup=main_menu())
        return

    cid = context.args[0].upper()
    cid = normalize_elemental_id(cid)  # Нормализуем ID элементаля
    
    # Проверка на элементаля
    if cid in ELEMENTAL_ID_MAP:
        if cid not in user_data.get('elementals', {}):
            await update.message.reply_text("У тебя нет этого элементаля", reply_markup=main_menu())
            return
        
        elements = ELEMENTAL_ID_MAP[cid]['elements']
        sell_price_single = ELEMENTAL_PRICES[elements]
        
        if len(context.args) == 1:
            await update.message.reply_text(
                f"У тебя есть элементаль: {ELEMENTAL_ID_MAP[cid]['name']}\n"
                f"Можно продать за {sell_price_single} WC\n\n"
                f"Для продажи: /sell {cid}",
                reply_markup=main_menu()
            )
            return
        
        # Удаляем элементаля
        del user_data['elementals'][cid]
        user_data["wc"] = user_data.get("wc", 0) + sell_price_single
        save_data()
        
        logger.info(f"Пользователь {user.id} продал элементаля {ELEMENTAL_ID_MAP[cid]['name']} за {sell_price_single} WC")
        
        await update.message.reply_text(
            t('shop_sold', count=1, name=ELEMENTAL_ID_MAP[cid]['name'], price=sell_price_single) + f"\n{t('balance', count=user_data['wc'], forms=t('wc_forms'))}",
            reply_markup=main_menu()
        )
        return
    
    # Оригинальный код для карт
    if cid not in CARD_ID_MAP:
        logger.warning(f"Пользователь {user.id} пытался продать несуществующую карту: {cid}")
        await update.message.reply_text(t('error_no_card'), reply_markup=main_menu())
        return

    card_info = CARD_ID_MAP[cid]
    rarity = card_info["rarity"]
    
    if rarity in ["особенные", "погодные", "элементали"]:
        await update.message.reply_text(
            t('shop_cannot_sell'),
            reply_markup=main_menu()
        )
        return

    if cid not in user_data["cards"]:
        logger.warning(f"Пользователь {user.id} пытался продать отсутствующую карту: {cid}")
        await update.message.reply_text(t('shop_not_enough_cards'), reply_markup=main_menu())
        return

    if len(context.args) == 1:
        available = user_data["cards"][cid]["count"]
        sell_price_single = math.floor(CARD_ID_MAP[cid]["price"] / 2)
        total_all = sell_price_single * available
        
        card_name = card_info["name"]
        if user_lang != 'ru':
            card_name = translate_card_name(card_name, user_lang)
        
        await update.message.reply_text(
            f"ты имеешь {available} × {card_name}.\n"
            f"если продашь одну капту, то будет {sell_price_single} WC.\n"
            f"или при продаже всех ({available}) получишь {total_all} WC.\n\n"
            f"Для продажи: /sell {cid} <кол-во> или /sell {cid} all",
            reply_markup=main_menu()
        )
        return

    count_arg = context.args[1].lower()
    if count_arg == "all":
        count = user_data["cards"][cid]["count"]
    else:
        try:
            count = int(count_arg)
            if count <= 0:
                raise ValueError()
        except Exception:
            await update.message.reply_text(t('error_invalid_amount'), reply_markup=main_menu())
            return

    if user_data["cards"][cid]["count"] < count:
        logger.warning(f"Пользователь {user.id} пытался продать больше карт чем есть: {count} > {user_data['cards'][cid]['count']}")
        await update.message.reply_text(t('shop_not_enough_cards'), reply_markup=main_menu())
        return

    sell_price_single = math.floor(CARD_ID_MAP[cid]["price"] / 2)
    total = sell_price_single * count

    user_data["cards"][cid]["count"] -= count
    if user_data["cards"][cid]["count"] <= 0:
        del user_data["cards"][cid]

    user_data["wc"] = user_data.get("wc", 0) + total
    save_data()

    card_name = card_info["name"]
    if user_lang != 'ru':
        card_name = translate_card_name(card_name, user_lang)
    
    logger.info(f"Пользователь {user.id} продал {count} × {CARD_ID_MAP[cid]['name']} за {total} WC")
    
    await update.message.reply_text(
        t('shop_sold', count=count, name=card_name, price=total) + f"\n{t('balance', count=user_data['wc'], forms=t('wc_forms'))}",
        reply_markup=main_menu()
    )

@with_translation
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /price с учетом запрещенных карт"""
    user = update.effective_user
    logger.info(f"Команда /price от пользователя {user.id}: {context.args}")
    
    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)
    
    if not context.args:
        await update.message.reply_text(t('shop_price', price='?', half='?'), reply_markup=main_menu())
        return

    cid = context.args[0].upper()
    cid = normalize_elemental_id(cid)  # Нормализуем ID элементаля
    
    # Проверка на элементаля
    if cid in ELEMENTAL_ID_MAP:
        elements = ELEMENTAL_ID_MAP[cid]['elements']
        sell_price_single = ELEMENTAL_PRICES[elements]
        
        count = 1
        if len(context.args) > 1:
            cnt = parse_count_arg(context.args[1], fallback=1)
            if cnt is None or cnt == "all":
                await update.message.reply_text(t('error_invalid_amount'), reply_markup=main_menu())
                return
            count = cnt
        
        total = sell_price_single * count
        await update.message.reply_text(f"{count} × {ELEMENTAL_ID_MAP[cid]['name']} можно продать за {total} WC", reply_markup=main_menu())
        return
    
    # Оригинальный код для карт
    if cid not in CARD_ID_MAP:
        await update.message.reply_text(t('error_no_card'), reply_markup=main_menu())
        return

    card_info = CARD_ID_MAP[cid]
    rarity = card_info["rarity"]
    
    if rarity in ["особенные", "погодные", "элементали"]:
        await update.message.reply_text(
            t('shop_cannot_sell'),
            reply_markup=main_menu()
        )
        return

    count = 1
    if len(context.args) > 1:
        cnt = parse_count_arg(context.args[1], fallback=1)
        if cnt is None or cnt == "all":
            await update.message.reply_text(t('error_invalid_amount'), reply_markup=main_menu())
            return
        count = cnt

    card_name = card_info["name"]
    if user_lang != 'ru':
        card_name = translate_card_name(card_name, user_lang)
    
    sell_price_single = math.floor(CARD_ID_MAP[cid]["price"] / 2)
    total = sell_price_single * count
    await update.message.reply_text(f"{count} × {card_name} можно продать за {total} WC", reply_markup=main_menu())

@with_translation
async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /view"""
    user = update.effective_user
    logger.info(f"Команда /view от пользователя {user.id}: {context.args}")
    
    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)
    
    if not context.args:
        await update.message.reply_text(" /view <ID карты>, например: /view W3", reply_markup=main_menu())
        return

    cid = context.args[0].upper()
    cid = normalize_elemental_id(cid)  # Нормализуем ID элементаля
    
    # Проверка на элементаля
    if cid in ELEMENTAL_ID_MAP:
        elemental = ELEMENTAL_ID_MAP[cid]
        caption = f"{elemental['name']} (Элементаль, {elemental['elements']} элемент(а)) {elemental['emoji']}"
        
        if elemental.get('url') and elemental['url'] != "https://placeholder.com/clock.png":
            await update.message.reply_photo(elemental['url'], caption=caption, reply_markup=main_menu())
        else:
            await update.message.reply_text(caption, reply_markup=main_menu())
        return
    
    if cid not in CARD_ID_MAP:
        await update.message.reply_text(t('error_no_card'), reply_markup=main_menu())
        return

    card = CARD_ID_MAP[cid]
    card_name = translate_card_name(card['name'], user_lang) if user_lang != 'ru' else card['name']
    rarity_text = t(f'rarity_{card["rarity"]}') if f'rarity_{card["rarity"]}' in TRANSLATIONS[user_lang] else card["rarity"]
    caption = f"{card_name}, {rarity_text} ({card['id']})"
    await update.message.reply_photo(card.get("url"), caption=caption, reply_markup=main_menu())

@with_translation
async def minigames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /minigames"""
    user = update.effective_user
    logger.info(f"Команда /minigames от пользователя {user.id}")
    
    t = context.t
    
    text = (
        "🎮 Миниигры:\n\n"
        "/dice <ставка> — Брось куб. Выпадает 5 или 6 и выигрыш увеличивается!\n"
        "/casino <ставка> — Крутится слот-машина. Комбинации могут принести x2 или x10!\n\n"
        "/solitaire - сами захотели пасьянс на зимбабвийские доллары  \n\n"
        "можно проебать коины, удачи тебе. она тебе пригодится"
    )
    await update.message.reply_text(text, reply_markup=main_menu())

@with_translation
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /dice"""
    user = update.effective_user
    logger.info(f"Команда /dice от пользователя {user.id}: {context.args}")
    
    load_data()
    uid = str(user.id)
    user_data = get_user(uid)

    t = context.t

    if not context.args:
        await update.message.reply_text(" /dice <ставка>. например /dice 2705", reply_markup=main_menu())
        return

    try:
        bet = int(context.args[0])
        if bet <= 0:
            raise ValueError()
    except:
        await update.message.reply_text("ты че, какие отрицательные числа и нули? а ну взял ставку от одного и больше.", reply_markup=main_menu())
        return

    if user_data.get("wc",0) < bet:
        logger.warning(f"Пользователь {user.id} пытался играть в кости без средств: ставка {bet}, баланс {user_data.get('wc',0)}")
        await update.message.reply_text(t('shop_not_enough_wc', need=bet, have=user_data.get('wc',0)), reply_markup=main_menu())
        return

    roll = random.randint(1,6)
    if roll == 6:
        win = bet * 3
        user_data["wc"] += win
        result_text = f"Ты бросил куб: 6\n НИХУЯ СЕБЕ! ты поулчаешь {win} WC"
        logger.info(f"Пользователь {user.id} выиграл в кости: {win} WC (выпало 6)")
    elif roll == 5:
        win = bet * 2
        user_data["wc"] += win
        result_text = f"Ты бросил куб: 5\n ништяк, ты выйграл {win} WC"
        logger.info(f"Пользователь {user.id} выиграл в кости: {win} WC (выпало 5)")
    else:
        user_data["wc"] -= bet
        result_text = f"Ты бросил куб: {roll}\n увы, но ты проебался {bet} WC"
        logger.info(f"Пользователь {user.id} проиграл в кости: {bet} WC (выпало {roll})")

    save_data()
    await update.message.reply_text(result_text, reply_markup=main_menu())

@with_translation
async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Команда /casino от пользователя {user.id}: {context.args}")
    
    load_data()
    uid = str(user.id)
    user_data = get_user(uid)

    t = context.t

    if not context.args:
        await update.message.reply_text(" /casino <ставка>. пример: /casino 1109", reply_markup=main_menu())
        return

    try:
        bet = int(context.args[0])
        if bet <= 0:
            raise ValueError()
    except:
        await update.message.reply_text("ставка должна быть больще чем 0.", reply_markup=main_menu())
        return

    if user_data.get("wc",0) < bet:
        logger.warning(f"Пользователь {user.id} пытался играть в казино без средств: ставка {bet}, баланс {user_data.get('wc',0)}")
        await update.message.reply_text(t('shop_not_enough_wc', need=bet, have=user_data.get('wc',0)), reply_markup=main_menu())
        return

    symbols = ["🍒","🍋","🔔","7️⃣"]
    slot = [random.choice(symbols) for _ in range(3)]
    win = 0

    if slot == ["7️⃣","7️⃣","7️⃣"]:
        win = bet * 10
        user_data["wc"] += win
        result_text = f"Слот: {' '.join(slot)}\n🎰 Джекпот! Выигрыш: {win} WC"
        logger.info(f"Пользователь {user.id} выиграл джекпот в казино: {win} WC")
    elif slot[0] == slot[1] == slot[2]:
        win = bet * 2
        user_data["wc"] += win
        result_text = f"Слот: {' '.join(slot)}\n🎰 Отлично! Выигрыш: {win} WC"
        logger.info(f"Пользователь {user.id} выиграл в казино: {win} WC")
    else:
        user_data["wc"] -= bet
        result_text = f"Слот: {' '.join(slot)}\n😢 Увы, ставка сгорела: {bet} WC"
        logger.info(f"Пользователь {user.id} проиграл в казино: {bet} WC")

    save_data()
    await update.message.reply_text(result_text, reply_markup=main_menu())

@with_translation
async def statr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /statr"""
    user = update.effective_user
    logger.info(f"Команда /statr от пользователя {user.id}")
    
    # 1. Загружаем данные (обязательно присваиваем переменной!)
    data = load_data()
    
    # 2. Обновляем данные пользователя (теперь не упадет из-за None)
    data = update_user_data(user, data)
    
    # 3. Сохраняем обновленный словарь обратно в файл
    save_data()
    
    # 4. Обновляем локальное состояние (твоя старая функция)
    get_user(user.id)
    
    t = context.t
    text = t('commands_list')
    
    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )

# ============ Обработка ошибок ============
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибки"""
    logger.error(f"Ошибка при обработке update {update}: {context.error}", exc_info=context.error)

# ================== Настройки администраторов ==================
ADMINS = [8520739067]
ADMIN_PASSWORD = "W57LZ00Ylemonov"

def is_admin(user_id):
    """Проверка прав администратора"""
    return user_id in ADMINS

async def admin_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Аутентификация администратора"""
    user_id = update.effective_user.id
    if is_admin(user_id):
        return True
    
    if context.args and context.args[0] == ADMIN_PASSWORD:
        ADMINS.append(user_id)
        await update.message.reply_text("✅ Доступ администратора предоставлен!")
        return True
    
    await update.message.reply_text("❌ Недостаточно прав.")
    return False

# ================== АДМИН ПАНЕЛЬ ==================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню админ-панели."""
    if not await admin_auth(update, context):
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👤 Управление пользователями", callback_data="admin_users")],
        [InlineKeyboardButton("🎴 Управление картами", callback_data="admin_cards")],
        [InlineKeyboardButton("🎁 Выдача", callback_data="admin_give")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")]
    ]
    
    await update.message.reply_text(
        "🛠️ мне лень делать админку и получения кодов, поэтому он тут. /createcode",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_admin_give_menu(query, context):
    """Меню выдачи"""
    keyboard = [
        [InlineKeyboardButton("💰 Выдать WC", callback_data="give_wc")],
        [InlineKeyboardButton("🎴 Выдать карту", callback_data="give_card")],
        [InlineKeyboardButton("🎁 Выдать всем WC", callback_data="give_all_wc")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        "🎁 **Система выдачи**\n\n"
        "Выберите что выдать:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_give_wc_menu(query, context):
    """Меню выдачи WC"""
    keyboard = [
        [InlineKeyboardButton("💵 100 WC", callback_data="give_wc_100")],
        [InlineKeyboardButton("💵 500 WC", callback_data="give_wc_500")],
        [InlineKeyboardButton("💵 1000 WC", callback_data="give_wc_1000")],
        [InlineKeyboardButton("💎 Произвольная сумма", callback_data="give_wc_custom")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_give")]
    ]
    
    await query.edit_message_text(
        "💰 **Выдача WC**\n\n"
        "Выберите сумму для выдачи:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_give_card_menu(query, context):
    """Меню выдачи карт"""
    keyboard = []
    
    rarities = ["обычная", "необычная", "редкая", "эпическая", "легендарная", "донатная", "экстра", "боссы", "особенные", "погодные", "элементали"]
    
    for rarity in rarities:
        if RARITY_TO_IDS.get(rarity):
            keyboard.append([InlineKeyboardButton(f"🎴 {rarity.capitalize()}", callback_data=f"give_card_rarity_{rarity}")])
    
    keyboard.append([InlineKeyboardButton("🆔 Поиск по ID", callback_data="give_card_search")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_give")])
    
    await query.edit_message_text(
        "🎴 **Выдача карт**\n\n"
        "Выберите редкость карты:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_give_card_rarity_menu(query, context, rarity):
    """Меню выдачи карт определенной редкости"""
    keyboard = []
    cards = RARITY_TO_IDS.get(rarity, [])
    
    for i in range(0, len(cards), 2):
        row = []
        for j in range(2):
            if i + j < len(cards):
                card_id = cards[i + j]
                card = CARD_ID_MAP[card_id]
                row.append(InlineKeyboardButton(card["name"], callback_data=f"give_card_{card_id}"))
        if row:
            keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="give_card")])
    
    await query.edit_message_text(
        f"🎴 **Выдача карт: {rarity}**\n\n"
        f"Выберите карту:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_give_all_wc_menu(query, context):
    """Меню выдачи WC всем"""
    keyboard = [
        [InlineKeyboardButton("💵 5 WC каждому", callback_data="give_all_wc_5")],
        [InlineKeyboardButton("💵 10 WC каждому", callback_data="give_all_wc_10")],
        [InlineKeyboardButton("💵 50 WC  ", callback_data="give_all_wc_50")],
        [InlineKeyboardButton("💵 100 WC каждому", callback_data="give_all_wc_100")],
        [InlineKeyboardButton("💵 150 каждому", callback_data="give_all_wc_150")],
        [InlineKeyboardButton("💵 500 WC каждому", callback_data="give_all_wc_500")],
        [InlineKeyboardButton("💵 1000 WC каждому", callback_data="give_all_wc_1000")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_give")]
    ]
    
    await query.edit_message_text(
        "💰 **Выдача WC всем пользователям**\n\n"
        "Выберите сумму для выдачи каждому:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_give_wc(query, context, amount, user_id=None):
    """Обработка выдачи WC"""
    load_data()
    
    if user_id:
        if user_id not in data["users"]:
            await query.edit_message_text(f"❌ Пользователь {user_id} не найден")
            return
        
        data["users"][user_id]["wc"] = data["users"][user_id].get("wc", 0) + amount
        save_data()
        
        await query.edit_message_text(
            f"✅ Выдано {amount} WC пользователю {user_id}\n"
            f"💰 Новый баланс: {data['users'][user_id]['wc']} WC"
        )
    else:
        await query.edit_message_text(
            f"💰 **Выдача {amount} WC**\n\n"
            f"Введите ID пользователя:\n"
            f"Пример: `123456789`\n\n"
            f"Или используйте команду:\n"
            f"`/addwc <user_id> {amount}`"
        )

async def handle_give_card(query, context, card_id, user_id=None, count=1):
    """Обработка выдачи карты"""
    # Нормализуем ID элементаля
    card_id = normalize_elemental_id(card_id)
    
    load_data()
    
    if user_id:
        if user_id not in data["users"]:
            await query.edit_message_text(f"❌ Пользователь {user_id} не найден")
            return
        
        user_data = data["users"][user_id]
        
        if card_id in CARD_ID_MAP:
            card_info = CARD_ID_MAP[card_id]
            
            if card_id in user_data["cards"]:
                user_data["cards"][card_id]["count"] += count
            else:
                user_data["cards"][card_id] = {
                    "name": card_info["name"],
                    "rarity": card_info["rarity"],
                    "count": count,
                    "url": card_info.get("url")
                }
            
            save_data()
            
            await query.edit_message_text(
                f"✅ Выдано {count} × {card_info['name']} пользователю {user_id}\n"
                f"🎴 Теперь у пользователя: {user_data['cards'][card_id]['count']} шт."
            )
        elif card_id in ELEMENTAL_ID_MAP:
            # Выдача элементаля
            elemental_info = ELEMENTAL_ID_MAP[card_id]
            add_elemental(user_data, card_id)
            save_data()
            
            await query.edit_message_text(
                f"✅ Выдан элементаль {elemental_info['name']} пользователю {user_id}"
            )
        else:
            await query.edit_message_text("❌ Карта не найдена")
    else:
        if card_id in CARD_ID_MAP:
            card_info = CARD_ID_MAP[card_id]
            await query.edit_message_text(
                f"🎴 **Выдача карты: {card_info['name']}**\n\n"
                f"Введите ID пользователя:\n"
                f"Пример: `123456789`\n\n"
                f"Или используйте команду:\n"
                f"`/addcard <user_id> {card_id} {count}`"
            )
        elif card_id in ELEMENTAL_ID_MAP:
            elemental_info = ELEMENTAL_ID_MAP[card_id]
            await query.edit_message_text(
                f"🌌 **Выдача элементаля: {elemental_info['name']}**\n\n"
                f"Введите ID пользователя:\n"
                f"Пример: `123456789`\n\n"
                f"Или используйте команду:\n"
                f"`/addcard <user_id> {card_id}`"
            )
        else:
            await query.edit_message_text("❌ Карта не найдена")

async def handle_give_all_wc(query, context, amount):
    """Обработка выдачи WC всем пользователям"""
    load_data()
    
    total_users = len(data["users"])
    total_given = 0
    affected_users = 0
    
    for user_id, user_data in data["users"].items():
        user_data["wc"] = user_data.get("wc", 0) + amount
        total_given += amount
        affected_users += 1
    
    save_data()
    admin_name = query.from_user.first_name
    notification_text = f"🎁 Администратор {admin_name} выдал всем по {amount} WC!"
    
    notified = 0
    for user_id in data["users"].keys():
        if await notify_user(context.bot, user_id, notification_text):
            notified += 1
    
    logger.info(f"Уведомления отправлены {notified} пользователям")
    
    await query.edit_message_text(
        f"✅ Выдано по {amount} WC всем пользователям!\n\n"
        f"👥 Пользователей: {affected_users}\n"
        f"💰 Всего выдано: {total_given} WC"
    )

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback'ов админ-панели"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ Недостаточно прав.")
        return
    
    callback_data = query.data
    logger.info(f"Админ callback от {query.from_user.id}: {callback_data}")
    
    try:
        if callback_data == "admin_stats":
            await show_admin_stats(query, context)
        elif callback_data == "admin_users":
            await show_admin_users_menu(query, context)
        elif callback_data == "admin_cards":
            await show_admin_cards_menu(query, context)
        elif callback_data == "admin_give":
            await show_admin_give_menu(query, context)
        elif callback_data == "admin_broadcast":
            await show_admin_broadcast_menu(query, context)
        elif callback_data == "back_main":
            await show_admin_main_menu(query, context)
            
        elif callback_data == "give_wc":
            await admin_give_wc_menu(query, context)
        elif callback_data == "give_card":
            await admin_give_card_menu(query, context)
        elif callback_data == "give_all_wc":
            await admin_give_all_wc_menu(query, context)
            
        elif callback_data.startswith("give_wc_"):
            if callback_data == "give_wc_custom":
                await query.edit_message_text(
                    "💰 **Выдача произвольной суммы WC**\n\n"
                    "Введите команду:\n"
                    "`/addwc <user_id> <amount>`\n\n"
                    "Пример:\n"
                    "`/addwc 123456789 1500`"
                )
            else:
                amount = int(callback_data.replace("give_wc_", ""))
                await handle_give_wc(query, context, amount)
                
        elif callback_data.startswith("give_card_rarity_"):
            rarity = callback_data.replace("give_card_rarity_", "")
            await admin_give_card_rarity_menu(query, context, rarity)
            
        elif callback_data.startswith("give_card_"):
            if callback_data == "give_card_search":
                await query.edit_message_text(
                    "🎴 **Поиск карты по ID**\n\n"
                    "Введите команду:\n"
                    "`/addcard <user_id> <card_id> [count]`\n\n"
                    "Пример:\n"
                    "`/addcard 123456789 WPR 2`\n\n"
                    "Список ID карт можно посмотреть в /shop"
                )
            else:
                card_id = callback_data.replace("give_card_", "")
                await handle_give_card(query, context, card_id)
                
        elif callback_data.startswith("give_all_wc_"):
            amount = int(callback_data.replace("give_all_wc_", ""))
            await handle_give_all_wc(query, context, amount)
            
        elif callback_data == "broadcast_start":
            await query.edit_message_text(
                "📢 **Начать рассылку**\n\n"
                "Используйте команду /broadcast <сообщение> для отправки сообщения всем пользователям.\n\n"
                "Пример:\n"
                "`/broadcast Привет! Это тестовая рассылка.`"
            )
        elif callback_data == "broadcast_stats":
            await query.edit_message_text(
                "📊 **Статистика рассылки**\n\n"
                "Функция статистики в разработке."
            )
            
        elif callback_data == "user_list":
            await query.edit_message_text(
                "📋 **Список пользователей**\n\n"
                "Функция списка пользователей в разработке."
            )
        elif callback_data == "user_search":
            await query.edit_message_text(
                "🔍 **Поиск пользователя по ID**\n\n"
                "Используйте команду /admin_user <user_id> для поиска информации о пользователе.\n\n"
                "Пример:\n"
                "`/admin_user 123456789`"
            )
            
        elif callback_data == "cards_stats":
            await query.edit_message_text(
                "📈 **Статистика карт**\n\n"
                "Функция статистики карт в разработке."
            )
                    
        elif callback_data.startswith("reset_confirm_"):
            user_id = callback_data.replace("reset_confirm_", "")
            await reset_user_confirmed(query, context, user_id)
        elif callback_data == "reset_cancel":
            await show_admin_main_menu(query, context)
            
        else:
            await query.edit_message_text(f"❌ Неизвестная команда: {callback_data}")
    except Exception as e:
        logger.error(f"Ошибка в админ callback: {e}")
        await query.edit_message_text("❌ Ошибка при обработке запроса")

async def show_admin_main_menu(query, context):
    """Главное меню админ-панели"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👤 Управление пользователями", callback_data="admin_users")],
        [InlineKeyboardButton("🎴 Управление картами", callback_data="admin_cards")],
        [InlineKeyboardButton("🎁 Выдача", callback_data="admin_give")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")]
    ]
    
    await query.edit_message_text(
        "🛠️ **Панель администратора**\nВыберите раздел:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_admin_stats(query, context):
    """Показать статистику"""
    load_data()
    
    total_users = len(data["users"])
    total_cards = sum(len(user["cards"]) for user in data["users"].values())
    total_wc = sum(user.get("wc", 0) for user in data["users"].values())
    
    card_stats = {}
    for user in data["users"].values():
        for card_id, card_info in user["cards"].items():
            if card_id not in card_stats:
                card_stats[card_id] = 0
            card_stats[card_id] += card_info["count"]
    
    most_common = sorted(card_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    stats_text = f"""📊 **Статистика бота**

👥 Пользователи: {total_users}
🎴 Всего карт: {total_cards}
💰 Общий баланс WC: {total_wc}

🏆 Самые популярные карты:
"""
    for card_id, count in most_common:
        card_name = CARD_ID_MAP.get(card_id, {}).get("name", "Неизвестно")
        stats_text += f"  {card_name}: {count}\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]]
    
    await query.edit_message_text(
        stats_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_admin_users_menu(query, context):
    """Меню управления пользователями"""
    keyboard = [
        [InlineKeyboardButton("📋 Список пользователей", callback_data="user_list")],
        [InlineKeyboardButton("🔍 Поиск по ID", callback_data="user_search")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        "👤 **Управление пользователями**\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_admin_cards_menu(query, context):
    """Меню управления картами"""
    keyboard = [
        [InlineKeyboardButton("📈 Статистика карт", callback_data="cards_stats")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        "🎴 **Управление картами**\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_admin_broadcast_menu(query, context):
    """Меню рассылки"""
    keyboard = [
        [InlineKeyboardButton("📢 Начать рассылку", callback_data="broadcast_start")],
        [InlineKeyboardButton("📊 Статистика рассылки", callback_data="broadcast_stats")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        "📢 **Рассылка сообщений**\n\nИспользуйте команду /broadcast <сообщение> для отправки.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def reset_user_confirmed(query, context, user_id):
    """Подтвержденный сброс пользователя"""
    load_data()
    
    if user_id in data["users"]:
        old_data = data["users"][user_id]
        data["users"][user_id] = {
            "cards": {},
            "wc": 0,
            "last_card_time": "2000-01-01T00:00:00",
            "chance_bonus": {"экстра": 0.0, "боссы": 0.0},
            "elementals": {},
            "active_craft": None
        }
        save_data()
        
        await query.edit_message_text(
            f"✅ Пользователь {user_id} сброшен!\n"
            f"Удалено: {len(old_data.get('cards', {}))} карт, {old_data.get('wc', 0)} WC"
        )
    else:
        await query.edit_message_text("❌ Пользователь не найден")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика бота через команду"""
    if not await admin_auth(update, context):
        return
    
    load_data()
    
    total_users = len(data["users"])
    total_cards = sum(len(user["cards"]) for user in data["users"].values())
    total_wc = sum(user.get("wc", 0) for user in data["users"].values())
    
    stats_text = f"""📊 **Статистика бота**

👥 Пользователи: {total_users}
🎴 Всего карт: {total_cards}
💰 Общий баланс WC: {total_wc}"""
    
    await update.message.reply_text(stats_text)

async def admin_user_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление пользователями через команду"""
    if not await admin_auth(update, context):
        return
    
    if context.args:
        user_id = context.args[0]
        load_data()
        user_data = data["users"].get(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ Пользователь не найден")
            return
        
        cards_count = sum(card["count"] for card in user_data["cards"].values())
        wc_balance = user_data.get("wc", 0)
        
        user_info = f"""👤 **Информация о пользователе** {user_id}

💰 Баланс: {wc_balance} WC
🎴 Карт в коллекции: {cards_count}
📅 Последняя карта: {user_data.get('last_card_time', 'Никогда')}"""
        
        await update.message.reply_text(user_info)
        return

async def admin_add_wc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить WC пользователю через команду"""
    if not await admin_auth(update, context):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /addwc <user_id> <amount>")
        return
    
    user_id, amount = context.args[0], int(context.args[1])
    load_data()
    
    if user_id not in data["users"]:
        await update.message.reply_text("❌ Пользователь не найден")
        return
    
    data["users"][user_id]["wc"] = data["users"][user_id].get("wc", 0) + amount
    save_data()
    admin_name = update.effective_user.first_name
    notification_text = f"🎁 Администратор {admin_name} выдал вам {amount} WC!"
    success = await notify_user(context.bot, user_id, notification_text)
    
    if not success:
        logger.warning(f"Не удалось уведомить пользователя {user_id} о выдаче WC")
    
    await update.message.reply_text(f"✅ Добавлено {amount} WC пользователю {user_id}")

async def admin_add_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить карту пользователю через команду"""
    if not await admin_auth(update, context):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /addcard <user_id> <card_id> [count]")
        return
    
    user_id, card_id = context.args[0], context.args[1].upper()
    count = int(context.args[2]) if len(context.args) > 2 else 1
    
    # Нормализуем ID элементаля
    card_id = normalize_elemental_id(card_id)
    
    load_data()
    
    if user_id not in data["users"]:
        await update.message.reply_text("❌ Пользователь не найден")
        return
    
    user_data = data["users"][user_id]
    
    if card_id in CARD_ID_MAP:
        card_info = CARD_ID_MAP[card_id]
        
        if card_id in user_data["cards"]:
            user_data["cards"][card_id]["count"] += count
        else:
            user_data["cards"][card_id] = {
                "name": card_info["name"],
                "rarity": card_info["rarity"],
                "count": count,
                "url": card_info.get("url")
            }
    elif card_id in ELEMENTAL_ID_MAP:
        # Добавление элементаля
        add_elemental(user_data, card_id)
    else:
        await update.message.reply_text("❌ Карта не найдена")
        return
    
    save_data()
    admin_name = update.effective_user.first_name
    if card_id in CARD_ID_MAP:
        notification_text = f"🎁 Администратор {admin_name} выдал вам карту: {CARD_ID_MAP[card_id]['name']} ({count} шт.)!"
    else:
        notification_text = f"🎁 Администратор {admin_name} выдал вам элементаля: {ELEMENTAL_ID_MAP[card_id]['name']}!"
    
    success = await notify_user(context.bot, user_id, notification_text)
    
    if not success:
        logger.warning(f"Не удалось уведомить пользователя {user_id} о выдаче")
    
    if card_id in CARD_ID_MAP:
        await update.message.reply_text(
            f"✅ Добавлено {count} × {CARD_ID_MAP[card_id]['name']} пользователю {user_id}"
        )
    else:
        await update.message.reply_text(
            f"✅ Добавлен элементаль {ELEMENTAL_ID_MAP[card_id]['name']} пользователю {user_id}"
        )

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Рассылка сообщения всем пользователям"""
    if not await admin_auth(update, context):
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /broadcast <сообщение>")
        return
    
    message = " ".join(context.args)
    load_data()
    
    users = data["users"]
    success = 0
    failed = 0
    
    progress_msg = await update.message.reply_text(f"📢 Рассылка... 0/{len(users)}")
    
    for i, user_id in enumerate(users.keys()):
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            success += 1
        except Exception as e:
            failed += 1
        
        if i % 10 == 0:
            await progress_msg.edit_text(
                f"📢 Рассылка... {i+1}/{len(users)}\n"
                f"✅ Успешно: {success}\n❌ Ошибок: {failed}"
            )
    
    await progress_msg.edit_text(
        f"✅ Рассылка завершена!\n"
        f"✅ Успешно: {success}\n❌ Ошибок: {failed}"
    )

async def admin_reset_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс данных пользователя"""
    if not await admin_auth(update, context):
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /resetuser <user_id>")
        return
    
    user_id = context.args[0]
    load_data()
    
    if user_id not in data["users"]:
        await update.message.reply_text("❌ Пользователь не найден")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, сбросить", callback_data=f"reset_confirm_{user_id}"),
            InlineKeyboardButton("❌ Отмена", callback_data="reset_cancel")
        ]
    ]
    
    await update.message.reply_text(
        f"⚠️ Вы уверены, что хотите сбросить данные пользователя {user_id}?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@with_translation
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать текущую погоду"""
    current_weather = get_current_weather()
    weather_info = WEATHER_SYSTEM[current_weather]
    
    t = context.t
    user_lang = lang_manager.get_user_lang(update.effective_user.id)
    
    last_change = datetime.fromisoformat(data["weather"]["changed_at"])
    next_change = last_change + timedelta(hours=weather_info["duration"])
    time_left = next_change - datetime.now()
    hours_left = int(time_left.total_seconds() / 3600)
    minutes_left = int((time_left.total_seconds() % 3600) / 60)
    
    weather_descriptions = {
        "ясная луна": "Серебристый свет озаряет небо, создавая идеальные условия для охоты за обычными картами",
        "грибная слякоть со снегом": "Странная грибная погода приносит необычные мутации Волзеров",
        "буря со мглой покрывающая небо": "Эпическая буря скрывает в своих вихрях редких Волзеров",
        "торнадо небес": "Небесные вихри закручивают реальность, принося мощных Волзеров",
        "мозговой штурм": "Психическая буря рождает интеллектуальных Волзеров с особыми способностями",
        "метеоритный дождь": "Космические обломки приносят инопланетных Волзеров из глубин космоса",
        "Цунами из-поднутри": "Аномалия пространства выворачивает реальность наизнанку",
        "Ано-р-мальный туман": "Туман искажает законы вероятности, открывая портал к уникальным Волзерам",
        "Затмение Марса": "Редчайшее космическое событие, открывающее доступ к легендарным Волзерам"
    }
    
    # Перевод для английского
    weather_descriptions_en = {
        "ясная луна": "Silvery moonlight illuminates the sky, creating perfect conditions for hunting common cards",
        "грибная слякоть со снегом": "Strange mushroom weather brings unusual Walzer mutations",
        "буря со мглой покрывающая небо": "Epic storm hides rare Walzers in its whirlwinds",
        "торнадо небес": "Celestial tornadoes twist reality, bringing powerful Walzers",
        "мозговой штурм": "Psychic storm gives birth to intelligent Walzers with special abilities",
        "метеоритный дождь": "Cosmic debris brings alien Walzers from deep space",
        "Цунами из-поднутри": "Space anomaly turns reality inside out",
        "Ано-р-мальный туман": "Fog distorts probability laws, opening a portal to unique Walzers",
        "Затмение Марса": "Rarest cosmic event, granting access to legendary Walzers"
    }
    
    if user_lang == 'en':
        description = weather_descriptions_en.get(current_weather, weather_descriptions[current_weather])
    else:
        description = weather_descriptions[current_weather]
    
    text = (
        f"{weather_info['emoji']} **{current_weather.upper()}**\n\n"
        f"{t('weather_chance', chance=weather_info['card_chance'])}\n"
        f"{t('weather_changes_in', hours=hours_left, minutes=minutes_left)}\n\n"
        f"📖 {description}\n\n"
    )
    
    weather_cards = CARDS.get("погодные", [])
    if weather_cards:
        random_card = random.choice(weather_cards)
        card_name = translate_card_name(random_card['name'], user_lang) if user_lang != 'ru' else random_card['name']
        text += f"🎴 Пример погодной карты: **{card_name}**\n\n"
    
    card_chance = weather_info["card_chance"]
    
    if card_chance <= 5:
        rarity_text = "🌕 VERY RARE" if user_lang == 'en' else "🌕 ОЧЕНЬ РЕДКАЯ"
        explanation = "Best time to hunt for cards!" if user_lang == 'en' else "Лучшее время для охоты за картами!"
    elif card_chance <= 10:
        rarity_text = "🌤️ RARE" if user_lang == 'en' else "🌤️ РЕДКАЯ"
        explanation = "Good chance to get weather cards" if user_lang == 'en' else "Хороший шанс получить погодную карту"
    elif card_chance <= 15:
        rarity_text = "💨 MEDIUM" if user_lang == 'en' else "💨 СРЕДНЯЯ"
        explanation = "Stable chances for cards" if user_lang == 'en' else "Стабильные шансы на карты"
    else:
        rarity_text = "🌫️ COMMON" if user_lang == 'en' else "🌫️ ЧАСТАЯ"
        explanation = "You can farm cards calmly" if user_lang == 'en' else "Можно спокойно фармить карты"
    
    text += f"📈 {rarity_text} - {explanation}"
    
    await update.message.reply_text(text, parse_mode='Markdown')

@with_translation
async def next_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать возможные следующие погоды"""
    current = get_current_weather()
    
    t = context.t
    user_lang = lang_manager.get_user_lang(update.effective_user.id)
    
    text = f"🌌 **Возможная следующая погода:**\n\n"
    
    weather_types = list(WEATHER_SYSTEM.keys())
    
    weights = []
    for weather_type in weather_types:
        if weather_type == current:
            weight = 0
        elif weather_type in data["weather"].get("previous", []):
            weight = (100 - WEATHER_SYSTEM[weather_type]["card_chance"]) * 0.3
        else:
            weight = 100 - WEATHER_SYSTEM[weather_type]["card_chance"]
        weights.append(weight)
    
    total_weight = sum(weights)
    
    for i, weather_type in enumerate(weather_types):
        if total_weight > 0:
            chance = (weights[i] / total_weight) * 100
        else:
            chance = 0
            
        emoji = WEATHER_SYSTEM[weather_type]["emoji"]
        card_chance = WEATHER_SYSTEM[weather_type]["card_chance"]
        
        if weather_type == current:
            text += f"{emoji} {weather_type}: CURRENT\n"
        elif chance > 0:
            text += f"{emoji} {weather_type}: {chance:.1f}% (card chance: {card_chance}%)\n"
        else:
            text += f"{emoji} {weather_type}: IMPOSSIBLE\n"
    
    text += f"\n💫 Current: {current} {WEATHER_SYSTEM[current]['emoji']}"
    
    await update.message.reply_text(text)

def get_current_weather():
    """Получить текущую погоду с защитой от повторов"""
    if "weather" not in data:
        weather_types = list(WEATHER_SYSTEM.keys())
        initial_weather = random.choice(weather_types)
        data["weather"] = {
            "type": initial_weather,
            "changed_at": datetime.now().isoformat(),
            "duration": WEATHER_SYSTEM[initial_weather]["duration"],
            "previous": []
        }
        save_data()
    
    last_change = datetime.fromisoformat(data["weather"]["changed_at"])
    hours_passed = (datetime.now() - last_change).total_seconds() / 3600
    
    if hours_passed >= data["weather"]["duration"]:
        change_weather()
    
    return data["weather"]["type"]

def change_weather():
    """Смена погоды с весами и защитой от повторов"""
    current_weather = data["weather"]["type"]
    
    if "previous" not in data["weather"]:
        data["weather"]["previous"] = []
    
    data["weather"]["previous"].append(current_weather)
    if len(data["weather"]["previous"]) > 3:
        data["weather"]["previous"].pop(0)
    
    weather_types = list(WEATHER_SYSTEM.keys())
    weights = []
    
    for weather_type in weather_types:
        base_weight = 100 - WEATHER_SYSTEM[weather_type]["card_chance"]
        
        if weather_type == current_weather:
            weight = 0
        elif weather_type in data["weather"]["previous"]:
            weight = base_weight * 0.3
        else:
            weight = base_weight
        
        weights.append(weight)
    
    if sum(weights) == 0:
        data["weather"]["previous"] = []
        weights = [100 - WEATHER_SYSTEM[wt]["card_chance"] for wt in weather_types]
        weights[weather_types.index(current_weather)] = 0
    
    new_weather = random.choices(weather_types, weights=weights)[0]
    
    data["weather"] = {
        "type": new_weather,
        "changed_at": datetime.now().isoformat(),
        "duration": WEATHER_SYSTEM[new_weather]["duration"],
        "previous": data["weather"]["previous"]
    }
    save_data()
    
    logger.info(f"Погода сменилась: {current_weather} -> {new_weather}")
    return new_weather

@with_translation
async def chance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /chance с учетом погоды"""
    user = update.effective_user
    logger.info(f"Команда /chance от пользователя {user.id}")
    
    load_data()
    uid = str(user.id)
    user_data = get_user(uid)
    bonus = user_data.get("chance_bonus", {"экстра": 0.0, "боссы": 0.0})

    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)

    current_weather = get_current_weather()
    weather_info = WEATHER_SYSTEM[current_weather]

    text_lines = []
    text_lines.append(f"{weather_info['emoji']} **{t('weather_current', name=current_weather, emoji=weather_info['emoji'])}**")
    text_lines.append(f"🎯 {t('weather_chance', chance=weather_info['card_chance'])}\n")

    text_lines.append("🎰 Общие шансы на карты:\n")

    order = ["обычная", "необычная", "редкая", "эпическая", "легендарная", "погодные", "донатная", "экстра", "боссы", "элементали"]
    
    for rarity in order:
        if rarity == "погодные":
            text_lines.append(f"🌪️ {t(f'rarity_{rarity}')} — {weather_info['card_chance']}% (зависит от погоды)")
        elif rarity == "донатная":
            text_lines.append(f"💎 {t(f'rarity_{rarity}')} — Только в магазине")
        elif rarity == "элементали":
            text_lines.append(f"🌌 {t(f'rarity_{rarity}')} — Только в магазине")
        elif rarity in ("экстра", "боссы"):
            total = RARITY_CHANCES.get(rarity, 0) + bonus.get(rarity, 0.0)
            text_lines.append(f"🔥 {t(f'rarity_{rarity}')} — {total:.4f}% (базовый {RARITY_CHANCES.get(rarity, 0)}%)")
        else:
            base = RARITY_CHANCES.get(rarity, 0)
            text_lines.append(f"• {t(f'rarity_{rarity}')} — {base}%")

    text = "\n".join(text_lines)
    await update.message.reply_text(text, reply_markup=main_menu())

# ========== ПАСЬЯНС "ЗИМБАБВИЙСКИЕ ДОЛЛАРЫ" ==========
SUITS = ['♦️', '♣️', '♥️', '♠️']
RANKS = ['2', '3', 'Э', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class SolitaireGame:
    def __init__(self, user_id):
        self.user_id = user_id
        self.stock = []
        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.tableau = [[] for _ in range(7)]
        self.selected = None
        self.score = 0
        
    def init_game(self):
        deck = []
        for suit in SUITS:
            for rank in RANKS:
                value = RANKS.index(rank) + 2
                zim_value = value * 100
                card = {
                    'suit': suit,
                    'rank': rank,
                    'value': value,
                    'zim_value': zim_value,
                    'face_up': False
                }
                deck.append(card)
        
        random.shuffle(deck)
        
        for i in range(7):
            for j in range(i + 1):
                card = deck.pop()
                if j == i:
                    card['face_up'] = True
                self.tableau[i].append(card)
        
        self.stock = deck
        
    def draw_card(self):
        if not self.stock and self.waste:
            self.stock = self.waste[::-1]
            self.waste = []
            for card in self.stock:
                card['face_up'] = False
        
        if self.stock:
            card = self.stock.pop()
            card['face_up'] = True
            self.waste.append(card)
            return True
        return False
    
    def can_move_to_foundation(self, card, suit):
        if not self.foundations[suit]:
            return card['rank'] == 'A'
        
        top_card = self.foundations[suit][-1]
        current_index = RANKS.index(card['rank'])
        top_index = RANKS.index(top_card['rank'])
        return current_index == top_index + 1 and card['suit'] == suit
    
    def can_move_to_tableau(self, card, pile_index):
        if not self.tableau[pile_index]:
            return card['rank'] == 'K'
        
        top_card = self.tableau[pile_index][-1]
        current_index = RANKS.index(card['rank'])
        top_index = RANKS.index(top_card['rank'])
        
        red_suits = ['♦️', '♥️']
        black_suits = ['♣️', '♠️']
        card_color = 'red' if card['suit'] in red_suits else 'black'
        top_color = 'red' if top_card['suit'] in red_suits else 'black'
        
        return current_index == top_index - 1 and card_color != top_color
    
    def move_card(self, source, destination):
        src_type, *src_args = source
        dest_type, *dest_args = destination
        
        if src_type == 'waste' and self.waste:
            card = self.waste[-1]
            cards_to_move = [card]
        elif src_type == 'foundation' and src_args:
            suit = src_args[0]
            if self.foundations[suit]:
                card = self.foundations[suit][-1]
                cards_to_move = [card]
            else:
                return False, "Пустая фундаментная стопка"
        elif src_type == 'tableau' and len(src_args) == 2:
            pile_idx, card_idx = src_args
            if 0 <= pile_idx < 7 and card_idx < len(self.tableau[pile_idx]):
                cards_to_move = self.tableau[pile_idx][card_idx:]
                if not all(card['face_up'] for card in cards_to_move):
                    return False, "Не все карты открыты"
            else:
                return False, "Неверный индекс карты"
        else:
            return False, "Неверный источник"
        
        if dest_type == 'foundation' and dest_args:
            suit = dest_args[0]
            if len(cards_to_move) == 1 and self.can_move_to_foundation(cards_to_move[0], suit):
                card = cards_to_move[0]
                if src_type == 'waste':
                    self.waste.pop()
                elif src_type == 'foundation':
                    self.foundations[src_args[0]].pop()
                elif src_type == 'tableau':
                    self.tableau[pile_idx] = self.tableau[pile_idx][:card_idx]
                
                self.foundations[suit].append(card)
                self.score += card['zim_value']
                return True, f"+{card['zim_value']} зимбабвийских долларов!"
                
        elif dest_type == 'tableau' and dest_args:
            pile_idx = dest_args[0]
            if len(cards_to_move) == 1 and self.can_move_to_tableau(cards_to_move[0], pile_idx):
                card = cards_to_move[0]
                if src_type == 'waste':
                    self.waste.pop()
                elif src_type == 'foundation':
                    self.foundations[src_args[0]].pop()
                elif src_type == 'tableau':
                    src_pile_idx = src_args[0]
                    self.tableau[src_pile_idx] = self.tableau[src_pile_idx][:card_idx]
                
                self.tableau[pile_idx].append(card)
                return True, "Карта перемещена"
        
        return False, "Невозможный ход"
    
    def check_victory(self):
        total_cards_in_foundations = sum(len(pile) for pile in self.foundations.values())
        return total_cards_in_foundations == 52
    
    def get_game_state(self):
        return {
            'stock_count': len(self.stock),
            'waste_top': self.waste[-1] if self.waste else None,
            'foundations': self.foundations,
            'tableau': self.tableau,
            'score': self.score,
            'selected': self.selected
        }

solitaire_games = {}

@with_translation
async def solitaire_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало новой игры в пасьянс"""
    user = update.effective_user
    user_id = str(user.id)
    
    t = context.t
    
    game = SolitaireGame(user_id)
    game.init_game()
    solitaire_games[user_id] = game
    
    text = render_solitaire_game(game, context)
    keyboard = solitaire_keyboard(game, context)
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

def render_solitaire_game(game, context=None):
    """Отрисовка состояния игры с переводом"""
    t = context.t if context and hasattr(context, 't') else lambda key, **kwargs: key
    
    state = game.get_game_state()
    text = t('solitaire_title') + "\n\n"
    
    text += f"💰 *{t('solitaire_score', score=state['score'])}*\n"
    text += f"💵 *{t('solitaire_wc', wc=state['score'] // 100)}*\n\n"
    
    stock_display = "📁" if state['stock_count'] > 0 else "🃏"
    waste_display = state['waste_top']['rank'] + state['waste_top']['suit'] if state['waste_top'] else "🃏"
    text += f"Сток: {stock_display} | Отбой: {waste_display}\n\n"
    
    foundations_line = "Фундаменты: "
    for suit in SUITS:
        if state['foundations'][suit]:
            top_card = state['foundations'][suit][-1]
            foundations_line += f"{top_card['rank']}{suit} "
        else:
            foundations_line += f"□{suit} "
    text += foundations_line + "\n\n"
    
    text += "Стопки:\n"
    max_pile_height = max(len(pile) for pile in state['tableau'])
    
    for row in range(max_pile_height):
        line = ""
        for pile_idx, pile in enumerate(state['tableau']):
            if row < len(pile):
                card = pile[row]
                if card['face_up']:
                    line += f"{card['rank']}{card['suit']} "
                else:
                    line += "🃏 "
            else:
                line += "   "
        text += line + "\n"
    
    text += "\n💡 *100 зимбабвийских долларов = 1 WC*"
    return text

def solitaire_keyboard(game, context=None):
    """Клавиатура для пасьянса с переводом"""
    t = context.t if context and hasattr(context, 't') else lambda key, **kwargs: key
    
    state = game.get_game_state()
    keyboard = []
    
    row = []
    row.append(InlineKeyboardButton(t('solitaire_draw'), callback_data="sol_draw"))
    if state['waste_top']:
        row.append(InlineKeyboardButton(t('solitaire_waste'), callback_data="sol_waste"))
    keyboard.append(row)
    
    row = []
    for i in range(7):
        pile = state['tableau'][i]
        if pile:
            top_card = pile[-1]
            label = f"{i+1}🃏" if not top_card['face_up'] else f"{i+1}{top_card['rank']}{top_card['suit']}"
        else:
            label = f"{i+1}□"
        row.append(InlineKeyboardButton(label, callback_data=f"sol_pile:{i}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    row = []
    for suit in SUITS:
        foundation = state['foundations'][suit]
        if foundation:
            top_card = foundation[-1]
            label = f"{top_card['rank']}{suit}"
        else:
            label = f"□{suit}"
        row.append(InlineKeyboardButton(label, callback_data=f"sol_base:{suit}"))
    keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton(t('solitaire_new'), callback_data="sol_new"),
        InlineKeyboardButton(t('solitaire_cashout'), callback_data="sol_cashout")
    ])
    
    return InlineKeyboardMarkup(keyboard)

@with_translation
async def solitaire_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    clicked_user_id = str(query.from_user.id)

    if clicked_user_id not in solitaire_games:
        await query.answer("Это не твоя игра! Начни свою: /solitaire", show_alert=True)
        return

    game = solitaire_games[clicked_user_id]
    data = query.data

    await query.answer()

    try:
        if data == 'sol_draw':
            if game.draw_card():
                await query.edit_message_text(
                    render_solitaire_game(game, context),
                    reply_markup=solitaire_keyboard(game, context),
                    parse_mode='Markdown'
                )
            else:
                await query.answer("Сток пуст!", show_alert=True)

        elif data == 'sol_waste':
            game.selected = ('waste',)
            await present_solitaire_destinations(query, game, context)

        elif data.startswith('sol_pile:'):
            pile_idx = int(data.split(':')[1])
            pile = game.tableau[pile_idx]
            if not pile:
                await query.answer("Стопка пуста!", show_alert=True)
                return
            card_idx = len(pile) - 1
            while card_idx >= 0 and not pile[card_idx]['face_up']:
                card_idx -= 1
            if card_idx < 0:
                await query.answer("Нет открытых карт!", show_alert=True)
            else:
                game.selected = ('tableau', pile_idx, card_idx)
                await present_solitaire_destinations(query, game, context)

        elif data.startswith('sol_base:'):
            suit = data.split(':')[1]
            if game.foundations[suit]:
                game.selected = ('foundation', suit)
                await present_solitaire_destinations(query, game, context)
            else:
                await query.answer("Фундамент пуст!", show_alert=True)

        elif data.startswith('dest_pile:'):
            if not game.selected:
                return
            dest_pile = int(data.split(':')[1])
            success, message = game.move_card(game.selected, ('tableau', dest_pile))
            game.selected = None
            await query.edit_message_text(
                f"{render_solitaire_game(game, context)}\n\n{message}",
                reply_markup=solitaire_keyboard(game, context),
                parse_mode='Markdown'
            )
            if success and game.check_victory():
                t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
                await query.message.reply_text(t('solitaire_victory'))

        elif data.startswith('dest_base:'):
            if not game.selected:
                return
            suit = data.split(':')[1]
            success, message = game.move_card(game.selected, ('foundation', suit))
            game.selected = None
            await query.edit_message_text(
                f"{render_solitaire_game(game, context)}\n\n{message}",
                reply_markup=solitaire_keyboard(game, context),
                parse_mode='Markdown'
            )
            if success and game.check_victory():
                t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
                await query.message.reply_text(t('solitaire_victory'))

        elif data == 'sol_new':
            game.init_game()
            game.score = 0
            await query.edit_message_text(
                render_solitaire_game(game, context),
                reply_markup=solitaire_keyboard(game, context),
                parse_mode='Markdown'
            )

        elif data == 'sol_cashout':
            wc_earned = game.score // 100
            if wc_earned <= 0:
                t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
                await query.answer(t('solitaire_no_money'), show_alert=True)
                return

            load_data()
            user_data = get_user(clicked_user_id)
            user_data["wc"] += wc_earned
            save_data()

            t = context.t if hasattr(context, 't') else lambda key, **kwargs: key

            await query.message.reply_text(
                f"Обменял {game.score:,} зимбабвийских долларов на {wc_earned} WC!\n"
                f"{t('balance', count=user_data['wc'], forms=t('wc_forms'))}",
                reply_markup=main_menu()
            )

            game.init_game()
            game.score = 0
            await query.edit_message_text(
                render_solitaire_game(game, context),
                reply_markup=solitaire_keyboard(game, context),
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Ошибка в пасьянса [user {clicked_user_id}]: {e}")
        await query.answer("Ошибка! Начни новую игру: /solitaire", show_alert=True)

async def present_solitaire_destinations(query, game, context=None):
    keyboard = []
    
    row = []
    for i in range(7):
        row.append(InlineKeyboardButton(str(i+1), callback_data=f"dest_pile:{i}"))
    keyboard.append(row)
    
    row = []
    for suit in SUITS:
        row.append(InlineKeyboardButton(suit, callback_data=f"dest_base:{suit}"))
    keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="sol_new")])
    
    await query.edit_message_text(
        "Выберите куда переместить карту:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====================== ШАМАНСТВО ======================

shaman_sessions = {}          # {user_id: {"victims": {item_id: count}, "wish": dict или None}}
last_shaman_click = {}        # Защита от спама: {user_id: timestamp последнего клика}

# Константы
SHAMAN_TIMES_MIN = {
    "обычная": 5, "необычная": 10, "редкая": 15,
    "эпическая": 20, "легендарная": 30, "экстра": 40,
    "боссы": 50, "погодные": 25, "элементали": 15
}

SHAMAN_SUCCESS_CHANCE_PER_CARD = {
    "обычная": 5.0, "необычная": 10.0, "редкая": 15.0,
    "эпическая": 20.0, "легендарная": 25.0, "экстра": 30.0,
    "боссы": 40.0, "погодные": 20.0, "элементали": 100.0
}

SHAMAN_MAX_PER_TYPE = {
    "обычная": 20, "необычная": 15, "редкая": 10,
    "эпическая": 8, "легендарная": 5, "экстра": 3,
    "боссы": 2, "погодные": 5, "элементали": 10
}

TROLL_CHANCE = 5.0
SUCCESS_BASE = 10.0
SUCCESS_PER_MIN = 1.0
MAX_SUCCESS = 80.0

@with_translation
async def shaman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск шаманства"""
    user_id = str(update.effective_user.id)
    load_data()
    user = get_user(user_id)

    t = context.t

    now = datetime.now().timestamp()
    if user.get("shaman_cooldown", 0) > now:
        rem = int((user["shaman_cooldown"] - now) // 60)
        await update.message.reply_text(t('shaman_cooldown', minutes=rem), reply_markup=main_menu())
        return

    shaman_sessions[user_id] = {"victims": {}, "wish": None}
    await show_shaman_main_menu(update.message, context)

async def show_shaman_main_menu(obj, context):
    """Универсальная функция: работает и с message, и с query"""
    user_id = str(obj.from_user.id)
    session = shaman_sessions.get(user_id, {"victims": {}, "wish": None})

    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    user_lang = lang_manager.get_user_lang(user_id) if hasattr(lang_manager, 'get_user_lang') else 'ru'

    victims_count = sum(session["victims"].values())
    wish_text = t('shaman_no_wish')
    if session["wish"]:
        w = session["wish"]
        if w["type"] == "elem":
            name = ELEMENTALS[w["id"]]["name"]
        else:
            card = CARD_ID_MAP[w["id"]]
            name = translate_card_name(card['name'], user_lang) if user_lang != 'ru' else card['name']
        wish_text = f"{name} ({w['cost']} WC)"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🃏 " + (t('shaman_select_victims') if 'shaman_select_victims' in TRANSLATIONS[user_lang] else "Выбери жертвы"), callback_data="shaman_pick_menu")],
        [InlineKeyboardButton(f"🔥 " + (t('shaman_start') if 'shaman_start' in TRANSLATIONS[user_lang] else "Начать") + f" ({victims_count})", callback_data="shaman_start")],
        [InlineKeyboardButton("❌ " + (t('cancel') if 'cancel' in TRANSLATIONS[user_lang] else "Отмена"), callback_data="shaman_cancel")]
    ])

    text = (
        f"🔮 *{t('shaman_title')}*\n\n"
        f"{t('shaman_victims', count=victims_count)}\n"
        f"{t('shaman_wish', wish=wish_text)}\n\n"
        f"{t('shaman_desc')}"
    )

    if hasattr(obj, "reply_text"):
        await obj.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await obj.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

async def show_pick_menu(query, context):
    """Меню выбора категории жертв"""
    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚪ " + t('rarity_common'), callback_data="shaman_pick_обычная"),
         InlineKeyboardButton("🔵 " + t('rarity_uncommon'), callback_data="shaman_pick_необычная")],
        [InlineKeyboardButton("🟢 " + t('rarity_rare'), callback_data="shaman_pick_редкая"),
         InlineKeyboardButton("🌌 " + t('rarity_elemental'), callback_data="shaman_pick_элементали")],
        [InlineKeyboardButton("◀ " + t('back'), callback_data="shaman_back_main")]
    ])

    await query.edit_message_text("🃏 *" + t('shaman_select_victims') + "*", parse_mode="Markdown", reply_markup=kb)

async def show_items_for_category(query, context, category):
    """Показывает предметы (карты или элементали) выбранной категории"""
    user_id = str(query.from_user.id)
    load_data()
    user = get_user(user_id)
    session = shaman_sessions.get(user_id, {"victims": {}})

    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    user_lang = lang_manager.get_user_lang(user_id) if hasattr(lang_manager, 'get_user_lang') else 'ru'

    items = []
    if category == "элементали":
        for eid, data in user.get("elementals", {}).items():
            cnt = data.get("level", 1)
            if cnt > 0 and eid in ELEMENTALS:
                items.append((eid, cnt, ELEMENTALS[eid]["name"]))
    else:
        for cid, data in user.get("cards", {}).items():
            if cid in CARD_ID_MAP and CARD_ID_MAP[cid]["rarity"] == category:
                cnt = data.get("count", 0)
                if cnt > 0:
                    card_name = CARD_ID_MAP[cid]["name"]
                    if user_lang != 'ru':
                        card_name = translate_card_name(card_name, user_lang)
                    items.append((cid, cnt, card_name))

    if not items:
        await query.answer(f"Нет {category} для жертв!", show_alert=True)
        return

    kb = []
    for iid, maxc, name in items:
        sel = session["victims"].get(iid, 0)
        lim = min(maxc, SHAMAN_MAX_PER_TYPE.get(category, 10))
        txt = f"{name} — {sel}/{lim}"
        kb.append([InlineKeyboardButton(txt, callback_data=f"shaman_toggle_{iid}")])

    kb.append([InlineKeyboardButton("◀ " + t('back'), callback_data="shaman_pick_menu")])

    await query.edit_message_text(
        f"*{category.capitalize()} для жертв*\nНажми → +1 / сброс",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def show_wish_menu(query, context):
    """Меню выбора желания"""
    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌌 " + t('rarity_elemental'), callback_data="shaman_wish_elem")],
        [InlineKeyboardButton("❌ " + t('shaman_no_wish'), callback_data="shaman_wish_none")],
        [InlineKeyboardButton("◀ " + t('back'), callback_data="shaman_back_main")]
    ])

    await query.edit_message_text(
        "✨ *" + t('shaman_select_wish') + "*\n(50% шанс при успехе, WC списываются сразу)",
        parse_mode="Markdown",
        reply_markup=kb
    )

@with_translation
async def shaman_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)

    print(f"ШАМАН КНОПКА НАЖАТА! data = {query.data!r}, user = {user_id}")
    
    if user_id not in shaman_sessions:
        await query.edit_message_text("Сессия истекла. /shaman")
        return

    session = shaman_sessions[user_id]

    logger.info(f"Шаман callback: {user_id} → {data}")

    try:
        if data == "shaman_back_main":
            await show_shaman_main_menu(query, context)

        elif data == "shaman_pick_menu":
            await show_pick_menu(query, context)

        elif data.startswith("shaman_pick_"):
            cat = data.replace("shaman_pick_", "")
            await show_items_for_category(query, context, cat)

        elif data.startswith("shaman_toggle_"):
            item_id = data.replace("shaman_toggle_", "")
            cat = "элементали" if item_id in ELEMENTALS else CARD_ID_MAP.get(item_id, {}).get("rarity")

            if not cat:
                await query.answer("Нельзя жертвовать это", show_alert=True)
                return

            load_data()
            user = get_user(user_id)

            max_cnt = (user["elementals"].get(item_id, {}).get("level", 0) if cat == "элементали"
                       else user["cards"].get(item_id, {}).get("count", 0))

            if max_cnt <= 0:
                await query.answer("У тебя этого нет!", show_alert=True)
                return

            sel = session["victims"].get(item_id, 0)
            lim = min(max_cnt, SHAMAN_MAX_PER_TYPE.get(cat, 10))

            if sel >= lim:
                session["victims"].pop(item_id, None)
                await query.answer("Сброшено")
            else:
                session["victims"][item_id] = sel + 1
                await query.answer(f"+1 → {sel+1}/{lim}")

            save_data()
            await show_items_for_category(query, context, cat)

        elif data == "shaman_wish_menu":
            await show_wish_menu(query, context)

        elif data.startswith("shaman_wish_"):
            if data == "shaman_wish_none":
                session["wish"] = None
                await query.answer("Желание снято")
                save_data()
                await show_shaman_main_menu(query, context)
                return

            rarity_or_type = data.replace("shaman_wish_", "")
            if rarity_or_type in ["эпическая", "легендарная", "экстра", "боссы"]:
                # Показать карты этой редкости
                card_ids = RARITY_TO_IDS.get(rarity_or_type, [])
                if not card_ids:
                    await query.answer("Нет карт этой редкости", show_alert=True)
                    return

                kb = []
                for cid in card_ids[:12]:  # лимит, чтобы не перегружать
                    if cid in CARD_ID_MAP:
                        card = CARD_ID_MAP[cid]
                        cost = int(card.get("price", 1000) * 0.5)
                        kb.append([InlineKeyboardButton(
                            f"{card['name']} — {cost} WC",
                            callback_data=f"shaman_wish_select_card_{cid}"
                        )])

                kb.append([InlineKeyboardButton("◀ " + (context.t('back') if hasattr(context, 't') else "Назад"), callback_data="shaman_wish_menu")])
                await query.edit_message_text(
                    f"Выбери карту ({rarity_or_type}):",
                    reply_markup=InlineKeyboardMarkup(kb)
                )
            elif rarity_or_type == "elem":
                kb = []
                for eid, el in ELEMENTALS.items():
                    cost = ELEMENTAL_WISH_COST
                    kb.append([InlineKeyboardButton(
                        f"{el['name']} — {cost} WC",
                        callback_data=f"shaman_wish_select_elem_{eid}"
                    )])
                kb.append([InlineKeyboardButton("◀ " + (context.t('back') if hasattr(context, 't') else "Назад"), callback_data="shaman_wish_menu")])
                await query.edit_message_text("Выбери элементаля:", reply_markup=InlineKeyboardMarkup(kb))

            elif data.startswith("shaman_wish_select_"):
                parts = data.split("_", 3)
                typ = parts[2]   # card / elem
                iid = parts[3]

                load_data()
                user = get_user(user_id)

                if typ == "card" and iid in CARD_ID_MAP:
                    cost = int(CARD_ID_MAP[iid]["price"] * 0.5)
                    if user["wc"] < cost:
                        await query.answer(f"Нужно {cost} WC!", show_alert=True)
                        return
                    user["wc"] -= cost
                    session["wish"] = {"type": "card", "id": iid, "cost": cost}
                    name = CARD_ID_MAP[iid]["name"]

                elif typ == "elem" and iid in ELEMENTALS:
                    cost = ELEMENTAL_WISH_COST
                    if user["wc"] < cost:
                        await query.answer(f"Нужно {cost} WC!", show_alert=True)
                        return
                    user["wc"] -= cost
                    session["wish"] = {"type": "elem", "id": iid, "cost": cost}
                    name = ELEMENTALS[iid]["name"]

                else:
                    await query.answer("Ошибка выбора", show_alert=True)
                    return

                save_data()

                # Показываем сообщение о выборе и сразу возвращаемся в главное меню
                await query.edit_message_text(
                    f"Выбрано: {name}",
                    parse_mode="Markdown"
                )
                # Даём небольшую паузу, чтобы пользователь увидел сообщение
                await asyncio.sleep(1.5)
                await show_shaman_main_menu(query, context)

        elif data == "shaman_cancel":
            wish = session.get("wish")
            if wish:
                load_data()
                user = get_user(user_id)
                user["wc"] += wish.get("cost", 0)
                save_data()
            shaman_sessions.pop(user_id, None)
            if user_id in last_shaman_click:
                del last_shaman_click[user_id]
            t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
            await query.edit_message_text("❌ " + t('shaman_cancel'), reply_markup=main_menu())

        elif data == "shaman_start":
            await start_shaman_ritual(query, context)

    except Exception as e:
        logger.error(f"Шаман ошибка у {user_id}: {e}", exc_info=True)
        await query.edit_message_text("❌ Что-то сломалось у шамана. Попробуй /shaman заново.")

@with_translation
async def start_shaman_ritual(query, context):
    user_id = str(query.from_user.id)
    session = shaman_sessions[user_id]

    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    user_lang = lang_manager.get_user_lang(user_id) if hasattr(lang_manager, 'get_user_lang') else 'ru'

    if not session["victims"]:
        await query.answer("Добавь хоть одну жертву!", show_alert=True)
        return

    load_data()
    user = get_user(user_id)

    now = datetime.now().timestamp()
    if user.get("shaman_cooldown", 0) > now:
        await query.answer("Кулдаун ещё не прошёл!", show_alert=True)
        return

    valid = {}
    total_min = 0
    total_ch = 0.0
    has_elem = False

    for iid, cnt in session["victims"].items():
        if iid in ELEMENTALS:
            avail = user["elementals"].get(iid, {}).get("level", 0)
            cnt = min(cnt, avail)
            if cnt > 0:
                valid[iid] = cnt
                total_min += cnt * SHAMAN_TIMES_MIN["элементали"]
                total_ch += cnt * 100.0
                has_elem = True
        elif iid in CARD_ID_MAP:
            r = CARD_ID_MAP[iid]["rarity"]
            avail = user["cards"].get(iid, {}).get("count", 0)
            cnt = min(cnt, avail)
            if cnt > 0 and r in SHAMAN_TIMES_MIN:
                valid[iid] = cnt
                total_min += cnt * SHAMAN_TIMES_MIN[r]
                total_ch += cnt * SHAMAN_SUCCESS_CHANCE_PER_CARD.get(r, 5.0)

    if not valid:
        await query.answer("Нет валидных жертв!", show_alert=True)
        return

    # Сжигаем
    for iid, cnt in valid.items():
        if iid in ELEMENTALS:
            user["elementals"][iid]["level"] -= cnt
            if user["elementals"][iid]["level"] <= 0:
                del user["elementals"][iid]
        else:
            user["cards"][iid]["count"] -= cnt
            if user["cards"][iid]["count"] <= 0:
                del user["cards"][iid]

    user["shaman_cooldown"] = int(now + total_min * 60)
    save_data()

    await query.edit_message_text("🕯️ Ритуал пошёл... Духи шепчут...")

    await asyncio.sleep(3)

    roll = random.uniform(0, 100)
    result = ""

    if has_elem:
        two_el = [e for e in ELEMENTALS if ELEMENTALS[e].get("elements", 1) == 2]
        if two_el:
            nid = random.choice(two_el)
            add_elemental(user, nid)
            result = t('shaman_success') + f" {t('shaman_result_elemental', name=ELEMENTALS[nid]['name'])}"
        else:
            user["wc"] += 100
            result = t('shaman_success') + " +100 WC"
    else:
        chance = min(SUCCESS_BASE + total_min * SUCCESS_PER_MIN, MAX_SUCCESS)
        if roll < TROLL_CHANCE:
            result = t('shaman_troll')
        elif roll < TROLL_CHANCE + chance:
            result = t('shaman_success')
            wish = session.get("wish")
            got_wish = False
            if wish and random.random() < 0.5:
                got_wish = True
                if wish["type"] == "card":
                    cid = wish["id"]
                    card_name = CARD_ID_MAP[cid]['name']
                    if user_lang != 'ru':
                        card_name = translate_card_name(card_name, user_lang)
                    user["cards"].setdefault(cid, {"count": 0, **CARD_ID_MAP[cid]})
                    user["cards"][cid]["count"] += 1
                    result += f"\n{t('shaman_result_card', name=card_name)}"
                else:
                    add_elemental(user, wish["id"])
                    result += f"\n{t('shaman_result_elemental', name=ELEMENTALS[wish['id']]['name'])}"

            if not got_wish:
                weights = {"эпическая":45, "легендарная":30, "экстра":15, "боссы":10}
                rar = random.choices(list(weights), weights=list(weights.values()))[0]
                cids = RARITY_TO_IDS.get(rar, [])
                if cids:
                    cid = random.choice(cids)
                    card_name = CARD_ID_MAP[cid]['name']
                    if user_lang != 'ru':
                        card_name = translate_card_name(card_name, user_lang)
                    user["cards"].setdefault(cid, {"count": 0, **CARD_ID_MAP[cid]})
                    user["cards"][cid]["count"] += 1
                    result += f"\n{t('shaman_result_card', name=card_name)} ({t(f'rarity_{rar}')})"
                else:
                    user["wc"] += 50
                    result += f"\n{t('shaman_result_wc', count=50)}"

            if random.random() < 0.08:
                base = [e for e in ELEMENTALS if ELEMENTALS[e].get("elements", 1) == 1]
                if base:
                    ex = random.choice(base)
                    add_elemental(user, ex)
                    result += f"\n{t('shaman_result_elemental', name=ELEMENTALS[ex]['name'])}"
        else:
            result = t('shaman_fail')

    save_data()
    shaman_sessions.pop(user_id, None)
    if user_id in last_shaman_click:
        del last_shaman_click[user_id]

    victims_total = sum(valid.values())
    chance_str = f"{total_ch:.1f}%" if has_elem else f"{chance:.1f}%"

    await query.edit_message_text(
        f"{result}\n\n"
        f"{t('shaman_victims', count=victims_total)}\n"
        f"Время: {total_min} мин\n"
        f"Шанс: {chance_str}\n"
        f"{t('shaman_cooldown', minutes=total_min)}",
        parse_mode="Markdown"
    )

@with_translation
async def top_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mode = query.data
    await show_top(query.message, context, mode)

async def show_top(message, context, mode="wc"):
    load_data()
    users = data["users"]
    
    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key
    
    if mode == "wc":
        sorted_users = sorted(users.items(), key=lambda x: x[1].get("wc", 0), reverse=True)[:10]
        title = t('top_wc')
    elif mode == "total":
        sorted_users = sorted(users.items(), key=lambda x: sum(c.get("count",0) for c in x[1].get("cards", {}).values()), reverse=True)[:10]
        title = t('top_cards')
    else:
        sorted_users = sorted(users.items(), key=lambda x: len(x[1].get("cards", {})), reverse=True)[:10]
        title = t('top_unique')
    
    text = f"🏆 *{t('top_title')}*\n\n{title}\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, (uid, u) in enumerate(sorted_users):
        username = u.get("username")
        first_name = u.get("first_name", "").strip()
        
        if username:
            name = f"@{username}"
        elif first_name and first_name != "None":
            name = first_name
        else:
            name = f"player {uid[-4:]}"
        
        if mode == "wc":
            value = f"{u.get('wc', 0):,} WC"
        elif mode == "total":
            value = f"{sum(c.get('count',0) for c in u.get('cards', {}).values())} cards"
        else:
            value = f"{len(u.get('cards', {}))} unique"
        
        text += f"{medals[i]} {name} — {value}\n"
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💰 WC", callback_data="wc"),
        InlineKeyboardButton("🎴 Count", callback_data="total"),
        InlineKeyboardButton("🌟 Unique", callback_data="unique")
    ]])

    bot_user = await context.bot.get_me()
    if message.from_user.id == bot_user.id:
        await message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

@with_translation
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_top(update.effective_message, context, "wc")

# ================== ПРОМОКОДЫ ==================
@with_translation
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🔑 Использование: /redeem КОД", reply_markup=main_menu())
        return

    code = " ".join(context.args).upper().strip()
    load_data()

    if "promo_codes" not in data:
        data["promo_codes"] = {}

    if code not in data["promo_codes"]:
        await update.message.reply_text("❌ Код не найден или истёк.", reply_markup=main_menu())
        return

    promo = data["promo_codes"][code]
    if promo["uses_left"] <= 0:
        await update.message.reply_text("❌ Код полностью использован.", reply_markup=main_menu())
        return

    user_id = str(update.effective_user.id)

    if user_id in promo.get("used_by", []):
        await update.message.reply_text("❌ Ты уже активировал этот код.", reply_markup=main_menu())
        return

    user = get_user(user_id)
    reward = promo["reward"]
    reward_text = ""

    if reward.startswith("wc "):
        amount = int(reward.split()[1])
        user["wc"] += amount
        reward_text = f"+{amount:,} WC"

    elif reward.startswith("card "):
        card_id = reward.split()[1]
        card_id = normalize_elemental_id(card_id)  # Нормализуем ID элементаля
        
        if card_id in CARD_ID_MAP:
            card_id_map = CARD_ID_MAP[card_id]
            if card_id not in user["cards"]:
                user["cards"][card_id] = {"name": card_id_map["name"], "rarity": card_id_map["rarity"], "count": 0, "url": card_id_map.get("url")}
            user["cards"][card_id]["count"] += 1
            reward_text = f"🎴 {card_id_map['name']}"
        elif card_id in ELEMENTAL_ID_MAP:
            add_elemental(user, card_id)
            reward_text = f"🌌 {ELEMENTAL_ID_MAP[card_id]['name']} (элементаль)"
        else:
            reward_text = "ошибка карты"

    promo["uses_left"] -= 1
    promo.setdefault("used_by", []).append(user_id)
    save_data()

    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key

    await update.message.reply_text(
        f"✅ Код *{code}* активирован!\n\nПолучено: {reward_text}\nОсталось использований: {promo['uses_left']}",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def create_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    if len(context.args) < 3:
        await update.effective_message.reply_text(
            "Формат:\n/createcode VOLZER2025 15 wc 500\n/createcode SANTA 1 card WGL"
        )
        return

    code = context.args[0].upper()

    try:
        uses = int(context.args[1])
        if uses <= 0:
            raise ValueError
    except:
        await update.effective_message.reply_text("Количество использований — положительное число!")
        return

    reward = " ".join(context.args[2:]).strip()
    if not reward:
        await update.effective_message.reply_text("Укажи награду!")
        return

    data.setdefault("promo_codes", {})[code] = {
        "reward": reward,
        "uses_left": uses,
        "total_uses": uses,
        "used_by": []
    }
    save_data()

    BOT_USERNAME = "walzer_combatbot"

    url = f"https://t.me/{BOT_USERNAME}?start=promo_{code}"

    button = InlineKeyboardMarkup([[
        InlineKeyboardButton("Активировать промокод", url=url)
    ]])

    await update.effective_message.reply_text(
        f"Код *{code}* успешно создан!\n"
        f"Награда: {reward}\n"
        f"Использований: {uses}\n\n"
        f"Готовый пост для канала ниже ↓",
        parse_mode="Markdown"
    )

    await update.effective_message.reply_text(
        f"*Новый промокод!*\n\n"
        f"Награда: {reward}\n"
        f"Осталось: {uses} использований\n\n"
        f"Жми кнопку — и сразу получишь награду",
        parse_mode="Markdown",
        reply_markup=button
    )

    await update.effective_message.reply_text(
        f"Или просто текстом:\n\n"
        f"*Новый промокод!*\n"
        f"Награда: {reward}\n"
        f"Осталось: {uses}\n\n"
        f"{url}",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@with_translation
async def commands_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /команды с полным списком команд"""
    user = update.effective_user
    logger.info(f"Команда /команды от пользователя {user.id}")
    
    t = context.t
    
    await update.message.reply_text(t('commands_list'), reply_markup=main_menu())

# ====================== CALLBACK ДЛЯ КНОПОК В MYCARDS ======================
async def elem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает только кнопку "Собрать заново" для элементалей.
    """
    query = update.callback_query
    await query.answer()

    if query.data != "elem_collect":
        await query.edit_message_text("Неизвестная команда.")
        return

    user_id = str(query.from_user.id)
    load_data()
    user = get_user(user_id)

    t = context.t if hasattr(context, 't') else lambda key, **kwargs: key

    now = datetime.now()
    total = 0

    for eid, edata in user.get('elementals', {}).items():
        produced = calculate_production_for_one(eid, edata, now)
        total += math.floor(produced)
        edata['stored'] = 0.0
        edata['last_collect'] = now.isoformat()

    if total > 0:
        user['wc'] += total

    save_data()

    if total > 0:
        await query.edit_message_text(
            t('elementals_collected', count=total)
        )
    else:
        await query.edit_message_text(
            "Пока ничего не накопилось.\n"
            f"Доход идёт каждую минуту, но нужно время."
        )

# ================== КОМАНДА СМЕНЫ ЯЗЫКА ==================
@with_translation
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /lang для смены языка"""
    user_id = update.effective_user.id
    
    t = context.t
    
    if not context.args:
        # Показываем текущий язык и клавиатуру выбора
        current_lang = lang_manager.get_user_lang(user_id)
        lang_names = {'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
        
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        
        await update.message.reply_text(
            f"🌐 Current language / Текущий язык: {lang_names[current_lang]}\n"
            "Choose language / Выбери язык:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Прямая смена языка через команду
    new_lang = context.args[0].lower()
    if new_lang in LANGUAGES:
        lang_manager.set_user_lang(user_id, new_lang)
        lang_name = {'ru': 'русский', 'en': 'English'}[new_lang]
        await update.message.reply_text(
            f"✅ Язык изменен на {lang_name}!\n"
            f"✅ Language changed to {lang_name}!"
        )
    else:
        await update.message.reply_text("❌ Поддерживаемые языки: ru, en")

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора языка через инлайн-кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = query.data.replace("lang_", "")
    
    if lang_manager.set_user_lang(user_id, lang):
        lang_name = {'ru': 'русский', 'en': 'English'}[lang]
        
        # Обновляем CARD_ID_MAP с переводом
        update_card_id_map_with_translation(lang)
        
        await query.edit_message_text(
            f"✅ Язык изменен на {lang_name}!\n"
            f"✅ Language changed to {lang_name}!"
        )
    else:
        await query.edit_message_text("❌ Ошибка при смене языка")

# =============================================
# ПРЕПОДВАЛЬЕ — ТОЛЬКО В ЛИЧКЕ, БЕЗ МЕНЮ
# =============================================

@with_translation
async def enter_prepodvalie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("тут такое ты не увидишь")
        return

    t = context.t

    await update.message.reply_text(
        t('prepodvalie_welcome'),
        parse_mode="Markdown",
        reply_markup=None
    )

@with_translation
async def back_to_combat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("тут такое ты не увидишь")
        return

    t = context.t

    await update.message.reply_text(
        t('prepodvalie_back'),
        reply_markup=main_menu()
    )

@with_translation
async def help_prepodvalie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = context.t
    await update.message.reply_text(
        t('prepodvalie_help'),
        reply_markup=None
    )

async def say_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("!скажи а где текст, лол")
        return
    text = " ".join(context.args)[:200]
    await update.message.reply_text(f"🗣 {text}")

async def infobot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤡 Я — подвал Волзер Комбата\n"
        "Живу тут с 2025 года\n"
        "У меня один голос\n"
        "Одна жизнь\n"
        "Ноль сожалений\n"
        "Если что-то сломалось — это фича"
    )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("!переведи en я в подвале")
        return
    await update.message.reply_text("Переводчик сдох в 2023. Я подвал, а не Яндекс.")

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    await update.message.reply_text(
        f"👤 ID: <code>{user.id}</code>\n"
        f"Имя: {user.full_name}\n"
        f"Ник: @{user.username or 'нет'}\n"
        f"Ты спустился в подвал. Поздравляю.",
        parse_mode="HTML"
    )

async def make_qrcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("!qrcode я в подвале")
        return
    text = " ".join(context.args)
    try:
        import qrcode
        qr = qrcode.make(text)
        bio = io.BytesIO()
        qr.save(bio, "PNG")
        bio.seek(0)
        await update.message.reply_photo(bio, caption=f"QR: {text[:60]}")
    except ImportError:
        await update.message.reply_text("qrcode не установлен, но текст: " + text)

async def prepodvalie_catcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    if not text.startswith("!"):
        return

    parts = text.split(maxsplit=1)
    command = parts[0][1:].lower()
    args = parts[1:] if len(parts) > 1 else []

    if command == "хелп" or command == "help":
        await help_prepodvalie(update, context)
    elif command == "скажи" or command == "say":
        context.args = args
        await say_voice(update, context)
    elif command == "инфобот" or command == "infobot":
        await infobot(update, context)
    elif command == "переведи" or command == "translate":
        context.args = args
        await translate_text(update, context)
    elif command == "юзер" or command == "user":
        await user_info(update, context)
    elif command == "qrcode":
        context.args = args
        await make_qrcode(update, context)
    elif command == "преподвалье" or command == "basement":
        await enter_prepodvalie(update, context)
    elif command == "комбат" or command == "combat":
        await back_to_combat(update, context)

async def handle_russian_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик русских команд"""
    message_text = update.message.text
    user = update.effective_user
    
    command = message_text.strip().split()[0][1:].lower()
    
    command_map = {
        'получить': getcard,
        'карта': getcard,
        'карту': getcard,
        'коллекция': mycards,
        'карты': mycards,
        'инвентарь': mycards,
        'магазин': shop,
        'купить': buy,
        'продать': sell,
        'цена': price,
        'стоимость': price,
        'посмотреть': view,
        'игры': minigames,
        'кубик': dice,
        'кости': dice,
        'кость': dice,
        'казино': casino,
        'рулетка': casino,
        'погода': weather,
        'следующая_погода': next_weather,
        'шанс': chance,
        'шансы': chance,
        'команды': commands_list,
        'старт': statr,
        'статр': statr,
        'помощь': statr,
        'пасьянс': solitaire_start,
        'косынка': solitaire_start,
        'шаман': shaman,
        'шаманить': shaman,
        'топ': top,
        'язык': set_language,
    }
    
    if command in command_map:
        logger.info(f"Русская команда от пользователя {user.id}: {command}")
        args = message_text.strip().split()[1:]
        context.args = args
        await command_map[command](update, context)

@with_translation
async def explanations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать документацию и руководства"""
    user = update.effective_user
    logger.info(f"Команда /explanations от пользователя {user.id}")
    
    t = context.t
    user_lang = lang_manager.get_user_lang(user.id)
    
    if user_lang == 'en':
        text = """ *Guides for Beginners*

*Main sections:*
• [Beginner's Guide](https://telegra.ph/Rukovodstvo-dlya-novichkov-v-Walzer-Combat-02-02) - how to start playing
• [Card Rarity System](https://telegra.ph/Sistema-kart-i-redkostej-02-02) - all about cards
• [Weather System](https://telegra.ph/Pogodnaya-sistema-02-02) - how weather cards work
• [Shamanism](https://telegra.ph/SHamanstvo-02-02) - rituals and sacrifices
• [Solitaire](https://telegra.ph/Pasyans-02-02) - Zimbabwean dollar rules

*Useful links:*
• [Updates and news](https://t.me/Walzer_Cards)
"""
    else:
        text = """ *Гайды для новичков*

*Основные разделы:*
• [Руководство для новичков](https://telegra.ph/Rukovodstvo-dlya-novichkov-v-Walzer-Combat-02-02) - как начать играть
• [Система карт и редкостей](https://telegra.ph/Sistema-kart-i-redkostej-02-02) - всё о картах
• [Погодная система](https://telegra.ph/Pogodnaya-sistema-02-02) - как работают погодные карты
• [Шаманство](https://telegra.ph/SHamanstvo-02-02) - ритуалы и жертвоприношения
• [Пасьянс](https://telegra.ph/Pasyans-02-02) - правила зимбабвийских долларов

*Полезные ссылки:*
• [Обновления и новости](https://t.me/Walzer_Cards)
"""
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_menu())
    
    
async def give_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # 1. Загружаем данные и проверяем, что они не None
    data = load_data()
    if data is None:
        data = {} # Инициализируем пустым словарем, если файл пуст

    # 2. Получаем язык отправителя (безопасно)
    user_profile = data.get(user_id, {})
    lang = user_profile.get("lang", "ru")

    # 3. Проверка на Reply
    if not update.message.reply_to_message:
        await update.message.reply_text(TRANSLATIONS[lang].get("give_no_reply", "❌ Ошибка: Используй эту команду ОТВЕТОМ на сообщение игрока."))
        return

    target_id = str(update.message.reply_to_message.from_user.id)
    target_name = update.message.reply_to_message.from_user.first_name

    if user_id == target_id:
        await update.message.reply_text(TRANSLATIONS[lang].get("give_self", "🤔 Ты не можешь подарить карту самому себе."))
        return

    # 4. Проверка аргументов (название карты)
    if not context.args:
        await update.message.reply_text(TRANSLATIONS[lang].get("give_no_args", "📝 Укажи название карты. Пример: `/give Безумный Волзер`"), parse_mode='Markdown')
        return

    card_name_input = " ".join(context.args).strip().lower()
    
    # 5. Поиск карты в CARDS и CARD_TRANSLATIONS
    found_card_id = None
    display_name = ""

    for rarity, cards_list in CARDS.items():
        for card in cards_list:
            c_id = card["id"]
            # Ищем совпадение в RU и EN словарях CARD_TRANSLATIONS
            name_ru = card["name"].lower() # Имя по умолчанию из CARDS
            name_en = CARD_TRANSLATIONS.get('en', {}).get(card["name"], "").lower()
            
            if card_name_input == name_ru or card_name_input == name_en:
                found_card_id = c_id
                # Для отображения берем перевод на язык отправителя
                display_name = CARD_TRANSLATIONS.get(lang, {}).get(card["name"], card["name"])
                break
        if found_card_id: break

    if not found_card_id:
        msg = TRANSLATIONS[lang].get("give_not_found", "❓ Карта '{name}' не найдена.").format(name=card_name_input)
        await update.message.reply_text(msg)
        return

    # 6. Проверка наличия карты у игрока
    user_cards = user_profile.get("cards", {})
    if user_cards.get(found_card_id, 0) <= 0:
        msg = TRANSLATIONS[lang].get("give_no_card", "🚫 У тебя нет карты «{name}».").format(name=display_name)
        await update.message.reply_text(msg)
        return

    # 7. Процесс передачи
    # Уменьшаем у отправителя
    data[user_id]["cards"][found_card_id] -= 1
    if data[user_id]["cards"][found_card_id] <= 0:
        del data[user_id]["cards"][found_card_id]

    # Добавляем получателю (создаем профиль, если его нет)
    if target_id not in data:
        data[target_id] = {"balance": 0, "cards": {}, "lang": "ru", "last_card_time": None}
    
    if "cards" not in data[target_id]:
        data[target_id]["cards"] = {}
        
    data[target_id]["cards"][found_card_id] = data[target_id]["cards"].get(found_card_id, 0) + 1

    # 8. Сохранение
    save_data(data)
    
    logger.info(f"TRADE: {user_id} gave {found_card_id} to {target_id}")
    
    # 9. Финальное сообщение
    success_msg = TRANSLATIONS[lang].get("give_success", "🎁 Ты успешно передал карту «**{name}**» игроку {target}!").format(name=display_name, target=target_name)
    await update.message.reply_text(success_msg, parse_mode='Markdown')

def main():
    """Основная функция запуска бота"""
    load_data()
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрация стандартных команд (латиница)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getcard", getcard))
    app.add_handler(CommandHandler("card", getcard))
    app.add_handler(CommandHandler("get", getcard))
    app.add_handler(CommandHandler("mycards", mycards))
    app.add_handler(CommandHandler("cards", mycards))
    app.add_handler(CommandHandler("collection", mycards))
    app.add_handler(CommandHandler("inventory", mycards))
    app.add_handler(CommandHandler("inv", mycards))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("store", shop))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("purchase", buy))
    app.add_handler(CommandHandler("sell", sell))
    app.add_handler(CommandHandler("sale", sell))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("cost", price))
    app.add_handler(CommandHandler("view", view))
    app.add_handler(CommandHandler("show", view))
    app.add_handler(CommandHandler("info", view))
    app.add_handler(CommandHandler("minigames", minigames))
    app.add_handler(CommandHandler("games", minigames))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("casino", casino))
    app.add_handler(CommandHandler("statr", statr))
    app.add_handler(CommandHandler("stats", statr))
    app.add_handler(CommandHandler("help", statr))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("next_weather", next_weather))
    app.add_handler(CommandHandler("nextweather", next_weather))
    app.add_handler(CommandHandler("chance", chance))
    app.add_handler(CommandHandler("chances", chance))
    app.add_handler(CommandHandler("commands", commands_list))
    app.add_handler(CommandHandler("cmd", commands_list))
    app.add_handler(CommandHandler("command", commands_list))
    app.add_handler(CommandHandler("commands_list", commands_list))
    app.add_handler(CommandHandler("solitaire", solitaire_start))
    app.add_handler(CommandHandler("solitaire_cmd", solitaire_start))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("leaderboard", top))
    app.add_handler(CommandHandler("shaman", shaman))
    app.add_handler(CommandHandler("lang", set_language))
    app.add_handler(CommandHandler("language", set_language))

    # Админ команды
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("admin_stats", admin_stats))
    app.add_handler(CommandHandler("admin_user", admin_user_management))
    app.add_handler(CommandHandler("addwc", admin_add_wc))
    app.add_handler(CommandHandler("addcard", admin_add_card))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    app.add_handler(CommandHandler("resetuser", admin_reset_user))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("code", redeem))
    app.add_handler(CommandHandler("createcode", create_code))
    
    app.add_handler(CommandHandler("explanations", explanations))
    
    app.add_handler(CommandHandler("give", give_card))

    # Регистрация обработчика для русских команд
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^/[\wа-яА-Я_]+'), handle_russian_command))

    # Регистрация callback-обработчиков
    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^(admin_|reset_|back_|user_|cards_|economy_|broadcast_|give_)"))
    app.add_handler(CallbackQueryHandler(solitaire_callback_handler, pattern=r"^(sol_|dest_)"))
    app.add_handler(CallbackQueryHandler(shaman_callback_handler, pattern=r"^shaman_"))
    app.add_handler(CallbackQueryHandler(top_callback, pattern="^(wc|total|unique)$"))
    app.add_handler(CallbackQueryHandler(elem_callback, pattern="^(elem_|synth_|bake_)"))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    
    app.add_handler(MessageHandler(filters.Regex(r'^![^\s]+'), prepodvalie_catcher))

    # Обработчик ошибок
    app.add_error_handler(error_handler)

    logger.info("Бот запущен успешно")
    print("Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()