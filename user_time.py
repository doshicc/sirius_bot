import threading
from datetime import datetime, timedelta
import logging

from db import execute_selection_query, execute_query
from info import INCORRECT_DATE_1, INCORRECT_DATE_2, INCORRECT_DATE_3


def check_time(user_date: str) -> str | bool:
    """
    Проверяет корректность введённой даты и времени.

    :param user_date: Дата и время в формате "ГГГГ-ММ-ДД ЧЧ:ММ".
    :type user_date: str
    :return: True, если дата и время корректны, иначе строка с ошибкой.
    :rtype: str | bool
    """
    try:
        time = datetime.strptime(user_date, "%Y-%m-%d %H:%M")
        current_time = datetime.now()
        if time < current_time or time == current_time:
            return INCORRECT_DATE_1
        elif (time - current_time).total_seconds() < 3600:
            return INCORRECT_DATE_3
        else:
            return True
    except:
        return INCORRECT_DATE_2


def check_schedule(user_id: int, user_date: str) -> list:
    """
    Возвращает список напоминаний для заданной даты и пользователя.

    :param user_id: Идентификатор пользователя.
    :type user_id: int
    :param user_date: Дата в формате "ГГГГ-ММ-ДД".
    :type user_date: str
    :return: Список напоминаний в формате [(name, date, time)].
    :rtype: list
    """
    sql_query = ("SELECT name, date, time "
                 "FROM events "
                 "WHERE user_id = ? AND date = ? "
                 "ORDER BY time")
    res = execute_selection_query(sql_query, (user_id, user_date))
    return res


def delete_old_reminders():
    """
    Удаляет напоминания, дата и время которых уже прошли.
    """
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
    sql_query = "DELETE FROM events WHERE date || ' ' || time < ?"
    execute_query(sql_query, (current_datetime,))
    logging.info("Удалены старые напоминания.")


def run_periodically():
    """
    Запускает автоматическое удаление старых записей.
    """
    delete_old_reminders()
    threading.Timer(600, run_periodically).start()


def reduce_by_hour(user_time: str) -> str:
    """
    Уменьшает время на один час.

    :param user_time: Время в формате "ЧЧ:ММ".
    :type user_time: str
    :return: Время, уменьшенное на один час, в формате "ЧЧ:ММ".
    :rtype: str
    """
    dt = datetime.strptime(user_time, "%H:%M")
    new_dt = dt - timedelta(hours=1)
    return new_dt.strftime("%H:%M")

