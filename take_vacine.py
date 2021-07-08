from lxml import html
import requests

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
    vaccines_from_file = take_from_file()
    if vaccines_internet != vaccines_from_file:
        write_vaccines_data(vaccines_internet)
        return True

