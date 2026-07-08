import sqlite3
import openpyxl


conn = sqlite3.connect(
    "chatbot.db",
    check_same_thread=False
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    username TEXT,
    phone TEXT,
    name TEXT,
    age TEXT,
    city TEXT
)
""")

conn.commit()



def save_user(telegram_id, username, phone, name, age, city):

    cursor.execute("""
        INSERT OR REPLACE INTO users
        (
            telegram_id,
            username,
            phone,
            name,
            age,
            city
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        telegram_id,
        username,
        phone,
        name,
        age,
        city
    ))

    conn.commit()



def get_user(telegram_id):

    cursor.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    return cursor.fetchone()



def export_to_excel():

    cursor.execute(
        "SELECT * FROM users"
    )

    users = cursor.fetchall()


    workbook = openpyxl.Workbook()
    sheet = workbook.active

    sheet.title = "Users"


    sheet.append([
        "Telegram ID",
        "Username",
        "Phone",
        "Name",
        "Age",
        "City"
    ])


    for user in users:
        sheet.append(user)


    workbook.save(
        "users_export.xlsx"
    )