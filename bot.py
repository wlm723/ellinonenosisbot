from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN, ADMINS
from database import save_user, export_to_excel


users = {}



# -------------------------
# START
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    users[user_id] = {
        "step": "name",
        "phone": None,
        "username": update.effective_user.username
    }


    await update.message.reply_photo(
        photo=open("logo.png", "rb"),
        caption=(
            "Καλώς ήρθατε στην Ελληνων Ένωσις (Ε.ΕΝ)! 👋\n\n"
            "Για να συνεχίσετε, παρακαλώ απαντήστε στις παρακάτω ερωτήσεις.\n\n"
            "Ποιο είναι το όνομά σας;"
        )
    )



# -------------------------
# QUESTIONS
# -------------------------

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text


    if user_id not in users:

        await update.message.reply_text(
            "Καλώς ήρθατε! Παρακαλώ πληκτρολογήστε /start πρώτα."
        )

        return



    step = users[user_id]["step"]



    if step == "name":

        users[user_id]["name"] = text
        users[user_id]["step"] = "age"


        await update.message.reply_text(
            "Πόσων ετών είστε;"
        )



    elif step == "age":

        users[user_id]["age"] = text
        users[user_id]["step"] = "city"


        await update.message.reply_text(
            "Σε ποια πόλη/περιοχή ζείτε;"
        )



    elif step == "city":

        users[user_id]["city"] = text
        users[user_id]["step"] = "phone"



        button = KeyboardButton(
            "📱 Αποστολή αριθμού τηλεφώνου",
            request_contact=True
        )


        keyboard = ReplyKeyboardMarkup(
            [
                [button],
                ["Παράλειψη"]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )


        await update.message.reply_text(
            "Θα θέλατε να μοιραστείτε τον αριθμό τηλεφώνου σας ώστε "
            "να μπορέσουμε να επικοινωνήσουμε μαζί σας;",
            reply_markup=keyboard
        )



    elif step == "phone":


        if text == "Παράλειψη":

            await finish_user(
                update.message,
                context,
                None
            )



        elif text.replace("+", "").isdigit():

            phone = text.replace(" ", "")


            if len(phone) == 10 and phone.startswith("69"):
                phone = "+30" + phone



            await finish_user(
                update.message,
                context,
                phone
            )



        else:

            await update.message.reply_text(
                "Παρακαλώ πατήστε το κουμπί για αποστολή αριθμού "
                "ή πληκτρολογήστε έναν έγκυρο αριθμό τηλεφώνου."
            )



# -------------------------
# RECEIVE CONTACT
# -------------------------

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id


    if user_id not in users:
        return


    phone = update.message.contact.phone_number


    await finish_user(
        update.message,
        context,
        phone
    )



# -------------------------
# SAVE USER
# -------------------------

async def finish_user(message, context, phone):

    user_id = message.chat.id


    users[user_id]["phone"] = phone



    save_user(
        telegram_id=user_id,
        username=users[user_id]["username"],
        phone=phone,
        name=users[user_id]["name"],
        age=users[user_id]["age"],
        city=users[user_id]["city"]
    )



    username = users[user_id]["username"]


    if username:
        username = "@" + username
    else:
        username = "Δεν υπάρχει"



    summary = (
        "📋 Νέα Υποβολή Χρήστη\n\n"
        f"Username: {username}\n"
        f"Τηλέφωνο: {phone or 'Δεν δόθηκε'}\n"
        f"Όνομα: {users[user_id]['name']}\n"
        f"Ηλικία: {users[user_id]['age']}\n"
        f"Πόλη: {users[user_id]['city']}\n"
        f"Telegram ID: {user_id}"
    )



    for admin in ADMINS:

        await context.bot.send_message(
            chat_id=admin,
            text=summary
        )



    await message.reply_text(
        "✅ Ευχαριστούμε! Οι πληροφορίες σας έχουν αποθηκευτεί.\n"
        "Ένας από τους διαχειριστές θα επικοινωνήσει μαζί σας σύντομα.",
        reply_markup=ReplyKeyboardRemove()
    )


    del users[user_id]



# -------------------------
# ADMIN EXPORT
# -------------------------

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMINS:
        return


    export_to_excel()


    await update.message.reply_document(
        document=open(
            "users_export.xlsx",
            "rb"
        )
    )



# -------------------------
# ADMIN MESSAGE
# -------------------------

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMINS:
        return



    if len(context.args) < 2:

        await update.message.reply_text(
            "Χρήση:\n/message USER_ID μήνυμα"
        )

        return



    user_id = int(context.args[0])

    text = " ".join(context.args[1:])



    await context.bot.send_message(
        chat_id=user_id,
        text=text
    )


    await update.message.reply_text(
        "✅ Το μήνυμα στάλθηκε."
    )



# -------------------------
# RUN
# -------------------------

def main():

    app = Application.builder().token(TOKEN).build()



    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    app.add_handler(
        CommandHandler(
            "export",
            export
        )
    )


    app.add_handler(
        CommandHandler(
            "message",
            send_message
        )
    )


    app.add_handler(
        MessageHandler(
            filters.CONTACT,
            contact
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message
        )
    )



    print("🤖 Το bot λειτουργεί...")


    app.run_polling()



if __name__ == "__main__":
    main()