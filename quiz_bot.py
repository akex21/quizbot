import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ----------------------------------------------------
# 1. Запуск Flask сервера (для работы на Render)
# ----------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ----------------------------------------------------
# 2. Токен бота
# ----------------------------------------------------
TOKEN = os.getenv("BOT_TOKEN", "8906869103:AAFND4E3H0g2oQC2cklM_Zd0ry5jzxRDHtE")

# ----------------------------------------------------
# 3. Список вопросов (15 вопросов)
# ----------------------------------------------------
QUESTIONS = [
    # Блок 1 (Вопросы 1-5)
    {
        "text": "1. Какое главное правило идеального вечера?",
        "options": ["Вкусная еда", "Уютный плед", "Хороший фильм", "Главное — быть вместе"],
        "photo_id": None
    },
    {
        "text": "2. Что мы выберем заказать на ужин?",
        "options": ["Пиццу", "Бургеры", "Суши", "Всё и сразу!"],
        "photo_id": None
    },
    {
        "text": "3. Идеальный отдых — это...",
        "options": ["Горы", "Море", "Дома под сериальчик", "Главное, чтобы без будильников"],
        "photo_id": None
    },
    {
        "text": "4. Какой напиток повышает настроение на 100%?",
        "options": ["Кофе", "Чай", "Газировка без сахара", "Какао с маршмеллоу"],
        "photo_id": None
    },
    {
        "text": "5. Суперсила, которой мы обладаем:",
        "options": ["Понимать друг друга без слов", "Телепортация к еде", "Спать по 10 часов", "Залипать в мемы"],
        "photo_id": None
    },

    # Блок 2 (Вопросы 6-10)
    {
        "text": "6. Если бы мы снимали фильм, какой это был бы жанр?",
        "options": ["Романтическая комедия", "Экшен / Детектив", "Аниме / Фэнтези", "Приключения"],
        "photo_id": None
    },
    {
        "text": "7. Главный секрет хорошего настроения с утра:",
        "options": ["Поспать ещё 5 минут", "Обнимашки", "Вкусный завтрак", "Утренний кофе"],
        "photo_id": None
    },
    {
        "text": "8. Что важнее всего в путешествиях?",
        "options": ["Красивые виды", "Вкусная локальная еда", "Комфорт", "Атмосфера и компания"],
        "photo_id": None
    },
    {
        "text": "9. Какой навык прокачан на максимум?",
        "options": ["Выбор лучшего места в ресторане", "Быстрый поиск мемов", "Забота друг о друге", "Планирование"],
        "photo_id": None
    },
    {
        "text": "10. Какое слово лучше всего описывает нас?",
        "options": ["Команда", "Дуэт", "Счастье", "Любовь"],
        "photo_id": None
    },

    # Блок 3 (Вопросы 11-15 — С вашими фото)
    {
        "text": "11. Что происходит на этой фотографии?",
        "options": ["Подпольный клуб", "Пересменка в Самокате", "Рэп-клип", "Качалка / Серьёзные переговоры"],
        "photo_id": "AgACAgIAAxkBAAMaanjCiF4PiJ7DySJEwEbM52vKLXMAAgMcaxvBpMBLN6p_Ufy-pw4BAAMCAAN5AAM9BA"
    },
    {
        "text": "12. В каком стиле сделан этот кадр?",
        "options": ["Острые козырьки", "Стильная мафия", "Джентльмены", "Кадр из культового кино"],
        "photo_id": "AgACAgIAAxkBAAMcanjDDAFoCCgh0ZqxT7N4zzJbtqMAAgYcaxvBpMBLgLgFZh6Bo3oBAAMCAAN5AAM9BA"
    },
    {
        "text": "13. Опиши этот эпичный поединок:",
        "options": ["Битва титанов", "Аниме-поединок", "Стойка карате перед зеркалом", "Бойцовский клуб"],
        "photo_id": "AgACAgIAAxkBAAMeanjDQSqC5F2YvLG4q0bQgH_NahsAAgccaxvBpMBL6edBXRysMgsBAAMCAAN5AAM9BA"
    },
    {
        "text": "14. Что происходит на этом архивном фото?",
        "options": ["Восполнение маны", "Перерыв на обед", "Маленький босс за работой", "Зарядка перед важными делами"],
        "photo_id": "AgACAgIAAxkBAAMganjDegQQv9fGbzREFTIPw4-21LkAAggcaxvBpMBLuSTpLGT9ickBAAMCAAN5AAM9BA"
    },
    {
        "text": "15. Финальный кадр! Какая тут атмосфера?",
        "options": ["Анонимный хакер", "Джентльмен под зонтом", "Таинственный герой", "Главный персонаж истории"],
        "photo_id": "AgACAgIAAxkBAAMianjDlvxBdlYhU1TCOGRKLE6_fDgAAgkcaxvBpMBLacGQtdSXZxQBAAMCAAN5AAM9BA"
    }
]

# ----------------------------------------------------
# 4. Вспомогательные функции для клавиатуры
# ----------------------------------------------------
def build_keyboard(question, selected_indices):
    keyboard = []
    for index, option in enumerate(question["options"]):
        is_selected = index in selected_indices
        prefix = "☑️ " if is_selected else "☐ "
        keyboard.append([
            InlineKeyboardButton(
                text=f"{prefix}{option}",
                callback_data=f"select_{index}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="Подтвердить выбор 🚀", callback_data="submit")
    ])
    return InlineKeyboardMarkup(keyboard)

# ----------------------------------------------------
# 5. Обработчики команд и вопросов
# ----------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["current_question_index"] = 0
    context.user_data["selected_options"] = set()
    context.user_data["answers"] = []

    welcome_text = (
        "Привет! 👋\n\n"
        "Добро пожаловать в специальную викторину!\n"
        "В каждом вопросе можно выбирать **несколько вариантов** (просто нажимай на них, чтобы поставить галочки ☑️), "
        "а затем нажимай кнопку **«Подтвердить выбор 🚀»**.\n\n"
        "Погнали!"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, parse_mode="Markdown")
        
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get("current_question_index", 0)
    
    # Если вопросы закончились
    if index >= len(QUESTIONS):
        final_text = (
            "🎉 **Ура! Викторина успешно пройдена!** 🎉\n\n"
            "Спасибо за прохождение! Ты умничка и справилась на 100%! ❤️✨"
        )
        if update.callback_query:
            await update.callback_query.message.reply_text(final_text, parse_mode="Markdown")
        else:
            await update.message.reply_text(final_text, parse_mode="Markdown")
        return

    question = QUESTIONS[index]
    context.user_data["selected_options"] = set()
    reply_markup = build_keyboard(question, context.user_data["selected_options"])

    chat_id = update.effective_chat.id

    # Если у вопроса есть фото
    if question.get("photo_id"):
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=question["photo_id"],
            caption=question["text"],
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=question["text"],
            reply_markup=reply_markup
        )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected = context.user_data.setdefault("selected_options", set())
    data = query.data
    current_index = context.user_data.get("current_question_index", 0)

    if current_index >= len(QUESTIONS):
        return

    current_q = QUESTIONS[current_index]

    if data.startswith("select_"):
        idx = int(data.split("_")[1])
        if idx in selected:
            selected.remove(idx)
        else:
            selected.add(idx)
        
        reply_markup = build_keyboard(current_q, selected)
        await query.edit_message_reply_markup(reply_markup=reply_markup)

    elif data == "submit":
        if not selected:
            await query.answer("Выберите хотя бы один вариант!", show_alert=True)
            return
        
        # Сохраняем ответ пользователя
        context.user_data.setdefault("answers", []).append({
            "question": current_q["text"],
            "selected": [current_q["options"][i] for i in selected]
        })

        # Переходим к следующему вопросу
        context.user_data["current_question_index"] += 1
        await send_question(update, context)

async def echo_photo_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Если боту присылают фото, он отвечает его file_id."""
    photo = update.message.photo[-1]
    file_id = photo.file_id
    await update.message.reply_text(f"Вот `file_id` твоей фотографии:\n\n`{file_id}`", parse_mode="Markdown")

# ----------------------------------------------------
# 6. Главная функция запуска
# ----------------------------------------------------
def main():
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()

    # Создаём и настраиваем Telegram бота
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(MessageHandler(filters.PHOTO, echo_photo_id))

    print("Бот успешно запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
