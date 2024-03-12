import telebot
from bot_token import *
from csv_functions import *
import csv
import datetime

bot = telebot.TeleBot(TOKEN)  # создаём объект бота с нашим токеном
days = {'M': 'пн',
        'T': 'вт',
        'W': 'ср',
        'Th': 'чт',
        'F': 'пт',
        'Sa': 'сб',
        'Su': 'вс'}

# todo: сделать напоминания
# todo: сделать вывод всех возможных (и занятых) групп
# todo: сделать регистрацию новых челов
@bot.message_handler(commands=['start'])
def start(message):
    main_menu = create_home_menu()
    setState(message.chat.id, 'home')
    bot.send_message(message.chat.id,
                     f'Здравствуйте, {message.chat.first_name}! \n'
                     f'Я ваш личный бот для записи ребенка на мероприятия и другие различные события\n'
                     f'٩(◕‿◕｡)۶\n'
                     f'Для помощи по боту можете воспользоваться командой /help',
                     parse_mode='html', reply_markup=main_menu)


def create_home_menu():
    main_menu = telebot.types.ReplyKeyboardMarkup(True, False)
    main_menu.row('/start', '/help')
    main_menu.row('Записаться на хобби', 'Записаться к врачу')
    main_menu.row('Посмотреть мои записи на хобби')
    main_menu.row('Отказаться от группы')
    return main_menu


@bot.message_handler(commands=['help'])
def give_help(message):
    bot.send_message(message.chat.id,
                     f'Здесь будет документашка\n',
                     parse_mode='html')


@bot.message_handler(commands=['getstate'])
def get_state_command(message):
    bot.send_message(message.chat.id,
                     f'{getState(message.chat.id)}',
                     parse_mode='html')


@bot.message_handler(content_types=['text'])
def message_reply(message):
    if getState(message.chat.id) == 'home':
        match message.text:
            case 'Записаться на хобби':
                choose_hobby_handler(message)
            case 'Записаться к врачу':
                make_an_appointment_with_doctor_handler(message)
            case 'Посмотреть мои записи на хобби':
                get_my_hobbies(message)
            case 'Отказаться от группы':
                refuse_hobby(message)
    elif getState(message.chat.id) == 'choose_hobby':
        match message.text:
            case '🎸Занятия на гитаре🎸':
                choose_guitar_group(message)
            case '💃Танцевальный кружок🕺':
                setState(message.chat.id, 'home')
                bot.send_message(message.chat.id,
                                 "Эта функция пока что не готова... Сори(",
                                 parse_mode='html',
                                 reply_markup=create_home_menu())
    elif getState(message.chat.id) == 'refuse_hobby':
        match message.text:
            case 'Занятия на гитаре':
                choose_guitar_group_to_refuse(message)
            case 'Танцы':
                setState(message.chat.id, 'home')
                bot.send_message(message.chat.id,
                                 "Эта функция пока что не готова... Сори(",
                                 parse_mode='html',
                                 reply_markup=create_home_menu())


def refuse_hobby(message):
    setState(message.chat.id, 'refuse_hobby')

    choose_hobby_to_refuse = telebot.types.ReplyKeyboardMarkup(True, True)
    choose_hobby_to_refuse.row('Занятия на гитаре')
    choose_hobby_to_refuse.row('Танцы')
    choose_hobby_to_refuse.row('/help')

    bot.send_message(message.chat.id,
                     f'От группы какого хобби вы хотите отказаться?\n',
                     parse_mode='html', reply_markup=choose_hobby_to_refuse)


def choose_guitar_group_to_refuse(message):
    setState(message.chat.id, 'refuse_guitar_group')

    # составление списка групп, в которых состоит пользователь
    guitar_groups_already = []
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        user_id = str(message.chat.id)
        for row in file_reader:
            if row["UserId"] == user_id and len(row["guitar"]) != 0:
                guitar_groups_already = row["guitar"].split(' ')
                break

    # если у пользователя нет групп по гитаре
    if len(guitar_groups_already) == 0:
        setState(message.chat.id, 'home')
        bot.send_message(message.chat.id,
                         f'У вас нет выбранных групп занятий по гитаре',
                         parse_mode='html', reply_markup=create_home_menu())
        return 0

    with open("Data/guitar_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        descriptions_of_groups = []
        groups = []
        for row in file_reader:
            # если человек уже состоит в данной группе берем информацию о ней
            if row["Group"] in guitar_groups_already:
                descriptions_of_groups.append(f'Группа №{row["Group"]} '
                                              f'с преподавателем {row["Teacher"]},\n'
                                              f'Занятия по {days[row["Day"]]} '
                                              f'в {row["Time"]}, '
                                              f'{row["Fullness"]} людей в группе\n')
                groups.append(f'Группа №{row["Group"]}')
    buttons = telebot.types.InlineKeyboardMarkup()
    for group in groups:
        buttons.add(telebot.types.InlineKeyboardButton(text=group, callback_data=f'{group[8:]} {message.chat.id}'))
    bot.send_message(message.chat.id,
                     f'Выберите группу, от которой хотите отказаться.\nВы можете отказаться от следующих групп:\n\n' +
                     '\n'.join(descriptions_of_groups),
                     parse_mode='html', reply_markup=buttons)


def get_my_hobbies(message):
    # получение заголовков столбцов в виде списка
    hobbies = []
    with open("Data/users.csv", encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        hobbies = next(csv_reader)
    # срезаем первый заголовок (id пользователя), оставшиеся - всевозможные хобби
    hobbies = hobbies[1:]

    groups_in_hobby = {hobby: [] for hobby in hobbies}
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["UserId"] == str(message.chat.id):
                for hobby in hobbies:
                    if len(row[hobby]) != 0:  # проверка на то, что в списке групп на данное хобби не пусто
                        groups_in_hobby[hobby] = row[hobby].split()
                break

    # сначала собираем в output описания групп по гитаре
    descriptions_of_groups_guitar = []
    with open("Data/guitar_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["Group"] in groups_in_hobby["guitar"]:
                descriptions_of_groups_guitar.append(f'Группа №{row["Group"]} '
                                                     f'с преподавателем {row["Teacher"]},\n'
                                                     f'Занятия по {days[row["Day"]]} '
                                                     f'в {row["Time"]}, '
                                                     f'{row["Fullness"]} людей в группе (включая вас)\n')
    # потом собираем описания групп по танцам
    descriptions_of_groups_dances = []
    with open("Data/dances_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["Group"] in groups_in_hobby["dances"]:
                descriptions_of_groups_dances.append(f'Группа №{row["Group"]} '
                                                     f'с хореографом {row["Choreographer"]},\n'
                                                     f'Занятия по {days[row["Day"]]} '
                                                     f'в {row["Time"]}, '
                                                     f'{row["Fullness"]} людей в группе (включая вас)\n')
    if len(descriptions_of_groups_guitar) == 0 and len(descriptions_of_groups_dances) == 0:
        output_message = 'У вас пока что нет записей на хобби'
    else:
        output_message = 'У вас есть следующие записи на хобби:\n\n'
    if len(descriptions_of_groups_guitar) != 0:
        output_message += 'Занятия по гитаре:\n' + ''.join(descriptions_of_groups_guitar) + '\n'
    if len(descriptions_of_groups_dances) != 0:
        output_message += 'Занятия по танцам:\n' + ''.join(descriptions_of_groups_dances) + '\n'
    bot.send_message(message.chat.id, output_message, parse_mode='html')


def choose_hobby_handler(message):
    setState(message.chat.id, 'choose_hobby')

    choose_hobby_menu = telebot.types.ReplyKeyboardMarkup(True, True)
    choose_hobby_menu.row('🎸Занятия на гитаре🎸')
    choose_hobby_menu.row('💃Танцевальный кружок🕺')
    choose_hobby_menu.row('/help')

    bot.send_message(message.chat.id,
                     f'Выберите хобби\n',
                     parse_mode='html', reply_markup=choose_hobby_menu)


def make_an_appointment_with_doctor_handler(message):
    setState(message.chat.id, 'choose_doctor')

    choose_doctor_menu = telebot.types.ReplyKeyboardMarkup(True, True)
    choose_doctor_menu.row('Стоматолог')
    choose_doctor_menu.row('Педиатр')
    choose_doctor_menu.row('/help')

    bot.send_message(message.chat.id,
                     f'Выберите нужного врача\n',
                     parse_mode='html', reply_markup=choose_doctor_menu)


def choose_guitar_group(message):
    setState(message.chat.id, 'choose_guitar_group')

    # составление списка групп, в которых пользователь уже состоит
    guitar_groups_already = []
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        user_id = str(message.chat.id)

        for row in file_reader:
            if row["UserId"] == user_id:
                guitar_groups_already = row["guitar"].split(' ')
                break

    # составление списка групп, в которые может зачислиться пользователь
    with open("Data/guitar_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        descriptions_of_groups = []
        groups = []
        for row in file_reader:
            # если группа переполнена, то пропускаем её
            fullness = list(map(int, row["Fullness"].split('/')))
            if fullness[0] >= fullness[1]:
                # если кол-во людей до "/" больше или равно людей после "/", т.е. группа переполнена
                continue
            # если человек уже состоит в данной группе, то пропускаем её
            if row["Group"] in guitar_groups_already:
                continue
            descriptions_of_groups.append(f'Группа №{row["Group"]} '
                                          f'с преподавателем {row["Teacher"]},\n'
                                          f'Занятия по {days[row["Day"]]} '
                                          f'в {row["Time"]}, '
                                          f'{row["Fullness"]} людей в группе\n')
            groups.append(f'Группа №{row["Group"]}')

    if len(groups) == 0:
        setState(message.chat.id, 'home')
        bot.send_message(message.chat.id,
                         f'Извините, для вас нет доступных групп.\n'
                         f'Вы состоите во всех группах, либо в оставшихся группах нет мест',
                         parse_mode='html', reply_markup=create_home_menu())
    else:
        buttons = telebot.types.InlineKeyboardMarkup()
        for group in groups:
            buttons.add(telebot.types.InlineKeyboardButton(text=group, callback_data=f'{group[8:]} {message.chat.id}'))
        bot.send_message(message.chat.id,
                         f'Выберите желаемую группу.\nВам доступны следующие группы:\n\n' +
                         '\n'.join(descriptions_of_groups),
                         parse_mode='html', reply_markup=buttons)


def edit_a_group_guitar(number_of_group, user_id, mode):
    # mode - 'add'/'remove' - добавить человека в группу или удалить из нее

    # правка файла hobbies (дозапись/удаление группы у пользователя)
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["UserId"] == user_id:
                old_guitar_groups = row["guitar"].split()
                if mode == 'add':
                    new_guitar_groups = sorted(old_guitar_groups + [number_of_group])
                elif mode == 'remove':
                    new_guitar_groups = old_guitar_groups.copy()
                    new_guitar_groups.remove(number_of_group)
                update_csv_cell("Data/users.csv",
                                "guitar",
                                file_reader.line_num - 2,
                                ' '.join(new_guitar_groups))
                break

    # правка файла guitar lessons (пополнение/уменьшение количества пользователей в группе)
    with open("Data/guitar_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["Group"] == number_of_group:
                old_fullness = row["Fullness"].split('/')
                if mode == 'add':
                    new_fullness = [str(int(old_fullness[0]) + 1), old_fullness[1]]
                elif mode == 'remove':
                    new_fullness = [str(int(old_fullness[0]) - 1), old_fullness[1]]
                update_csv_cell("Data/guitar_lessons.csv",
                                "Fullness",
                                file_reader.line_num - 2,
                                '/'.join(new_fullness))
                break

    # завершение зачисления/удаления из группы и возвращение в состояние "home"
    setState(user_id, 'home')
    message = (f'Вы зачислены в группу' if mode == 'add' else f'Вы отказались от группы') + f' №{number_of_group}\n'
    bot.send_message(user_id,
                     message,
                     parse_mode='html', reply_markup=create_home_menu())


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    call.data = call.data.split()
    match getState(call.data[1]):
        case 'choose_guitar_group':
            edit_a_group_guitar(call.data[0], call.data[1], 'add')
        case 'refuse_guitar_group':
            edit_a_group_guitar(call.data[0], call.data[1], 'remove')


def main():
    bot.infinity_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
