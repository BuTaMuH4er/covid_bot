from lxml import html
from models import User, Vaccine
import requests
from db import db_session

def take_data_message():
    vaccines = dict()
    url = 'https://www.mos.ru/city/projects/covid-19/privivka/#!%2Ftab%2F316410519-2'
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 Firefox/85.0'}
    page = requests.get(url, headers=headers).text
    tree = html.fromstring(page)
    messages_vacine = tree.xpath('//div[@class = "t412"]//div[@class="t412__wrapper"]')
    for i in messages_vacine:
        str_full = i.text_content().strip()
        list_strings = str_full.split('\n')
        vaccines[list_strings[0].strip()] = list_strings[1].strip().capitalize().split('.')[0]
    return vaccines


def write_vaccines_data(vacc_dict):
    with open('vaccines_data.txt', 'w') as file:
        file.seek(0)
        for key,val in vacc_dict.items():
            file.write('{};{}\n'.format(key,val))


def take_from_file():
    vaccines = dict()
    with open('vaccines_data.txt', 'r') as file:
        for line in file.readlines():
            key,val = line.strip().split(';')
            vaccines[key] = val
    return vaccines


def write_or_not():
    vaccines_internet = take_data_message()
    vaccines_from_db = take_vaccine_db()
    if vaccines_internet != vaccines_from_db:
        write_vaccine_db(vaccines_internet)
        return True


def add_user_db(chat_id, name):
    find_user = User.query.filter_by(chat_id=chat_id).first()
    if find_user == None:
        new_user = User(chat_id=chat_id, name=name, subscribe=True, send_info=False)
        db_session.add(new_user)
        db_session.commit()
        return False
    #нужно добавить проверку есть ли подписка и тогда выдавать сообщение что пользователь снова подписан
    else:
        find_user.subscribe = True
        find_user.send_info = False
        db_session.commit()
        return True


def remove_user_db(chat_id):
    find_user = User.query.filter_by(chat_id=chat_id).first()
    find_user.subscribe = False
    db_session.commit()


def distribution_list():
    distribution_list = User.query.filter(User.send_info == False, User.subscribe == True).all()
    return [x.chat_id for x in distribution_list]


def del_distribution_list(chat_id):
    user_send_message = User.query.filter_by(chat_id=chat_id).first()
    user_send_message.send_info = True
    db_session.commit()


def take_vaccine_db():
    vaccines = dict()
    all_vaccines_db = Vaccine.query.all()
    for i in all_vaccines_db:
        vaccines[i.vaccine] = i.info_availability
    return vaccines


def write_vaccine_db(vaccines):
    for vaccine, info in vaccines.items():
        new_vaccine = Vaccine(vaccine=vaccine, info_availability=info)
        take_from_table = Vaccine.query.filter_by(vaccine=vaccine).first()
        if take_from_table != None:
            take_from_table.info_availability = info
        else:
            db_session.add(new_vaccine)
        db_session.commit()


