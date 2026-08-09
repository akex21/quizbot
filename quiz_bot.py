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
    # Блок 1: Еда и привычки Саши (1-5)
    {
        "text": "1. Какое главное правило идеального вечера для Саши?",
        "options": ["Вкусная еда (пицца/бургеры)", "Уютный плед и фильмец", "Поиграть или посмотреть аниме", "Главное — провести его с Ксюшей"],
        "photo_id": None
    },
    {
        "text": "2. Что Саша с большей вероятностью заставит заказать на ужин?",
        "options": ["Пиццу Пепперони / Карбонару", "Сочные бургеры и фри", "Суши и роллы", "Всё и сразу, гулять так гулять!"],
        "photo_id": None
    },
    {
        "text": "3. Любимый напиток Саши для поднятия тонуса:",
        "options": ["Хороший кофе", "Газировка Zero / фруктовая минералка", "Вкусный чай", "Энергетик / Сок"],
        "photo_id": None
    },
    {
        "text": "4. Как выглядит идеальный выходной день Саши?",
        "options": ["Выспаться без будильника", "Спокойный отдых / поездка", "Залипать в мемы, игры и сериалы", "Вкусный завтрак и прогулка"],
        "photo_id": None
    },
    {
        "text": "5. Главная суперсила Саши:",
        "options": ["Понимать Ксюшу без слов", "Мгновенно выбирать, что покушать", "Находить лучшие мемы", "Быть самым заботливым"],
        "photo_id": None
    },

    # Блок 2: Отдых, вкусы и мечты (6-10)
    {
        "text": "6. Идеальное место, куда Саша хотел бы съездить отдохнуть:",
        "options": ["Тихий домик в горах", "Уютное побережье у моря", "Интересное путешествие в новый город", "Остаться дома в тишине и уюте"],
        "photo_id": None
    },
    {
        "text": "7. Что обязательно должно быть в идеальном путешествии для Саши?",
        "options": ["Красивые виды и природа", "Вкусная еда", "Полный комфорт", "Душевная компания и Ксюша рядом"],
        "photo_id": None
    },
    {
        "text": "8. Если бы про Сашу снимали кино, какой это был бы жанр?",
        "options": ["Уютная романтическая комедия", "Экшен / Детектив", "Аниме / Фэнтези", "Приключения"],
        "photo_id": None
    },
    {
        "text": "9. Какой навык у Саши прокачан на 10/10?",
        "options": ["Выбор лучшей еды и ресторанов", "Отправка идеальных мемов в Telegram", "Забота и поддержка", "План и организаторские способности"],
        "photo_id": None
    },
    {
        "text": "10. Какой формат отдыха Саша предпочтет вечером?",
        "options": ["Посмотреть фильм / аниме с Ксюшей", "Вкусный ужин и разговоры", "Покататься / погулять", "Поиграть в любимую игру"],
        "photo_id": None
    },

    # Блок 3: Характер и настроение (11-15)
    {
        "text": "11. Главный секрет отличного настроения Саши с утра:",
        "options": ["Поспать ещё «буквально 5 минут»", "Утренние обнимашки с Ксюшей", "Вкусный завтрак / кофе", "Хорошие новости"],
        "photo_id": None
    },
    {
        "text": "12. Что делает Саша, если сильно устал после рабочего дня?",
        "options": ["Заказывает вкусную еду", "Ложится обниматься и отдыхать", "Смотрит смешные видео / мемы", "Переключается на любимое хобби"],
        "photo_id": None
    },
    {
        "text": "13. Какое качество в Ксюше Саша ценит больше всего?",
        "options": ["Чувство юмора и доброту", "Заботу и нежность", "Умение слушать и понимать", "Всё перечисленное и даже больше!"],
        "photo_id": None
    },
    {
        "text": "14. Как Саша проявляет свою заботу?",
        "options": ["Накормит вкусняшками", "Крепко обнимет и поддержит", "Решит любой сложный вопрос", "Заставит улыбнуться мемом или шуткой"],
        "photo_id": None
    },
    {
        "text": "15. Какое слово лучше всего характеризует Сашу?",
        "options": ["Надёжный", "Заботливый", "Умный", "Любимый"],
        "photo_id": None
    },

    # Блок 4: Факты и секреты (16-20)
    {
        "text": "16. Что Саша сделает, чтобы поднять настроение Ксюше?",
        "options": ["Пришлёт самый милый/смешной мем", "Купит её любимую вкусняшку", "Крепко обнимет", "Придумает что-то приятное"],
        "photo_id": None
    },
    {
        "text": "17. Назови любимый способ Саши перегрузить мозги:",
        "options": ["Вкусный перекус", "Просмотр хорошего тайтла / фильма", "Качественный сон", "Прогулка или смена обстановки"],
        "photo_id": None
    },
    {
        "text": "18. Какой «секретный ингредиент» делает Сашу счастливым?",
        "options": ["Когда Ксюша улыбается", "Вкусная еда под рукой", "Когда всё идёт по плану", "Уютный и спокойный вечер"],
        "photo_id": None
    },
    {
        "text": "19. Насколько хорошо Саша знает, чего хочет Ксюша?",
        "options": ["На 100%", "Угадывает с полуслова", "Читает мысли", "Все варианты верны!"],
        "photo_id": None
    },
    {
        "text": "20. Финальный факт: Кто главный любимчик Саши?",
        "options": ["Ксюша", "Конечно же Ксюша", "Без вариантов — Ксюша", "Ксюша ❤️"],
        "photo_id": None
    },

    # Блок 5: Фото-вопросы про Сашу (21-25)
    {
        "text": "21. Что происходит на этой фотографии с Сашей?",
        "options": ["Подпольный клуб", "Пересменка в Самокате", "Рэп-клип", "Качалка / Серьёзные переговоры"],
        "photo_id": "AgACAgIAAxkBAAMaanjCiF4PiJ7DySJEwEbM52vKLXMAAgMcaxvBpMBLN6p_Ufy-pw4BAAMCAAN5AAM9BA"
    },
    {
        "text": "22. В каком стиле выполнен этот кадр Саши?",
        "options": ["Острые козырьки", "Стильная мафия", "Джентльмены", "Кадр из культового кино"],
        "photo_id": "AgACAgIAAxkBAAMcanjDDAFoCCgh0ZqxT7N4zzJbtqMAAgYcaxvBpMBLgLgFZh6Bo3oBAAMCAAN5AAM9BA"
    },
    {
        "text": "23. Опиши этот эпичный поединок с участием Саши:",
        "options": ["Битва титанов", "Аниме-поединок", "Стойка карате перед зеркалом", "Бойцовский клуб"],
        "photo_id": "AgACAgIAAxkBAAMeanjDQSqC5F2YvLG4q0bQgH_NahsAAgccaxvBpMBL6edBXRysMgsBAAMCAAN5AAM9BA"
    },
    {
        "text": "24. Что происходит на этом архивном фото маленького Саши?",
        "options": ["Восполнение маны", "Перерыв на обед", "Маленький босс за работой", "Зарядка перед важными делами"],
        "photo_id": "AgACAgIAAxkBAAMganjDegQQv9fGbzREFTIPw4-21LkAAggcaxvBpMBLuSTpLGT9ickBAAMCAAN5AAM9BA"
    },
    {
        "text": "25. Финальный кадр! Какая тут атмосфера у Саши?",
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
