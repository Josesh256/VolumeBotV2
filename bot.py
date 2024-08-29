import asyncio
import logging
import subprocess
from aiogram import Bot, Dispatcher
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.types import Message
import config
import pandas as pd

admin = int(config.info.admin.get_secret_value())
dp = Dispatcher()
bot = Bot(token=config.info.telegram_bot_api.get_secret_value())
logging.basicConfig(level=logging.INFO)

process = None

@dp.message(Command('start'))
async def work(message: Message):
    if message.from_user.id == admin:
        await message.answer('/start_bot - Inicia el bot \n'
                             '/stop_bot - Detiene el bot \n'
                             '/info - Muestra la configuración actual del bot \n'
                             '/sol_usdt - Cambia entre SOL y USDT \n'
                             '/raydium_jupiter - Cambia entre Raydium y Jupiter \n'
                             'token <dirección del token> - Cambia la dirección del token \n'
                             'sleep_min <numero> - Tiempo mínimo de pausa entre transacciones en segundos \n'
                             'sleep_max <numero> - Tiempo máximo de pausa entre transacciones en segundos \n'
                             'volume <numero> - Volumen en USDT \n'
                             'Envía un archivo txt para agregar las claves privadas de las billeteras donde se generará el volumen\n'
                             )
    else:
        await message.answer('No eres el administrador.')

@dp.message(Command('start_bot'))
async def start_futures_bot(message: Message):
    if message.from_user.id == admin:
        global process
        if process is None:
            command = [
                'python',
                'models.py',
            ]
            process = subprocess.Popen(command)
            await message.answer('Bot iniciado')
        else:
            await message.answer('El bot ya está iniciado')
    else:
        await message.answer('No eres el administrador.')

@dp.message(Command('stop_bot'))
async def stop(message: Message):
    if message.from_user.id == admin:
        global process
        if process is not None:
            process.terminate()
            process = None
            await message.answer('Bot detenido')
        else:
            await message.answer('El bot ya está detenido')
    else:
        await message.answer('No eres el administrador.')

@dp.message(Command('sol_usdt'))
async def change_currency(message: Message):
    if message.from_user.id == admin:
        df = pd.read_csv('settings.csv')
        if df['usdt'][0]:
            df['usdt'][0] = False
            df.to_csv('settings.csv', index=False)
            await message.answer('Cambiado a volumen en SOL')
        else:
            df['usdt'][0] = True
            df.to_csv('settings.csv', index=False)
            await message.answer('Cambiado a volumen en USDT')
    else:
        await message.answer('No eres el administrador.')

@dp.message(Command('raydium_jupiter'))
async def change_dex(message: Message):
    if message.from_user.id == admin:
        df = pd.read_csv('settings.csv')
        if df['raydium'][0]:
            df['raydium'][0] = False
            df.to_csv('settings.csv', index=False)
            await message.answer('Cambiado a volumen a través de Jupiter')
        else:
            df['raydium'][0] = True
            df.to_csv('settings.csv', index=False)
            await message.answer('Cambiado a volumen a través de Raydium')
    else:
        await message.answer('No eres el administrador.')

@dp.message(Command('info'))
async def show_info(message: Message):
    if message.from_user.id == admin:
        dct = pd.read_csv('settings.csv').to_dict('records')[0]
        value = 'USDT' if dct['usdt'] else 'SOL'
        dex = 'Raydium' if dct['raydium'] else 'Jupiter'

        await message.answer(f'Valor en usdt: {dct["value"]}\n'
                             f'El volumen se ejecuta a través de {dex} en {value}\n'
                             f'Tiempo mínimo de pausa entre transacciones: {dct["sleep_min"]}\n'
                             f'Tiempo máximo de pausa entre transacciones: {dct["sleep_max"]}\n')
    else:
        await message.answer('No eres el administrador.')

@dp.message()
async def handle_message(message: Message):
    if message.from_user.id == admin:
        if message.content_type == ContentType.DOCUMENT:
            file_id = message.document.file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            await bot.download_file(file_path, 'private_keys.txt')
            await message.reply('Has añadido nuevas claves privadas')

        if 'sleep_max' in message.text:
            sleep_max = message.text.split()[1]
            df = pd.read_csv('settings.csv')
            df['sleep_max'][0] = int(sleep_max)
            df.to_csv('settings.csv', index=False)
            await message.reply(f'Has cambiado el tiempo máximo de pausa entre transacciones a {sleep_max}')

        if 'token' in message.text:
            token = message.text.split()[1]
            df = pd.read_csv('settings.csv')
            df['token'][0] = str(token)
            df.to_csv('settings.csv', index=False)
            await message.reply(f'Has cambiado la dirección del token a {token}')

        if 'sleep_min' in message.text:
            sleep_min = message.text.split()[1]
            df = pd.read_csv('settings.csv')
            df['sleep_min'][0] = int(sleep_min)
            df.to_csv('settings.csv', index=False)
            await message.reply(f'Has cambiado el tiempo mínimo de pausa entre transacciones a {sleep_min}')

        if 'volume' in message.text.lower():
            volume = message.text.split()[1]
            df = pd.read_csv('settings.csv')
            df['value'][0] = int(volume)
            df.to_csv('settings.csv', index=False)
            await message.reply(f'Has cambiado el volumen de rotación a {volume} USDT')

    else:
        await message.answer('No eres el administrador.')

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
