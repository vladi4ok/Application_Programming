from locale import currency

from model import Session, User, Account, Transfer
session = Session()
user1 = User(UserName = 'ivanenko_ivan', firstName='Ivan', lastName='Ivanenko', email='exampl1@gmail.com',
            phone='+380999977777', password='123456789')
user2 = User(UserName = 'shcherbii_ostap', firstName='Ostap', lastName='Shcherbii', email='exampl@gmail.com',
            phone='+380957777777', password='12345678')
user3 = User(UserName = 'user_name', firstName='name', lastName='user', email='exampl3@gmail.com',
            phone='+380922777777', password='754615')


Account1 = Account(balance = 1500, currencyCode = 'UAH', UserName = 'shcherbii_ostap')
Account2 = Account(balance = 1000, currencyCode = 'UAH', UserName = 'ivanenko_ivan')
Account3 = Account(balance = 2000, currencyCode = 'UAH', UserName = 'user_name')

Transfer1 = Transfer(amount = 50, currencyCode = 'UAH', fromAccountNumber = 1, toAccountNumber = 2)
Transfer2 = Transfer(amount = 500, currencyCode = 'UAH', fromAccountNumber = 3, toAccountNumber = 1)

session.add(user1)
session.add(user2)
session.add(user3)
session.commit()
session.add(Account1)
session.commit()
session.add(Account2)
session.add(Account3)

session.add(Transfer1)
session.add(Transfer2)

session.commit()

print(session.query(User).all())
print(session.query(Account).all())
print(session.query(Transfer).all())

session.close()