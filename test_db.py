from take_vacine import add_user_db, remove_user_db, distribution_list
from models import User

#a = add_user_db('222', 'names')
b = remove_user_db('111')
c = distribution_list()
print(type(c))
print(c)
for i in c:
    print(i)