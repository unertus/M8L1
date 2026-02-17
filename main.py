
import telebot
from telebot import types
from config import BOT_TOKEN
from dictss import dict_1, quest, answears, get_answer_by_id, get_all_questions_list, find_answer_in_dict_1
from database import init_db, save_request

bot = telebot.TeleBot('7489040132:AAH6Li1JhY-Qb-bn0dSV5QFA-GOhGDfmWmw')
user_state = {}  # Хранилище состояний: {chat_id: "tech"|"sales"|None}



def main_menu():
    """Главное меню"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("❓ Частые вопросы", callback_data="faq"),
        types.InlineKeyboardButton("🛠 Сайт/Оплата (программисты)", callback_data="tech"),
        types.InlineKeyboardButton("📦 Товар (отдел продаж)", callback_data="sales")
    )
    return markup

def back_btn():
    """Кнопка назад"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 В меню", callback_data="menu"))
    return markup

def faq_buttons():
    """Кнопки с вопросами из ваших словарей"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for qid, qtext in get_all_questions_list():
        markup.add(types.InlineKeyboardButton(f"{qid}) {qtext}", callback_data=f"faq_{qid}"))
    markup.add(types.InlineKeyboardButton("🔙 В меню", callback_data="menu"))
    return markup



@bot.message_handler(commands=['start'])
def start(message):
    """Команда /start"""
    text = (f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Я бот поддержки 'Продаем все на свете'.\n"
            "Выберите раздел:")
    bot.send_message(message.chat.id, text, reply_markup=main_menu())
    user_state[message.chat.id] = None

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    """Обработка кнопок"""
    cid = call.message.chat.id
    mid = call.message.message_id
    
    
    if call.data == "menu":
        bot.edit_message_text("Выберите раздел:", cid, mid, reply_markup=main_menu())
    
    
    elif call.data == "faq":
        bot.edit_message_text("📚 <b>Выберите вопрос:</b>", cid, mid, 
                             parse_mode="HTML", reply_markup=faq_buttons())
    
    
    elif call.data.startswith("faq_"):
        try:
            qid = int(call.data.replace("faq_", ""))
            answer = get_answer_by_id(qid)
            question = quest.get(qid, "Вопрос")
            if answer:
                text = f"🔹 <b>{qid}) {question}</b>\n\n{answer}"
                bot.edit_message_text(text, cid, mid, parse_mode="HTML", reply_markup=back_btn())
            else:
                bot.answer_callback_query(call.id, "❌ Ответ не найден")
        except:
            bot.answer_callback_query(call.id, "Ошибка")
    
    # Техподдержка (программисты)
    elif call.data == "tech":
        bot.edit_message_text(
            "🛠 <b>Проблема с сайтом или оплатой?</b>\n\n"
            "Напишите, что случилось — программисты получат ваше сообщение:",
            cid, mid, parse_mode="HTML", reply_markup=back_btn()
        )
        user_state[cid] = "tech"
    
    # Отдел продаж
    elif call.data == "sales":
        bot.edit_message_text(
            "📦 <b>Проблема с товаром?</b>\n\n"
            "Опишите ситуацию — отдел продаж свяжется с вами:",
            cid, mid, parse_mode="HTML", reply_markup=back_btn()
        )
        user_state[cid] = "sales"

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) in ["tech", "sales"])
def handle_request(message):
    """Обработка заявки"""
    cid = message.chat.id
    state = user_state[cid]
    
   
    if message.text and "назад" in message.text.lower():
        user_state[cid] = None
        start(message)
        return
    
    dept = "🛠 Программисты" if state == "tech" else "📦 Отдел продаж"
    
    user_text = None
    
    # Текст или голосовое
    if message.voice:
        user_text = "🎤 Голосовое сообщение"
    elif message.text:
        user_text = message.text
    else:
        # Если что-то другое (фото, стикер, документ и т.д.)
        bot.send_message(
            cid, 
            "❌ Пожалуйста, отправьте текст или голосовое сообщение.\n"
            "Фото, стикеры и документы не принимаются.",
            reply_markup=back_btn()
        )
        return 
    
    # Сохраняем в БД
    save_request(
        user_id = message.from_user.id,
        username = message.from_user.username,
        message = user_text,
        department= dept
    )
    
  
    
    # Ответ пользователю
    bot.send_message(
        cid,
        f"✅ <b>Заявка принята!</b>\n{dept} скоро свяжется с вами.",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
    user_state[cid] = None

@bot.message_handler(func=lambda msg: user_state.get(msg.chat.id) is None and msg.text)
def auto_faq(message):
    """Автопоиск ответа в dict_1"""
    question, answer = find_answer_in_dict_1(message.text)
    if answer:
        bot.send_message(
            message.chat.id,
            f"🔹 <b>{question}</b>\n\n{answer}\n\nНе помогло? Выберите раздел ниже.",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
        return
  


if __name__ == "__main__":
    init_db()
    print("🚀 Бот запущен!")
    bot.infinity_polling()