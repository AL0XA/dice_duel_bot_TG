import logging
import configparser
import time
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pandas as pd
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


config = configparser.ConfigParser()
config.read('config.ini')
API_TOKEN = config.get(section='settings', option='API_TOKEN')
storage = MemoryStorage()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage=storage)
inline_btn_1 = InlineKeyboardButton('Игрок 1', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
inline_btn_2 = InlineKeyboardButton('Игрок 2', callback_data='button2')
inline_kb2 = InlineKeyboardMarkup().add(inline_btn_2)
inline_kb_full = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)
inline_kb_full.add(inline_btn_2)
chat_id = config.get('settings','chat_id')

async def anti_flood(*args, **kwargs): # Antiflood function
    m = args[0]
    await m.answer("Не флуди :)")

@dp.message_handler(commands=['start','duel','game','basket'])
@dp.throttled(anti_flood,rate=3)
async def send_welcome(message: types.Message):
    first_index = int(config.get('data', 'first_index'))
    second_index = int(config.get('data', 'second_index'))
    first_player_name = config.get('data', '1_player_name')
    second_player_name = config.get('data', '2_player_name')
    users = pd.read_csv('users.csv', encoding='utf-8')
    if message.text == '/duel' or message.text == '/duel@{Your_Bot_Name}':
        await message.reply("Кто будет играть?", reply_markup=inline_kb_full)
    elif message.text == '/game' or message.text == '/game@{Your_Bot_Name}':
        first_score = users['score'][first_index]
        second_score = users['score'][second_index]
        if first_player_name == '' or second_player_name == '':
            await message.reply('Игроки не зарегестрированы, используйте команду /duel')
        elif first_score <= 0 or first_score == 25:
            await message.reply(f'{first_player_name} у вас недостаточно средств ')
        elif second_score <= 0 or second_score == 25:
            await message.reply(f'{second_player_name} у вас недостаточно средств ')
        else:
            msg = await message.answer_dice(emoji="🎲")
            await message.answer(f'Бросок {first_player_name}')
            first_player_value = msg.dice.value
            time.sleep(3)
            msg = await message.answer_dice(emoji="🎲")
            await message.answer(f'Бросок {second_player_name}')
            second_player_value = msg.dice.value
            time.sleep(3)
            if first_player_value > second_player_value:
                first_score = users['score'][first_index] + 50
                second_score = users['score'][second_index] - 50
                users.at[users.index[first_index], 'score'] = first_score
                users.at[users.index[second_index], 'score'] = second_score
                users.to_csv('users.csv', header='count', index=False)
                await message.reply(f'Победил {first_player_name}! Ваш счет: {first_score}')
                first_player_name = ''
                second_player_name = ''
                config.set('data', '1_player_name', first_player_name)
                config.set('data', '2_player_name', second_player_name)
                with open('config.ini', 'w') as conf_file:
                    config.write(conf_file)
            elif second_player_value > first_player_value:
                first_score = users['score'][first_index] - 50
                second_score = users['score'][second_index] + 50
                users.at[users.index[first_index], 'score'] = first_score
                users.at[users.index[second_index], 'score'] = second_score
                users.to_csv('users.csv', header='count', index=False)
                await message.reply(f'Победил {second_player_name}! Ваш счет: {second_score}')
                first_player_name = ''
                second_player_name = ''
                config.set('data', '1_player_name', first_player_name)
                config.set('data', '2_player_name', second_player_name)
                with open('config.ini', 'w') as conf_file:
                    config.write(conf_file)
            elif second_player_value == first_player_value:
                first_score = users['score'][first_index] + 25
                second_score = users['score'][second_index] + 25
                users.at[users.index[first_index], 'score'] = first_score
                users.at[users.index[second_index], 'score'] = second_score
                users.to_csv('users.csv', header='count', index=False)
                await message.reply(f'Ничья!\n{first_player_name} ваш счет: {first_score}\n{second_player_name} ваш счет: {second_score}')
                first_player_name = ''
                second_player_name = ''
                config.set('data', '1_player_name', first_player_name)
                config.set('data', '2_player_name', second_player_name)
                with open('config.ini', 'w') as conf_file:
                    config.write(conf_file)
    elif message.text == '/basket':
        msg = await message.answer_dice(emoji="🎯")
        print(msg.dice.value)
        # if msg.dice.value == 5:
        #     user_id = message.from_user.id


@dp.callback_query_handler()
async def duel(callback_query: types.CallbackQuery):
    code = callback_query.data
    users = pd.read_csv('users.csv', encoding='utf-8')
    chek = 0
    await bot.answer_callback_query(callback_query.id)
    if code == 'button1':
        i = 0
        user_id = str(callback_query.from_user.id)
        config.set('data', '1_player_id', user_id)
        while i < len(users):
            if str(users['id'][i]) == user_id:
                first_player = users['name'][i]
                first_index = str(i)
                i = len(users)
                print(first_player)
                config.set('data', '1_player_name', first_player)
                config.set('data', 'first_index', first_index)
                with open('config.ini', 'w') as conf_file:
                    config.write(conf_file)
            else:
                i += 1
    elif code == 'button2':
        user_id = str(callback_query.from_user.id)
        config.set('data', '2_player_id', user_id)
        i = 0
        while i < len(users):
            if str(users['id'][i]) == user_id:
                second_player = users['name'][i]
                second_index = str(i)
                i = len(users)
                print(second_player)
                config.set('data', '2_player_name', second_player)
                config.set('data', 'second_index', second_index)
                with open('config.ini', 'w') as conf_file:
                    config.write(conf_file)
            else:
                i += 1
    first_player_name = config.get('data', '1_player_name')
    second_player_name = config.get('data', '2_player_name')
    if first_player_name == second_player_name:
        await bot.send_message(callback_query.message.chat.id,f'Хуй тебе пидрила ебаная, нельзя играть с самим собой')
        first_player_name = ''
        second_player_name = ''
        config.set('data', '1_player_name', first_player_name)
        config.set('data', '2_player_name', second_player_name)
        with open('config.ini', 'w') as conf_file:
            config.write(conf_file)
    elif second_player_name == '':
        await bot.send_message(callback_query.message.chat.id,'Жду игрока №2!')
    elif first_player_name == '':
        await bot.send_message(callback_query.message.chat.id, 'Жду игрока №1!')
    else:
        chek = 1
    if chek == 1:
        await bot.send_message(callback_query.message.chat.id, f'Игроки зарегестрированы: {first_player_name} VS {second_player_name}')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
