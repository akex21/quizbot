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
# 1. Запуск Flask сервера (для поддержания работы на Render)
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
# 3. Список из 25 вопросов (5 блоков по 5 вопросов)
# ----------------------------------------------------
QUESTIONS = [
    # Блок 1: Еда и идеальный вечер (1-5)
    {
        "text": "1. Какое главное правило нашего идеального вечера?",
        "options": ["Вкусная еда (пицца/бургеры)", "Уютный плед и фильмец", "Обнимашки", "Главное — быть вместе"],
        "photo_id": None
    },
    {
        "text": "2. Что мы с большей вероятностью закажем на ужин?",
        "options": ["Пепперони или Карбонару", "Сочные бургеры и фри", "Суши и роллы", "Всё и сразу, гулять так гулять!"],
        "photo_id": None
    },
    {
        "text": "3. Идеальный напиток для поднятия настроения:",
        "options": ["Кофе с утра", "Вкусный чай", "Газировка Zero / сок", "Горячий шоколад"],
        "photo_id": None
    },
    {
        "text": "4. Как выглядит идеальный выходной день?",
        "options": ["Выспаться без будильника", "Пойти гулять на свежем воздухе", "Залипать в мемасы и сериалы", "Вкусный завтрак в постель"],
        "photo_id": None
    },
    {
        "text": "5. Наша секретная суперсила как пары:",
        "options": ["Понимать друг друга с одного взгляда", "Мгновенно выбирать, что покушать", "Спать по 10 часов", "Поддерживать в любой ситуации"],
        "photo_id": None
    },

    # Блок 2: Атмосфера, отдых и путешествия (6-10)
    {
        "text": "6. Идеальное место для совместного отдыха:",
        "options": ["Тихий домик в горах", "Уютный пляж у моря", "Путешествие в новый город", "Дома под одеялом"],
        "photo_id": None
    },
    {
        "text": "7. Что обязательно должно быть в любом путешествии?",
        "options": ["Красивые виды для фото", "Местная вкусная еда", "Полный комфорт", "Душевная атмосфера"],
        "photo_id": None
    },
    {
        "text": "8. Если бы про нас снимали кино, какой это был бы жанр?",
        "options": ["Романтическая комедия", "Захватывающее приключение", "Аниме / Фэнтези", "Уютный лайфстайл"],
        "photo_id": None
    },
    {
        "text": "9. Какой навык у нас прокачан на 10/10?",
        "options": ["Идеальный выбор мест для прогулок", "Отправка лучших мемов в Telegram", "Забота друг о друге", "Умение вовремя обняться"],
        "photo_id": None
    },
    {
        "text": "10. Какая музыка лучше всего подходит под наше настроение?",
        "options": ["Душевные акустические треки", "Бодрый трек для дороги", "Саундтреки из любимых фильмов/аниме", "Лофай для уютных вечеров"],
        "photo_id": None
    },

    # Блок 3: Увлечения, юмор и привычки (11-15)
    {
        "text": "11. Главный секрет отличного настроения с утра:",
        "options": ["Поспать ещё «буквально 5 минут»", "Утренние обнимашки", "Вкусный завтрак", "Заряд положительных эмоций"],
        "photo_id": None
    },
    {
        "text": "12. Что делать, если устали после тяжелого дня?",
        "options": ["Заказать любимую еду", "Лечь вместе обнявшись", "Посмотреть смешные видео", "Поболтать обо всём на свете"],
        "photo_id": None
    },
    {
        "text": "13. Какое качество в партнере ценится больше всего?",
        "options": ["Чувство юмора", "Доброта и забота", "Умение слушать и понимать", "Надёжность"],
        "photo_id": None
    },
    {
        "text": "14. Наш любимый формат времяпрепровождения:",
        "options": ["Ночной просмотр фильмов", "Совместная готовка или заказ еды", "Прогулки по вечернему городу", "Душевные разговоры обо всём"],
        "photo_id": None
    },
    {
        "text": "15. Если нужно принять важное решение, мы...",
        "options": ["Советуемся и решаем вместе", "Взвешиваем все плюсы и минусы", "Доверяем интуиции", "Поддерживаем выбор друг друга"],
        "photo_id": None
    },

    # Блок 4: Воспоминания и личные приколы (16-20)
    {
        "text": "16. Что делаем, когда нужно поднять настроение?",
        "options": ["Присылаем милые или смешные мемы", "Покупаем что-нибудь вкусненькое", "Крепко обнимаем", "Говорим приятные слова"],
        "photo_id": None
    },
    {
        "text": "17. Наш идеальный домашний вечер — это:",
        "options": ["Сериал + вкусняшки", "Игры или викторины", "Разговоры по душам", "Просто отдых в тишине рядом"],
        "photo_id": None
    },
    {
        "text": "18. Какой суперспособностью обладает Ксюша?",
        "options": ["Дарить тепло и улыбку", "Быть самой милой", "Быстро поднимать настроение", "Украшать собой любой день"],
        "photo_id": None
    },
    {
        "text": "19. Какое слово лучше всего описывает наш союз?",
        "options": ["Команда", "Счастье", "Любовь", "Уют"],
        "photo_id": None
    },
    {
        "text": "20. Насколько мы классные?",
        "options": ["10 из 10", "100 из 10", "Бесконечность!", "Лучшая пара на свете!"],
        "photo_id": None
    },

    # Блок 5: Фото-вопросы (21-25)
    {
        "text": "21. Что происходит на этой фотографии?",
        "options": ["Подпольный клуб", "Пересменка в Самокате", "Рэп-клип", "Качалка / Серьёзные переговоры"],
        "photo_id": "AgACAgIAAxkBAAMaanjCiF4PiJ7DySJEwEbM52vKLXMAAgMcaxvBpMBLN6p_Ufy-pw4BAAMCAAN5AAM9BA"
    },
    {
        "text": "22. В каком стиле сделан этот кадр?",
        "options": ["Острые козырьки", "Стильная мафия", "Джентльмены", "Кадр из культового кино"],
        "photo_id": "AgACAgIAAxkBAAMcanjDDAFoCCgh0ZqxT7N4zzJbtqMAAgYcaxvBpMBLgLgFZh6Bo3oBAAMCAAN5AAM9BA"
    },
    {
        "text": "23. Опиши этот эпичный поединок:",
        "options": ["Битва титанов", "Аниме-поединок", "Стойка карате перед зеркалом", "Бойцовский клуб"],
        "photo_id": "AgACAgIAAxkBAAMeanjDQSqC5F2YvLG4q0bQgH_NahsAAgccaxvBpMBL6edBXRysMgsBAAMCAAN5AAM9BA"
    },
    {
        "text": "24. Что происходит на этом архивном фото?",
        "options": ["Восполнение маны", "Перерыв на обед", "Маленький босс за работой", "Зарядка перед важными делами"],
        "photo_id": "AgACAgIAAxkBAAMganjDegQQv9fGbzREFTIPw4-21LkAAggcaxvBpMBLuSTpLGT9ickBAAMCAAN5AAM9BA"
    },
    {
        "text": "25. Финальный кадр! Какая тут атмосфера?",
        "options": ["Анонимный хакер", "Джентльмен под зонтом", "Таинственный герой", "Главный персонаж истории"],
        "photo_id": "AgACAgIAAxkBAAMianjDlvxBdlYhU1TCOGRKLE6_fDgAAgkcaxvBpMBLacGQtdSXZxQBAAMCAAN5AAM9BA"
    }
]

# ----------------------------------------------------
# 4. Вспомогательные функции для клавиатуры мультивыбора
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
# 5. Обработчики команд и логика викторины
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
    
    if index >= len(QUESTIONS):
        final_text = (
            "🎉 **Ура! Викторина из 25 вопросов успешно пройдена!** 🎉\n\n"
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
        
        context.user_data.setdefault("answers", []).append({
            "question": current_q["text"],
            "selected": [current_q["options"][i] for i in selected]
        })

        context.user_data["current_question_index"] += 1
        await send_question(update, context)

async def echo_photo_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    await update.message.reply_text(f"Вот `file_id` твоей фотографии:\n\n`{file_id}`", parse_mode="Markdown")

# ----------------------------------------------------
# 6. Главная функция запуска
# ----------------------------------------------------
def main():
    threading.Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(MessageHandler(filters.PHOTO, echo_photo_id))

    print("Бот успешно запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
