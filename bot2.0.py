import telebot
from telebot import types

bot = telebot.TeleBot('1792282194:AAHS45Vu6zVNPvDA2WMItgCiFLr1E8tNypw')

@bot.message_handler(commands=['start'])
def send_welcome(message):

    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/Помощь', '/Телефон')
    keyboard.row('/Аддрес', '/Сайт')
    bot.send_message(message.chat.id, f'Здравствуйте {message.from_user.first_name} .Я бот помощник интернет магазина flask shop. Для работы с мной используйте команды /', reply_markup=keyboard)

@bot.message_handler(commands=['Аддрес'])
def send_message(message):
    bot.send_message(message.chat.id, 'Адрес: г. Москва, ул. Льва Толстого, 16,')
    bot.send_photo(message.chat.id, 'https://www.google.com/maps/vt/data=zX0dR23DdbyWHNSb2pVHtR154RqHYvAAVeABVOjbqCaMAsZ2HNdPcEIdEiEOUjtp5KnH6EpkisaFdSIyMPW9j_QyRiXvQtJl1V5-KjiiyZKcN902jy7Zgf81n_tFEerYsLr-AKN2jFGwv4-QO8PYKiJq2-o63CrCfMqYRCF_J4PrnJ7njUEwHwgRDuTXkLnO1z7sB3kxr3xaNKIqEg1hAZu9Vv78hp89lBBGfJ8-DpXkCpGs6ox4B2dXcOelBKClxqHO6QioHYg5V_0i_4NudYkGlp1zo0EBTGmEc4awWfPSr6e39ePS2ZiX')

@bot.message_handler(commands=['Помощь'])
def send_message(message):
    bot.send_message(message.chat.id, 'Для связи с специалистом используйте наш аддрес электронной почты flejm198765@gmail.com ')

@bot.message_handler(commands=['Телефон'])
def send_message(message):
    bot.send_message(message.chat.id, 'Телефон: +7(495)776-3030 ')

@bot.message_handler(commands = ['Сайт'])
def url(message):
    markup = types.InlineKeyboardMarkup()
    btn_my_site= types.InlineKeyboardButton(text='Наш сайт', url='http://127.0.0.1:5000/')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "Нажми на кнопку и перейдите на наш сайт.", reply_markup = markup)

bot.polling(none_stop=True)