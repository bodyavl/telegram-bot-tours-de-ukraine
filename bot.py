# bot.py

import telebot
from telebot import types

from config import API_TOKEN
from catalog import get_catalog, get_item_by_id
from orders import handle_order
from admin import (
    handle_admin, handle_add_item, handle_remove_item, handle_orders
)
import messages

bot = telebot.TeleBot(API_TOKEN)

# --- Reply Keyboard ---
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
main_menu.add(
    types.KeyboardButton("📚 Каталог турів"),
    types.KeyboardButton("ℹ️ Інформація про бота"),
    types.KeyboardButton("🆘 Допомога"),
    types.KeyboardButton("✍️ Залишити відгук")
)




# --- /start ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, messages.WELCOME_TEXT, reply_markup=main_menu)

# --- /help ---
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, messages.HELP_TEXT)

# --- /info ---
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, messages.INFO_TEXT)

# --- /catalog ---
@bot.message_handler(commands=['catalog'])
def catalog(message):
    catalog = get_catalog()
    for item in catalog:
        btn = types.InlineKeyboardMarkup()
        btn.add(types.InlineKeyboardButton("🔍 Деталі", callback_data=f"detail_{item['id']}"))
        btn.add(types.InlineKeyboardButton("🛒 Замовити", callback_data=f"order_{item['id']}"))
        msg = f"📌 {item['name']}\n💸 {item['price']} грн"
        bot.send_message(message.chat.id, msg, reply_markup=btn)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.lower()
    if "каталог" in text:
        catalog(message)
    elif "інформація" in text or "про бота" in text:
        info(message)
    elif "допомога" in text:
        help_cmd(message)
    elif "відгук" in text:
        feedback(message)
    else:
        bot.send_message(message.chat.id, messages.UNKNOWN_COMMAND)

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

# --- /admin ---
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

# --- /feedback ---
@bot.message_handler(commands=['feedback'])
def feedback(message):
    bot.send_message(message.chat.id, "✍️ Напишіть свій відгук:")
    bot.register_next_step_handler(message, process_feedback)

def process_feedback(message):
    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, f"📝 Новий відгук від @{message.from_user.username}:\n{message.text}")
    bot.send_message(message.chat.id, messages.FEEDBACK_THANKS)

# --- Інші повідомлення ---
@bot.message_handler(func=lambda m: True)
def default(message):
    text = message.text.lower()
    if "товари" in text or "каталог" in text:
        catalog(message)
    elif "замовлення" in text:
        bot.send_message(message.chat.id, "📦 Щоб замовити товар, відкрийте /catalog")
    else:
        bot.send_message(message.chat.id, messages.UNKNOWN_COMMAND)

# --- Запуск ---
if __name__ == '__main__':
    bot.polling(none_stop=True)
