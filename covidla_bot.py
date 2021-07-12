from config import API_KEY_BOT
from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import csv, logging, time
from datetime import datetime
from take_vacine import take_data_message, write_or_not, take_from_file, add_user_db, remove_user_db, distribution_list, del_distribution_list

logging.basicConfig(filename='bot.log', level=logging.INFO)


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


def send_new_data_vaccine(context):
    ask_vaccine = write_or_not()
    if ask_vaccine:
        vaccines = take_from_file()
        chat_ids = distribution_list()
        for men in chat_ids:
            for key, val in vaccines.items():
                dp.bot.send_message(chat_id=men, text=f'<b>{key}</b>:\n{val}', parse_mode=ParseMode.HTML)
            del_distribution_list(men)
            time.sleep(15) #пока сообщения будут так отправляться, необходимо написать класс для очереди сообщений


if __name__ == '__main__':

    mybot = Updater(API_KEY_BOT, use_context=True)
    dp = mybot.dispatcher

    jq = mybot.job_queue
    jq.run_repeating(send_new_data_vaccine, interval=1800)

    dp.add_handler(CommandHandler('start', start_bot, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.regex('^Да$'), add_user))
    dp.add_handler(MessageHandler(Filters.regex('^Нет$'), remove_user))
    dp.add_handler(MessageHandler(Filters.regex('^Есть чо'), send_data_vaccine))
    time_now = datetime.today().strftime("%H:%M:%S  %d/%m/%Y")
    logging.info(f'{time_now} Бот стартовал')
    mybot.start_polling()
    mybot.idle()
