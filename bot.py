import os
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from binance.client import Client

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "0"))
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY")

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Sen Sertac'in kisisel asistanisin. Yara bakim uzmani, estetik cerrah ve yatirimci. Turkce konus, kisa ve oz yanitlar ver."""

def get_binance_summary():
    try:
        binance = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY, tld='com')
        futures = binance.futures_account()
        positions = [p for p in futures['positions'] if float(p['positionAmt']) != 0]
        summary = "Binance Futures:\n"
        for p in positions:
            summary += f"{p['symbol']}: {float(p['unrealizedProfit']):.2f} USDT\n"
        return summary
    except Exception as e:
        return f"Binance verisi alinamadi: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        await update.message.reply_text("Yetkisiz erisim.")
        return
    user_message = update.message.text
    if "pozisyon" in user_message.lower() or "binance" in user_message.lower():
        await update.message.reply_text(get_binance_summary())
        return
    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )
    await update.message.reply_text(response.content[0].text)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot baslatildi...")
    app.run_polling()

if __name__ == "__main__":
    main()
