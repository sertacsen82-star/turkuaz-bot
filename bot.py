import os
import asyncio
import json
import anthropic
import httpx
import redis
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ENV VARS
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
ALLOWED_USER_ID = int(os.environ.get('ALLOWED_USER_ID', '0'))
REDIS_URL = os.environ.get('REDIS_URL', None)
PORT = int(os.environ.get('PORT', 8000))

# ANTHROPIC
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Sen Sertac'in kisisel asistanisin. Yara bakim uzmani, estetik cerrah ve yatirimci. Ekran adlari kullanarak konusabilirsin. Kripto fiyatlari icin /price BTCUSDT veya /top komutlari kullanabilirsin."""

# REDIS CACHE
cache = None
if REDIS_URL:
    try:
        cache = redis.from_url(REDIS_URL, decode_responses=True)
        cache.ping()
        print('Redis connected!')
    except Exception as e:
        print(f'Redis not available: {e}')

def get_cache(key):
    if cache:
        try:
            data = cache.get(key)
            if data:
                return json.loads(data)
        except:
            pass
    return None

def set_cache(key, value, ttl=10):
    if cache:
        try:
            cache.setex(key, ttl, json.dumps(value))
        except:
            pass

# BINANCE API
BINANCE_BASE = 'https://api.binance.com/api/v3'

async def fetch_price(symbol: str) -> dict:
    symbol = symbol.upper()
    cached = get_cache(f'price:{symbol}')
    if cached:
        cached['cached'] = True
        return cached
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f'{BINANCE_BASE}/ticker/24hr', params={'symbol': symbol})
        resp.raise_for_status()
        data = resp.json()
        result = {
            'symbol': symbol,
            'price': float(data['lastPrice']),
            'change_24h': float(data['priceChangePercent']),
            'high_24h': float(data['highPrice']),
            'low_24h': float(data['lowPrice']),
            'volume_24h': float(data['volume']),
            'cached': False
        }
        set_cache(f'price:{symbol}', result, ttl=10)
        return result

async def fetch_top(limit: int = 10) -> list:
    cached = get_cache(f'top:{limit}')
    if cached:
        return cached
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f'{BINANCE_BASE}/ticker/24hr')
        all_tickers = resp.json()
        usdt_pairs = sorted([t for t in all_tickers if t['symbol'].endswith('USDT')], key=lambda x: float(x['quoteVolume']), reverse=True)[:limit]
        result = [{'symbol': t['symbol'], 'price': float(t['lastPrice']), 'change_24h': float(t['priceChangePercent']), 'volume_usdt': float(t['quoteVolume'])} for t in usdt_pairs]
        set_cache(f'top:{limit}', result, ttl=60)
        return result

# FASTAPI
api = FastAPI(title='Crypto Data API')
api.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@api.get('/')
async def root():
    return {'status': 'ok', 'service': 'turkuaz-bot + crypto-api', 'version': '2.0.0'}

@api.get('/health')
async def health():
    return {'status': 'healthy', 'redis': cache is not None, 'timestamp': datetime.utcnow().isoformat()}

@api.get('/price/{symbol}')
async def get_price(symbol: str):
    try:
        return await fetch_price(symbol)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Symbol {symbol} not found')

@api.get('/top')
async def get_top_coins(limit: int = 10):
    coins = await fetch_top(limit)
    return {'coins': coins}

# TELEGRAM BOT
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        await update.message.reply_text('Yetkisiz erisim.')
        return
    user_message = update.message.text
    # /price komutu
    if user_message and user_message.lower().startswith('/price '):
        symbol = user_message.split(' ', 1)[1].strip().upper()
        try:
            data = await fetch_price(symbol)
            reply = (
                f'📊 *{data["symbol"]}*\n'
                f'💰 Fiyat: `${data["price"]:,.4f}`\n'
                f'📈 24s Degisim: `{data["change_24h"]:+.2f}%`\n'
                f'🔺 24s Yuksek: `${data["high_24h"]:,.4f}`\n'
                f'🔻 24s Dusuk: `${data["low_24h"]:,.4f}`\n'
                f'{"⚡ Cache" if data.get("cached") else "🔄 Canli"}'
            )
            await update.message.reply_text(reply, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f'Hata: {symbol} bulunamadi.')
        return
    # /top komutu
    if user_message and user_message.lower().startswith('/top'):
        try:
            limit = 5
            parts = user_message.split(' ')
            if len(parts) > 1:
                limit = int(parts[1])
            coins = await fetch_top(limit)
            lines = [f'🏆 Top {limit} Kripto (Hacme Gore)']
            for i, c in enumerate(coins, 1):
                icon = '📈' if c['change_24h'] >= 0 else '📉'
                lines.append(f'{i}. {c["symbol"]}: ${c["price"]:,.4f} {icon} {c["change_24h"]:+.2f}%')
            await update.message.reply_text('\n'.join(lines))
        except Exception as e:
            await update.message.reply_text(f'Hata: {str(e)}')
        return
    # AI asistan
    response = claude.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{'role': 'user', 'content': user_message}]
    )
    await update.message.reply_text(response.content[0].text)

# MAIN - asyncio.gather ile hem bot hem API ayni process'te
async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print('Telegram bot started!')
    try:
        await asyncio.Event().wait()
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

async def run_api():
    config = uvicorn.Config(api, host='0.0.0.0', port=PORT, log_level='info')
    server = uvicorn.Server(config)
    print(f'FastAPI started on port {PORT}!')
    await server.serve()

async def main():
    await asyncio.gather(run_bot(), run_api())

if __name__ == '__main__':
    asyncio.run(main())
