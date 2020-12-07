import functools
import os

from flask import Flask, request
import telebot

from app.numbers_written_form import number_written_form, parse_number_written_form


APP_URL = "https://write-number-bot.herokuapp.com/"
API_TOKEN = os.environ.get("API_TOKEN")
ADMINS = [781613729]
UNSUPPORTED_CONTENT_TYPES = """animation audio contact dice document game invoice location passport_data
                               photo poll sticker successful_payment venue video video_note voice""".split()

app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN)


def reset_webhook(url):
    """ Tell telegram, that the bot lives on `url` now.
    """
    assert url.startswith("https://")
    info = bot.get_webhook_info()
    if info.last_error_message:
        print(f"last webhook error: {info.last_error_date} {info.last_error_message}")
    webhook_url = info.url[:info.url.rindex("/") + 1] if info.url else None
    if webhook_url != url:
        print(f"resetting the webhook to {url[8:]}{API_TOKEN[:3]}...")
        bot.remove_webhook()
        bot.set_webhook(url=url + API_TOKEN)
    else:
        print(f"webhook is already set.")


@app.route("/" + API_TOKEN, methods=["POST"])
def process_new_updates():
    """ This handler is used by Telegram, to send new messages to the bot.
    """
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf8"))])
    return "success"


@app.route("/", methods=["GET"])
def handle_root():
    reset_webhook(APP_URL)
    return "200, OK!"


def user_name(user):
    """ Pick a best name for the user. Both username and last_name of a telegram user can be None.
    """
    if user.username:
        return f"@{user.username}"
    elif user.last_name:
        return f"{user.first_name} {user.last_name}"
    else:
        return user.first_name


def notify_admin(text, user=None):
    if user:
        text = f"{user.id} {user_name(user)} {text}"
    print(text)
    if not user or user.id != ADMINS[0]:
        bot.send_message(chat_id=ADMINS[0], text=text)


def send_message(chat_id, text, **kwargs):
    """ Wrapper around bot.send_message(), that catches Exceptions, and notifies admin about them,
        for example, if user deleted their account, or blocked the bot from sending messages to them.
    """
    try:
        msg = bot.send_message(chat_id=chat_id, text=text, **kwargs)
        print(f"SENT MESSAGE {chat_id} {msg.message_id}: {text!r}")  # log outgoing bot message
        # heroku log lines are limited by 10k bytes, and tg messages - by 4096 characters; most messages will fit.
        return msg
    except Exception as e:
        notify_admin(f"Failed to send message {text!r} to user {chat_id}! Got {type(e).__name__}:\n{e}")
        raise e


def generic_handler_wrapper(handler):
    @functools.wraps(handler)
    def wrapper(msg):
        user = msg.from_user
        try:
            return handler(msg, user)
        except Exception as e:
            notify_admin(f"Error occurred while serving {user_name(user)} in {handler.__name__}: {e}\n" +
                         f"After user have sent: {msg.text or msg.content_type!r}")
            send_message(user.id, "Something went wrong :(")
            raise  # full stacktrace will be printed in stderr, which can be viewed in heroku logs
    return wrapper


@bot.message_handler(commands=["start"])
@generic_handler_wrapper
def handle_start(msg, user):
    notify_admin(f"started the chat: {msg.text!r}", user=user)
    send_message(user.id, "Hi! Send me a number, and I will write it, in plain english.")


@bot.message_handler(content_types=["text"])
@generic_handler_wrapper
def handle_text(msg, user):
    notify_admin(f"wrote: {msg.text!r}", user=user)
    s = msg.text.strip()
    if s.isdigit():
        x = int(s)
        try:
            response = number_written_form(x)
        except Exception as ex:
            response = f"I'm sorry, number {x} is not supported yet :("
    else:
        try:
            response = parse_number_written_form(s)
        except Exception as ex:
            response = str(ex)
    send_message(user.id, response)


@bot.message_handler(func=lambda msg: True, content_types=UNSUPPORTED_CONTENT_TYPES)
@generic_handler_wrapper
def handle_strange_content_types(msg, user):
    notify_admin(f"sent content-type {msg.content_type!r}", user=user)
    send_message(user.id, f"I'm sorry, content type {msg.content_type} is not supported :(")
    bot.forward_message(ADMINS[0], user.id, msg.message_id)
