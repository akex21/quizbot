import os
import random
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

# ---------------------------------------------------------
# 1. Запуск Flask-сервера (для поддержания работы на Render)
# ---------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---------------------------------------------------------
# 2. Токен бота
# ---------------------------------------------------------
TOKEN = os.getenv("BOT_TOKEN", "8906869103:AAFND4E3H0g2oQC2cklM_Zd0ry5jzxRDHtE")

# ---------------------------------------------------------
# 3. Пул случайных шуточных реакций при ошибке
# ---------------------------------------------------------
WRONG_ANSWER_TEASES = [
    "Так-так, записываю это в журнал маленьких ошибочек! 📝 Попробуй ещё раз 😉",
    "Холодно, о-о-очень холодно! ❄️ Саня смотрит с легким удивлением... Подумай ещё!",
    "Ответ засчитан, но моё сердце только что слегка сжалось... ❤️ Перевыбирай!",
    "Эх, а я ведь верил... Штрафной балл за недоверие к моим вкусам! 🍕 Давай заново!",
    "Система зафиксировала попытку сбить бота с толку 🤖 Попробуй ещё раз!",
    "Не-а! Саша качает головой и ждёт правильного ответа 🙃",
    "Почти! Но у этой загадки есть совсем другой секрет ⚡",
]

# ---------------------------------------------------------
# 4. БАЗА ВОПРОСОВ (25 ВОПРОСОВ)
# ---------------------------------------------------------
QUIZ_DATA = [
    # БЛОК 1: Вкусняшки, еда и привычки
    {
        "text": (
            "<b>Блок 1 (1/25) 🍔</b>\n"
            "Что Саша с наибольшим удовольствием выбирает, когда хочется"
            " сытно перекусить фастфудом?"
        ),
        "options": [
            "1️⃣ Двойной чизбургер или чикенбургер 🍔",
            "2️⃣ Пицца Пепперони или Карбонара 🍕",
            "3️⃣ Картофель фри и наггетсы 🍟",
            "4️⃣ Сочный донер, шаурма, ролл или гирос 🌯",
        ],
        "correct": [0, 1, 3],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 1 (2/25) 🥤</b>\n"
            "Каким напитком Саша предпочтёт освежиться в течение дня?"
        ),
        "options": [
            "1️⃣ Cola Zero 🥤",
            (
                "2️⃣ Фруктовая минералка / газировка (лимон, манго, малина,"
                " тархун) 🥭"
            ),
            "3️⃣ Горячий крепкий эспрессо без сахара ☕",
            "4️⃣ Классический молочный коктейль 🥛",
        ],
        "correct": [0, 1],
        "custom_error": (
            "Серьёзно, эспрессо или коктейль? Я же за свежую газировку и Cola"
            " Zero! 🥤 Давай ещё раз!"
        ),
    },
    {
        "text": (
            "<b>Блок 1 (3/25) 🍕</b>\n"
            "Какую пиццу Саша выбирает чаще всего для уютного вечера?"
        ),
        "options": [
            "1️⃣ Пепперони 🍕",
            "2️⃣ Чесночный цыплёнок 🧄",
            "3️⃣ Четыре сезона или Карбонара 🥓",
            "4️⃣ Гавайская с ананасами 🍍",
        ],
        "correct": [0, 1, 2],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 1 (4/25) 🍋</b>\n"
            "Какая вкусовая нотка в напитках и минералках Саше особенно"
            " нравится?"
        ),
        "options": [
            (
                "1️⃣ Цитрусовые и фруктовые (лимон, лайм, манго, тархун, груша,"
                " малина) 🍋"
            ),
            "2️⃣ Супер-острый соус или пряный имбирь 🌶",
            "3️⃣ Трюфельный или ореховый аромат 🍄",
            "4️⃣ Натуральный мятно-ментоловый вкус 🌿",
        ],
        "correct": [0],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 1 (5/25) 🌙</b>\n"
            "Как выглядит идеальный вечерний режим и отдых для Саши после"
            " долгого дня?"
        ),
        "options": [
            "1️⃣ Режим совы: почитать, посмотреть аниме или пообщаться 🌙",
            "2️⃣ Сыграть катку с друзьями (например, в CS2) 🎯",
            "3️⃣ Лечь спать ровно в 21:00, чтобы встать на пробежку в 6:00 🏃‍♂️",
            "4️⃣ Провести вечер за генеральной уборкой 🧹",
        ],
        "correct": [0, 1],
        "custom_error": None,
    },
    # БЛОК 2: Увлечения, книги, аниме и игры
    {
        "text": (
            "<b>Блок 2 (6/25) 🧠</b>\n"
            "Кто из этих персонажей аниме/манги ближе всего Саше по духу или"
            " характеру?"
        ),
        "options": [
            "1️⃣ Шикамару Нара (гениальный стратег) 🧠",
            "2️⃣ Наруто Узумаки (непреклонная энергия) 🍥",
            "3️⃣ Эрен Йегер / Эрза Скарлет (сила воли) ⚔️",
            "4️⃣ Сайтама (абсолютное спокойствие) 👊",
        ],
        "correct": [0, 2],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 2 (7/25) 📖</b>\n"
            "Какой роман или классическое произведение Саша особенно ценит за"
            " сюжет?"
        ),
        "options": [
            "1️⃣ «Граф Монте-Кристо» (Александр Дюма) 📖",
            "2️⃣ «Преступление и наказание» (Ф.М. Достоевский) 🪓",
            "3️⃣ «Мастер и Маргарита» (М.А. Булгаков) 🐈‍⬛",
            "4️⃣ «Герой нашего времени» (М.Ю. Лермонтов) 🎭",
        ],
        "correct": [0],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 2 (8/25) 🏔️</b>\n"
            "Какой отпуск или формат отдыха звучит для Саши как идеальная"
            " перезагрузка?"
        ),
        "options": [
            "1️⃣ Спокойный отдых в горах в уютной компании 🏔",
            "2️⃣ Отдых у моря в тихом месте с близкими и любимой 🌊",
            "3️⃣ Шумная вечеринка в клубе на 100 человек 🎉",
            "4️⃣ Экстрим-тур с ночёвками в палаточном лагере ⛺",
        ],
        "correct": [0, 1],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 2 (9/25) 🎯</b>\n"
            "В какую игру Саша чаще всего любит зайти для отдыха или каток с"
            " друзьями?"
        ),
        "options": [
            "1️⃣ Counter-Strike 2 (CS2) 🎯",
            "2️⃣ Dota 2 ⚔️",
            "3️⃣ Genshin Impact 🌸",
            "4️⃣ Minecraft / Terraria ⛏",
        ],
        "correct": [0],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 2 (10/25) 🥋</b>\n"
            "Какими видами спорта Саша реально занимался в своей жизни?"
        ),
        "options": [
            "1️⃣ Карате (боевые искусства и дисциплина) 🥋",
            "2️⃣ Плавание (дистанция и выносливость) 🏊",
            "3️⃣ Баскетбол и волейбол (командный азарт) 🏀🏐",
            "4️⃣ Футбол ⚽",
        ],
        "correct": [0, 1, 2],
        "custom_error": (
            "А вот и коварная ловушка! ⚽ Футбол — это миф! Попробуй другой"
            " вариант 😉"
        ),
    },
    # БЛОК 3: Факты и Фотки обо мне
    {
        "text": (
            "<b>Блок 3 (11/25) 📸</b>\n"
            "Что за суровый «подпольный клуб» запечатлён на этом фото?"
        ),
        "photo_id": "AgACAgIAAxkBAAMaanjCiF4PiJ7DySJEwEbM52vKLXMAAgMcaxvBpMBLN6p_Ufy-pw4BAAMCAAN5AAM9BA",
        "options": [
            "1️⃣ Сверхсекретная качалка с пацанами 🏋️‍♂️",
            "2️⃣ Подготовка к ограблению века 🕵️‍♂️",
            "3️⃣ Съёмки андеграунд рэп-клипа 🎤",
            "4️⃣ Пересменка в Самокат-сервисе 🛴",
        ],
        "correct": [0, 2, 3],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 3 (12/25) 📸</b>\n"
            "В каком легендарном стиле и образе собралась эта банда?"
        ),
        "photo_id": "AgACAgIAAxkBAAMcanjDDAFoCCgh0ZqxT7N4zzJbtqMAAgYcaxvBpMBLgLgFZh6Bo3oBAAMCAAN5AAM9BA",
        "options": [
            "1️⃣ «Острые козырьки» / Стильная Мафия 🎩",
            "2️⃣ Секретная служба охраны президента 🕶️",
            "3️⃣ Специальный отряд с игрушечным оружием 🔫",
            "4️⃣ Модельное агентство на показе коллекции 🧥",
        ],
        "correct": [0, 2],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 3 (13/25) 📸</b>\n"
            "Какая эпичная битва происходит на этом кадре перед зеркалом?"
        ),
        "photo_id": "AgACAgIAAxkBAAMeanjDQSqC5F2YvLG4q0bQgH_NahsAAgccaxvBpMBL6edBXRysMgsBAAMCAAN5AAM9BA",
        "options": [
            "1️⃣ Демонстрация фирменных стоек карате 🥋",
            "2️⃣ Спарринг за последние жареные пельмени 🥟",
            "3️⃣ Напряжённый аниме-поединок ⚔️",
            "4️⃣ Репетиция перед уличным баттлом 🥊",
        ],
        "correct": [0, 1, 2],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 3 (14/25) 📸</b>\n"
            "Что за маленькая легенда восстанавливает силы на этом архивном"
            " кадре?"
        ),
        "photo_id": "AgACAgIAAxkBAAMganjDegQQv9fGbzREFTIPw4-21LkAAggcaxvBpMBLuSTpLGT9ickBAAMCAAN5AAM9BA",
        "options": [
            "1️⃣ Маленький Саша восстанавливает ману 🍼",
            "2️⃣ Главный босс этой квартиры 👑",
            "3️⃣ Будущий IT-специалист на перерыве 💻",
            "4️⃣ Все варианты верны! ❤️",
        ],
        "correct": [0, 1, 2, 3],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 3 (15/25) 📸</b>\n"
            "Какой супер-секретный статус или роль у Саши на этом кадре?"
        ),
        "photo_id": "AgACAgIAAxkBAAMianjDlvxBdlYhU1TCOGRKLE6_fDgAAgkcaxvBpMBLacGQtdSXZxQBAAMCAAN5AAM9BA",
        "options": [
            "1️⃣ Анонимный хакер под прикрытием ☔",
            "2️⃣ Элегантный джентльмен 🎩",
            "3️⃣ Человек, готовый к любой погоде в помещении 🌧️",
            "4️⃣ Главный анонимный поклонник Ксюши 🕶️",
        ],
        "correct": [0, 1, 2, 3],
        "custom_error": None,
    },
    # БЛОК 4: Приключения, Характер и Мечты
    {
        "text": (
            "<b>Блок 4 (16/25) 🚂</b>\n"
            "Какая романтика поездок и транспорта Саше ближе всего по душе?"
        ),
        "options": [
            "1️⃣ Поезд: полка у окна, чаёк и аниме/манга 🚂",
            "2️⃣ Самолёт: главное — долететь за пару часов ✈️",
            "3️⃣ Автомобильное путешествие под музыку 🚗",
            "4️⃣ Пеший поход с огромным рюкзаком на 30 кг 🎒",
        ],
        "correct": [0, 2],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 4 (17/25) 🌊</b>\n"
            "Где Саша восстанавливает ресурс и энергию лучше всего?"
        ),
        "options": [
            "1️⃣ В тишине и уютном месте у моря 🌊",
            "2️⃣ В горах, где чистый воздух и красивейшие виды 🏔️",
            "3️⃣ Дома под пледом с вкусной едой и тайтлом/игрой 🍕",
            "4️⃣ В центре шумного мегаполиса 🏙️",
        ],
        "correct": [0, 1, 2],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 4 (18/25) 🧠</b>\n"
            "Какая главная сильная сторона включается у Саши в сложных"
            " ситуациях?"
        ),
        "options": [
            "1️⃣ Ледяное спокойствие и умение всё разложить по полкам 🧠",
            "2️⃣ Стратегический ум и поиск решения 🎯",
            "3️⃣ Забота и стремление защитить тех, кто рядом ❤️",
            "4️⃣ Начать паниковать и громко кричать 😱",
        ],
        "correct": [0, 1, 2],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 4 (19/25) ❤️</b>\n"
            "Что способно гарантированно поднять Саше настроение даже в самый"
            " хмурый день?"
        ),
        "options": [
            "1️⃣ Уютный вечер с любимым человеком / Ксюшей ❤️",
            "2️⃣ Вкусный сет из пиццы/бургера и прохладный напиток 🍔",
            "3️⃣ Хорошая катка в CS2 или крутая глава манги 🎯",
            "4️⃣ Утренняя внезапная контрольная 📐",
        ],
        "correct": [0, 1, 2],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 4 (20/25) ✨</b>\n"
            "Какая атмосфера для вечера звучит для Саши идеально?"
        ),
        "options": [
            "1️⃣ Тихий, тёплый вечер, когда не нужно никуда спешить 🌙",
            "2️⃣ Ночной марафон фильмов, аниме или сериалов 🎬",
            "3️⃣ Посиделки с близкими друзьями 👥",
            "4️⃣ Поход на ночную дискотеку в шумный клуб 💃",
        ],
        "correct": [0, 1, 2],
        "custom_error": None,
    },
    # БЛОК 5: Характер, фишки и главный секрет
    {
        "text": (
            "<b>Блок 5 (21/25) 💡</b>\n"
            "Как Саша обычно подходит к реализации важных задач или идей?"
        ),
        "options": [
            "1️⃣ Разложить всё по полочкам: структура, аналитика и план 🧠",
            "2️⃣ Делать всё наугад в последнюю минуту 🎲",
            "3️⃣ Написать документ на 100 страниц и бросить 📄",
            "4️⃣ Сидеть и ждать, пока всё сделается само собой 😴",
        ],
        "correct": [0],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 5 (22/25) 💖</b>\n"
            "В чём больше всего проявляется настоящая забота Саши?"
        ),
        "options": [
            "1️⃣ В поступках, поддержке, внимания к мелочам и уюте ❤️",
            "2️⃣ В отправке 500 мемов в минуту 📲",
            "3️⃣ В сухих SMS раз в три дня 📱",
            "4️⃣ В подарках вроде набора отвёрток 🧰",
        ],
        "correct": [0],
        "custom_error": (
            "Мемы — это база, но настоящая забота глубже! ❤️ Попробуй ещё!"
        ),
    },
    {
        "text": (
            "<b>Блок 5 (23/25) 🛡️</b>\n"
            "Какие черты характера описывают Сашу точнее всего?"
        ),
        "options": [
            "1️⃣ Спокойствие, надёжность, ум, верность и тонкий юмор 💡",
            "2️⃣ Драма на ровном месте и эмоциональные качели 🎭",
            "3️⃣ Легкомыслие и спонтанность без мыслей о будущем 🎈",
            "4️⃣ Шумность и стремление быть в центре огромной компании 🗣",
        ],
        "correct": [0],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 5 (24/25) 🔋</b>\n"
            "Что для Саши является самым лучшим «подзарядником» для души?"
        ),
        "options": [
            "1️⃣ Улыбка и тепло от Ксюши + вкусный перекус и спокойствие ❤️",
            "2️⃣ Тусовка в шумном ночном клубе до 6 утра 🪩",
            "3️⃣ Пробежать марафон на 42 км на рассвете 🏃‍♂️",
            "4️⃣ Читать комментарии в интернетах 📱",
        ],
        "correct": [0],
        "custom_error": None,
    },
    {
        "text": (
            "<b>Блок 5 (25/25) 🏆</b>\n"
            "Кто самая лучшая, любимая и неповторимая девочка для Саши на всём"
            " белом свете?"
        ),
        "options": [
            "1️⃣ Ксюша ❤️",
            "2️⃣ Ксюша 🥰",
            "3️⃣ Конечно же, Ксюша! 💖",
            "4️⃣ Абсолютно все варианты выше — единственная правда! ✨",
        ],
        "correct": [0, 1, 2, 3],
        "custom_error": None,
    }
]

# ---------------------------------------------------------
# 5. Вспомогательные функции для клавиатуры с галочками
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 6. Обработчики команд и логика квиза
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["current_question_index"] = 0
    context.user_data["selected_options"] = set()

    welcome_text = (
        "<b>Привет! 👋</b>\n\n"
        "Добро пожаловать в специальную викторину!\n"
        "Выбирай варианты ответа (можно поставить галочки ☑️ напротив нескольких), "
        "а затем нажимай <b>«Подтвердить выбор 🚀»</b>.\n\n"
        "Погнали!"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, parse_mode="HTML")
        
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get("current_question_index", 0)
    
    if index >= len(QUIZ_DATA):
        final_text = (
            "🎉 <b>Ура! Викторина полностью пройдена!</b> 🎉\n\n"
            "Ты отлично знаешь Сашу! Спасибо за прохождение, ты умничка на 100%! ❤️✨"
        )
        if update.callback_query:
            await update.callback_query.message.reply_text(final_text, parse_mode="HTML")
        else:
            await update.message.reply_text(final_text, parse_mode="HTML")
        return

    question = QUIZ_DATA[index]
    context.user_data["selected_options"] = set()
    reply_markup = build_keyboard(question, context.user_data["selected_options"])

    chat_id = update.effective_chat.id

    if question.get("photo_id"):
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=question["photo_id"],
            caption=question["text"],
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=question["text"],
            parse_mode="HTML",
            reply_markup=reply_markup
        )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    selected = context.user_data.setdefault("selected_options", set())
    data = query.data
    current_index = context.user_data.get("current_question_index", 0)

    if current_index >= len(QUIZ_DATA):
        await query.answer()
        return

    current_q = QUIZ_DATA[current_index]

    if data.startswith("select_"):
        await query.answer()
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

        # Проверяем, являются ли ВСЕ выбранные варианты правильными
        is_correct = all(idx in current_q["correct"] for idx in selected)

        if not is_correct:
            # Если ответ неверный — показываем личную шутку или случайный подкол
            error_msg = current_q.get("custom_error") or random.choice(WRONG_ANSWER_TEASES)
            await query.answer(error_msg, show_alert=True)
            return
        
        # Если всё верно
        await query.answer("Супер! Верно! 🎉")
        context.user_data["current_question_index"] += 1
        await send_question(update, context)

async def echo_photo_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    await update.message.reply_text(f"Вот `file_id` твоей фотографии:\n\n`{file_id}`", parse_mode="Markdown")

# ---------------------------------------------------------
# 7. Главная функция запуска
# ---------------------------------------------------------
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
