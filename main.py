from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token="8164921689:AAGk7wgP3ZZ_mGFOcn_s_fH8GDtwIovaXrY")
dp = Dispatcher()
ADMIN_ID = 6531953933

# Список петов с уникальными ценами
pets = {
    "pet_A": {"name": "🦊 Лиса", "price": "744T"},
    "pet_B": {"name": "🧟‍♀️ Чикен зомби", "price": "744T"},
    "pet_C": {"name": "🐝 Королева", "price": "744T"},
    "pet_D": {"name": "🦟️ Стрекоза", "price": "1.5Q"},
    "pet_E": {"name": "🦋 Бабочка", "price": "1.5Q"},
    "pet_F": {"name": "🐙 Осьминог", "price": "1.5Q"},
    "pet_G": {"name": "🦝 Енот", "price": "2.2Q"},
    "pet_H": {"name": "🦖 T-rex", "price": "3Q"}
}


# Состояния FSM
class Form(StatesGroup):
    waiting_for_review = State()


# Стартовое сообщение
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        'Здравствуйте, я бот по скупке петов!\n\n'
        'Перед началом сделки хотел бы уточнить:\n'
        '1. Скупаются только те петы, что есть в прайсе.\n'
        '2. В сделке вы идёте первыми — на гарантов время не трачу.\n\n'
        'Все правила сделаны ради быстрых сделок.\n\n'
        'Если вы согласны с нашими правилами — нажмите кнопку ниже.'
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я соглашаюсь", callback_data="agree")]
    ])
    await message.answer(text, reply_markup=markup)


# Меню питомцев
@dp.callback_query(F.data == "agree")
async def agree_handler(callback: types.CallbackQuery):
    await callback.answer()

    buttons = []
    for code, pet in pets.items():
        label = f"{pet['name']} — {pet['price']}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=code)])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        'Спасибо! Вы приняли правила. Можем продолжать 😊\n'
        'Выберите питомца, которого хотите продать:',
        reply_markup=markup
    )


# Обработка выбора пета
@dp.callback_query(F.data.in_(pets.keys()))
async def pet_handler(callback: types.CallbackQuery):
    await callback.answer()
    pet = pets[callback.data]

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="подтвердить заказ!", callback_data="accept")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_list")]
    ])

    await callback.message.edit_text(
        f"Я сообщу о вашем выборе Скупщику @Slaizers, и через 5-10 минут, он зайдёт\n"
        f"Вы выбрали {pet['name']}. Вы получите {pet['price']} шекелей.\n"
        f'Чтобы продать питомца, добавьте в друзья по нику: *Slaizers_KaneKi*\n'
        f'Или перейдите по ссылке: https://www.roblox.com/share?code=342c3f402c85fb4fbbee31eb5c4e0672&type=Server',
        reply_markup=markup,
        parse_mode="Markdown"
    )

    # Сообщение админу
    user = callback.from_user
    try:
        await bot.send_message(
            ADMIN_ID,
            f"👤 @{user.username or user.first_name} выбрал: {pet['name']} — {pet['price']}\n"
            f"ID пользователя: {user.id}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки админу: {e}")


# Кнопка "подтвердить"
@dp.callback_query(F.data == "accept")
async def accept_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        'Спасибо за сделку, напишите пожалуйста отзыв.\n'
        'например: @Slaizers, всё безопастно и быстро'
    )
    await state.set_state(Form.waiting_for_review)


# Обработка отзыва
@dp.message(Form.waiting_for_review)
async def process_review(message: types.Message, state: FSMContext):
    user = message.from_user
    try:
        # Пересылаем отзыв админу
        await bot.send_message(
            ADMIN_ID,
            f"📝 Новый отзыв от @{user.username or user.first_name} (ID: {user.id}):\n"
            f"{message.text}"
        )
        await message.answer('Спасибо за ваш отзыв! Мы ценим ваше мнение.')
    except Exception as e:
        logger.error(f"Ошибка при обработке отзыва: {e}")
        await message.answer('Произошла ошибка при отправке отзыва. Пожалуйста, попробуйте позже.')
    finally:
        await state.clear()


# Кнопка "Назад"
@dp.callback_query(F.data == "back_to_list")
async def back_handler(callback: types.CallbackQuery):
    await callback.answer()

    buttons = []
    for code, pet in pets.items():
        label = f"{pet['name']} — {pet['price']}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=code)])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        'Выберите питомца, которого хотите продать:',
        reply_markup=markup
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())