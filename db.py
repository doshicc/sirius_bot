import sqlite3
import logging

from info import DATABASE_NAME


def create_db(database_name: str = DATABASE_NAME) -> None:
    """
    Создает подключение к базе данных SQLite.

    :param database_name: Имя файла базы данных.
    :type database_name: str
    """
    with sqlite3.connect(database_name) as con:
        cur = con.cursor()


def execute_query(sql_query: str, data: tuple = None, db_path: str = DATABASE_NAME) -> None:
    """
    Выполняет SQL-запрос для изменения данных в базе данных.

    :param sql_query: SQL-запрос.
    :type sql_query: str
    :param data: Данные для подстановки в запрос (опционально).
    :type data: tuple
    :param db_path: Путь к базе данных (по умолчанию DATABASE_NAME).
    :type db_path: str
    """
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            if data:
                cursor.execute(sql_query, data)
            else:
                cursor.execute(sql_query)

            connection.commit()
            logging.info(f"Данные {data} успешно добавлены в базу данных.")

    except sqlite3.Error as e:
        logging.error(f"Ошибка при добавлении данных: {e}")


def execute_selection_query(sql_query: str, data: tuple = None, db_path: str = DATABASE_NAME) -> list:
    """
    Выполняет SQL-запрос для получения данных из базы данных.

    :param sql_query: SQL-запрос.
    :type sql_query: str
    :param data: Данные для подстановки в запрос (опционально).
    :type data: tuple
    :param db_path: Путь к базе данных (по умолчанию DATABASE_NAME).
    :type db_path: str
    :return: Список строк, полученных из базы данных.
    :rtype: list
    """
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            connection.row_factory = sqlite3.Row

            if data:
                cursor.execute(sql_query, data)
            else:
                cursor.execute(sql_query)
            rows = cursor.fetchall()
            return rows

    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении данных: {e}")
        return []


def create_table() -> None:
    """
    Создает таблицу `events` в базе данных, если она не существует.

    Таблица содержит следующие столбцы:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - user_id: INTEGER
    - name: TEXT
    - date: TEXT
    - time: TEXT
    """

    sql_query = '''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    date TEXT,
    time TEXT
)
'''
    execute_query(sql_query)
    logging.info('Таблица создана')


def insert_row(user_id: int, name: str, date: str, time: str) -> None:
    """
    Вставляет новое напоминание в таблицу `events`.

    :param user_id: Идентификатор пользователя.
    :type user_id: int
    :param name: Название напоминания.
    :type name: str
    :param date: Дата напоминания в формате "ГГГГ-ММ-ДД".
    :type date: str
    :param time: Время напоминания в формате "ЧЧ:ММ".
    :type time: str
    """
    sql_query = 'INSERT INTO events (user_id, name, date, time) VALUES (?, ?, ?, ?)'
    execute_query(sql_query, (user_id, name, date, time))
    logging.info(f"Напоминание для пользователя {user_id} успешно записано.")

