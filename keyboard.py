from telebot.types import ReplyKeyboardMarkup


def create_keyboard(buttons_list: list) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопками.

    :param buttons_list: Список кнопок для клавиатуры.
    :type buttons_list: list
    :return: Клавиатура с кнопками.
    :rtype: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

