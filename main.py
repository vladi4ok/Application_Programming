from flask import Flask, jsonify, request, make_response
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import db_utils
from model import *
import bcrypt
from constants import *
from decimal import Decimal
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/money_transfer'

ma = Marshmallow(app)


class UserSchema(Schema):
    class Meta:
        model = User
        fields = ('UserName', 'firstName', 'lastName', 'email', 'phone', 'password')


class AccountSchema(Schema):
    class Meta:
        model = Account
        fields = ('AccountNumber', 'balance', 'currencyCode', 'UserName')


class TransferSchema(Schema):
    class Meta:
        model = Transfer
        fields = ('idTransfer', 'amount', 'currencyCode', 'fromAccountNumber', 'toAccountNumber')


@app.route(BASE_PATH + '/hello-world-1')
def hello_world():
    return "<p>Hello World 1</p>"


# Lab-8
auth = HTTPBasicAuth()


@auth.verify_password
def user_auth(username, password):
    session = Session()
    try:
        user = session.query(User).filter_by(UserName=username).one()
    except:
        return jsonify(BAD_USERNAME), 404
    if bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8')):
        return username, 200
    else:
        return jsonify(BAD_PASSWORD), 401


# USER

@app.route(BASE_PATH + USER_PATH + '/<UserName>', methods=['GET'])
def get_user_by_nick(UserName):
    try:
        user = db_utils.get_user(User, UserName)
    except:
        return jsonify(USER_NOT_FOUND), 404

    return jsonify({'user': UserSchema().dump(user)})


@app.route(BASE_PATH + USER_PATH, methods=['POST'])
def create_user():
    try:
        user_data = UserSchema().load(request.json)
        try:
            if db_utils.get_user(User, user_data.get('UserName')):
                return jsonify(USER_ALREADY_EXISTS), 409
        except:
            pass
        # password hashing ------------------------------------
        passwd = user_data.get('password')
        b = bytes(passwd, 'utf-8')
        hashed_password = bcrypt.hashpw(b, bcrypt.gensalt())
        user_data['password'] = hashed_password
        # -----------------------------------------------------
        db_utils.create_entry(User, **user_data)
        return jsonify(USER_CREATED), 201
    except:
        return jsonify(SOMETHING_WENT_WRONG), 400


@app.route(BASE_PATH + USER_PATH + '/<UserName>', methods=['DELETE'])
@auth.login_required
def delete_user_by_nick(UserName):
    auth_rez = auth.current_user()
    if auth_rez[1] != 200:
        return auth_rez

    if auth_rez[0] != UserName:
        return jsonify(ACCESS_DENIED), 403

    try:
        db_utils.get_user(User, UserName)
    except:
        return jsonify(USER_NOT_FOUND), 404

    db_utils.delete_user(User, UserName)
    return jsonify(USER_DELETED), 200


@app.route(BASE_PATH + USER_PATH + '/<UserName>', methods=['PUT'])
@auth.login_required
def update_user(UserName):
    auth_rez = auth.current_user()
    if auth_rez[1] != 200:
        return auth_rez

    if auth_rez[0] != UserName:
        return jsonify(ACCESS_DENIED), 403

    try:
        user_data = UserSchema().load(request.json, partial=True)
        if user_data.get('UserName'):
            return jsonify(CANT_CHANGE_ID), 400
    except:
        pass
    try:
        try:
            user = db_utils.get_user(User, UserName)
        except:
            return jsonify(USER_NOT_FOUND), 404

        if user_data.get('password'):
            # password hashing ------------------------------------
            passwd = user_data.get('password')
            b = bytes(passwd, 'utf-8')
            hashed_password = bcrypt.hashpw(b, bcrypt.gensalt())
            user_data['password'] = hashed_password
            # -----------------------------------------------------

        updated_user = db_utils.update_user(user, **user_data)

        if updated_user == None:
            return jsonify(SOMETHING_WENT_WRONG), 400

        return jsonify(USER_UPDATED), 200
    except:
        return jsonify(SOMETHING_WENT_WRONG), 400


# ACCOUNT
@app.route(BASE_PATH + ACCOUNT_PATH + '/<AccountNumber>', methods=['GET'])
@auth.login_required
def get_account_num(AccountNumber):
    auth_rez = auth.current_user()
    if auth_rez[1] != 200:
        return auth_rez

    try:
        account = db_utils.get_account(Account, AccountNumber)
    except:
        return jsonify(ACCOUNT_NOT_FOUND), 404

    if auth_rez[0] != account.UserName:
        return jsonify(ACCESS_DENIED), 403

    return jsonify({'account': AccountSchema().dump(account)})


@app.route(BASE_PATH + ACCOUNT_PATH + '/<AccountNumber>', methods=['DELETE'])
@auth.login_required
def delete_account_num(AccountNumber):
    auth_rez = auth.current_user()
    if auth_rez[1] != 200:
        return auth_rez

    try:
        account = db_utils.get_account(Account, AccountNumber)
    except:
        return jsonify(ACCOUNT_NOT_FOUND), 404

    if auth_rez[0] != account.UserName:
        return jsonify(ACCESS_DENIED), 403

    db_utils.delete_account(Account, AccountNumber)
    return jsonify(ACCOUNT_DELETED), 200


@app.route(BASE_PATH + ACCOUNT_PATH + '/<AccountNumber>', methods=['PUT'])
@auth.login_required
def update_account(AccountNumber):
    auth_rez = auth.current_user()
    if auth_rez[1] != 200:
        return auth_rez

    try:
        account_data = AccountSchema().load(request.json, partial=True)

        if not account_data:
            return jsonify(EMPTY_DATA), 400

        if account_data.get('AccountNumber'):
            return jsonify(CANT_CHANGE_NUMBER), 400
    except:
        pass
    try:
        if account_data.get('UserName'):
            return jsonify(CANT_CHANGE_ID), 400
    except:
        pass
    try:
        try:
            account = db_utils.get_account(Account, AccountNumber)
        except:
            return jsonify(ACCOUNT_NOT_FOUND), 404

        if auth_rez[0] != account.UserName:
            return jsonify(ACCESS_DENIED), 403

        db_utils.update_account(account, **account_data)

        return jsonify(ACCOUNT_UPDATED), 200
    except:
        return jsonify(SOMETHING_WENT_WRONG), 400


@app.route(BASE_PATH + ACCOUNT_PATH, methods=['POST'])
@auth.login_required
def create_account():
    auth_rez = auth.current_user()
    if auth_rez[1] != 200:
        return auth_rez
    if auth_rez[0] != request.json['UserName']:
        return jsonify(ACCESS_DENIED), 403

    try:
        account_data = AccountSchema().load(request.json)
        try:
            if db_utils.get_account(Account, account_data.get('AccountNumber')):
                return jsonify(ACCOUNT_ALREADY_EXISTS), 409
        except:
            pass
        db_utils.create_entry(Account, **account_data)
        return jsonify(ACCOUNT_CREATED), 201
    except:
        return jsonify(SOMETHING_WENT_WRONG), 400


# TRANSFER
@app.route(BASE_PATH + TRANSFER_PATH, methods=['POST'])
@auth.login_required
def create_transfer():
    auth_rez = auth.current_user()
    if auth_rez[1] != 200:
        return auth_rez

    transfer_data = TransferSchema().load(request.json)
    try:
        if db_utils.get_transfer(Transfer, transfer_data.get('idTransfer')):
            return jsonify(TRANSFER_ALREADY_EXISTS), 409
    except:
        pass

    session = Session()
    try:
        acc = session.query(Account).filter_by(AccountNumber=transfer_data.get('fromAccountNumber')).one()
        if auth_rez[0] != acc.UserName:
            return jsonify(ACCESS_DENIED), 403
    except:
        pass

    try:
        if transfer_data.get('fromAccountNumber') == transfer_data.get('toAccountNumber'):
            return jsonify(TRANSFER_USER_DUBLICATION), 400
    except:
        pass
    try:
        sender = db_utils.get_account(Account, transfer_data.get('fromAccountNumber'))
        sender_dict = AccountSchema().dump(sender)
        if transfer_data.get('amount') > sender_dict.get('balance'):
            return jsonify(TRANSFER_FAIL), 400
    except:
        pass

    fromAcc = db_utils.get_account(Account, transfer_data.get('fromAccountNumber'))
    amount = transfer_data.get('amount')
    fromAcc_dict = AccountSchema().dump(fromAcc)
    fromAccBalance = fromAcc_dict.get('balance')
    number_with_commas = Decimal(format(Decimal(fromAccBalance) - Decimal(amount), '.2f'))

    dataFrom = {"balance": number_with_commas}

    db_utils.update_account(fromAcc, **dataFrom)

    toAcc = db_utils.get_account(Account, transfer_data.get('toAccountNumber'))

    toAcc_dict = AccountSchema().dump(toAcc)
    toAccBalance = toAcc_dict.get('balance')
    number_with_commas_to = Decimal(format(Decimal(toAccBalance) + Decimal(amount), '.2f'))

    dataTo = {"balance": number_with_commas_to}

    db_utils.update_account(toAcc, **dataTo)

    db_utils.create_entry(Transfer, **transfer_data)

    return jsonify(TRANSFER_CREATED), 201


@app.route(BASE_PATH + TRANSFER_PATH + '/<idTransfer>', methods=['GET'])
def get_transfer(idTransfer):
    try:
        transfer = db_utils.get_transfer(Transfer, idTransfer)
    except:
        return jsonify(TRANSFER_NOT_FOUND), 404

    return jsonify({'transfer': TransferSchema().dump(transfer)})


if __name__ == '__main__':
    app.run()

# waitress-serve --host 127.0.0.1 --port=5000 --call "main:create_app"
# http://127.0.0.1:5000/api/v1/hello-world-1
# venv\Scripts\activate
# curl -v -XGET http://localhost:5000/api/v1/hello-world-1

# http://127.0.0.1:5000/api/v1/user/shcherbii_ostap
# http://127.0.0.1:5000/api/v1/user/ivanenko_ivan
# http://127.0.0.1:5000/api/v1/user/user_name

# POSTED: (UserName,email,phone -> unique)
# {"UserName":"vikusia","email":"vikal3@gmail.com","firstName":"Vika","lastName":"Mood","password":"12345","phone":"+380931040257"}
# {"UserName":"yura","email":"yura3@gmail.com","firstName":"Yura","lastName":"Yanio","password":"123j45","phone":"+380931048257"}
# {"UserName":"yura2","email":"yura2003@gmail.com","firstName":"Yura","lastName":"Yanio","password":"123j45","phone":"+380931048258"}
# {"UserName": "ivanko","email": "ivik2003@gmail.com","firstName": "Ivan","lastName": "Solomchak","password": "92j3j45","phone": "+380931048259"}
