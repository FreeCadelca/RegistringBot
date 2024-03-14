import telebot
from bot_token import *
import csv

# создаём бота с нашим токеном, который получили от botfather
bot = telebot.TeleBot(TOKEN)
# словарь для перевода дней недели с английского на русский
days = {'M': 'пн',
        'T': 'вт',
        'W': 'ср',
        'Th': 'чт',
        'F': 'пт',
        'Sa': 'сб',
        'Su': 'вс'}


# вспомогательная функция для обновления ячейки в csv таблице
def update_csv_cell(path: str, col: str, row_num: int, new_value: str):
    new_rows = []
    with open(path, encoding='utf-8') as file:
        # получение заголовков столбцов в виде списка
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
    with open(path, encoding='utf-8') as file:
        # копирование всех строк из старого csv файла
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            new_row = {i: row[i] for i in headers}
            new_rows.append(new_row)

    # теперь, когда мы скопировали всю информацию из старого csv в словарь, можем изменять нужную ячейку
    new_rows[row_num][col] = new_value

    # записываем в файл заново все данные с изменённой ячейкой,
    # нужно перезаписывать всю таблицу, csv по-другому не умеет
    with open(path, "w", newline='\n', encoding='utf-8') as file:
        data = csv.DictWriter(file, delimiter=',', fieldnames=headers)
        data.writerow(dict((heads, heads) for heads in headers))
        data.writerows(new_rows)


# вспомогательная функция для получения состояния пользователя в users.csv
def getState(user_id):
    user_id = str(user_id)
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["UserId"] == user_id:
                return row["state"]


# вспомогательная функция для обновления состояния пользователя на новое в users.csv
def setState(user_id, new_state: str):
    user_id = str(user_id)
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["UserId"] == user_id:
                update_csv_cell("Data/users.csv", "state", file_reader.line_num - 2, new_state)
                break


# вспомогательная функция для добавления новой строчки в csv таблице.
# Функция нужна по большей мере для регистрации нового пользователя в функции start - обработчике /start,
# больше нигде не используется
def add_row(path: str, new_row: str):
    # получение заголовков столбцов в виде списка
    with open(path, encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)

    # копирование всех строк из старого csv файла
    rows = []
    with open(path, encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            new_row_to_add = {i: row[i] for i in headers}
            rows.append(new_row_to_add)

    # теперь, когда мы скопировали всю информацию из старого csv в словарь, можем добавить туда новую строку
    new_row = new_row.split(',')
    new_row_dict = dict()
    for i in range(len(headers)):
        new_row_dict[headers[i]] = new_row[i]
    rows.append(new_row_dict)

    # записываем в файл заново весь словарь с данными
    # (снова потому что csv по-другому не умеет)
    with open(path, "w", newline='\n', encoding='utf-8') as file:
        data = csv.DictWriter(file, delimiter=',', fieldnames=headers)
        data.writerow(dict((heads, heads) for heads in headers))
        data.writerows(rows)


# вспомогательная функция для записи сообщений чата в Texts.txt
def write_to_logs(message: str, who: str):
    # who - 'user'/'bot'
    with open("Texts.txt", "a", encoding="utf-8") as file:
        if who == 'user':
            file.write(f'User:\n{message}\n\n')
        elif who == 'bot':
            file.write(f'Bot:\n{message}\n\n')


# обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    write_to_logs(message.text, 'user')
    # проверяем, существует ли в базе данных пользователь
    isUserExist = False
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        user_id = str(message.chat.id)
        for row in file_reader:
            if row["UserId"] == user_id:
                # если нашли, то записываем истину в переменную-флаг и выходим из цикла
                isUserExist = True
                break
    # если пользователь не существует, то добавляем в users.csv строчку с ним
    if isUserExist == False:
        add_row("Data/users.csv", f'{str(message.chat.id)},home,,')

    main_menu = create_home_menu()
    setState(message.chat.id, 'home')
    bot.send_message(message.chat.id,
                     f'Здравствуйте, {message.chat.first_name}! \n'
                     f'Я ваш личный бот для записи в группы по хобби\n'
                     f'٩(◕‿◕｡)۶\n'
                     f'Для помощи по боту можете воспользоваться командой /help',
                     parse_mode='html', reply_markup=main_menu)
    write_to_logs(f'Здравствуйте, {message.chat.first_name}! \n'
                  f'Я ваш личный бот для записи в группы по хобби\n'
                  f'٩(◕‿◕｡)۶\n'
                  f'Для помощи по боту можете воспользоваться командой /help',
                  'bot')


# функция для создания кнопок меню домашней страницы
def create_home_menu():
    home_menu = telebot.types.ReplyKeyboardMarkup(True, False)
    home_menu.row('/start', '/help')
    home_menu.row('Записаться на хобби')
    home_menu.row('Посмотреть мои записи на хобби', 'Отказаться от группы')
    return home_menu


# обработчик команды /help
@bot.message_handler(commands=['help'])
def give_help(message):
    write_to_logs(message.text, 'user')
    help_message = (f'Я - бот для записи в группы по хобби.\n\n'
                    f'Для того, чтобы записаться в группу, нажимите ниже на кнопку "Записаться на хобби", '
                    f'далее можете посмотреть все существующие группы или выбрать то занятие, '
                    f'в группу по которому вы хотите записаться (гитара/танцы). '
                    f'После этого вам будут предложены группы, в которые у вас есть возможность записаться, '
                    f'нажмите на кнопку с нужной вам группой под сообщением бота.\n\n'
                    f'<u>Имейте в виду, что пока бот предлагает вам выбрать группы, остальные команды '
                    f'(кроме /start, /home и /help), не будут работать.</u>\n\n'
                    f'Также вы можете отказаться от группы, нажав на соответствующую кнопку на клавиатуре или '
                    f'посмотреть свои выбранные группы')
    bot.send_message(message.chat.id, help_message, parse_mode='html')
    write_to_logs(help_message, 'bot')


# обработчик команды /getstate (использовается для отладки)
@bot.message_handler(commands=['getstate'])
def get_state_command(message):
    write_to_logs(message.text, 'user')
    bot.send_message(message.chat.id,
                     f'{getState(message.chat.id)}',
                     parse_mode='html')
    write_to_logs(f'{getState(message.chat.id)}', 'bot')


# обработчик команды /home
@bot.message_handler(commands=['home'])
def home(message):
    write_to_logs(message.text, 'user')
    setState(message.chat.id, 'home')
    bot.send_message(message.chat.id,
                     f'Перемещаю на домашнюю страницу\n',
                     parse_mode='html', reply_markup=create_home_menu())
    write_to_logs(f'Перемещаю на домашнюю страницу\n', 'bot')


# обработчик всех текстовых сообщений (не команд!),
# в нашем случае - кнопок, которые реализуются без команд (без / в начале)
@bot.message_handler(content_types=['text'])
def message_reply(message):
    write_to_logs(message.text, 'user')
    # сначала проверяем состояния пользователя, после этого уже можем отправлять сообщение
    # на нужные функции ообработки в зависимости от кнопки, которую нажал пользователь
    if getState(message.chat.id) == 'home':
        match message.text:
            case 'Записаться на хобби':
                choose_hobby_handler(message)
            case 'Посмотреть мои записи на хобби':
                get_my_hobbies(message)
            case 'Отказаться от группы':
                refuse_hobby(message)
    elif getState(message.chat.id) == 'choose_hobby':
        match message.text:
            case '🎸Занятия на гитаре🎸':
                choose_group(message, 'guitar')
            case '💃Занятия танцами🕺':
                choose_group(message, 'dances')
            case 'Посмотреть все существующие группы':
                groups_info(message)
    elif getState(message.chat.id) == ('choose_guitar_group' or 'choose_dances_group'):
        match message.text:
            case 'Посмотреть все существующие группы':
                groups_info(message)
    elif getState(message.chat.id) == 'refuse_hobby':
        match message.text:
            case 'Занятия на гитаре':
                choose_group_to_refuse(message, "guitar")
            case 'Занятия танцами':
                choose_group_to_refuse(message, "dances")


# функция для выдачи информации о всех имеющихся хобби у пользователя
def get_my_hobbies(message):
    # получаем заголовки столбцов файла users.csv в виде списка
    with open("Data/users.csv", encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        hobbies = next(csv_reader)
    # срезаем первый элемент (это id пользователя), оставшиеся - всевозможные хобби
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
    # собираем итоговое сообщение пользователю
    output_message = ''
    if len(descriptions_of_groups_guitar) == 0 and len(descriptions_of_groups_dances) == 0:
        output_message = 'У вас пока что нет записей на хобби'
    else:
        output_message = 'У вас есть следующие записи на хобби:\n\n'
    if len(descriptions_of_groups_guitar) != 0:
        output_message += 'Занятия по гитаре:\n' + ''.join(descriptions_of_groups_guitar) + '\n'
    if len(descriptions_of_groups_dances) != 0:
        output_message += 'Занятия по танцам:\n' + ''.join(descriptions_of_groups_dances) + '\n'
    bot.send_message(message.chat.id, output_message, parse_mode='html')
    write_to_logs(output_message, 'bot')


# функция для выдачи информации о всех хобби в базе данных бота
def groups_info(message):
    # сначала собираем в output описания групп по гитаре
    descriptions_of_groups_guitar = []
    with open("Data/guitar_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            descriptions_of_groups_guitar.append(f'Группа №{row["Group"]} '
                                                 f'с преподавателем {row["Teacher"]},\n'
                                                 f'Занятия по {days[row["Day"]]} '
                                                 f'в {row["Time"]}, '
                                                 f'{row["Fullness"]} людей в группе\n')
    # потом собираем описания групп по танцам
    descriptions_of_groups_dances = []
    with open("Data/dances_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            descriptions_of_groups_dances.append(f'Группа №{row["Group"]} '
                                                 f'с хореографом {row["Choreographer"]},\n'
                                                 f'Занятия по {days[row["Day"]]} '
                                                 f'в {row["Time"]}, '
                                                 f'{row["Fullness"]} людей в группе\n')
    # собираем итоговое сообщение пользователю
    output_message = 'Существующие группы:\n\n'
    if len(descriptions_of_groups_guitar) != 0:
        output_message += 'Группы по гитаре:\n' + ''.join(descriptions_of_groups_guitar) + '\n'
    if len(descriptions_of_groups_dances) != 0:
        output_message += 'Группы по танцам:\n' + ''.join(descriptions_of_groups_dances) + '\n'
    bot.send_message(message.chat.id, output_message, parse_mode='html')
    write_to_logs(output_message, 'bot')


# функция, "собирающая" меню выбора хобби
def choose_hobby_handler(message):
    setState(message.chat.id, 'choose_hobby')

    choose_hobby_menu = telebot.types.ReplyKeyboardMarkup(True, False)
    choose_hobby_menu.row('/home', '/help')
    choose_hobby_menu.row('🎸Занятия на гитаре🎸')
    choose_hobby_menu.row('💃Занятия танцами🕺')
    choose_hobby_menu.row('Посмотреть все существующие группы')
    choose_hobby_menu.row('/help')

    bot.send_message(message.chat.id,
                     f'Выберите хобби\n',
                     parse_mode='html', reply_markup=choose_hobby_menu)
    write_to_logs(f'Выберите хобби\n', 'bot')


# функция, реализующая подбор возможных групп для записи
def choose_group(message, type_of_group):
    bot.send_message(message.chat.id,
                     f'Ищем для вас группы...\n',
                     parse_mode='html',
                     reply_markup=create_home_menu())
    write_to_logs(f'Ищем для вас группы...\n', 'bot')

    # type_of_group = 'guitar'/'dances'
    setState(message.chat.id, 'choose_' + type_of_group + '_group')

    # составление списка групп, в которых пользователь уже состоит
    groups_already = []
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        user_id = str(message.chat.id)

        for row in file_reader:
            if row["UserId"] == user_id:
                groups_already = row[type_of_group].split(' ')
                break

    # составление списка групп, в которые может зачислиться пользователь
    with open(f"Data/{type_of_group}_lessons.csv", encoding='utf-8') as file:
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
            if row["Group"] in groups_already:
                continue
            # собираем описание для текущей рассматриваемой группы
            description = f'Группа №{row["Group"]} '
            if type_of_group == 'guitar':
                description += f'с преподавателем {row["Teacher"]},\n'
            elif type_of_group == 'dances':
                description += f'с хореографом {row["Choreographer"]},\n'
            description += f'Занятия по {days[row["Day"]]} в {row["Time"]}, {row["Fullness"]} людей в группе\n'
            descriptions_of_groups.append(description)
            groups.append(f'Группа №{row["Group"]}')

    if len(groups) == 0:
        setState(message.chat.id, 'home')
        bot.send_message(message.chat.id,
                         f'Извините, для вас нет доступных групп.\n'
                         f'Вы состоите во всех группах, либо в оставшихся группах нет мест',
                         parse_mode='html', reply_markup=create_home_menu())
        write_to_logs(f'Извините, для вас нет доступных групп.\n'
                      f'Вы состоите во всех группах, либо в оставшихся группах нет мест',
                      'bot')
    else:
        buttons = telebot.types.InlineKeyboardMarkup()
        for group in groups:
            buttons.add(telebot.types.InlineKeyboardButton(text=group, callback_data=f'{group[8:]} {message.chat.id}'))
        bot.send_message(message.chat.id,
                         f'Выберите желаемую группу.\nВам доступны следующие группы:\n\n' +
                         '\n'.join(descriptions_of_groups),
                         parse_mode='html', reply_markup=buttons)
        write_to_logs(f'Выберите желаемую группу.\nВам доступны следующие группы:\n\n' +
                      '\n'.join(descriptions_of_groups),
                      'bot')


# функция, "собирающая" меню отказа от хобби
def refuse_hobby(message):
    setState(message.chat.id, 'refuse_hobby')

    choose_hobby_to_refuse = telebot.types.ReplyKeyboardMarkup(True, True)
    choose_hobby_to_refuse.row('/home', '/help')
    choose_hobby_to_refuse.row('Занятия на гитаре', 'Занятия танцами')

    bot.send_message(message.chat.id,
                     f'От группы какого хобби вы хотите отказаться?\n',
                     parse_mode='html', reply_markup=choose_hobby_to_refuse)
    write_to_logs(f'От группы какого хобби вы хотите отказаться?\n', 'bot')


# функция, реализующая подбор возможных групп для отказа
def choose_group_to_refuse(message, type_of_group):
    setState(message.chat.id, f'refuse_{type_of_group}_group')

    # составляем список групп, в которых пользователь уже состоит
    groups_already = []
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        user_id = str(message.chat.id)
        for row in file_reader:
            if row["UserId"] == user_id and len(row[type_of_group]) != 0:
                groups_already = row[type_of_group].split(' ')
                break

    # если у пользователя нет групп по данному виду хобби
    if len(groups_already) == 0:
        setState(message.chat.id, 'home')
        bot.send_message(message.chat.id,
                         f'У вас нет выбранных групп занятий по данному виду хобби',
                         parse_mode='html', reply_markup=create_home_menu())
        write_to_logs(f'У вас нет выбранных групп занятий по данному виду хобби', 'bot')
        return 0
    # начинаем собирать список описаний каждой группы
    with open(f"Data/{type_of_group}_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        descriptions_of_groups = []
        groups = []
        for row in file_reader:
            # если человек уже состоит в данной группе берем информацию о ней
            if row["Group"] in groups_already:
                # собираем описание для текущей рассматриваемой группы
                description = f'Группа №{row["Group"]} '
                if type_of_group == 'guitar':
                    description += f'с преподавателем {row["Teacher"]},\n'
                elif type_of_group == 'dances':
                    description += f'с хореографом {row["Choreographer"]},\n'
                description += f'Занятия по {days[row["Day"]]} в {row["Time"]}, {row["Fullness"]} людей в группе\n'
                descriptions_of_groups.append(description)
                groups.append(f'Группа №{row["Group"]}')
    buttons = telebot.types.InlineKeyboardMarkup()
    for group in groups:
        buttons.add(telebot.types.InlineKeyboardButton(text=group, callback_data=f'{group[8:]} {message.chat.id}'))
    bot.send_message(message.chat.id,
                     f'Выберите группу, от которой хотите отказаться.\nВы можете отказаться от следующих групп:\n\n' +
                     '\n'.join(descriptions_of_groups),
                     parse_mode='html', reply_markup=buttons)
    write_to_logs(f'Выберите группу, от которой хотите отказаться.\nВы можете отказаться от следующих групп:\n\n' +
                  '\n'.join(descriptions_of_groups),
                  'bot')


# функция, реализующая изменения информации о группах пользователя после его выбора (вид группы и отказ/зачисление)
def edit_a_group(number_of_group, user_id, type_of_group, mode):
    # mode - 'add'/'remove' - добавить человека в группу или удалить из нее
    # type_of_group = 'guitar'/'dances'

    # правка файла hobbies (дозапись/удаление группы у пользователя)
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["UserId"] == user_id:
                old_groups = row[type_of_group].split()
                if mode == 'add':
                    new_groups = sorted(old_groups + [number_of_group])
                elif mode == 'remove':
                    new_groups = old_groups.copy()
                    new_groups.remove(number_of_group)
                update_csv_cell("Data/users.csv",
                                type_of_group,
                                file_reader.line_num - 2,
                                ' '.join(new_groups))
                break

    # правка файла lessons (пополнение/уменьшение количества пользователей в группе)
    with open(f"Data/{type_of_group}_lessons.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["Group"] == number_of_group:
                old_fullness = row["Fullness"].split('/')
                if mode == 'add':
                    new_fullness = [str(int(old_fullness[0]) + 1), old_fullness[1]]
                elif mode == 'remove':
                    new_fullness = [str(int(old_fullness[0]) - 1), old_fullness[1]]
                update_csv_cell(f"Data/{type_of_group}_lessons.csv",
                                "Fullness",
                                file_reader.line_num - 2,
                                '/'.join(new_fullness))
                break

    # оповещение об успешном зачислении/удалении из группы и возвращение в состояние "home"
    setState(user_id, 'home')
    message = (f'Вы зачислены в группу' if mode == 'add' else f'Вы отказались от группы') + f' №{number_of_group}\n'
    bot.send_message(user_id, message, parse_mode='html', reply_markup=create_home_menu())
    write_to_logs(message, 'bot')


# обработчик кнопок под сообщениями бота (inline keyboard) - выбора групп для отказа/зачисления
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    call.data = call.data.split()
    write_to_logs(f'*Нажата кнопка "Группа №{call.data[0]}" на InlineKeyboard*', 'user')
    # в зависимости от состояния пользователя, перенаправляем его данные в функцию edit_a_group с нужными
    # параметрами: id пользователя, номер группы, вид хобби, добавление/удаление
    match getState(call.data[1]):
        case 'choose_guitar_group':
            edit_a_group(call.data[0], call.data[1], 'guitar', 'add')
        case 'refuse_guitar_group':
            edit_a_group(call.data[0], call.data[1], 'guitar', 'remove')
        case 'choose_dances_group':
            edit_a_group(call.data[0], call.data[1], 'dances', 'add')
        case 'refuse_dances_group':
            edit_a_group(call.data[0], call.data[1], 'dances', 'remove')


# главная функция, запускающая бесконечную работу бота
def main():
    bot.infinity_polling()


# запуск функции main
if __name__ == '__main__':
    main()
