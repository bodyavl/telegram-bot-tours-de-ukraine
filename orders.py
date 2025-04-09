from config import ADMIN_IDS
from catalog import get_item_by_id

def handle_order(bot, message, user, item_id):
    item = get_item_by_id(item_id)
    if not item:
        bot.send_message(message.chat.id, "На жаль, товар не знайдено.")
        return

    user_info = f"\n👤 Користувач: {user.first_name} (@{user.username or 'немає'})\n🆔 ID: {user.id}"
    order_msg = f"🛒 НОВЕ ЗАМОВЛЕННЯ:\n{item['name']} - {item['price']}₴{user_info}"
    bot.send_message(message.chat.id, "✅ Ваше замовлення прийнято! Адміністратор зв'яжеться з вами найближчим часом.")
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, order_msg)
