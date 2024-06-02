import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import MessageHandler, filters
import sqlite3

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Создание и подключение к базе данных
conn = sqlite3.connect('career_advice.db')
c = conn.cursor()

# Создание таблицы с советами
c.execute('''CREATE TABLE IF NOT EXISTS advice
             (id INTEGER PRIMARY KEY, category TEXT, advice TEXT)''')
conn.commit()

# Заполнение таблицы примерами данных
sample_data = [
    ('IT', 'Рассмотрите возможность стать разработчиком программного обеспечения.'),
    ('IT', 'Попробуйте изучить Data Science.'),
    ("IT", "советую посетить эти сайты "),
    ('Marketing', 'Карьерный путь в цифровом маркетинге может быть интересным.'),
    ('Marketing', 'Подумайте о роли менеджера по продукту.'),
    ('Marketing', 'ПОсмотрите на возможные сайты с продукцыей.'),
    
]

c.executemany('INSERT INTO advice (category, advice) VALUES (?, ?)', sample_data)
conn.commit()

# Функция для получения совета по категории
def get_advice(category):
    c.execute('SELECT advice FROM advice WHERE category = ?', (category,))
    return c.fetchall()

# Стартовая функция
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я помогу вам выбрать карьеру. Выберите интересующую категорию:', reply_markup=main_menu_keyboard())

# Главное меню
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('IT', callback_data='category_IT')],
        [InlineKeyboardButton('Маркетинг', callback_data='category_Marketing')],
        
        # Добавьте другие категории по мере необходимости
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчик выбора категории
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    category = query.data.split('_')[1]
    advices = get_advice(category)
    
    if advices:
        response = f'Советы для карьеры в категории {category}:\n'
        for advice in advices:
            response += f"- {advice[0]}\n"
    else:
        response = f'Извините, в категории {category} пока нет советов.'
    
    await query.edit_message_text(text=response, reply_markup=back_to_main_menu_keyboard())

# Кнопка "Назад"
def back_to_main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Назад', callback_data='main_menu')]]
    return InlineKeyboardMarkup(keyboard)

# Возврат в главное меню
async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text='Выберите интересующую категорию:', reply_markup=main_menu_keyboard())

# Основная функция
def main():
    # Вставьте сюда свой токен
    application = Application.builder().token("6919803088:AAFNDYxJ631t9ZvHjVp4Q3oG5o2rZl7Yx6w").build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(category_handler, pattern='^category_'))
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern='^main_menu'))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
