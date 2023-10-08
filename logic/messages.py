
def timer_message(total: int, rest: int = 0, status: bool = True):
    text = f'Идёт медитация\n\nВыбранное время: {total} минут'
    if rest:
        text += f'\n\nОставшееся время: {rest}'
    text += f'\n\nRunning' if status else f'\n\nPaused'

    return text
