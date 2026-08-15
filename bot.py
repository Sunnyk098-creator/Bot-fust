import os
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message


BOT_TOKEN = os.getenv("BOT_TOKEN")

# Your demo login page
LOGIN_URL = "https://ultra-pay.in/login"

# Set this to YOUR actual backend login API.
LOGIN_API = os.getenv("LOGIN_API")


class LoginForm(StatesGroup):
    phone = State()
    password = State()
    pin = State()


bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "💳 Ultra Pay Demo\n\n"
        "📱 Send your 10-digit Ultra Pay number:"
    )

    await state.set_state(LoginForm.phone)


@dp.message(LoginForm.phone)
async def phone_handler(message: Message, state: FSMContext):

    phone = message.text.strip()

    if not phone.isdigit() or len(phone) != 10:
        await message.answer(
            "❌ Invalid number.\n\n"
            "Please send your 10-digit Ultra Pay number:"
        )
        return

    await state.update_data(phone=phone)

    await message.answer("🔐 Enter your password:")
    await state.set_state(LoginForm.password)


@dp.message(LoginForm.password)
async def password_handler(message: Message, state: FSMContext):

    password = message.text.strip()

    if not password:
        await message.answer("❌ Password cannot be empty.")
        return

    await state.update_data(password=password)

    # Delete password message
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer("🔢 Enter your 4-digit PIN:")
    await state.set_state(LoginForm.pin)


@dp.message(LoginForm.pin)
async def pin_handler(message: Message, state: FSMContext):

    pin = message.text.strip()

    if not pin.isdigit() or len(pin) != 4:
        await message.answer(
            "❌ PIN must contain exactly 4 digits."
        )
        return

    data = await state.get_data()

    # Delete PIN message
    try:
        await message.delete()
    except Exception:
        pass

    if not LOGIN_API:
        await message.answer(
            "⚠️ Demo API is not configured.\n\n"
            f"Login page:\n{LOGIN_URL}"
        )
        await state.clear()
        return

    await message.answer("⏳ Checking your Ultra Pay Demo account...")

    payload = {
        "phone": data["phone"],
        "password": data["password"],
        "pin": pin
    }

    try:

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.post(
                LOGIN_API,
                json=payload
            ) as response:

                if response.status != 200:
                    await message.answer(
                        "❌ Login failed.\n"
                        f"HTTP Status: {response.status}"
                    )
                    await state.clear()
                    return

                result = await response.json()

        if result.get("success") is True:

            balance = result.get("balance", 0)

            await message.answer(
                "✅ Login Successful!\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "💳 ULTRA PAY\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"💰 Balance: ₹{balance}\n\n"
                "🔐 Demo account verified."
            )

        else:

            await message.answer(
                "❌ Invalid Ultra Pay Demo credentials."
            )

    except aiohttp.ClientError:
        await message.answer(
            "⚠️ Could not connect to the Demo API."
        )

    except Exception as e:
        print("ERROR:", e)

        await message.answer(
            "⚠️ Something went wrong."
        )

    await state.clear()


async def main():

    print("🚀 Ultra Pay Demo Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
