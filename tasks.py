levels = {
    1: {
        "title": "Введение в Kali Linux",
        "task": "Установи Kali Linux. Изучи интерфейс. Выполни команду: `uname -a`.",
        "exam": "Что показывает команда `uname -a`?"
    },
    2: {
        "title": "Работа с терминалом",
        "task": "Изучи команды: `ls`, `cd`, `mkdir`, `touch`. Создай структуру папок для проекта.",
        "exam": "Как создать папку и файл в Kali через терминал?"
    }
    # Добавим больше по мере развития
}

def get_level_task(level):
    return levels.get(level, {"title": "???", "task": "Нет задания", "exam": "Нет экзамена"})
