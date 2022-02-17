from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    ForeignKey,
)

from sqlalchemy import orm, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:root@localhost:3306/money_transfer"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionFactory = sessionmaker(bind=engine)

Session = scoped_session(SessionFactory)

Base = declarative_base()


class User(Base):
    __tablename__ = "User"

    UserName = Column(String(length=45), primary_key=True, unique=True)
    firstName = Column(String(length=45), nullable=False)
    lastName = Column(String(length=45), nullable=False)
    email = Column(String(length=45), nullable=False, unique=True)
    phone = Column(String(length=45), nullable=False, unique=True)
    password = Column(String(length=100), nullable=False)

    # to implement cascade deleting
    # account = relationship("Account", cascade="all,delete", backref="user")

    def __str__(self):
        return f"User ID : {self.UserName}\n" \
               f"firstName : {self.firstName}\n" \
               f"lastName : {self.lastName}\n" \
               f"email : {self.email}\n" \
               f"phone : {self.phone}\n" \
               f"password : {self.password}\n"


class Account(Base):
    __tablename__ = "Account"

    AccountNumber = Column(Integer, primary_key=True, unique=True)
    balance = Column(DECIMAL(10, 2), nullable=False)
    currencyCode = Column(String(length=45), nullable=False)
    UserName = Column(String(length=45), ForeignKey("User.UserName"), nullable=False)

    user = relationship("User")


class Transfer(Base):
    __tablename__ = "Transfer"
    idTransfer = Column(Integer, primary_key=True, unique=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currencyCode = Column(String(length=45), nullable=False)
    fromAccountNumber = Column(Integer, ForeignKey("Account.AccountNumber"), nullable=False)
    toAccountNumber = Column(Integer, ForeignKey("Account.AccountNumber"), nullable=False)

    # добавив on delete щоб реалізувати каскадне видалення (вирішив зробити через тригери)
    # fromAccountNumber = Column(Integer, ForeignKey("Account.AccountNumber", ondelete='CASCADE'), nullable=False)
    # toAccountNumber = Column(Integer, ForeignKey("Account.AccountNumber", ondelete='CASCADE'), nullable=False)

    # Account = orm.relationship("Account")
    Account = orm.relationship("Account", foreign_keys=[fromAccountNumber])
    Account = orm.relationship("Account", foreign_keys=[toAccountNumber])
