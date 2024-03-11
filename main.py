import telebot
from bot_token import *
import csv

bot = telebot.TeleBot(TOKEN)  # создаём объект бота с нашим токеном
main_menu = telebot.types.ReplyKeyboardMarkup(True, False)
state = None

@bot.message_handler(commands=['start'])
def start(message):
    move_to_home()
    bot.send_message(message.chat.id,
                     f'Здравствуйте, {message.chat.first_name}! \n'
                     f'Я ваш личный бот для записи ребенка на мероприятия и другие различные события\n'
                     f'٩(◕‿◕｡)۶\n'
                     f'Для помощи по боту можете воспользоваться командой /help',
                     parse_mode='html', reply_markup=main_menu)

def move_to_home():
    global state
    state = 'home'
    main_menu.row('Записаться на хобби')
    main_menu.row('Записаться к врачу')
    main_menu.row('/help')


@bot.message_handler(commands=['help'])
def start(message):
    move_to_home()
    bot.send_message(message.chat.id,
                     f'Здравствуйте, {message.chat.first_name}! \n'
                     f'Я ваш личный бот для записи ребенка на мероприятия и другие различные события\n'
                     f'٩(◕‿◕｡)۶\n'
                     f'Для помощи по боту можете воспользоваться командой /help',
                     parse_mode='html', reply_markup=main_menu)

@bot.message_handler(content_types=['text'])
def message_reply(message):
    pass


def main():
    global main_menu
    # with open("Data/pediatr.csv", encoding='utf-8') as file:
    #     # Создаем объект DictReader, указываем символ-разделитель ","
    #     file_reader = csv.DictReader(file, delimiter=",")
    #     # Счетчик для подсчета количества строк и вывода заголовков столбцов
    #     count = 0
    #     # Считывание данных из CSV файла
    #     for row in file_reader:
    #         # Вывод строк
    #         print(row)
    #         count += 1
    #     print(f'Всего в файле {count + 1} строк.')
    bot.infinity_polling()




# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
