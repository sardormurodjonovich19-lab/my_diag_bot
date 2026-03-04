import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ВАШ ТОКЕН
TOKEN = "8786806379:AAEeRWMSJX3o6DmiMzDl8OnfH3QdqxNPpw0"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Все 20 вопросов
QUESTIONS = [
    "1. У вас есть чувство тошноты?",
    "2. Была ли у вас рвота более двух раз?",
    "3. Беспокоит ли вас диарея (жидкий стул)?",
    "4. Чувствуете ли вы спазмы или резкую боль в животе?",
    "5. Повысилась ли температура выше 37.5°C?",
    "6. Чувствуете ли вы сильную слабость или озноб?",
    "7. Есть ли сильное вздутие живота?",
    "8. Симптомы появились через 2–6 часов после еды?",
    "9. Есть ли такие же симптомы у тех, кто ел с вами?",
    "10. Ели ли вы продукты с истекшим сроком?",
    "11. Употребляли ли вы лесные грибы?",
    "12. Ели ли вы плохо прожаренное мясо или рыбу?",
    "13. Пили ли вы сырое молоко или ели творог?",
    "14. Ели ли вы салаты с майонезом или кремовые торты?",
    "15. Ели ли вы немытые овощи или фрукты?",
    "16. Пили ли вы воду из-под крана или водоема?",
    "17. Есть ли в рвоте или стуле примеси крови?",
    "18. Есть ли двоение в глазах или 'туман'?",
    "19. Есть ли сильная сухость во рту и трудно ли глотать?",
    "20. Уменьшилось ли количество мочеиспусканий?"
]

user_states = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_states[message.chat.id] = {"step": 0, "yes_count": 0, "critical": False}
    await message.answer("🏥 Добро пожаловать! Я помогу оценить ваше состояние.\nОтвечайте на вопросы кнопками 'Да' или 'Нет'.")
    await ask_question(message)

async def ask_question(message: types.Message):
    uid = message.chat.id
    step = user_states[uid]["step"]
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="yes")
    builder.button(text="❌ Нет", callback_data="no")
    
    await message.answer(QUESTIONS[step], reply_markup=builder.as_markup())

@dp.callback_query()
async def handle_answer(callback: types.CallbackQuery):
    uid = callback.message.chat.id
    if uid not in user_states: return

    # Проверка на критические вопросы (грибы, консервы, глаза, кровь - это вопросы 11, 17, 18, 19)
    step = user_states[uid]["step"]
    if callback.data == "yes":
        user_states[uid]["yes_count"] += 1
        if step in [10, 16, 17, 18]: # Индексы критических вопросов
            user_states[uid]["critical"] = True

    user_states[uid]["step"] += 1
    
    if user_states[uid]["step"] < len(QUESTIONS):
        await callback.message.edit_text(QUESTIONS[user_states[uid]["step"]])
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Да", callback_data="yes")
        builder.button(text="❌ Нет", callback_data="no")
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    else:
        await show_result(callback.message, uid)
    await callback.answer()

async def show_result(message: types.Message, uid: int):
    data = user_states[uid]
    res = "🏁 **ИТОГ ПРОВЕРКИ:**\n\n"
    
    if data["critical"]:
        res += "🆘 **ОПАСНОСТЬ!** У вас есть признаки тяжелого отравления. **СРОЧНО ВЫЗОВИТЕ СКОРУЮ ПОМОЩЬ (103/112)!**"
    elif data["yes_count"] > 5:
        res += "⚠️ Вероятное пищевое отравление. Рекомендуется пить много воды, принять сорбенты и проконсультироваться с врачом."
    else:
        res += "✅ Ваше состояние не выглядит критическим. Наблюдайте за самочувствием."
    
    res += "\n\n*Данный бот не является врачом и носит справочный характер.*"
    await message.answer(res, parse_mode="Markdown")
    del user_states[uid]

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
