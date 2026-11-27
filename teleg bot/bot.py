import json
import random
import json
import os
import aiohttp
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv
from handlers.command_handler import CommandHandler
from handlers.text_handler import TextHandler


from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler as TelegramCommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)


# ==========================
# ТОКЕН БОТА
# ==========================
load_dotenv()

TOKEN = os.environ.get('TOKEN')


# ==========================
# ФАЙЛ С ПОЛЬЗОВАТЕЛЯМИ
# ==========================

USER_FILE = "user.json"


if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)


# ==========================
# ЗАГРУЗКА ДАННЫХ
# ==========================

def load_users():
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================
# СОХРАНЕНИЕ ДАННЫХ
# ==========================

def save_users(data):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ==========================
# ВРЕМЕННОЕ ХРАНЕНИЕ СОСТОЯНИЙ
# ==========================

user_states = {}


# ==========================
# КНИГИ
# ==========================

BOOKS = {
    "фэнтези": [
        "📖 «Гарри Поттер» — Дж. К. Роулинг",
        "📖 «Властелин колец» — Толкин",
        "📖 «Хоббит» — Толкин"
    ],

    "детектив": [
        "📖 «Убийство в Восточном экспрессе» — Агата Кристи",
        "📖 «Шерлок Холмс» — Артур Конан Дойл",
        "📖 «Девушка с татуировкой дракона»"
    ],

    "роман": [
        "📖 «Гордость и предубеждение»",
        "📖 «Анна Каренина»",
        "📖 «Поющие в терновнике»"
    ],

    "ужасы": [
        "📖 «Оно» — Стивен Кинг",
        "📖 «Дракула»",
        "📖 «Франкенштейн»"
    ],

    "приключения": [
        "📖 «Остров сокровищ»",
        "📖 «Три мушкетёра»",
        "📖 «Дети капитана Гранта»"
    ],

    "классика": [
        "📖 «Война и мир»",
        "📖 «Преступление и наказание»",
        "📖 «Мастер и Маргарита»"
    ],

    "фантастика": [
        "📖 «Дюна»",
        "📖 «451° по Фаренгейту»",
        "📖 «Марсианин»"
    ]
}


# ==========================
# ЦИТАТЫ
# ==========================

QUOTES = [
    "📚 Книга — это мечта, которую вы держите в руках.",
    "📚 Чтение открывает новые миры.",
    "📚 Хорошая книга меняет человека."
]


my_name = "букля"
my_age = 15
my_hobby = "бэкенд-разработка"


def format_about():
    return (
        f"привет, меня зовут {my_name}.\n"
        f"мне {my_age} лет.\n"
        f"мое хобби: {my_hobby}.\n"
        "меня создал ученик CAP Education"
    )


async def send(update, text, **kwargs):
    await update.message.reply_text(text, **kwargs)


def get_random_message(messages):
    return random.choice(messages)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_about())


def get_user_id(update):
    return str(update.effective_user.id)


# ==========================
# /start
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["😊 Настроение", "💡 Совет дня"],
        ["📖 О боте"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "👋 Привет!\n"
        "Я книжный бот 📚\n"
        "Выбери действие:",
        reply_markup=reply_markup
    )

    users = load_users()
    user_id = get_user_id(update)

    if user_id not in users:
        users[user_id] = {
            "name": "",
            "genre": "",
            "author": "",
            "book": "",
            "color": ""
        }
        save_users(users)

    inline_keyboard = [
        [
            InlineKeyboardButton(
                "📖 О боте",
                callback_data="about"
            )
        ],
        [
            InlineKeyboardButton(
                "📜 Цитата",
                callback_data="quote"
            )
        ],
        [
            InlineKeyboardButton(
                "👤 Автор",
                callback_data="author"
            )
        ]
    ]

    await update.message.reply_text(
        "Дополнительные кнопки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard)
    )


# ==========================
# Inline кнопки
# ==========================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if query.data == "about":

        await query.edit_message_text(
            "📚 Я бот, который помогает выбирать книги и "
            "делится интересными цитатами."
        )

    elif query.data == "quote":

        await query.edit_message_text(
            random.choice(QUOTES)
        )

    elif query.data == "author":

        await query.edit_message_text(
            "👤 Автор бота: Данара"
        )


# ==========================
# /help
# ==========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📖 Команды:\n\n"
        "/start — запуск бота\n"
        "/help — помощь\n"
        "/time — время\n"
        "/quote — цитата\n"
        "/setprofile — заполнить профиль\n"
        "/profile — мой профиль\n"
        "/games — игра\n"
        "/leaderboard — рейтинг игроков\n"
        "/about - обо мне\n\n"
        "Напиши жанр книги:\n"
        "фэнтези, детектив, роман, ужасы"
    )


# ==========================
# /time
# ==========================

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    await update.message.reply_text(
        f"🕒 Сейчас: {now}"
    )


# ==========================
# /quote
# ==========================

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        get_random_message(QUOTES)
    )


# ==========================
# /setprofile
# ==========================

async def setprofile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    user_states[user_id] = "name"

    await update.message.reply_text(
        "👤 Введите ваше имя:"
    )


# ==========================
# /profile
# ==========================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    users = load_users()

    user_id = get_user_id(update)

    if user_id not in users:

        await update.message.reply_text(
            "❌ Профиль еще не заполнен.\n"
            "Используйте команду /setprofile"
        )

        return

    user = users[user_id]

    await update.message.reply_text(

        f"👤 Имя: {user['name']}\n"
        f"📚 Любимый жанр: {user['genre']}\n"
        f"✍ Любимый автор: {user['author']}\n"
        f"📖 Любимая книга: {user['book']}\n"
        f"🎨 Любимый цвет: {user['color']}"
    )


# ==========================
# Жанры книг
# ==========================

async def recommend_book(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    # ВАЖНО: используем строку везде
    user_id = str(update.effective_user.id)

    # ==========================
    # ПРОВЕРКА ИГРЫ
    # ==========================

    if user_id in games:
        await handle_guess(update, context)
        return

    users = load_users()

    # Если пользователь проходит заполнение анкеты
    if user_id in user_states:

        state = user_states[user_id]

        if state == "name":

            if user_id not in users:
                users[user_id] = {}

            users[user_id]["name"] = update.message.text
            user_states[user_id] = "genre"

            save_users(users)

            await update.message.reply_text(
                "📚 Ваш любимый жанр?"
            )

            return

        elif state == "genre":

            users[user_id]["genre"] = update.message.text
            user_states[user_id] = "author"

            save_users(users)

            await update.message.reply_text(
                "✍ Кто ваш любимый автор?"
            )

            return

        elif state == "author":

            users[user_id]["author"] = update.message.text
            user_states[user_id] = "book"

            save_users(users)

            await update.message.reply_text(
                "📖 Какая ваша любимая книга?"
            )

            return

        elif state == "book":

            users[user_id]["book"] = update.message.text
            user_states[user_id] = "color"

            save_users(users)

            await update.message.reply_text(
                "🎨 Какой ваш любимый цвет?"
            )

            return

        elif state == "color":

            users[user_id]["color"] = update.message.text

            save_users(users)

            del user_states[user_id]

            await update.message.reply_text(
                "✅ Профиль успешно сохранен!"
            )

            return

    for genre, books in BOOKS.items():

        if genre in text:

            await update.message.reply_text(
                f"📚 Жанр: {genre}\n\n"
                + "\n".join(books)
            )

            return

    if text == "😊 настроение":

        await update.message.reply_text(
            "😊 Отличного настроения!"
        )

    elif text == "💡 совет дня":

        await update.message.reply_text(
            "💡 Читай каждый день хотя бы 10 минут!"
        )

    elif text == "📖 о боте":

        await update.message.reply_text(
            "📚 Этот бот помогает находить книги."
        )

async def weather(update, context):
    city = " ".join(context.args)

    if not city:
        await update.message.reply_text(
            "❌ Пожалуйста, укажите город."
        )
        return
    API_KEY = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 401:
                    await update.message.reply_text(
                        "❌Неверный API ключ. Пожалуйста, проверьте настройки."
                    )
                    return
                if response.status == 404:
                    await update.message.reply_text(
                        "❌ Город не найден."
                    )
                    return
                if response.status >= 500:
                    await update.message.reply_text(
                        "❌ Ошибка сервера. Пожалуйста, попробуйте позже."
                    )
                    return

                response.raise_for_status()
                data = await response.json()

        temp = data["main"]["temp"]
        await update.message.reply_text(
            f"🌡️ Температура в {city}: {temp}°C"
        )
    except asyncio.TimeoutError:
        await update.message.reply_text(
            "❌ Превышено время ожидания ответа от сервера."  )

    except aiohttp.ClientError as e:
        await update.message.reply_text(
            f"❌ Ошибка при подключении к серверу: {e}"  )
    except (KeyError, ValueError):
        await update.message.reply_text(
            "❌ Ошибка обработки данных о погоде."
        )

# ==========================
# ИГРА
# ==========================

games = {}



FILE_NAME = "players.json"

def save_data(data):
    try:
        with open (FILE_NAME, "w", encoding="utf-8")as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        return{}
    except json.JSONDecodeError:
        return{}


def load_data():
    if not os.path.exists(FILE_NAME):
        return {}

    with open(FILE_NAME, "r", encoding="utf-8-sig") as f:
        return json.load(f)

players = load_data()
# =========================
# /games
# ==========================

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    secret = random.randint(1, 10)

    games[user_id] = secret
    games[user_id + "_attempts"] = 0

    await update.message.reply_text(
        "🎮 я загадал число от 1 до 10. Угадай!"
    )


# ==========================
# УГАДЫВАНИЕ
# ==========================

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    if user_id not in games:
        return

    text = update.message.text

    if not text.isdigit():

        await update.message.reply_text(
            "это не число, попробуй еще раз"
        )

        return

    attempts_key = user_id + "_attempts"

    games[attempts_key] = games.get(attempts_key, 0) + 1

    attempts = games[attempts_key]

    guess = int(text)

    secret = games[user_id]

    if guess < secret:

        await update.message.reply_text(
            "больше"
        )

    elif guess > secret:

        await update.message.reply_text(
            "меньше"
        )

    else:

        # Создаем игрока, если его еще нет
        if user_id not in players:

            players[user_id] = {
                "name": update.effective_user.first_name,
                "wins": 0,
                "best": None
            }

        # Добавляем победу
        players[user_id]["wins"] += 1

        # Обновляем лучший результат
        if (
            players[user_id]["best"] is None
            or attempts < players[user_id]["best"]
        ):

            players[user_id]["best"] = attempts

        save_data(players)

        await update.message.reply_text(
            f"🎉 молодец! это число было {secret}\n"
            f"попыток: {attempts}"
        )

        del games[user_id]
        del games[attempts_key]


# ==========================
# /leaderboard
# ==========================

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # сортировка игроков по количеству побед
    # срез [:5] оставляет только топ-5
    top_players = sorted(
        players.values(),
        key=lambda player: player["wins"],
        reverse=True
    )[:5]

    if not top_players:

        await update.message.reply_text(
            "🏆 Рейтинг пока пуст!"
        )

        return

    text = "🏆 ТОП-5 ИГРОКОВ\n\n"

    # enumerate используется для нумерации мест
    for place, player in enumerate(top_players, start=1):

        text += (
            f"{place}. {player['name']} — "
            f"{player['wins']} побед 🏆\n"
        )

    await update.message.reply_text(text)


# ==========================
# LIST COMPREHENSION
# ==========================

# пользователи, у которых 3 или больше побед
players_with_3_wins = [
    player
    for player in players.values()
    if player["wins"] >= 3
]

#jokes


async def joke(update, context):
    url = "https://v2.jokeapi.dev/joke/Any?type=twopart&safe-mode"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:

                if response.status >= 500:
                    await update.message.reply_text(
                        "❌ Ошибка сервера. Попробуйте позже."
                    )
                    return

                response.raise_for_status()
                data = await response.json()

        await update.message.reply_text(
            f"😂 {data['setup']}\n{data['delivery']}"
        )

    except asyncio.TimeoutError:
        await update.message.reply_text(
            "❌ Сервер не отвечает."
        )

    except aiohttp.ClientError:
        await update.message.reply_text(
            "❌ Ошибка подключения к серверу."
        )

    except (KeyError, ValueError):
        await update.message.reply_text(
            "❌ Ошибка обработки данных."
        )

# ==========================
# Запуск
# ==========================


def main():

    app = Application.builder().token(TOKEN).build()

    command_handler = CommandHandler({
        "start": start,
        "help": help_command,
        "time": time_command,
        "quote": quote_command,
        "setprofile": setprofile,
        "profile": profile,
        "about": about_command,
        "games": start_game,
        "leaderboard": leaderboard,
        "weather": weather,
        "joke": joke
    })

    command_handler.register(app)

    text_handler = TextHandler(recommend_book)
    text_handler.register(app)

    app.add_handler(CallbackQueryHandler(button))

    print("Бот успешно запущен!")

    app.run_polling()

if __name__ == "__main__":
    main()