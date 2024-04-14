import time
import schedule
from bd import user

#настройка рассылки: изначально импортим БД в которой хранятся id пользователей, затем достаем id
def send_message1(bot):
    def send_rassl():
        qq = user['id']
        bot.send_message(qq, 'Настало время подвигаться! Выпейте стакан воды и проведите небольшую разминку!')

    schedule.every(60).minutes.do(send_rassl) #настраиваем таким образом, чтобы рассылка приходила каждый час

    while True:
        schedule.run_pending()
        time.sleep(1)