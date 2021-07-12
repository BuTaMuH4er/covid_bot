from take_vacine import add_user_db, remove_user_db, take_vaccine_db, take_data_message, write_vaccine_db
from models import User

#a = add_user_db('222', 'names')
vaccines = take_data_message()
from_db_vac = take_vaccine_db()
if vaccines == from_db_vac:
    print('ку-ку епта')
else:
    print('бяда')