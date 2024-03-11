import telebot
from bot_token import *
import csv
import datetime

bot = telebot.TeleBot(TOKEN)  # создаём объект бота с нашим токеном
main_menu = telebot.types.ReplyKeyboardMarkup(True, False)
state = None


@bot.message_handler(commands=['start'])
def start(message):
    global state
    main_menu.row('Записаться на хобби')
    main_menu.row('Записаться к врачу')
    main_menu.row('/help')
    state = 'home'
    bot.send_message(message.chat.id,
                     f'Здравствуйте, {message.chat.first_name}! \n'
                     f'Я ваш личный бот для записи ребенка на мероприятия и другие различные события\n'
                     f'٩(◕‿◕｡)۶\n'
                     f'Для помощи по боту можете воспользоваться командой /help',
                     parse_mode='html', reply_markup=main_menu)


@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id,
                     f'Здесь будет документашка\n',
                     parse_mode='html')


@bot.message_handler(content_types=['text'])
def message_reply(message):
    if state == 'home':
        match message.text:
            case 'Записаться на хобби':
                choose_hobby_handler(message)
            case 'Записаться к врачу':
                make_an_appointment_with_doctor_handler(message)
    elif state == 'choose_hobby':
        match message.text:
            case '🎸Занятия на гитаре🎸':
                choose_guitar_group(message)
            case '💃Танцевальный кружок🕺':
                pass
    elif state == 'choose_doctor':
        pass


def choose_hobby_handler(message):
    global state
    state = 'choose_hobby'

    choose_hobby_menu = telebot.types.ReplyKeyboardMarkup(True, True)
    choose_hobby_menu.row('🎸Занятия на гитаре🎸')
    choose_hobby_menu.row('💃Танцевальный кружок🕺')
    choose_hobby_menu.row('/help')

    bot.send_message(message.chat.id,
                     f'Выберите хобби\n',
                     parse_mode='html', reply_markup=choose_hobby_menu)


def make_an_appointment_with_doctor_handler(message):
    global state
    state = 'choose_doctor'

    choose_doctor_menu = telebot.types.ReplyKeyboardMarkup(True, True)
    choose_doctor_menu.row('Стоматолог')
    choose_doctor_menu.row('Педиатр')
    choose_doctor_menu.row('/help')

    bot.send_message(message.chat.id,
                     f'Выберите нужного врача\n',
                     parse_mode='html', reply_markup=choose_doctor_menu)


def choose_guitar_group(message):
    global state
    state = 'choose_guitar_group'

    # todo: Здесь нужно сначала чекнуть, какие вообще есть возможные группы на запись
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

    buttons = telebot.types.InlineKeyboardMarkup()
    buttons.add(telebot.types.InlineKeyboardButton(text="1 группа (...)", callback_data=f'1 {message.chat.id}'))
    buttons.add(telebot.types.InlineKeyboardButton(text="2 группа (...)", callback_data=f'2 {message.chat.id}'))

    bot.send_message(message.chat.id,
                     f'Выберите желаемую группу\n',
                     parse_mode='html', reply_markup=buttons)


def join_a_group_guitar(number_of_group, user_id):
    #  todo: здесь нужно добавить челика в кол-во человек в группе и пометить у него
    print(f'чел хочет попасть в {number_of_group}, id={user_id}')

    global state
    state = 'home'


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    match state:
        case 'choose_guitar_group':
            call.data = call.data.split()
            join_a_group_guitar(call.data[0], call.data[1])
        case 'choose_doctor':
            None


def main():
    bot.infinity_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
