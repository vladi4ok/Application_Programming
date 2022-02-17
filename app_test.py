from unittest import TestCase, main
from unittest.mock import ANY

import sqlalchemy

from main import app
from constants import *
from model import User, Account, Transfer, Base, Session, engine
import db_utils
import bcrypt
import json
from flask import url_for
from base64 import b64encode

app.testing = True
client = app.test_client()


class MyTestCase(TestCase):
    client = app.test_client()

    def setUp(self):
        super().setUp()

        # User data
        self.user_1_data = {
            "email": "user1@gmail.com",
            "firstName": "Vlad",
            "lastName": "Diachyk",
            "password": "user1",
            "phone": "0880777899",
            "UserName": "user1"
        }

        self.user_1_data_hashed = {
            **self.user_1_data,
            "password": bcrypt.hashpw(bytes(self.user_1_data['password'], 'utf-8'), bcrypt.gensalt())
        }

        self.user_1_credentials = b64encode(b"user1:user1").decode('utf-8')

        self.user_2_data = {
            "email": "user2@gmail.com",
            "firstName": "Bob",
            "lastName": "Marlin",
            "password": "user2",
            "phone": "0980722899",
            "UserName": "user2"
        }

        self.user_2_data_hashed = {
            **self.user_2_data,
            "password": bcrypt.hashpw(bytes(self.user_2_data['password'], 'utf-8'), bcrypt.gensalt())
        }

        self.user_2_credentials = b64encode(b"user2:user2").decode('utf-8')

        # Account data
        self.account_1_data = {
            "AccountNumber": 1,
            "balance": 1000,
            "currencyCode": 'UAH',
            "UserName": 'user1'
        }

        self.account_2_data = {
            "AccountNumber": 2,
            "balance": 1000,
            "currencyCode": 'UAH',
            "UserName": 'user2'
        }

        # Transfer data
        self.transfer_1_data = {
            "idTransfer": 1,
            "amount": 100,
            "currencyCode": 'UAH',
            "fromAccountNumber": 1,
            "toAccountNumber": 2
        }

        self.transfer_2_data = {
            "idTransfer": 2,
            "amount": 200,
            "currencyCode": 'UAH',
            "fromAccountNumber": 2,
            "toAccountNumber": 1
        }

    def tearDown(self):
        self.close_session()

    def close_session(self):
        Session.close()

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def get_auth_headers(self, credentials):
        return {"Authorization": f"Basic {credentials}"}

    # Methods for the database
    def clear_user_db(self):
        engine.execute('SET FOREIGN_KEY_CHECKS=0;')
        engine.execute('delete from user;')

    def clear_account_db(self):
        engine.execute('SET FOREIGN_KEY_CHECKS=0;')
        engine.execute('delete from account;')

    def clear_transfer_db(self):
        engine.execute('SET FOREIGN_KEY_CHECKS=0;')
        engine.execute('delete from transfer;')

    def create_all_users(self):
        self.client.post('api/v1/user', json=self.user_1_data)
        self.client.post('api/v1/user', json=self.user_2_data)

    def create_all_accounts(self):
        self.client.post('api/v1/account', json=self.account_1_data,
                         headers=self.get_auth_headers(self.user_1_credentials))
        self.client.post('api/v1/account', json=self.account_2_data,
                         headers=self.get_auth_headers(self.user_2_credentials))

    def create_all_transfers(self):
        self.client.post('api/v1/transfer', json=self.transfer_1_data,
                         headers=self.get_auth_headers(self.user_1_credentials))
        self.client.post('api/v1/transfer', json=self.transfer_2_data,
                         headers=self.get_auth_headers(self.user_2_credentials))


class TestUser(MyTestCase):
    def test_create_user_1(self):
        self.clear_user_db()
        response = self.client.post('api/v1/user', json=self.user_1_data)
        self.assertEqual(response.status_code, 201)

    def test_create_not_unique_user(self):
        self.clear_user_db()
        self.client.post('api/v1/user', json=self.user_1_data)
        response = self.client.post('api/v1/user', json=self.user_1_data)
        self.assertEqual(response.status_code, 409)

    def test_get_user_by_nick(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.get('api/v1/user/user1', headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'user':
            {
                "UserName": "user1",
                "email": "user1@gmail.com",
                "firstName": "Vlad",
                "lastName": "Diachyk",
                "password": ANY,
                "phone": "0880777899"
            }})

    def test_get_user_by_not_existing_nick(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.get('api/v1/user/user3', headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 404)

    def test_get_user_by_id_access_denied(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.get('api/v1/user/user1', headers=self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(response.status_code, 403)

    def test_update_user(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.put('api/v1/user/user1', data=json.dumps({
            "email": "new@gmail.com",
            "firstName": "Vladww",
            "lastName": "Diachykww",
            "password": "userwww",
            "phone": "02777899"
        }),
                                   content_type='application/json',
                                   headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 200)

    def test_update_user_id(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.put('api/v1/user/user1', data=json.dumps({"UserName": 'user22'}),
                                   content_type='application/json',
                                   headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 400)

    def test_update_user_access_denied(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.put('api/v1/user/user1', data=json.dumps({"email": "yura90@gmail.com"}),
                                   content_type='application/json',
                                   headers=self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(response.status_code, 403)

    def test_delete_user(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.delete('api/v1/user/user1', headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 200)

    def test_delete_user_access_denied(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.delete('api/v1/user/user1', headers=self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(response.status_code, 403)


class TestAccount(MyTestCase):
    def test_create_account(self):
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        response = self.client.post('api/v1/account', json=self.account_1_data,
                                    headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 201)

    def test_create_existing_account(self):
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()
        response = self.client.post('api/v1/account', json=self.account_1_data,
                                    headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 409)

    def test_create_account_access_denied(self):
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        response = self.client.post('api/v1/account', json=self.account_1_data,
                                    headers=self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(response.status_code, 403)

    def test_delete_account(self):
        self.clear_account_db()
        self.create_all_accounts()

        response = self.client.delete('api/v1/account/1',
                                      headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 200)

    def test_delete_account_access_denied(self):
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()

        response = self.client.delete('api/v1/account/1',
                                      headers=self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(response.status_code, 403)

    def test_delete_not_existing_account(self):
        self.clear_account_db()
        self.create_all_accounts()

        response = self.client.delete('api/v1/account/0',
                                      headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 404)

    def test_update_account(self):
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()

        response = self.client.put('api/v1/account/1', data=json.dumps({
            "balance": 1000,
            "currencyCode": 'UAH'
        }),
                                   content_type='application/json',
                                   headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 200)

    def test_update_account_id(self):
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()

        response = self.client.put('api/v1/account/1', data=json.dumps({"AccountNumber": 11}),
                                   content_type='application/json',
                                   headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 400)

    def test_update_account_access_denied(self):
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()

        response = self.client.put('api/v1/account/1', data=json.dumps({"currencyCode": "USD"}),
                                   content_type='application/json',
                                   headers=self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(response.status_code, 403)


class TestTransfer(MyTestCase):
    def test_create_transfer(self):
        self.clear_transfer_db()
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()

        response = self.client.post('api/v1/transfer', json=self.transfer_1_data,
                                    headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 201)

    def test_create_not_unique_transfer(self):
        self.clear_transfer_db()
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()
        self.create_all_transfers()

        response = self.client.post('api/v1/transfer', json=self.transfer_1_data,
                                    headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 409)

    def test_create_transfer_access_denied(self):
        self.clear_transfer_db()
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()

        response = self.client.post('api/v1/transfer', json=self.transfer_1_data,
                                    headers=self.get_auth_headers(self.user_2_credentials))
        self.assertEqual(response.status_code, 403)

    def test_create_transfer_not_enough_balance(self):
        self.clear_transfer_db()
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()

        response = self.client.post('api/v1/transfer', data=json.dumps({
            "idTransfer": 3,
            "amount": 3000,
            "currencyCode": 'UAH',
            "fromAccountNumber": 1,
            "toAccountNumber": 2
        }),
                                    content_type='application/json',
                                    headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 400)

    def test_create_transfer_user_duplication(self):
        self.clear_transfer_db()
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()

        response = self.client.post('api/v1/transfer', data=json.dumps({
            "idTransfer": 3,
            "amount": 100,
            "currencyCode": 'UAH',
            "fromAccountNumber": 1,
            "toAccountNumber": 1
        }),
                                    content_type='application/json',
                                    headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 400)

    def test_get_transfer_by_id(self):
        self.clear_transfer_db()
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()
        self.create_all_transfers()

        response = self.client.get('api/v1/transfer/1',
                                   headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 200)

    def test_get_transfer_by_not_existing_id(self):
        self.clear_transfer_db()
        self.clear_account_db()
        self.clear_user_db()
        self.create_all_users()
        self.create_all_accounts()
        self.create_all_transfers()

        response = self.client.get('api/v1/transfer/4',
                                   headers=self.get_auth_headers(self.user_1_credentials))
        self.assertEqual(response.status_code, 404)


class TestAuth(MyTestCase):
    def test_get_user_by_id_with_wrong_username(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.get('api/v1/user/1',
                                   headers=self.get_auth_headers(b64encode(b"adwqddqw:user1").decode('utf-8')))
        self.assertEqual(response.status_code, 404)

    def test_get_user_by_id_with_wrong_password(self):
        self.clear_user_db()
        self.create_all_users()

        response = self.client.get('api/v1/user/1',
                                   headers=self.get_auth_headers(b64encode(b"user1:adcqwcqc").decode('utf-8')))
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    main()
