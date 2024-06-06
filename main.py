from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup

import sqlite3
import random
import json

data = json.load(open('cfg.json'))
token = data['token']
my_address = data['ton_address']
loger_id = data['log_channel']
support = data['support']

profil_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('👛 Изменить адрес', callback_data='change_address')).add(InlineKeyboardButton('🛒 История покупок', callback_data='history')).add(InlineKeyboardButton('⁉️ Тех. Поддержка', callback_data='help'))

start_kb=ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton('📁 Каталог'), KeyboardButton('👤 Профиль'))
start_kb.add(KeyboardButton('⁉️ Помощь'))

class States(StatesGroup):
    change_address=State()
    change_address1=State()

db = sqlite3.connect("database.sqlite", check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY,
    address TEXT
)""")
db.commit()

bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

async def start_payment(id, nick):
    await bot.send_message(loger_id, f'Пользователь <b>{nick}</b> создал заявку на оплату', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(nick, url=f'tg://openmessage?user_id={id}')))

def get_addrees(id):
    sql.execute(f"SELECT address FROM users WHERE id = {id}")
    row = sql.fetchone()
    try:
        if row[0]==None:
            return '❌ Не указан!'
    except:
        pass
    if row==None:
        return '❌ Не указан!'
    else:
        return row[0]

def change_address(id, address):
    sql.execute(f'UPDATE users SET address = "{address}" WHERE id = {id}')
    db.commit()

def dell_user(id):
    sql.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()

def creat_user(id):
    sql.execute(f"SELECT * FROM users WHERE id = {id}")
    raw = sql.fetchone()
    if raw is None:
        sql.execute(f"INSERT or IGNORE INTO users VALUES (?, ?)", (id, None))
        db.commit()

def get_all_id():
    sql.execute("Select id from users")
    return sql.fetchall()

@dp.message_handler(commands=['start'])
async def start_bot(msg: types.Message):
    creat_user(msg.from_user.id)
    await bot.send_message(msg.from_user.id, f'''
👋 Привет, <b>{(msg.from_user.first_name).replace('<', '').replace('>', '').replace('/', '')}</b>
📞 Добро пожаловать в первого телеграм бота по продаже <b>анонимных Telegram номеров</b> от <b>fragment</b>
⁉️ Как вы знаете, цены на такие номера <b>растут</b>, а вскоре их <b>продажи прекратятся на всегда!</b>
💎 У нас же вы всегда сможете покупать анонимные <b>+888</b> номера по фиксированной цене <b>10TON</b>
''', reply_markup=start_kb)

@dp.message_handler()
async def message(msg):
    id = msg.from_user.id
    if msg.text=='👤 Профиль':
        await bot.send_message(msg.from_user.id, f'''
👨‍💼 Вот ваш профиль:
 👤 Ник: <code>{(msg.from_user.first_name).replace('<', '').replace('>', '').replace('/', '')}</code>
 🔢 ID: <code>{id}</code>
 👛 Ваш TON адрес: <code>{get_addrees(id)}</code>
 📊  Совершенно <b>0</b> покупок на сумму ≈<b>0TON</b>
 🔨 Предупреждения от администрации: <code>0</code>
 💎 Статус: <code>Новичек</code>
''', reply_markup=profil_kb)
    elif msg.text=='⁉️ Помощь':
        await bot.send_message(id, f'''
💎 Данный бот создан для простой покупки <b>анонимных +888 Telegram номеров</b> от <b>fragment</b>
💸 Оплата осуществляется <b>прямым переводом на TON кошелёк</b>
🖼️ После оплаты на ваш <b>TON адрес</b> будет отправлена <b>NFT</b> с передачей прав. Она будет видна на сайте <code>https://fragment.com/numbers</code> и вы сможете принимать на нее код или выставить на аукцион
⁉️ По всем вопросам обращаться к нашему администратору: @{support}
''', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('💎 Статусы', callback_data='status')))
    elif msg.text=='📁 Каталог':
        await bot.send_message(id, '💎 Выберите товар для покупки:', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('📞 Случайный +888 номер | 100шт', callback_data='random_number')).add(InlineKeyboardButton('⬅️ Вернуться', callback_data='back_main')))
@dp.callback_query_handler(lambda call: True)
async def handler_call(call: types.CallbackQuery):
    id = call.message.chat.id
    if call.data=='status':
        await bot.send_message(id, '''
💎 Вот все наши статусы:
👤 Новичек: <b>0 покупок</b>
📞 Покупатель: <b>1 покупка</b>
👨‍💼 Частный покупатель: <b>3-5 покупок</b>
🎁  Местный: <b>10+ покупок</b>
''')
    elif call.data=='help':
        await bot.send_message(id, f'⁉️ По всем вопросам обращаться к нашему администратору: @{support}')
    elif call.data=='random_number':
        await call.message.edit_text('''
🎁 Вы выбрали товар: <code>📞 Случайный +888 номер</code>
📊 Количество товара: <code>999 шт</code>
💎 Нажмите кнопку <code>🎁 Купить</code> чтобы перейти к покупке 
''', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('🎁 Купить', callback_data='buy_random_number')).add(InlineKeyboardButton('❌ Отменить платеж', callback_data='stop')))
    elif call.data=='buy_random_number':
        await call.message.edit_text('''
📞 Ваш номер: <b>+888<tg-spoiler>********</tg-spoiler></b>
💳 Нажмите кнопку <code>💸 Оплатить</code> для покупки
''', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('💸 Оплатить', callback_data='confirm_buy_random_number')).add(InlineKeyboardButton('❌ Отменить платеж', callback_data='stop')))
    elif call.data=='confirm_buy_random_number':
        await call.message.edit_text('💸 Выберите метод оплаты:', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('💎 Прямой перевод на адрес', callback_data='send_buy_random_number')))
    elif call.data=='send_buy_random_number':
        code = random.randint(99999, 9999999)
        await start_payment(id, call.message.chat.first_name)
        await call.message.edit_text(f'''
💎 Вы создали заявку на покупку номера:
 💸 TON адрес для оплаты: <code>{my_address}</code>
💰 Сумма: <code>10</code> <b>TON</b>
🔢 Уникальный комментарий(укажите его в комментарии к транзакции): <code>{code}</code>
👛 Ваш TON адрес(на него будет отправлена NFT): <code>{get_addrees(id)}</code>
⁉️ <b>NFT</b> будет отпрвлена на указанный в настройках <b>адрес</b>, если же он не указан, то на адрес, <b>с которого производилась оплата</b>!
''', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('🔃 Проверить оплату', callback_data=f'check_payment_{code}')).add(InlineKeyboardButton('❌ Отменить платеж', callback_data='stop')))
    elif 'change_address' in call.data:
        await call.message.delete()
        globals()[f'msg_{id}'] = await bot.send_message(id, '💎 Отправьте ваш <b>TON адрес</b> (<b>не из cryptobot!</b>):')
        await States.change_address.set()
    elif 'check_payment' in call.data:
        await bot.answer_callback_query(call.id, '❌ Оплата не найдена!')
    elif call.data=='history':
        await bot.send_message(id, '🛒 На данный момент у вас <b>0</b> покупок')
    elif call.data=='stop':
        await call.message.delete()
        await bot.send_message(id, '💎 Выберите товар для покупки:', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('📞 Случайный +888 номер | 999шт', callback_data='random_number')).add(InlineKeyboardButton('⬅️ Вернуться', callback_data='back_main')))
    elif call.data=='back_main':
        await call.message.delete()
        await bot.send_message(id, f'''
👋 Привет, <b>{(call.message.chat.first_name).replace('<', '').replace('>', '').replace('/', '')}</b>
📞 Добро пожаловать в первого телеграм бота по продаже <b>анонимных Telegram номеров</b> от <b>fragment</b>
⁉️ Как вы знаете, скоро цены на такие номера <b>начнут расти</b>, а вскоре их <b>продажи прекратятся на всегда!</b>
💎 У нас же вы всегда сможете покупать анонимные <b>+888</b> номера по фиксированной цене <b>10 TON</b>
''', reply_markup=start_kb)

@dp.message_handler(content_types=types.ContentType.ANY, state=States.change_address)
async def send_text(msg: types.ContentType.ANY, state: FSMContext):
    await msg.delete()
    await (globals()[f'msg_{msg.from_user.id}']).delete()
    await state.update_data(address=str(msg.text))
    globals().pop(f'msg_{msg.from_user.id}')
    await bot.send_message(msg.from_user.id, f'✅ Подтвердите смену адреса на <code>{msg.text}</code>', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('✅ Подтвердить', callback_data='confirm')).add(InlineKeyboardButton('❌ Отмена', callback_data='cancle')))
    await States.change_address1.set()

@dp.callback_query_handler(lambda call: True, state=States.change_address1)
async def handler_call(call: types.CallbackQuery, state: FSMContext):
    id = call.message.chat.id
    await call.message.delete()
    if call.data=='confirm':
        address = str((await state.get_data())['address'])
        change_address(id, address)
        await bot.send_message(id, f'✅ Ваш адрес успешно изменен на <code>{address}</code>')
        await bot.send_message(id, f'''
👨‍💼 Вот ваш профиль:
👤 Ник: <code>{(call.message.chat.first_name).replace('<', '').replace('>', '').replace('/', '')}</code>
🔢 ID: <code>{id}</code>
👛 Ваш TON адрес: <code>{get_addrees(id)}</code>
📊  Совершенно <b>0</b> покупок на сумму ≈<b>0TON</b>
🔨 Предупреждения от администрации: <code>0</code>
💎 Статус: <code>Новичек</code>
''', reply_markup=profil_kb)
    elif call.data=='cancel':
        await bot.send_message(id, f'❌ Операция отменена')
        await bot.send_message(id, f'''
👨‍💼 Вот ваш профиль:
👤 Ник: <code>{(call.message.chat.first_name).replace('<', '').replace('>', '').replace('/', '')}</code>
🔢 ID: <code>{id}</code>
👛 Ваш TON адрес: <code>{get_addrees(id)}</code>
📊  Совершенно <b>0</b> покупок на сумму ≈<b>0TON</b>
🔨 Предупреждения от администрации: <code>0</code>
💎 Статус: <code>Новичек</code>
''', reply_markup=profil_kb)
    return await state.finish()

if __name__ == '__main__':
        try:
            executor.start_polling(dp)
        except:
            pass