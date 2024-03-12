import csv


def update_csv_cell(path, col, row_num, new_value):
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

    # записываем в старый файл новые данные
    with open(path, "w", newline='\n') as file:
        data = csv.DictWriter(file, delimiter=',', fieldnames=headers)
        data.writerow(dict((heads, heads) for heads in headers))
        data.writerows(new_rows)


def getState(user_id):
    user_id = str(user_id)
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["UserId"] == user_id:
                return row["state"]


def setState(user_id, new_state):
    user_id = str(user_id)
    with open("Data/users.csv", encoding='utf-8') as file:
        file_reader = csv.DictReader(file, delimiter=",")
        for row in file_reader:
            if row["UserId"] == user_id:
                update_csv_cell("Data/users.csv", "state", file_reader.line_num - 2, new_state)
                break
