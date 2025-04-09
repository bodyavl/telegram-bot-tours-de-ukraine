import os
import logging
from flask import Flask, request
import telebot
from telebot import types

from config import API_TOKEN
from catalog import get_catalog, get_item_by_id
from orders import handle_order
from admin import (
    handle_admin,
    handle_add_item,
    handle_remove_item,
    handle_orders
)
import messages

# --- Логування ---
logging.basicConfig(level=logging.DEBUG)

# --- Ініціалізація ---
bot = telebot.TeleBot(API_TOKEN, threaded=False)
app = Flask(__name__)

# --- Клавіатура ---
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
main_menu.add(
    types.KeyboardButton("📚 Каталог турів"),
    types.KeyboardButton("ℹ️ Інформація про бота"),
    types.KeyboardButton("🆘 Допомога"),
    types.KeyboardButton("✍️ Залишити відгук")
)

# --- Команди ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, messages.WELCOME_TEXT, parse_mode="Markdown", reply_markup=main_menu)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, messages.HELP_TEXT, parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, messages.INFO_TEXT, parse_mode="Markdown")

@bot.message_handler(commands=['catalog'])
def catalog(message):
    catalog = get_catalog()
    for item in catalog:
        btn = types.InlineKeyboardMarkup(row_width=2)
        btn.add(
            types.InlineKeyboardButton("🔍 Деталі", callback_data=f"detail_{item['id']}"),
            types.InlineKeyboardButton("🛒 Замовити", callback_data=f"order_{item['id']}")
        )
        msg = f"📌 {item['name']}\n💸 {item['price']} грн"
        bot.send_message(message.chat.id, msg, reply_markup=btn)

@bot.message_handler(commands=['order'])
def order_info(message):
    bot.send_message(message.chat.id, "📦 Щоб оформити замовлення, відкрийте /catalog і натисніть кнопку 'Замовити'.")

# --- Inline кнопки ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("detail_"):
        item_id = int(call.data.split("_")[1])
        item = get_item_by_id(item_id)
        if item:
            text = f"📌 {item['name']}\n📝 {item['description']}\n💰 {item['price']} грн"
            bot.send_message(call.message.chat.id, text)
    elif call.data.startswith("order_"):
        item_id = int(call.data.split("_")[1])
        handle_order(bot, call.message, call.from_user, item_id)
    elif call.data == "catalog":
        catalog(call.message)

# --- Адміністративні команди ---
@bot.message_handler(commands=['admin'])
def admin(message):
    handle_admin(bot, message)

@bot.message_handler(commands=['add_item'])
def add_item(message):
    handle_add_item(bot, message)

@bot.message_handler(commands=['remove_item'])
def remove_item(message):
    handle_remove_item(bot, message)

@bot.message_handler(commands=['orders'])
def orders(message):
    handle_orders(bot, message)

# --- Відгуки ---
@bot.message_handler(commands=['feedback'])
def feedback(message):
    bot.send_message(message.chat.id, "✍️ Напишіть свій відгук:")
    bot.register_next_step_handler(message, process_feedback)

def process_feedback(message):
    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, f"📝 Новий відгук від @{message.from_user.username or 'невідомо'}:\n{message.text}")
    bot.send_message(message.chat.id, messages.FEEDBACK_THANKS)

# --- Відповіді на довільні повідомлення ---
@bot.message_handler(func=lambda message: True)
def default(message):
    text = message.text.lower()
    if "каталог" in text or "товари" in text:
        catalog(message)
    elif "замовлення" in text:
        order_info(message)
    elif "привіт" in text or "доброго дня" in text:
        bot.send_message(message.chat.id, "👋 Вітаю! Чим можу допомогти?")
    elif "як зробити замовлення" in text:
        bot.send_message(message.chat.id, "🔽 Просто відкрий /catalog і натисни '🛒 Замовити' під потрібним туром.")
    else:
        bot.send_message(message.chat.id, messages.UNKNOWN_COMMAND)

# --- Обробка запитів Telegram (Webhook) ---
@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    logging.debug(f"📨 UPDATE: {json_str}")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

# --- Ping маршрут ---
@app.route("/", methods=["GET"])
def index():
    return "Tours de Ukraine bot is running!", 200

# --- Встановлення Webhook ---
if __name__ == "__main__":
    bot.remove_webhook()
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{API_TOKEN}"
    print("🔗 Setting webhook:", webhook_url)
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
