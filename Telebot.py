import telebot
from telebot import types

import requests
import threading
from multiprocessing import *
import random
import time
import schedule
import json
import emoji


from bd import user #импортим БД
from rassl import send_message1


TOKEN = '7152466437:AAGCQnCHeVB24SR3z5Geavirf38WiMHNRx4'


HELP = '''
Список команд:
/start - первый запуск
/help - основные команды
/reg - регистрация
/prog - программа тренировок
/chan - изменить данные о пользователе
/plan - план питания
/sov - полезный совет
/eda - простые и полезные рецепты
/mot - мотивационные цитаты
/razv - мемы / edits
/gif - гифка!

Данный бот может помочь с подбором тренировок,а также плана питания для различных целей
'''

bot = telebot.TeleBot(TOKEN)

slovar = {}

# Создаём отдельный поток для планировщика
thread_scheduler = threading.Thread(target=send_message1, args=(bot,))


#прописываем хэндллер для команды старт
@bot.message_handler(commands=['start'])
def start_handler(message):
    user['id'] = message.chat.id
    # Запускаем поток
    thread_scheduler.start()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ans1 = types.KeyboardButton('/help')
    markup.add(ans1)
    bot.register_next_step_handler(message, help_handler)#передаем сообщение в указанную функцию
    bot.send_message(message.from_user.id, f"Привет! Я твой персональный фитнес-помощник. Готовы начать?"
                                           f"\n Напишите '/help' для получения списка команд")


#прописываем хэндллер для команды хэлп
@bot.message_handler(commands=['help'])
def help_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2) #добавляем реплай кнопки с основным функционалом бота
    btn1 = types.KeyboardButton('/reg')
    btn2 = types.KeyboardButton('/chan')
    btn3 = types.KeyboardButton('/prog')
    btn4 = types.KeyboardButton('/plan')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.from_user.id, HELP, reply_markup=markup)


#прописываем хэндллер для команды рег
@bot.message_handler(commands=['reg'])
def reg_handler(message):
    bot.send_message(message.from_user.id, 'Введите ваше имя')
    bot.register_next_step_handler(message, reg_info)


#прописываем хэндллер для введенного текста
@bot.message_handler(commands=['text'])
def reg_info(message):
    user['id'] = message.from_user.id #в графу id в БД присваем id пользователя по сообщению
    user['name'] = message.text #в графу имени в БД присваиваем введенное пользователем имя
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Мужчина')
    btn2 = types.KeyboardButton('Женщина')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Введите ваш пол', reply_markup=markup)
    bot.register_next_step_handler(message, gen_info)


def gen_info(message):
    if message.text == 'Мужчина': #в зависимости от введенного текста (выбранной кнопки) присваем пол пользователю
        user["gender"] = 'Male'
    else:
        user["gender"] = 'Female'

    bot.send_message(message.chat.id, 'Введите ваш вес')
    bot.register_next_step_handler(message, weight_info)


def weight_info(message):
    if 35 < int(message.text) < 300:
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('1')
        btn2 = types.KeyboardButton('2')
        btn3 = types.KeyboardButton('3')
        markup.add(btn1, btn2, btn3)
        weight = int(message.text)
        if 40 <= weight <= 60:
            user["weight"] = '40-60'
        elif 60 < weight <= 80:
            user["weight"] = '60-80'
        elif 80 < weight <= 100:
            user["weight"] = '80-100'
        elif weight > 100:
            user["weight"] = '100+'
        bot.register_next_step_handler(message, pos_info)
        bot.send_message(message.chat.id, 'Сколько раз в неделю Вы готовы посещать тренажерный зал?', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Неверный формат ввода, повторите попытку')
        bot.register_next_step_handler(message, weight_info)


def pos_info(message):
    if message.text == '1':
        user['pos'] = '1'
    elif message.text == '2':
        user['pos'] = '2'
    elif message.text == '3':
        user['pos'] = '3'

    bot.send_message(message.chat.id, 'Введите ваш возраст')
    bot.register_next_step_handler(message, age_info)


def age_info(message):
    if 14 < int(message.text) < 80:
        age = int(message.text)
        if 14 < age <= 18:
            user["age"] = '14-18'
        elif 18 < age <= 25:
            user["age"] = '19-25'
        elif 25 < age <= 40:
            user["age"] = '26-40'
        elif 40 < age:
            user["age"] = '40+'
        markup = types.InlineKeyboardMarkup() #создаем inline кнопки
        btn1 = types.InlineKeyboardButton(text='Не имел опыта ранее', callback_data='0')
        btn2 = types.InlineKeyboardButton(text='Имел небольшой опыт (1-3 года', callback_data='1-3')
        btn3 = types.InlineKeyboardButton(text='Опытный атлет (3+ года', callback_data='3+')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, 'Охарактеризуйте ваш опыт тренировок', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Неверный формат ввода, повторите попытку')
        bot.register_next_step_handler(message, age_info)


#прописываем хэндлер для инлайн конопок
@bot.callback_query_handler(func=lambda call: call.data in ['0', '1-3', '3+'])
def exp_info_obr(call):
    if call.data == '0':
        user["exp"] = 'beginner'
    elif call.data == '1-3':
        user["exp"] = 'average'
    elif call.data == '3+':
        user["exp"] = 'advanced'
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Набор массы', callback_data='gains')
    btn2 = types.InlineKeyboardButton(text='Похудение', callback_data='loss')
    btn3 = types.InlineKeyboardButton(text='Удержание веса', callback_data='retention')
    markup.add(btn1, btn2, btn3)
    bot.send_message(call.message.chat.id, 'Охарактеризуйте вашу цель', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['gains', 'loss', 'retention'])
def goal_info_obr(call):
    if call.data == 'gains':
        user["goal"] = 'Набор веса'
    elif call.data == 'loss':
        user["goal"] = 'Похудение'
    elif call.data == 'retention':
        user["goal"] = 'Удержание веса'
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Программа тренировок', callback_data='prog')
    btn2 = types.InlineKeyboardButton(text='План питания', callback_data='plan')
    btn3 = types.InlineKeyboardButton(text='Комбо', callback_data='combo')
    markup.add(btn1, btn2, btn3)
    bot.send_message(call.message.chat.id, 'Охарактеризуйте ваши пожелания', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['prog', 'plan', 'combo'])
def choice_info_obr(call):
    if call.data == 'prog':
        user["choice"] = 'Программа тренировок'
    elif call.data == 'plan':
        user["choice"] = 'План питания'
    elif call.data == 'combo':
        user["choice"] = 'План питания + Программа тренировок'

    bot.send_message(call.message.chat.id, f" Отлично! Регистрация окончена. Ваш профиль: "    #выводим анкету пользователя, используя записанную инфу в БД
                                           f"\nВаш пол: {user['gender']}"
                                           f"\nВаш ID: {user['id']}"
                                           f"\nВаше имя: {user['name']}"
                                           f"\nВаша весовая категория: {user['weight']}"
                                           f"\nВаша возрастная категория: {user['age']}"
                                           f"\nОпыт тренировок: {user['exp']}"
                                           f"\nВаша цель: {user['goal']}"
                                           f"\nВы выбрали: {user['choice']}")


#прописываем хэндлер для команлы чейндж (для редактирования пользовательской анкеты)
@bot.message_handler(commands=['chan'])
def req_info(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='пол', callback_data='gender')
    btn2 = types.InlineKeyboardButton(text='имя', callback_data='name')
    btn3 = types.InlineKeyboardButton(text='вес', callback_data='weight')
    btn4 = types.InlineKeyboardButton(text='возраст', callback_data='age')
    btn5 = types.InlineKeyboardButton(text='опыт тренировок', callback_data='exp')
    btn6 = types.InlineKeyboardButton(text='цель', callback_data='goal')
    btn7 = types.InlineKeyboardButton(text='посещения', callback_data='pos')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    bot.send_message(message.chat.id, 'Выберете что бы вы хотели изменить в своем профиле, введите новые данные', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['gender', 'name', 'weight', 'age', 'exp', 'goal', 'pos'])
def req_info_obr(call):
    #создаем временную БД для записи параметра изменения
    global change
    change = {"info": None}
    if call.data == 'gender':
        change['info'] = 'gender'
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Мужчина')
        btn2 = types.KeyboardButton('Женщина')
        markup.add(btn1, btn2)
        bot.send_message(call.message.chat.id, 'Введите ваш пол', reply_markup=markup)
    elif call.data == 'name':
        change['info'] = 'name'
        bot.send_message(call.message.chat.id, 'Напишите ваше имя')
    elif call.data == 'weight':
        change['info'] = 'weight'
        bot.send_message(call.message.chat.id, 'Введите ваш вес в кг')
    elif call.data == 'age':
        change['info'] = 'age'
        bot.send_message(call.message.chat.id, 'Введите вас возраст')
    elif call.data == 'exp':
        change['info'] = 'exp'
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Не имел опыта')
        btn2 = types.KeyboardButton('Имел небольшой опыт (1-3 года)')
        btn3 = types.KeyboardButton('Опытный атлет')
        markup.add(btn1, btn2, btn3)
        bot.send_message(call.message.chat.id, 'Введите новые данные', reply_markup=markup)
    elif call.data == 'goal':
        change['info'] = 'goal'
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Набор веса')
        btn2 = types.KeyboardButton('Похудение')
        btn3 = types.KeyboardButton('Удержание веса')
        markup.add(btn1, btn2, btn3)
        bot.send_message(call.message.chat.id, 'Введите новые данные', reply_markup=markup)
    elif call.data == 'pos':
        change['info'] = 'pos'
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('1 день')
        btn2 = types.KeyboardButton('2 дня')
        btn3 = types.KeyboardButton('3 дня')
        markup.add(btn1, btn2, btn3)
        bot.send_message(call.message.chat.id, 'Введите новые данные', reply_markup=markup)
    bot.register_next_step_handler(call.message, rech_info)


@bot.message_handler(commands=['text'])
def rech_info(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Проверить данные')
    btn2 = types.KeyboardButton('Не проверять данные')
    markup.add(btn1, btn2)
    if change['info'] == 'gender':
        if message.text == 'Мужчина':
            user['gender'] = 'Male'
        elif message.text == 'Женщина':
            user['gender'] = 'Female'
        else:
            bot.send_message(message.chat.id, 'Проверьте корректность введенных данных')
    elif change['info'] == 'weight':
        weight = int(message.text)
        if 40 <= weight <= 60:
            user["weight"] = '40-60'
        elif 60 < weight <= 80:
            user["weight"] = '60-80'
        elif 80 < weight <= 100:
            user["weight"] = '80-100'
        elif weight > 100:
            user["weight"] = '100+'
    elif change['info'] == 'age':
        age = int(message.text)
        if 14 < age <= 18:
            user["age"] = '14-18'
        elif 18 < age <= 25:
            user["age"] = '19-25'
        elif 25 < age <= 40:
            user["age"] = '26-40'
        elif 40 < age:
            user["age"] = '40+'
    elif change['info'] == 'exp':
        if message.text == 'Не имел опыта':
            user['exp'] = 'beginner'
        elif message.text == 'Имел небольшой опыт (1-3 года)':
            user['exp'] = 'average'
        elif message.text == 'Опытный атлет':
            user['exp'] = 'advanced'
        else:
            bot.send_message(message.chat.id, 'Проверьте корректность введенных данных')
    elif change['info'] == 'name':
        user['name'] = message.text
    elif change['info'] == 'goal':
        if message.text == 'Набор веса':
            user['goal'] = 'Набор веса'
        elif message.text == 'Похудение':
            user['goal'] = 'Похудение'
        elif message.text == 'Удержание веса':
            user['goal'] = 'Удержание веса'
        else:
            bot.send_message(message.chat.id, 'Проверьте корректность введенных данных')
    elif change['info'] == 'pos':
        if message.text == '1 день':
            user['pos'] = '1'
        elif message.text == '2 дня':
            user['pos'] = '2'
        elif message.text == '3 дня':
            user['pos'] = '3'
        else:
            bot.send_message(message.chat.id, 'Проверьте корректность введенных данных')
        user['pos'] = message.text

    bot.send_message(message.chat.id, 'Хотите ли Вы проверить изменения?', reply_markup=markup)
    bot.register_next_step_handler(message, prov)


def prov(message):
    if message.text == 'Проверить данные':
        bot.send_message(message.chat.id, f" Отлично! Изменения внесены. Ваш профиль: "   #в случае необходимости выводим измененную анкету пользователя
                                               f"\nВаш пол: {user['gender']}"
                                               f"\nВаш ID: {user['id']}"
                                               f"\nВаше имя: {user['name']}"
                                               f"\nВаша весовая категория: {user['weight']}"
                                               f"\nВаша возрастная категория: {user['age']}"
                                               f"\nОпыт тренировок: {user['exp']}"
                                               f"\nВаша цель: {user['goal']}"
                                               f"\nВы выбрали: {user['choice']}")
    else:
        pass


#прописываем хэндлер для команды прог
@bot.message_handler(commands=['prog'])
def prog_info(message): #после регистрации, на основе введенных пользователем данных и целей, программа автоматически подбирает для пользователя программу тренировок, в случае если пользователь хочет получить программу ДО регистрации, он получает сообщение о непройденной регистрации и направляется на нее
    if user['age'] != None and user['name'] != None and user['gender'] != None and user['weight'] != None and user['exp'] != None and user['goal'] != None and user['choice'] != None:
        if user['age'] == '14-18' and user['exp'] in ['beginner', 'average', 'advanced'] and user['pos'] == '1':
            bot.send_message(message.chat.id, f"1. 10 минут разминка (легкое кардио, различные базовые "
                                           f"упражнения разминки)"
                                           f"\n2. Приседания со штангой 3 подхода по 6-10 раз, вес подбирается "
                                           f"индивидуально, техника выполнения: "
                                           f"https://www.youtube.com/watch?v=7Yg2YVNdd8c"
                                           f"\n3. Жим лежа 3 подхода по 6-8 раз, вес подбирается индивидуально, "
                                           f"техника выполнения: https://www.youtube.com/watch?v=rIZirGYcbD8"
                                           f"\n4. Подъем штанги на бицепс 3 подхода по 7-10 раз, вес подбирается "
                                           f"индивидуально, техника "
                                           f"выполнения: https://www.youtube.com/watch?v=WpbyWZjmkpU"
                                           f"\n5. Тяга горизонтального блока к поясу 4 подхода по "
                                           f"6-9 раз, вес подбирается индивидуально, "
                                           f"техника выполнения: https://www.youtube.com/watch?v=hUV6XDtNTLU"
                                           f"\n6. Отжимания на брусьях 3 подхода по "
                                           f"10 раз (если 10 повторений пока невозможны, используйте "
                                           f"тренажер-гравитрон, вес подбирается индивидуально), "
                                           f"техника выполнения: https://www.youtube.com/watch?v=NsHU9USqGEU"
                                           f"\n7. Заминка: 10 минут легкой пробежки на беговой "
                                           f"дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                                           f"\n ---------------------------------"
                                           f"\n ВАЖНО! Под индивидуальным подбором веса подразумевается выбор "
                                           f"такого веса, что указанные повторения должны выполняться с "
                                           f"ощутимой тяжестью (70-80% от максимальных возможностей)")
            bot.send_message(message.chat.id, emoji.emojize('Хорошей тренировки! :flexed_biceps:'))

        elif user['age'] in ['19-25', '26-40', '40+'] and user['exp'] in ['beginner', 'average'] and user['pos'] == '1':
            bot.send_message(message.chat.id, f"1. 10 минут разминка (легкое кардио, различные базовые "
                                           f"упражнения разминки)"
                                           f"\n2. Приседания со штангой 3 подхода по 6-10 раз, вес подбирается "
                                           f"индивидуально, техника выполнения: "
                                           f"https://www.youtube.com/watch?v=7Yg2YVNdd8c"
                                           f"\n3. Жим лежа 3 подхода по 6-8 раз, вес подбирается индивидуально, "
                                           f"техника выполнения: https://www.youtube.com/watch?v=rIZirGYcbD8"
                                           f"\n4. Подъем штанги на бицепс 3 подхода по 7-10 раз, вес подбирается "
                                           f"индивидуально, техника "
                                           f"выполнения: https://www.youtube.com/watch?v=WpbyWZjmkpU"
                                           f"\n5. Тяга горизонтального блока к поясу 4 подхода по "
                                           f"6-9 раз, вес подбирается индивидуально, "
                                           f"техника выполнения: https://www.youtube.com/watch?v=hUV6XDtNTLU"
                                           f"\n6. Отжимания на брусьях 3 подхода по "
                                           f"10 раз (если 10 повторений пока невозможны, используйте "
                                           f"тренажер-гравитрон, вес подбирается индивидуально), "
                                           f"техника выполнения: https://www.youtube.com/watch?v=NsHU9USqGEU"
                                           f"\n7. Заминка: 10 минут легкой пробежки на беговой "
                                           f"дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                                           f"\n ---------------------------------"
                                           f"\n ВАЖНО! Под индивидуальным подбором веса подразумевается выбор "
                                           f"такого веса, что указанные повторения должны выполняться с "
                                           f"ощутимой тяжестью (70-80% от максимальных возможностей)")
            bot.send_message(message, emoji.emojize('Хорошей тренировки! :flexed_biceps:'))

        elif user['age'] in ['19-25', '26-40', '40+'] and user['exp'] in ['advanced'] and user['pos'] == '1':
            bot.send_message(message.chat.id,
                             f"1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки)"
                             f"\n2. Приседания со штангой | Приседания в тренажере Гакк | Приседания в тренажере Смит 3 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=7Yg2YVNdd8c"
                             f"\n3. Жим лежа штанги | гантелей 3 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=rIZirGYcbD8"
                             f"\n4. Подъем штанги на бицепс EZ-гриф | прямой гриф | скамья Скотта 4 подхода по 7-10 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=WpbyWZjmkpU"
                             f"\n5. Тяга горизонтального блока к поясу | тяга штанги к поясу стоя | тяга гантелей в наклоне 4 подхода по 6-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=hUV6XDtNTLU"
                             f"\n6. Отжимания на брусьях без веса | с весом 3 подхода по 10 раз (если 10 повторений пока невозможны, используйте тренажер-гравитрон, вес подбирается индивидуально), техника выполнения: https://www.youtube.com/watch?v=NsHU9USqGEU"
                             f"\n7. Заминка: 10 минут легкой пробежки на беговой дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                             f"\n ---------------------------------"
                             f"\n ВАЖНО! Под индивидуальным подбором веса подразумевается выбор такого веса, что указанные повторения должны выполняться с ощутимой тяжестью (80-90% от максимальных возможностей). Рекомендуется чередование предложенных упражнений при возникновении дискомфорта при выполнении одного конкретного")
            bot.send_message(message.chat.id, emoji.emojize('Хорошей тренировки! :flexed_biceps:'))

        elif user['age'] in ['14-18', '19-25', '26-40', '40+'] and user['exp'] in ['beginner', 'average'] and user['pos'] == '2':
            bot.send_message(message.chat.id, f"PUSH DAY"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки)"
                                           f"\n2. Жим платформы (ногами) 3-4 подхода по 8-10 раз, вес подбирается индивидуально техника выполнения: https://www.youtube.com/watch?v=jyphzYKrptw"
                                           f"\n3. Жим лежа штанги | гантелей 3-4 подхода по 7-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=rIZirGYcbD8"
                                           f"\n4. Жим гантелей сидя 3 подхода по 7-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=MT0Z1J6TPKE"
                                           f"\n5. Французский жим EZ-гриф | гантели 3 подхода по 6-10 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=DMK5bD6BZY4"
                                           f"\n ---------------------------------"
                                           f"\nPULL DAY"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки)"
                                           f"\n2. Приседания со штангой 2 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=7Yg2YVNdd8c"
                                           f"\n3. Подъем штанги на бицепс 3 подхода по 7-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=WpbyWZjmkpU"
                                           f"\n4. Тяга горизонтального блока к поясу | тяга штанги к поясу стоя | тяга гантелей в наклоне 4 подхода по 6-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=hUV6XDtNTLU"
                                           f"\n5. Становая тяга 3 подхода по 7-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=108Ga1EdL_Q"
                                           f"\n6. Подтягивания без веса | с весом 4 подхода по 6-8 раз (если 6-8 повторений пока невозможны, используйте тренажер-гравитрон, вес подбирается индивидуально), техника выполнения: https://www.youtube.com/watch?v=K5UVjeNCKmY"
                                           f"\n ---------------------------------"
                                           f"\n ВАЖНО! Под индивидуальным подбором веса подразумевается выбор такого веса, что указанные повторения должны выполняться с ощутимой тяжестью (70-80% от максимальных возможностей)")
            bot.send_message(message.chat.id, emoji.emojize('Хорошей тренировки! :flexed_biceps:'))

        elif user['age'] in ['14-18', '19-25', '26-40', '40+'] and user['exp'] in ['advanced'] and user['pos'] == '2':
            bot.send_message(message.chat.id, f"PUSH DAY"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки)"
                                           f"\n2. Жим платформы (ногами) 4 подхода по 10-12 раз, вес подбирается индивидуально техника выполнения: https://www.youtube.com/watch?v=jyphzYKrptw"
                                           f"\n3. Жим лежа штанги | гантелей 3-4 подхода по 7-9 раз (также можно добавить жим штанги в наклоне, например, 3 подхода жима лежа и 2 подхода жима в наклоне, техника выполнения: https://www.youtube.com/watch?v=mLuPbLq2PW4), вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=rIZirGYcbD8"
                                           f"\n4. Жим гантелей сидя 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=MT0Z1J6TPKE"
                                           f"\n5. Французский жим EZ-гриф | гантели 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=DMK5bD6BZY4"
                                           f"\n ---------------------------------"
                                           f"\nPULL DAY"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки)"
                                           f"\n2. Приседания со штангой 3 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=7Yg2YVNdd8c"
                                           f"\n3. Подъем штанги на бицепс 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=WpbyWZjmkpU"
                                           f"\n4. Тяга горизонтального блока к поясу | тяга штанги к поясу стоя | тяга гантелей в наклоне 4 подхода по 8-10 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=hUV6XDtNTLU"
                                           f"\n5. Становая тяга 3 подхода по 7-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=108Ga1EdL_Q"
                                           f"\n6. Подтягивания без веса | с весом 3 подхода по 8-10 раз (если 8-10 повторений пока невозможны, используйте тренажер-гравитрон, вес подбирается индивидуально), техника выполнения: https://www.youtube.com/watch?v=K5UVjeNCKmY"
                                           f"\n ---------------------------------"
                                           f"\n ВАЖНО! Под индивидуальным подбором веса подразумевается выбор такого веса, что указанные повторения должны выполняться с ощутимой тяжестью (80-90% от максимальных возможностей)")
            bot.send_message(message.chat.id, emoji.emojize('Хорошей тренировки! :flexed_biceps:'))

        elif user['age'] in ['14-18', '19-25', '26-40', '40+'] and user['exp'] in ['beginner', 'average'] and user['pos'] == '3':
            bot.send_message(message.chat.id, f"1 тренировочный день (грудь - трицепс)"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки"
                                           f"\n2. Жим лежа штанги | гантелей 3-4 подхода по 7-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=rIZirGYcbD8)"
                                           f"\n3. Жим лежа на наклонной скамье штанги | гантелей по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=mLuPbLq2PW4&t=4s"
                                           f"\n4. Упражнения на блоке (трицепс), 3-4 подхода по 8-10 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=Kn4h8gY7raQ"
                                           f"\n5. Французский жим EZ-гриф | гантели 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=DMK5bD6BZY4"
                                           f"\n6. Заминка: 10 минут легкой пробежки на беговой дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                                           f"\n ---------------------------------"
                                           f"\n2 тренировочный день (спина - бицепс)"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки"
                                           f"\n2. Тяга горизонтального блока к поясу | тяга штанги к поясу стоя | тяга гантелей в наклоне 3-4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=hUV6XDtNTLU"
                                           f"\n3. Тяга вертикального блока, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=GTs3xqB_ZgQ"
                                           f"\n4. Подъем штанги на бицепс 3-4 подхода по 7-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=WpbyWZjmkpU"
                                           f"\n5. Упражнения на блоке | со свободным весом на брахиалис 3-4 подхода по 7-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=DpaIZ2SHrDE"
                                           f"\n6. Заминка: 10 минут легкой пробежки на беговой дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                                           f"\n ---------------------------------"
                                           f"\n3 тренировочный день (ноги - плечи)"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки"
                                           f"\n2. Приседания со штангой 3 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=7Yg2YVNdd8c"
                                           f"\n3. Выполнение упражнения на тренажере 'Leg exstensions' 2-3 подхода по 8-10 раз, техника выполнения (доступно с субтитрами): https://www.youtube.com/watch?v=ljO4jkwv8wQ"
                                           f"\n4. Выполнение упражнения на заднюю поверхность бедра (по выбору) 2-3 подхода по 8-10 раз, техника выполнения упражнений: https://www.youtube.com/watch?v=66mQ-79Me3k"
                                           f"\n5.  Жим гантелей сидя 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=MT0Z1J6TPKE"
                                           f"\n6. Махи гантелями 3-4 подхода по 8-10 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=Q3j7XYxrJtk"
                                           f"\n7. Заминка: 10 минут легкой пробежки на беговой дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                                           f"\n ВАЖНО! Под индивидуальным подбором веса подразумевается выбор такого веса, что указанные повторения должны выполняться с ощутимой тяжестью (70-80% от максимальных возможностей)")
            bot.send_message(message.chat.id, emoji.emojize('Хорошей тренировки! :flexed_biceps:'))

        elif user['age'] in ['14-18', '19-25', '26-40', '40+'] and user['exp'] in ['advanced'] and user['pos'] == '3':
            bot.send_message(message.chat.id, f"1 тренировочный день (грудь - трицепс)"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки"
                                           f"\n2. Жим лежа штанги | гантелей 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=rIZirGYcbD8)"
                                           f"\n3. Жим лежа на наклонной скамье штанги | гантелей по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=mLuPbLq2PW4&t=4s"
                                           f"\n4. Упражнения на блоке (трицепс), 4 подхода по 8-10 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=Kn4h8gY7raQ"
                                           f"\n5. Французский жим EZ-гриф | гантели 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=DMK5bD6BZY4"
                                           f"\n6. Заминка: 10 минут легкой пробежки на беговой дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                                           f"\n ---------------------------------"
                                           f"\n2 тренировочный день (спина - бицепс)"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки"
                                           f"\n2. Тяга горизонтального блока к поясу | тяга штанги к поясу стоя | тяга гантелей в наклоне 4 подхода по 7-10 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=hUV6XDtNTLU"
                                           f"\n3. Тяга вертикального блока, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=GTs3xqB_ZgQ"
                                           f"\n4. Подъем штанги на бицепс 4 подхода по 7-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=WpbyWZjmkpU"
                                           f"\n5. Упражнения на блоке | со свободным весом на брахиалис 4 подхода по 6-9 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=DpaIZ2SHrDE"
                                           f"\n6. Заминка: 10 минут легкой пробежки на беговой дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                                           f"\n ---------------------------------"
                                           f"\n3 тренировочный день (ноги - плечи)"
                                           f"\n1. 10 минут разминка (легкое кардио, различные базовые упражнения разминки"
                                           f"\n2. Приседания со штангой 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=7Yg2YVNdd8c"
                                           f"\n3. Выполнение упражнения на тренажере 'Leg exstensions' 3-4 подхода по 8-10 раз, техника выполнения (доступно с субтитрами): https://www.youtube.com/watch?v=ljO4jkwv8wQ"
                                           f"\n4. Выполнение упражнения на заднюю поверхность бедра (по выбору) 3-4 подхода по 8-10 раз, техника выполнения упражнений: https://www.youtube.com/watch?v=66mQ-79Me3k"
                                           f"\n5.  Жим гантелей сидя 4 подхода по 6-8 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=MT0Z1J6TPKE"
                                           f"\n6. Махи гантелями 4 подхода по 8-10 раз, вес подбирается индивидуально, техника выполнения: https://www.youtube.com/watch?v=Q3j7XYxrJtk"
                                           f"\n7. Заминка: 10 минут легкой пробежки на беговой дорожке ИЛИ растяжка ИЛИ 2-3 подхода упражнений на пресс (по выбору)"
                                           f"\n ВАЖНО! Под индивидуальным подбором веса подразумевается выбор такого веса, что указанные повторения должны выполняться с ощутимой тяжестью (80-90% от максимальных возможностей). Для более опытных атлетов допускается самостоятельная регулировка тех или иных упражнений и их чередование, также возможно комбинирование некоторых тренировочных дней и изменение split-программы для более комфортной")
            bot.send_message(message.chat.id, emoji.emojize('Хорошей тренировки! :flexed_biceps:'))

    else:
        bot.send_message(message.chat.id, f"Для начала пройдите регистрацию! \n/reg")


#Хэндлер для команды план
@bot.message_handler(commands=['plan'])
def plan_info(message): #аналогично программе тренировок пользователь полуает готовый план питания, в случае если регистрация не пройдена, пользователь направляется на нее
    if user['age'] != None and user['name'] != None and user['gender'] != None and user['weight'] != None and user['exp'] != None and user['goal'] != None and user['choice'] != None:
        if user['weight'] in ['40-60', '60-80'] and user['goal'] == 'Набор веса':

            bot.send_message(message.chat.id, f"Для мужчины: 1.5-1.7г белков на кг веса | Для женщины: 1.2-1.5г белков на кг веса"
                                              f"\nДля мужчины: 2.3-2.7г углеводов на кг веса | Для женщины: 1.7-2г углеводов на кг веса"
                                              f"\nДля мужчины: 0.7-1.1г жиров на кг веса | Для женщины: 0.5-0.9г жиров на кг веса")
            bot.send_message(message.chat.id, emoji.emojize('Приятного аппетита! :green_apple:'))

        elif user['weight'] in ['80-100', '100+'] and user['goal'] == 'Набор веса':
            bot.send_message(message.chat.id,
                             f"Для мужчины: 1.8-2.2г белков на кг веса | Для женщины: 1.4-1.7г белков на кг веса"
                             f"\nДля мужчины: 2.7-3г углеводов на кг веса | Для женщины: 2.1-2.4г углеводов на кг веса"
                             f"\nДля мужчины: 1-1.4г жиров на кг веса | Для женщины: 0.7-1.1г жиров на кг веса")
            bot.send_message(message.chat.id, emoji.emojize('Приятного аппетита! :green_apple:'))

        elif user['weight'] in ['40-60', '60-80'] and user['goal'] == 'Похудение':
            bot.send_message(message.chat.id,
                             f"Для мужчины: 1.4-1.8г белков на кг веса | Для женщины: 1.3-1.6г белков на кг веса"
                             f"\nДля мужчины: 1.7-2г углеводов на кг веса | Для женщины: 1.3-1.5г углеводов на кг веса"
                             f"\nДля мужчины: 0.5-0.9г жиров на кг веса | Для женщины: 0.4-0.8г жиров на кг веса")
            bot.send_message(message.chat.id, emoji.emojize('Приятного аппетита! :green_apple:'))

        elif user['weight'] in ['80-100', '100+'] and user['goal'] == 'Похудение':
            bot.send_message(message.chat.id,
                             f"Для мужчины: 1.6-2г белков на кг веса | Для женщины: 1.3-1.7г белков на кг веса"
                             f"\nДля мужчины: 1.9-2.1г углеводов на кг веса | Для женщины: 1.5-1.7г углеводов на кг веса"
                             f"\nДля мужчины: 0.7-1.1г жиров на кг веса | Для женщины: 0.6-1г жиров на кг веса")
            bot.send_message(message.chat.id, emoji.emojize('Приятного аппетита! :green_apple:'))

        elif user['weight'] in ['40-60', '60-80'] and user['goal'] == 'Удержание веса':
            bot.send_message(message.chat.id,
                             f"Для мужчины: 1.3-1.6г белков на кг веса | Для женщины: 1.1-1.3г белков на кг веса"
                             f"\nДля мужчины: 2-2.4г углеводов на кг веса | Для женщины: 1.5-1.7г углеводов на кг веса"
                             f"\nДля мужчины: 0.7-1.1г жиров на кг веса | Для женщины: 0.5-0.9г жиров на кг веса")
            bot.send_message(message.chat.id, emoji.emojize('Приятного аппетита! :green_apple:'))

        elif user['weight'] in ['80-100', '100+'] and user['goal'] == 'Удержание веса':
            bot.send_message(message.chat.id, f"Для мужчины: 1.7-2.1г белков на кг веса | Для женщины: 1.3-1.8г белков на кг веса"
                                              f"\nДля мужчины: 2.4-2.6г углеводов на кг веса | Для женщины: 1.7-2г углеводов на кг веса"
                                              f"\nДля мужчины: 0.9-1.3г жиров на кг веса | Для женщины: 0.8-1.2г жиров на кг веса")
            bot.send_message(message.chat.id, emoji.emojize('Приятного аппетита! :green_apple:'))
    else:
        bot.send_message(message.chat.id, f"Для начала пройдите регистрацию! \n/reg")


#эндлер дла команды сов
@bot.message_handler(commands=['sov']) #функция выдает рандомный из 10 написанных полезнвх советов
def baza(message):
    global df
    df = {'1': None, '2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None}
    df['1'] = 'Слушайте свое тело: Важно научиться слушать свое тело и реагировать на его сигналы. Если вы чувствуете усталость или болезненные ощущения, дайте себе время на восстановление, чтобы избежать переутомления и травмирования.'
    df['2'] = 'Задайте конкретные цели: Определите, что именно вы хотите достичь от своей тренировки, будь то улучшение физической формы, набор мышечной массы или увеличение выносливости.'
    df['3'] = 'Регулярность: Стройте тренировочный график и придерживайтесь его. Регулярность – ключ к достижению результатов.'
    df['4'] = 'Разнообразие: Включайте в тренировочный план разнообразные упражнения, чтобы стимулировать все группы мышц и предотвратить привыкание.'
    df['5'] = 'Правильная техника: Уделите внимание правильной технике выполнения упражнений, это поможет избежать травм и максимизировать эффективность тренировки.'
    df['6'] = 'Отдых и восстановление: Не забывайте о необходимости отдыха между тренировками. Мышцам нужно время на восстановление и рост.'
    df['7'] = 'Питание: Обеспечьте свой организм правильным питанием, подходящим для ваших целей тренировки. Оно должно быть богато белками, углеводами и здоровыми жирами.'
    df['8'] = 'Гидратация: Пейте достаточное количество воды перед, во время и после тренировки, чтобы избежать обезвоживания.'
    df['9'] = 'Сон: Уделяйте достаточное внимание сну, так как это время, когда ваш организм восстанавливается и строит мышцы.'
    df['10'] = 'Постоянное совершенствование: Всегда стремитесь к постоянному улучшению. Это может быть увеличение веса, повышение числа повторений или улучшение времени выполнения упражнения.'

    random_number = random.randint(1, 10)
    ind = str(random_number)
    bot.send_message(message.chat.id, emoji.emojize('Совет дня:star:'))
    bot.send_message(message.chat.id, f"{df[ind]}")


#хэндлер для команды еда
@bot.message_handler(commands=['eda'])
def baza1(message): #функция выдает рандомный из 10 написанных рецептов
    global df1
    df1 = {'1': None, '2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None}
    df1['1'] = 'Овсяная каша с фруктами: Заварите овсянку на воде или молоке, добавьте свежие фрукты (например, нарезанные яблоки или ягоды), орехи и мед для сладости.'
    df1['2'] = 'Гречневая каша с овощами: Приготовьте гречку и добавьте обжаренные на сковороде овощи (морковь, лук, перец), приправьте зеленью и соевым соусом.'
    df1['3'] = 'Салат с тунцом и овощами: Смешайте консервированный тунец с нарезанными помидорами, огурцами, листьями салата и добавьте лимонный сок и оливковое масло.'
    df1['4'] = 'Печеные овощи с куриной грудкой: Нарежьте куриную грудку и овощи (картошку, баклажаны, цукини) на кусочки, запекайте в духовке с приправами до готовности.'
    df1['5'] = 'Омлет с овощами: Взбейте яйца с молоком, добавьте нарезанные овощи (помидоры, шпинат, перец), затем обжарьте на сковороде.'
    df1['6'] = 'Тосты с авокадо: Разотрите спелый авокадо на хлебе, посыпьте кунжутом или перцем чили и добавьте кусочки помидора сверху.'
    df1['7'] = 'Суп-пюре из брокколи: Приготовьте брокколи и картофель, затем взбейте их в блендере с куриного бульона до получения однородной массы.'
    df1['8'] = 'Запеченный лосось с зеленым гарниром: Запеките филе лосося в духовке, подавайте с киноа или овощным салатом с зеленью.'
    df1['9'] = 'Куриные котлеты с овсянкой: Смешайте мелко нарезанные куриные филе с вареной овсянкой, формируйте котлеты и обжаривайте на сковороде до золотистой корочки.'
    df1['10'] = 'Фруктовый смузи: Смешайте свежие или замороженные фрукты (бананы, клубника, манго) с йогуртом или молоком в блендере до получения однородной консистенции.'

    random_number = random.randint(1, 10)
    ind = str(random_number)
    bot.send_message(message.chat.id, emoji.emojize('Полезный рецепт дня:pear:'))
    bot.send_message(message.chat.id, f"{df1[ind]}")


 #хэндлер для команды мот
@bot.message_handler(commands=['mot'])
def baza1(message): #функция выдает рандомный из 10 прописанных мотивационных цитат
    global df1
    df2 = {'1': None, '2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, '10': None}
    df2['1'] = "Самая большая преграда на пути к достижению успеха - это отказ от своих мечтаний. Не останавливайтесь, двигайтесь вперед!"
    df2['2'] = "Каждый новый день - это новая возможность стать лучше, чем вчера. Поверьте в себя и стремитесь к своим целям с упорством."
    df2['3'] = "Не бойтесь испытаний на пути к своим мечтам. Именно они делают нас сильнее и помогают нам расти."
    df2['4'] = "Даже самый длинный путь начинается с первого шага. Не откладывайте свои мечты на завтра, начинайте сегодня!"
    df2['5'] = "Секрет успеха - это уверенность в своих силах и готовность преодолевать любые трудности на пути к цели."
    df2['6'] = "Помните, что ваша упорная работа и настойчивость непременно приведут вас к успеху. Никогда не сдавайтесь!"
    df2['7'] = "Лучший способ предсказать будущее - это создать его самому. Двигайтесь вперед с уверенностью и решимостью."
    df2['8'] = "Помните, что каждое усилие, которое вы вкладываете в свои мечты, приближает вас к их осуществлению. Никогда не унывайте!"
    df2['9'] = "Не сравнивайте свой путь с путем других. Ваш путь уникален, и только вы можете определить свой собственный успех."
    df2['10'] = "Будьте готовы к неудачам, но не позволяйте им остановить вас. Из неудач мы учимся и растем сильнее. Вперед, к новым вершинам!"

    random_number = random.randint(1, 10)
    ind = str(random_number)
    bot.send_message(message.chat.id, emoji.emojize('Цитата дня:sparkles:'))
    bot.send_message(message.chat.id, f"{df2[ind]}")


#хэндлер для команды разв
@bot.message_handler(commands=['razv'])
def func_ent(message): #функция осуществляет СНАЧАЛА выбор контента пользователем, а ЗАТЕМ отправку рандомного из изначально заготовленных варинатов
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='мемы', callback_data='mem')
    btn2 = types.InlineKeyboardButton(text='edits', callback_data='edit')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Что бы вы хотели посмотреть?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['mem', 'edit'])
def mem_edit(call):
    if call.data == 'mem':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='gym', callback_data='gym')
        btn2 = types.InlineKeyboardButton(text='другое', callback_data='other')
        markup.add(btn1, btn2)
        bot.send_message(call.message.chat.id, 'Выберите тематику', reply_markup=markup)
    elif call.data == 'edit':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='gym', callback_data='gym1')
        btn2 = types.InlineKeyboardButton(text='cars', callback_data='cars')
        btn3 = types.InlineKeyboardButton(text='cartoon', callback_data='anime')
        markup.add(btn1, btn2, btn3)
        bot.send_message(call.message.chat.id, 'Выберите тематику', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['gym1', 'cars', 'gym', 'anime', 'other'])
def mem_edit_handler(call):
    global arr1
    arr1 = {'1': None, '2': None, '3': None, '4': None, '5': None}
    if call.data == 'gym1':
        arr1['1'] = 'https://www.youtube.com/shorts/JJBbqI-svZ8'
        arr1['2'] = 'https://www.youtube.com/shorts/5LkZtLzSNDw'
        arr1['3'] = 'https://www.youtube.com/shorts/0PjjpA07M7k'
        arr1['4'] = 'https://www.youtube.com/shorts/TdyuvcnDZEQ'
        arr1['5'] = 'https://www.youtube.com/shorts/iP5zBr1g4Jk'

        random_number = random.randint(1, 5)
        ind = str(random_number)
        bot.send_message(call.message.chat.id, emoji.emojize('Зарядись энергией:trophy:'))
        bot.send_message(call.message.chat.id, f"{arr1[ind]}")

    elif call.data == 'cars':
        arr1['1'] = 'https://www.youtube.com/watch?v=Jf4CRO_iEn8'
        arr1['2'] = 'https://www.youtube.com/watch?v=LitHV3Q-rSI'
        arr1['3'] = 'https://www.youtube.com/watch?v=p-X42xUa2wQ'
        arr1['4'] = 'https://www.youtube.com/shorts/X6Q82dXnOBY'
        arr1['5'] = 'https://www.youtube.com/shorts/RMQtaHZLq7A'

        random_number = random.randint(1, 5)
        ind = str(random_number)
        bot.send_message(call.message.chat.id, emoji.emojize('Врум врум :racing_car:'))
        bot.send_message(call.message.chat.id, f"{arr1[ind]}")

    elif call.data == 'anime':
        arr1['1'] = 'https://www.youtube.com/shorts/iNPoLFxbFO0'
        arr1['2'] = 'https://www.youtube.com/watch?v=ntosogSwBpQ'
        arr1['3'] = 'https://www.youtube.com/shorts/3rz7-IL69UU'
        arr1['4'] = 'https://www.youtube.com/watch?v=MKLNGSxF_qQ'
        arr1['5'] = 'https://www.youtube.com/watch?v=Zx8z4rYulpg'

        random_number = random.randint(1, 5)
        ind = str(random_number)
        bot.send_message(call.message.chat.id, emoji.emojize(':ninja:'))
        bot.send_message(call.message.chat.id, f"{arr1[ind]}")

    elif call.data == 'gym':
        arr1['1'] = 'https://www.youtube.com/shorts/B2eLuxXtRKA'
        arr1['2'] = 'https://www.youtube.com/shorts/KBGYSiQyaS8'
        arr1['3'] = 'https://www.youtube.com/shorts/-WM5xi5eb78'
        arr1['4'] = 'https://www.youtube.com/shorts/OQ1kCxC9IRQ'
        arr1['5'] = 'https://www.youtube.com/shorts/yYBwbS98ATI'

        random_number = random.randint(1, 5)
        ind = str(random_number)
        bot.send_message(call.message.chat.id, emoji.emojize(':basketball:'))
        bot.send_message(call.message.chat.id, f"{arr1[ind]}")

    elif call.data == 'other':
        arr1['1'] = 'https://www.youtube.com/watch?v=oPj8U65R24g'
        arr1['2'] = 'https://www.youtube.com/watch?v=6PeddQQj728'
        arr1['3'] = 'https://www.youtube.com/watch?v=KZ4ug9CSv7M'
        arr1['4'] = 'https://www.youtube.com/watch?v=---0oN1Kvo0'
        arr1['5'] = 'https://www.youtube.com/watch?v=H6iftfEPf7o'

        random_number = random.randint(1, 5)
        ind = str(random_number)
        bot.send_message(call.message.chat.id, emoji.emojize(':smiling_face:'))
        bot.send_message(call.message.chat.id, f"{arr1[ind]}")


#Хэндлер для обработки команды гиф
@bot.message_handler(commands=['gif'])
def giphy_search(message):
    slovar[message.chat.id] = '52'
    bot.send_message(message.chat.id, "Что бы вы хотели увидеть?")


@bot.message_handler(func=lambda message: True)
def search(message): #вывод гифки по текстовому запросу
    if message.chat.id in slovar:
        search_query = message.text
        giphy_response = requests.get(f"https://api.giphy.com/v1/gifs/search?api_key=Fzrn4803D5P4vd6348wNFpfPxfSrUped&q={search_query}&limit=1")
        gif_url = giphy_response.json()['data'][0]['images']['original']['url']
        bot.send_document(message.chat.id, gif_url)
        del slovar[message.chat.id]


bot.polling(none_stop=True)