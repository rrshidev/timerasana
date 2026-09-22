# -*- coding: utf-8 -*-
"""Централизованная локализация таймер-бота TimerAsana (ru/en).

Все строки UI сосредоточены здесь. t(lang, key, **kw) возвращает перевод;
`ru` — исходный (и полный) набор строк, `en` — перевод.
Язык пользователя хранится в единой БД Dharana (app_users.timer_language).
"""

LANGUAGES = ('ru', 'en')


def normalize_lang(lang) -> str:
    """Приводит значение к 'ru'|'en' (все не-'en' считаются 'ru')."""
    if lang and str(lang).lower().startswith('en'):
        return 'en'
    return 'ru'


def lang_from_telegram(language_code) -> str:
    """Язык по умолчанию из Telegram language_code (например 'en'/'en-US')."""
    if not language_code:
        return 'ru'
    code = str(language_code).lower()
    if code.startswith('en'):
        return 'en'
    return 'ru'


def t(lang, key: str, **kwargs) -> str:
    """Перевод строки. Неизвестные ключи -> 'ru' -> сам ключ."""
    lang = normalize_lang(lang)
    text = TRANSLATIONS.get(lang, {}).get(key)
    if text is None:
        text = TRANSLATIONS['ru'].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


RU = {
    # ===== Главное меню бота (команды) =====
    'welcome_greeting_name': 'Намаскар, {name}! 🙏',
    'welcome_greeting': 'Намаскар! 🙏',
    'welcome_body': (
        'Добро пожаловать в **TimerAsana** — таймер для йогических практик '
        'проекта **Dharana** 🧘\n\n'
        'Что я умею:\n'
        '• 🧘 **Медитация** — от 1 до 60 минут\n'
        '• 🧘‍♂️ **Асана** — практика с циклами работы и отдыха\n'
        '• 🌬️ **Пранаяма** — дыхательные упражнения с настройкой\n\n'
        'Полезные ссылки:\n'
        '• Основной бот Dharana — [@yogaasana_bot](https://t.me/yogaasana_bot)\n'
        '• Веб-приложение — [dharana.ru](https://dharana.ru)\n\n'
        'Выбери действие ниже 👇'
    ),
    'help_text': (
        '**TimerAsana** — таймер для йогических практик проекта Dharana.\n\n'
        '🕐 **ТАЙМЕР** 🕐\n\n'
        '🧘 **Медитация** — выбери время от 1 до 60 минут (пресеты или ручной ввод)\n'
        '🧘‍♂️ **Асана** — настраиваемые циклы работы и отдыха (30с-3м работа, 10с-1м отдых, 3-20 циклов)\n'
        '🌬️ **Пранаяма** — дыхательные упражнения (1-8 упражнений, 10с-2м каждое, 5с-1м отдых)\n\n'
        'Управление во время практики: пауза, продолжить, стоп, сброс.\n\n'
        'Команды:\n'
        '----> /start 🚀 - Главное меню\n'
        '----> /help ❓ - Справка\n'
        '----> /about_us 🙏 - О проекте и авторах'
    ),
    'about_text': (
        '🙏 **TimerAsana — часть проекта Dharana**\n\n'
        'TimerAsana — это таймер для йогических практик: медитации, асан и пранаямы. '
        'Он создан как часть экосистемы **Dharana** — проекта, который помогает '
        'делать йогу регулярной и доступной каждому.\n\n'
        '**Dharana** включает:\n'
        '• Основной бот [@yogaasana_bot](https://t.me/yogaasana_bot) — каталог из 100+ асан, '
        'готовые комплексы, генератор практики, асана дня\n'
        '• Веб-приложение [dharana.ru](https://dharana.ru)\n'
        '• TimerAsana — этот таймер для практик\n\n'
        'Два человека. Йога. Немного кода. И желание, чтобы ваша практика '
        'была регулярной и приносила радость.\n\n'
        'Связаться с нами:\n'
        '@RrshiDev · @yogaolleg\n'
        'instagram.com/yogaolleg/\n\n'
        'Хорошей практики! 🙏'
    ),

    # ===== Кнопки (главное меню) =====
    'kb_timer': '⏱️ Таймер',
    'kb_about': '🙏 О нас',
    'kb_language': '🌐 Язык',
    'kb_back': '🔙 Назад',
    'kb_start': '▶️ Начать',

    # ===== Выбор языка =====
    'lang_choose': '🌐 **Язык / Language**\n\nВыбери язык интерфейса:',
    'kb_lang_ru': '🇷🇺 Русский',
    'kb_lang_en': '🇬🇧 English',
    'lang_set_ru': '✅ Язык переключён на русский.',
    'lang_set_en': '✅ Language switched to English.',

    # ===== Главное меню таймера =====
    'timer_main_text': (
        '🕐 **Таймер для практики**\n\n'
        'Выбери тип практики:\n'
        '🧘 Медитация — простая практика осознанности\n'
        '🧘‍♂️ Асана — практика поз с чередованием работы/отдыха\n'
        '🌬️ Пранаяма — дыхательные упражнения'
    ),
    'kb_meditation': '🧘 Медитация',
    'kb_asana': '🧘‍♂️ Асана',
    'kb_pranayama': '🌬️ Пранаяма',
    'kb_exit_timer': '🔙 Выйти из таймера',

    # ===== Единицы времени =====
    'dur_s': '{n}с',
    'dur_m': '{n}м',
    'sec_word': '{n} секунд',
    'min_word': '{n} минут',

    # ===== Медитация =====
    'med_menu_text': '🧘 **Медитация**\n\nВыбери длительность практики:',
    'med_min_1': '1 минута',
    'med_min_5': '5 минут',
    'med_min_10': '10 минут',
    'med_min_15': '15 минут',
    'med_min_20': '20 минут',
    'med_min_30': '30 минут',
    'med_min_45': '45 минут',
    'med_min_60': '60 минут',
    'med_custom': '⌨️ Ввести время вручную',
    'med_started': (
        '🧘 Медитация на {minutes} минут начата!\n\n'
        'Сконцентрируйся на дыхании и будь настоящем моменте. 🙏\n\n'
        'Используй кнопки управления ниже:'
    ),
    'med_custom_prompt': (
        '⌨️ **Ввод времени медитации**\n\n'
        'Напиши количество минут (от 1 до 120):\n'
        'Например: 7 или 15 или 45\n\n'
        'Используй обычное сообщение, а не кнопку.'
    ),
    'med_not_digit': 'Используй кнопки меню или команду /start. Для таймера нажми «⏱️ Таймер» 😉',
    'med_range_error': '⚠️ Время должно быть от 1 до 120 минут. Попробуй еще раз.',
    'med_notification': (
        '🔔 **Медитация началась!**\n\n'
        'Длительность: {minutes} минут\n'
        'Сосредоточься на дыхании... 🧘'
    ),
    'med_done': (
        '🧘 **Медитация завершена!**\n\n'
        'Отличная практика! Надеюсь, ты чувствуешь себя спокойно и гармонично. 🙏\n\n'
        'Хочешь начать новую медитацию?'
    ),
    'med_running': (
        '{emoji} **Медитация**\n\n'
        'Осталось времени: {time}\n'
        '{bar}\n\n'
        'Прогресс: {progress}'
    ),

    # ===== Асана =====
    'asana_menu_text': (
        '🧘‍♂️ **Таймер асан**\n\n'
        '⏱️ Работа: {work}\n'
        '⏸️ Отдых: {rest}\n'
        '🔄 Циклы: {cycles}\n\n'
        'Настрой параметры или начни практику:'
    ),
    'asana_choose_work': '⏱️ **Выбери время работы:**',
    'asana_choose_rest': '⏸️ **Выбери время отдыха:**',
    'asana_choose_cycles': '🔄 **Выбери количество циклов:**',
    'asana_started': (
        '🧘‍♂️ **Практика асан начата!**\n\n'
        '⏱️ Работа: {work}\n'
        '⏸️ Отдых: {rest}\n'
        '🔄 Циклы: {cycles}\n\n'
        'Начинаем с первого подхода! 💪'
    ),
    'kb_work_time': '⏱️ Время работы',
    'kb_rest_time': '⏸️ Время отдыха',
    'kb_cycles': '🔄 Количество циклов',
    'cycles_n': '{n} циклов',

    # ===== Пранаяма =====
    'pranayama_menu_text': (
        '🌬️ **Пранаяма**\n\n'
        '📊 Упражнений: {exercises}\n'
        '⏱️ Время упражнения: {exercise_time}\n'
        '⏸️ Время отдыха: {rest_time}\n\n'
        'Настрой параметры или начни практику:'
    ),
    'pranayama_choose_exercises': '📊 **Выбери количество упражнений:**',
    'pranayama_choose_ex_time': '⏱️ **Выбери время упражнения:**',
    'pranayama_choose_rest': '⏸️ **Выбери время отдыха:**',
    'pranayama_started': (
        '🌬️ **Практика пранаямы начата!**\n\n'
        '📊 Упражнений: {exercises}\n'
        '⏱️ Время упражнения: {exercise_time}\n'
        '⏸️ Время отдыха: {rest_time}\n\n'
        'Начинаем с первого упражнения! 🧘‍♂️'
    ),
    'kb_exercises': '📊 Количество упражнений',
    'kb_ex_time': '⏱️ Время упражнения',
    'ex_1': '1 упражнение',
    'ex_2': '2 упражнения',
    'ex_3': '3 упражнения',
    'ex_4': '4 упражнения',
    'ex_5': '5 упражнений',
    'ex_6': '6 упражнений',
    'ex_7': '7 упражнений',
    'ex_8': '8 упражнений',

    # ===== Управление таймером =====
    'kb_pause': '⏸️ Пауза',
    'kb_stop': '⏹️ Стоп',
    'kb_reset': '🔄 Сброс',
    'kb_resume': '▶️ Продолжить',
    'kb_delete': '🗑️ Удалить',
    'timer_stopped': (
        '⏹️ **Таймер остановлен**\n\n'
        'Практика завершена. Хорошая работа! 🙏\n\n'
        'Хочешь начать новую практику?'
    ),
    'timer_deleted': '🗑️ Таймер удален\n\nХочешь начать новую практику?',
    'timer_back': '🔙 **Возвращаю в главное меню таймера...**',
    'timer_exit': '🔙 **Выход из таймера...**\n\nВыбери действие ниже 👇',
    'practice_completed': '🎉 **Практика завершена!**\n\nОтличная работа! 🙏',

    # ===== Сообщения состояния таймера =====
    'asana_name': '🧘 **Асана**',
    'pranayama_name': '🌬️ **Пранаяма**',
    'practice_done': '{name} **— практика завершена!**\n\n'
                     'Отличная работа! Все циклы выполнены. 💪\n\n'
                     'Ты молодец! Хочешь начать новую практику?',
    'phase_work': 'Работа',
    'phase_rest': 'Отдых',
    'state_line': (
        '{emoji} **{name}**\n\n'
        'Фаза: {phase}\n'
        'Осталось: {time}\n'
        '{bar}\n\n'
        'Цикл: {cycle}/{cycles}\n'
        'Общее время: {total}'
    ),
    'phase_notif_rest': (
        '🔔 **Время работы завершено!**\n\n'
        'Отдыхай! Восстанови дыхание и подготовься к следующему подходу. 🛏️\n\n'
        'Отдых: {rest} секунд'
    ),
    'phase_notif_work': (
        '🔔 **Отдых завершен!**\n\n'
        'Приготовься! Начинаем следующий подход. 💪\n\n'
        'Работа: {work} секунд'
    ),
}

EN = {
    # ===== Main menu (commands) =====
    'welcome_greeting_name': 'Namaskar, {name}! 🙏',
    'welcome_greeting': 'Namaskar! 🙏',
    'welcome_body': (
        'Welcome to **TimerAsana** — a timer for yoga practices '
        'from the **Dharana** project 🧘\n\n'
        'What I can do:\n'
        '• 🧘 **Meditation** — from 1 to 60 minutes\n'
        '• 🧘‍♂️ **Asana** — practice with work/rest cycles\n'
        '• 🌬️ **Pranayama** — breathing exercises with custom settings\n\n'
        'Useful links:\n'
        '• Main Dharana bot — [@yogaasana_bot](https://t.me/yogaasana_bot)\n'
        '• Web app — [dharana.ru](https://dharana.ru)\n\n'
        'Choose an action below 👇'
    ),
    'help_text': (
        '**TimerAsana** — a timer for yoga practices from the Dharana project.\n\n'
        '🕐 **TIMER** 🕐\n\n'
        '🧘 **Meditation** — pick a time from 1 to 60 minutes (presets or manual input)\n'
        '🧘‍♂️ **Asana** — configurable work/rest cycles (30s-3m work, 10s-1m rest, 3-20 cycles)\n'
        '🌬️ **Pranayama** — breathing exercises (1-8 exercises, 10s-2m each, 5s-1m rest)\n\n'
        'Controls during practice: pause, resume, stop, reset.\n\n'
        'Commands:\n'
        '----> /start 🚀 - Main menu\n'
        '----> /help ❓ - Help\n'
        '----> /about_us 🙏 - About the project and authors'
    ),
    'about_text': (
        '🙏 **TimerAsana is part of the Dharana project**\n\n'
        'TimerAsana is a timer for yoga practices: meditation, asanas and pranayama. '
        'It is part of the **Dharana** ecosystem — a project that helps '
        'make yoga regular and accessible to everyone.\n\n'
        '**Dharana** includes:\n'
        '• Main bot [@yogaasana_bot](https://t.me/yogaasana_bot) — a catalog of 100+ asanas, '
        'ready-made sequences, a practice generator, asana of the day\n'
        '• Web app [dharana.ru](https://dharana.ru)\n'
        '• TimerAsana — this practice timer\n\n'
        'Two people. Yoga. A bit of code. And a wish for your practice '
        'to be regular and joyful.\n\n'
        'Reach us:\n'
        '@RrshiDev · @yogaolleg\n'
        'instagram.com/yogaolleg/\n\n'
        'Happy practice! 🙏'
    ),

    # ===== Buttons (main menu) =====
    'kb_timer': '⏱️ Timer',
    'kb_about': '🙏 About us',
    'kb_language': '🌐 Language',
    'kb_back': '🔙 Back',
    'kb_start': '▶️ Start',

    # ===== Language picker =====
    'lang_choose': '🌐 **Language / Язык**\n\nChoose the interface language:',
    'kb_lang_ru': '🇷🇺 Русский',
    'kb_lang_en': '🇬🇧 English',
    'lang_set_ru': '✅ Язык переключён на русский.',
    'lang_set_en': '✅ Language switched to English.',

    # ===== Timer main menu =====
    'timer_main_text': (
        '🕐 **Practice timer**\n\n'
        'Choose a practice type:\n'
        '🧘 Meditation — a simple mindfulness practice\n'
        '🧘‍♂️ Asana — pose practice alternating work/rest\n'
        '🌬️ Pranayama — breathing exercises'
    ),
    'kb_meditation': '🧘 Meditation',
    'kb_asana': '🧘‍♂️ Asana',
    'kb_pranayama': '🌬️ Pranayama',
    'kb_exit_timer': '🔙 Exit timer',

    # ===== Time units =====
    'dur_s': '{n}s',
    'dur_m': '{n}m',
    'sec_word': '{n} seconds',
    'min_word': '{n} minutes',

    # ===== Meditation =====
    'med_menu_text': '🧘 **Meditation**\n\nChoose your practice duration:',
    'med_min_1': '1 minute',
    'med_min_5': '5 minutes',
    'med_min_10': '10 minutes',
    'med_min_15': '15 minutes',
    'med_min_20': '20 minutes',
    'med_min_30': '30 minutes',
    'med_min_45': '45 minutes',
    'med_min_60': '60 minutes',
    'med_custom': '⌨️ Enter time manually',
    'med_started': (
        '🧘 {minutes}-minute meditation started!\n\n'
        'Focus on your breath and stay in the present moment. 🙏\n\n'
        'Use the control buttons below:'
    ),
    'med_custom_prompt': (
        '⌨️ **Manual meditation time**\n\n'
        'Type the number of minutes (1 to 120):\n'
        'For example: 7 or 15 or 45\n\n'
        'Send it as a regular message, not a button.'
    ),
    'med_not_digit': 'Use the menu buttons or the /start command. For the timer press "⏱️ Timer" 😉',
    'med_range_error': '⚠️ Time must be between 1 and 120 minutes. Please try again.',
    'med_notification': (
        '🔔 **Meditation started!**\n\n'
        'Duration: {minutes} minutes\n'
        'Focus on your breath... 🧘'
    ),
    'med_done': (
        '🧘 **Meditation complete!**\n\n'
        'Great practice! I hope you feel calm and balanced. 🙏\n\n'
        'Want to start a new meditation?'
    ),
    'med_running': (
        '{emoji} **Meditation**\n\n'
        'Time left: {time}\n'
        '{bar}\n\n'
        'Progress: {progress}'
    ),

    # ===== Asana =====
    'asana_menu_text': (
        '🧘‍♂️ **Asana timer**\n\n'
        '⏱️ Work: {work}\n'
        '⏸️ Rest: {rest}\n'
        '🔄 Cycles: {cycles}\n\n'
        'Adjust the settings or start the practice:'
    ),
    'asana_choose_work': '⏱️ **Choose work duration:**',
    'asana_choose_rest': '⏸️ **Choose rest duration:**',
    'asana_choose_cycles': '🔄 **Choose the number of cycles:**',
    'asana_started': (
        '🧘‍♂️ **Asana practice started!**\n\n'
        '⏱️ Work: {work}\n'
        '⏸️ Rest: {rest}\n'
        '🔄 Cycles: {cycles}\n\n'
        'Starting with the first set! 💪'
    ),
    'kb_work_time': '⏱️ Work time',
    'kb_rest_time': '⏸️ Rest time',
    'kb_cycles': '🔄 Number of cycles',
    'cycles_n': '{n} cycles',

    # ===== Pranayama =====
    'pranayama_menu_text': (
        '🌬️ **Pranayama**\n\n'
        '📊 Exercises: {exercises}\n'
        '⏱️ Exercise time: {exercise_time}\n'
        '⏸️ Rest time: {rest_time}\n\n'
        'Adjust the settings or start the practice:'
    ),
    'pranayama_choose_exercises': '📊 **Choose the number of exercises:**',
    'pranayama_choose_ex_time': '⏱️ **Choose exercise duration:**',
    'pranayama_choose_rest': '⏸️ **Choose rest duration:**',
    'pranayama_started': (
        '🌬️ **Pranayama practice started!**\n\n'
        '📊 Exercises: {exercises}\n'
        '⏱️ Exercise time: {exercise_time}\n'
        '⏸️ Rest time: {rest_time}\n\n'
        'Starting with the first exercise! 🧘‍♂️'
    ),
    'kb_exercises': '📊 Number of exercises',
    'kb_ex_time': '⏱️ Exercise time',
    'ex_1': '1 exercise',
    'ex_2': '2 exercises',
    'ex_3': '3 exercises',
    'ex_4': '4 exercises',
    'ex_5': '5 exercises',
    'ex_6': '6 exercises',
    'ex_7': '7 exercises',
    'ex_8': '8 exercises',

    # ===== Timer controls =====
    'kb_pause': '⏸️ Pause',
    'kb_stop': '⏹️ Stop',
    'kb_reset': '🔄 Reset',
    'kb_resume': '▶️ Resume',
    'kb_delete': '🗑️ Delete',
    'timer_stopped': (
        '⏹️ **Timer stopped**\n\n'
        'Practice finished. Well done! 🙏\n\n'
        'Want to start a new practice?'
    ),
    'timer_deleted': '🗑️ Timer deleted\n\nWant to start a new practice?',
    'timer_back': '🔙 **Back to the timer main menu...**',
    'timer_exit': '🔙 **Exiting the timer...**\n\nChoose an action below 👇',
    'practice_completed': '🎉 **Practice complete!**\n\nGreat work! 🙏',

    # ===== Timer state messages =====
    'asana_name': '🧘 **Asana**',
    'pranayama_name': '🌬️ **Pranayama**',
    'practice_done': '{name} **— practice complete!**\n\n'
                     'Great job! All cycles finished. 💪\n\n'
                     'Well done! Want to start a new practice?',
    'phase_work': 'Work',
    'phase_rest': 'Rest',
    'state_line': (
        '{emoji} **{name}**\n\n'
        'Phase: {phase}\n'
        'Left: {time}\n'
        '{bar}\n\n'
        'Cycle: {cycle}/{cycles}\n'
        'Total time: {total}'
    ),
    'phase_notif_rest': (
        '🔔 **Work phase finished!**\n\n'
        'Rest! Catch your breath and prepare for the next set. 🛏️\n\n'
        'Rest: {rest} seconds'
    ),
    'phase_notif_work': (
        '🔔 **Rest finished!**\n\n'
        'Get ready! Starting the next set. 💪\n\n'
        'Work: {work} seconds'
    ),
}

TRANSLATIONS = {
    'ru': RU,
    'en': EN,
}