from flask import Flask, request
import telegram
import telegram.ext
import json
import datetime
import re

# Requirements
USERNAME = "PythonAnywhere_Username"
SECRET = "long_auto-generated_key_to_avoid_external_interference"
AUTH_KEY = "Telegram_Bot_Auth_Key_(TOKEN)"
url = "https://" + USERNAME + ".pythonanywhere.com/" + SECRET
CLIENTS_PATH = "absolute_path_to_(clients.txt)_file"

# Upcoming Birthdays Function
birthdays = ""


def upcoming_birthdays(request_type):
    global birthdays
    _RE_COMBINE_WHITESPACE = re.compile(r"\s+")
    birthdays = _RE_COMBINE_WHITESPACE.sub(" ", birthdays)
    birthdays_dict = json.loads(birthdays)
    today = f"{datetime.datetime.now().day}/{datetime.datetime.now().month}"

    if request_type == "today":
        if (today in birthdays_dict):
            return f"*{birthdays_dict[today]}*'s birthday is on _{today}_ 😊"

    elif request_type == "tomorrow":
        tomorrow_date = datetime.datetime.now() + datetime.timedelta(days=1)
        tomorrow = f"{tomorrow_date.day}/{tomorrow_date.month}"
        if (tomorrow in birthdays_dict):
            return f"*{birthdays_dict[tomorrow]}*'s birthday is on _{tomorrow}_ 😊"

    elif request_type == "upcoming":
        upcoming_date = datetime.datetime.now() + datetime.timedelta(days=1)
        while True:
            tested_day = f"{upcoming_date.day}/{upcoming_date.month}"
            if (tested_day in birthdays_dict):
                return f"Closest Upcoming Birthday :\n\n*{birthdays_dict[tested_day]}*'s birthday is on _{tested_day}_ 🤩"
            else:
                upcoming_date += datetime.timedelta(days=1)

    elif request_type == "thismonth":
        thismonth_birthdays = "This Month's Upcoming Birthdays (Total _totalhere_):"
        total = 0
        for i in range(1, 32):
            tested_day = f"{i}/{datetime.datetime.now().month}"
            if (tested_day in birthdays_dict):
                thismonth_birthdays += f"\n\n*{birthdays_dict[tested_day]}*'s birthday is on _{tested_day}_ 🤩"
                total += 1
        thismonth_birthdays = thismonth_birthdays.replace("totalhere", str(total))
        return thismonth_birthdays

# Handlers


def upcoming(update, context):
    chat_id = update.message.chat.id
    pinned_msg = bot.get_chat(chat_id=chat_id).pinned_message
    global birthdays
    birthdays = str(pinned_msg.text.replace("\n", ""))
    update.message.reply_text(upcoming_birthdays("upcoming"), parse_mode=telegram.ParseMode.MARKDOWN)


def thismonth(update, context):
    chat_id = update.message.chat.id
    pinned_msg = bot.get_chat(chat_id=chat_id).pinned_message
    global birthdays
    birthdays = str(pinned_msg.text.replace("\n", ""))
    update.message.reply_text(upcoming_birthdays("thismonth"), parse_mode=telegram.ParseMode.MARKDOWN)


def today(update, context):
    chat_id = update.message.chat.id
    pinned_msg = bot.get_chat(chat_id=chat_id).pinned_message
    global birthdays
    birthdays = str(pinned_msg.text.replace("\n", ""))
    today_birthday = upcoming_birthdays("today")
    if today_birthday != None:
        update.message.reply_text(today_birthday, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        update.message.reply_text("Just take care of yourself for today 🥰", parse_mode=telegram.ParseMode.MARKDOWN)


def tomorrow(update, context):
    chat_id = update.message.chat.id
    pinned_msg = bot.get_chat(chat_id=chat_id).pinned_message
    global birthdays
    birthdays = str(pinned_msg.text.replace("\n", ""))
    tomorrow_birthday = upcoming_birthdays("tomorrow")
    if tomorrow_birthday != None:
        update.message.reply_text(tomorrow_birthday, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        update.message.reply_text("You don't trust me then 🙄.\n_No birthdays for tomorrow._", parse_mode=telegram.ParseMode.MARKDOWN)


def birthday(update, context):
    start_message = update.message.reply_text("{\n\"1/" + str(datetime.datetime.now().month) + "\": \"Name1\",\n\"20/" + str(datetime.datetime.now().month) + "\": \"Name2\"\n}", parse_mode=telegram.ParseMode.MARKDOWN)
    start_message.chat.unpin_all_messages()
    update.message.reply_text("_Fill your own list on the same pattern and *PIN* it.\nPlease try not to add too much extra *spaces* or *indentations* to avoid breaking the list!!_", parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=start_message.message_id)
    update.message.reply_text("*Send me your list of memorable birthdays, and I promise I won't forget a single one* 😊", parse_mode=telegram.ParseMode.MARKDOWN)
    with open(CLIENTS_PATH, "r") as clients:
        clients_id = clients.readlines()
        for i in range(len(clients_id)):
            clients_id[i] = clients_id[i][:-1]
        if (str(update.message.chat.id) not in clients_id):
            add_new_client_id(update.message.chat.id)


def add_new_client_id(new_id):
    with open(CLIENTS_PATH, "a") as clients:
        clients.write(str(new_id) + "\n")


def set_birthdays(update, context):
    msg = update.message
    msg.chat.unpin_all_messages()
    new_msg = update.message.reply_text(msg.text)
    new_msg.pin()


# Flask API & Webhook
# Dispatcher
bot = telegram.Bot(AUTH_KEY)
dp = telegram.ext.Dispatcher(bot, None, workers=0, use_context=True)

# Add Handlers
dp.add_handler(telegram.ext.CommandHandler("start", birthday))
dp.add_handler(telegram.ext.CommandHandler("upcoming", upcoming))
dp.add_handler(telegram.ext.CommandHandler("thismonth", thismonth))
dp.add_handler(telegram.ext.CommandHandler("today", today))
dp.add_handler(telegram.ext.CommandHandler("tomorrow", tomorrow))
dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, set_birthdays))

# Start Webhook
bot.delete_webhook()
bot.set_webhook(url=url)

# Process Updates
app = Flask(__name__)


@app.route("/" + SECRET, methods=["POST"])
def telegram_webhook():
    json_string = request.stream.read().decode("utf-8")
    update = telegram.Update.de_json(json.loads(json_string), bot)
    dp.process_update(update)
    return "OK", 200


@app.route("/" + SECRET + "/daily-reminder", methods=["POST"])
def daily_reminder():
    with open(CLIENTS_PATH, "r") as clients:
        clients_id = clients.readlines()
        for i in range(len(clients_id)):
            clients_id[i] = clients_id[i][:-1]
            chat_id = clients_id[i]
            pinned_msg = bot.get_chat(chat_id=chat_id).pinned_message
            global birthdays
            birthdays = str(pinned_msg.text.replace("\n", ""))
            tomorrow_birthdays = upcoming_birthdays("tomorrow")
            if (tomorrow_birthdays != "" and tomorrow_birthdays != None):
                bot.send_message(chat_id=chat_id, text="I told you I won't forget 😎")
                bot.send_message(chat_id=chat_id, text=upcoming_birthdays("tomorrow"), parse_mode=telegram.ParseMode.MARKDOWN)
    return "Reminded: {}/{}/{}".format(datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year), 200
