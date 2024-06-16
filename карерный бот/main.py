import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler
import sqlite3

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Подключение к базе данных
conn = sqlite3.connect('career_advice.db')
c = conn.cursor()

# Создание таблицы с советами
c.execute('''CREATE TABLE IF NOT EXISTS advice
             (id INTEGER PRIMARY KEY, category TEXT, advice TEXT)''')
conn.commit()

# Заполнение таблицы примерами данных (если таблица пуста)
sample_data = [
    ('IT', 'Рассмотрите возможность стать разработчиком программного обеспечения.'),
    ('IT', 'Попробуйте изучить Data Science.'),
    ('Marketing', 'Карьерный путь в цифровом маркетинге может быть интересным.'),
    ('Marketing', 'Подумайте о роли менеджера по продукту.'),
    ('Design', 'Изучите графический дизайн и создавайте визуальные концепции.'),
    ('Design', 'Попробуйте себя в веб-дизайне, разрабатывая интерфейсы сайтов.'),
    ('Finance', 'Рассмотрите карьеру финансового аналитика.'),
    ('Finance', 'Подумайте о роли бухгалтера или аудитора.'),
    ('Healthcare', 'Изучите медицинские науки для карьеры врача или медсестры.'),
    ('Healthcare', 'Попробуйте себя в фармацевтике.'),
    ('Education', 'Рассмотрите карьеру учителя или преподавателя.'),
    ('Education', 'Изучите педагогические методы для работы с детьми.'),
    ('Engineering', 'Изучите машиностроение или электротехнику.'),
    ('Engineering', 'Подумайте о карьере в гражданском строительстве.'),
    ('Law', 'Рассмотрите возможность стать юристом.'),
    ('Law', 'Изучите право и попробуйте себя в юридическом консалтинге.'),
    ('Arts', 'Попробуйте карьеру в изобразительном искусстве или фотографии.'),
    ('Arts', 'Изучите актёрское мастерство или режиссуру.')
]

c.executemany('INSERT INTO advice (category, advice) VALUES (?, ?)', sample_data)
conn.commit()

# Структура вопросов и ответов
questions = {
    'IT': [
        ("Вы любите программирование?", 'Да', 'Нет'),
        ("Вам интересно работать с данными?", 'Да', 'Нет'),
    ],
    'Marketing': [
        ("Вам нравится анализировать рынок?", 'Да', 'Нет'),
        ("Вы творческий человек?", 'Да', 'Нет'),
    ],
    'Design': [
        ("Вы увлечены визуальным искусством?", 'Да', 'Нет'),
        ("Вы любите создавать что-то новое?", 'Да', 'Нет'),
    ],
    'Finance': [
        ("Вам нравится работать с цифрами?", 'Да', 'Нет'),
        ("Вы внимательны к деталям?", 'Да', 'Нет'),
    ],
    'Healthcare': [
        ("Вы хотите помогать людям?", 'Да', 'Нет'),
        ("Вас интересуют медицинские науки?", 'Да', 'Нет'),
    ],
    'Education': [
        ("Вам нравится обучать других?", 'Да', 'Нет'),
        ("Вы терпеливый человек?", 'Да', 'Нет'),
    ],
    'Engineering': [
        ("Вам интересны технологии?", 'Да', 'Нет'),
        ("Вы любите решать сложные задачи?", 'Да', 'Нет'),
    ],
    'Law': [
        ("Вам интересны законы и правосудие?", 'Да', 'Нет'),
        ("Вы умеете хорошо аргументировать?", 'Да', 'Нет'),
    ],
    'Arts': [
        ("Вы творческая личность?", 'Да', 'Нет'),
        ("Вы увлечены искусством?", 'Да', 'Нет'),
    ]
}

# Определение состояний для ConversationHandler
CATEGORY, QUESTION, RESULT = range(3)

# Стартовая функция
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я помогу вам выбрать карьеру. Выберите интересующую категорию:', reply_markup=main_menu_keyboard())

# Главное меню
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('IT', callback_data='category_IT')],
        [InlineKeyboardButton('Маркетинг', callback_data='category_Marketing')],
        [InlineKeyboardButton('Дизайн', callback_data='category_Design')],
        [InlineKeyboardButton('Финансы', callback_data='category_Finance')],
        [InlineKeyboardButton('Здравоохранение', callback_data='category_Healthcare')],
        [InlineKeyboardButton('Образование', callback_data='category_Education')],
        [InlineKeyboardButton('Инженерия', callback_data='category_Engineering')],
        [InlineKeyboardButton('Право', callback_data='category_Law')],
        [InlineKeyboardButton('Искусство', callback_data='category_Arts')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text='Выберите интересующую категорию:', reply_markup=main_menu_keyboard())
    return CATEGORY

# Обработчик выбора категории
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    category = query.data.split('_')[1]
    context.user_data['category'] = category
    context.user_data['answers'] = []
    logging.info(f"Category selected: {category}")
    return await ask_question(update, context)

# Задать вопрос
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = context.user_data['category']
    questions_list = questions[category]
    question_index = len(context.user_data['answers'])

    if question_index < len(questions_list):
        question_text, yes_text, no_text = questions_list[question_index]
        keyboard = [
            [InlineKeyboardButton(yes_text, callback_data='answer_Yes')],
            [InlineKeyboardButton(no_text, callback_data='answer_No')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.edit_message_text(text=question_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text=question_text, reply_markup=reply_markup)
        logging.info(f"Question asked: {question_text}")
        return QUESTION
    else:
        return await show_result(update, context)

# Обработчик ответов на вопросы
async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    answer = query.data.split('_')[1]
    context.user_data['answers'].append(answer)
    logging.info(f"Answer received: {answer}")
    return await ask_question(update, context)

# Показать результат
async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = context.user_data['category']
    answers = context.user_data['answers']

    # Логика определения лучшего совета
    advice = get_best_advice(category, answers)
    response = f'Ваши ответы: {", ".join(answers)}\n'
    response += f'Наиболее подходящий совет для карьеры в категории {category}:\n'
    response += f"- {advice}"

    await update.callback_query.edit_message_text(text=response, reply_markup=back_to_main_menu_keyboard())
    logging.info(f"Result shown for category {category}")
    return RESULT

def back_to_main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Назад', callback_data='main_menu')]]
    return InlineKeyboardMarkup(keyboard)

# Возврат в главное меню
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text='Выберите интересующую категорию:', reply_markup=main_menu_keyboard())
    return ConversationHandler.END

def get_best_advice(category, answers):
    c.execute('SELECT DISTINCT advice FROM advice WHERE category = ?', (category,))
    advices = c.fetchall()
    # Простой пример логики оценки советов
    score = {advice[0]: 0 for advice in advices}
    for answer in answers:
        if answer == 'Yes':
            for advice in advices:
                if 'да' in advice[0].lower():
                    score[advice[0]] += 1
        else:
            for advice in advices:
                if 'нет' in advice[0].lower():
                    score[advice[0]] += 1
    best_advice = max(score, key=score.get)
    return best_advice

# Основная функция
def main():
    # Вставьте сюда свой токен
    application = Application.builder().token("").build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(category_handler, pattern='^category_')],
        states={
            QUESTION: [CallbackQueryHandler(answer_handler, pattern='^answer_')],
            RESULT: [CallbackQueryHandler(back_to_main_menu, pattern='^main_menu')],
        },
        fallbacks=[CallbackQueryHandler(back_to_main_menu, pattern='^main_menu')]
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern='^main_menu'))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
           
