from config import API_KEY_BOT
from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import csv, logging, telegram.bot
from datetime import datetime
from take_vacine import take_data_message, write_or_not, take_vaccine_db, add_user_db, remove_user_db, distribution_list, del_distribution_list
from celery import Celery
from celery.schedules import crontab
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request

celery_app = Celery('covid_tasks', broker='redis://localhost:6379/0')
logging.basicConfig(filename='bot.log', level=logging.INFO)

class MQBot(telegram.bot.Bot):
    def __init__(self, *args, is_queued_def=True, msq_queue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = msq_queue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        return super(MQBot, self).send_message(*args, **kwargs)


def main():
    request = Request(con_pool_size=8)
    bot = MQBot(API_KEY_BOT, request=request)
    mybot = Updater(bot=bot, use_context=True)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', start_bot, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.regex('^Да$'), add_user))
    dp.add_handler(MessageHandler(Filters.regex('^Нет$'), remove_user))
    dp.add_handler(MessageHandler(Filters.regex('^Есть чо'), send_data_vaccine))
    time_now = datetime.today().strftime("%H:%M:%S  %d/%m/%Y")
    logging.info(f'{time_now} Бот стартовал')
    mybot.start_polling()
    mybot.idle()


def read_list_users():
    users_chat_id = set()
    try:
        with open('users.csv', 'r') as file:
            for line in file.readlines():
                users_chat_id.add(line.strip())
    except FileNotFoundError:
        return users_chat_id
    return users_chat_id


def write_user_chat_id(user_chat_id=None):
    users_chat_id = list(read_list_users())
    if (str(user_chat_id) not in users_chat_id) and user_chat_id != None:
        users_chat_id.append(user_chat_id)
        with open('users.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerows(map(lambda x: [x], set(users_chat_id)))
            return read_list_users()


def wait_please(update, context):
    update.message.reply_text(f'Ожидайте обновления информации. Либо актуальная онлайн информация по нажатию конпки "Есть чо?"')


def start_bot(update, context):
    keyboard = [['Да', 'Нет', 'Есть чо?']]
    buttons = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(f'Привет! Хочешь узнать про наличие вакцины в Москве?', reply_markup=buttons)


def add_user(update, context):
    chat_id = str(update.message.chat.id)
    username = update.message.chat.username
    add_user = add_user_db(chat_id, username)
    if add_user == True:
        return update.message.reply_text(f'Вы уже есть в списке. Сообщение о наличии вакцины будет после обновления. \n'
                                  f'Актуальная информация с сайта mos.ru по нажатию кнопки "Есть чо?"')
    else:
        update.message.reply_text(f'Вы добавлены в список рассылки. В случае обновления информации я вас проинформирую. \n'
                              f'Актуальная информация с сайта mos.ru по нажатию кнопки "Есть чо?"')


def remove_user(update, context):
    update.message.reply_text(f'Тогда помочь вам нечем. Если вы были в списке рассылки, то больше я вас не побеспокою.')
    chat_id = str(update.message.chat.id)
    remove_user_db(chat_id)


def send_data_vaccine(update, context):
    vaccines = take_data_message()
    for key, val in vaccines.items():
        update.message.reply_text(f'<b>{key}</b>:\n{val}', parse_mode=ParseMode.HTML)


@celery_app.task(bind=True)
def send_new_data_vaccine(context):

    request = Request(con_pool_size=8)
    bot = MQBot(API_KEY_BOT, request=request)
    mybot = Updater(bot=bot, use_context=True)
    dp = mybot.dispatcher

    ask_vaccine = write_or_not()
    chat_ids = distribution_list()
    if ask_vaccine or len(chat_ids) > 0:
        vaccines = take_vaccine_db()
        for men in chat_ids:
            for key, val in vaccines.items():
                dp.bot.send_message(chat_id=men, text=f'<b>{key}</b>:\n{val}', parse_mode=ParseMode.HTML)
            del_distribution_list(men)


@celery_app.on_after_configure.connect
def periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/10'), send_new_data_vaccine.s())

if __name__ == '__main__':
    main()
