from flask import Flask, jsonify, request, make_response
from flask_marshmallow import Marshmallow
import db_utils
from model import *
import bcrypt
from constants import *

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:sqlLp9lp@localhost:3306/baza_pp'

    ma = Marshmallow(app)

    class UserSchema(ma.SQLAlchemyAutoSchema):
        class Meta:
            model = User

    class AccountSchema(ma.SQLAlchemyAutoSchema):
        class Meta:
            model = Account
            fields = ('AccountNumber', 'balance', 'currencyCode', 'UserName')

    class TransferSchema(ma.SQLAlchemyAutoSchema):
        class Meta:
            model = Transfer
            fields = ('idTransfer', 'amount', 'currencyCode', 'fromAccountNumber', 'toAccountNumber')

    @app.route(BASE_PATH + '/hello-world-1')
    def hello_world():
        return "<p>Hello World 1</p>"

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
            except: pass
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
    def delete_user_by_nick(UserName):
        try:
              db_utils.get_user(User, UserName)
        except: return jsonify(USER_NOT_FOUND), 404

        db_utils.delete_user(User, UserName)
        return jsonify(USER_DELETED), 200

    @app.route(BASE_PATH + USER_PATH + '/<UserName>', methods=['PUT'])
    def update_user(UserName):
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
    def get_account_num(AccountNumber):
        try:
            account = db_utils.get_account(Account, AccountNumber)
        except:
            return jsonify(ACCOUNT_NOT_FOUND), 404

        return jsonify({'account': AccountSchema().dump(account)})

    @app.route(BASE_PATH + ACCOUNT_PATH + '/<AccountNumber>', methods=['DELETE'])
    def delete_account_num(AccountNumber):
        try:
            db_utils.get_account(Account, AccountNumber)
        except:
            return jsonify(ACCOUNT_NOT_FOUND), 404

        account = db_utils.delete_account(Account, AccountNumber)
        return jsonify(ACCOUNT_DELETED), 200

    @app.route(BASE_PATH + ACCOUNT_PATH + '/<AccountNumber>', methods=['PUT'])
    def update_account(AccountNumber):
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

            db_utils.update_account(account, **account_data)

            return jsonify(ACCOUNT_UPDATED), 200
        except:
            return jsonify(SOMETHING_WENT_WRONG), 400

    @app.route(BASE_PATH + ACCOUNT_PATH, methods=['POST'])
    def create_account():
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
    def create_transfer():
        try:
            transfer_data = TransferSchema().load(request.json)
            try:
                if db_utils.get_transfer(Transfer, transfer_data.get('idTransfer')):
                    return jsonify(TRANSFER_ALREADY_EXISTS), 409
            except:
                pass
            try:
                if transfer_data.get('fromAccountNumber') == transfer_data.get('toAccountNumber'):
                    return jsonify(TRANSFER_USER_DUBLICATION), 400
            except:
                pass
            try:
                sender = db_utils.get_account(Account,transfer_data.get('fromAccountNumber'))
                sender_dict = AccountSchema().dump(sender)
                if transfer_data.get('amount') > sender_dict.get('balance'):
                    return jsonify(TRANSFER_FAIL),400
            except:
                pass

            fromAcc = db_utils.get_account(Account, transfer_data.get('fromAccountNumber'))
            amount = transfer_data.get('amount')
            fromAcc_dict = AccountSchema().dump(fromAcc)
            fromAccBalance = fromAcc_dict.get('balance')
            number_with_commas = format(fromAccBalance - amount, '.2f')


            dataFrom = {"balance" : number_with_commas}

            db_utils.update_account(fromAcc, **dataFrom )

            toAcc = db_utils.get_account(Account, transfer_data.get('toAccountNumber'))

            toAcc_dict = AccountSchema().dump(toAcc)
            toAccBalance = toAcc_dict.get('balance')
            number_with_commas_to = format(toAccBalance + amount, '.2f')

            dataTo = {"balance" : number_with_commas_to}

            db_utils.update_account(toAcc, **dataTo)

            db_utils.create_entry(Transfer, **transfer_data)

            return jsonify(TRANSFER_CREATED), 201
        except:
            return jsonify(SOMETHING_WENT_WRONG), 400

    @app.route(BASE_PATH + TRANSFER_PATH + '/<idTransfer>', methods=['GET'])
    def get_transfer(idTransfer):
        try:
            transfer = db_utils.get_transfer(Transfer, idTransfer)
        except:
            return jsonify(TRANSFER_NOT_FOUND), 404

        return jsonify({'transfer': TransferSchema().dump(transfer)})

    return app

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