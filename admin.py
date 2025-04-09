from config import ADMIN_IDS, BOT_DATA
from catalog import tours

def is_admin(user_id):
    return user_id in ADMIN_IDS

def handle_admin(bot, message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "⛔ У вас немає прав доступу.")
        return
    keyboard = (
        "/add_item Назва; Опис; Ціна\n"
        "/remove_item ID\n"
        "/orders"
    )
    bot.send_message(message.chat.id, f"🛠 Адмін-меню:\n{keyboard}")

def handle_add_item(bot, message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, name, description, price = message.text.split(";", 3)
        item = {
            "id": len(tours) + 1,
            "name": name.strip(),
            "description": description.strip(),
            "price": float(price.strip())
        }
        tours.append(item)
        bot.send_message(message.chat.id, "✅ Товар додано.")
    except:
        bot.send_message(message.chat.id, "⚠️ Формат: /add_item Назва; Опис; Ціна")

def handle_remove_item(bot, message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, id_str = message.text.split(" ", 1)
        item_id = int(id_str.strip())
        for i, item in enumerate(tours):
            if item["id"] == item_id:
                tours.pop(i)
                bot.send_message(message.chat.id, "🗑 Товар видалено.")
                return
        bot.send_message(message.chat.id, "❌ Товар не знайдено.")
    except:
        bot.send_message(message.chat.id, "⚠️ Формат: /remove_item ID")

def handle_orders(bot, message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(message.chat.id, "📦 Замовлення наразі не зберігаються в БД.")
