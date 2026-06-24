import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
CREDENTIALS_FILE = "credentials.json"

QUESTIONS = [
    "Введите <b>Аккаунт</b>:",
    "Введите <b>Имя</b>:",
    "Введите <b>Категорию</b>:",
    "Введите <b>Артикул</b>:",
    "Введите <b>Штук</b>:",
    "Введите <b>Самовыкуп/раздача</b>:",
    "Введите <b>Цену за шт/тг</b>:",
    "Введите <b>Общую сумму</b>:",
]

HEADERS = [
    "Аккаунт", "Имя", "Категория", "Артикул",
    "Штук", "Самовыкуп/раздача", "Цена за шт/тг", "Общая сумма",
]
