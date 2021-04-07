from flask import jsonify, Blueprint, abort, Response
from flask_restful import Resource, Api, reqparse, fields
from flask_jwt_extended import (
                                create_access_token, create_refresh_token, 
                                get_jwt_identity, jwt_required
                                )
from hashlib import md5

from uuid import uuid4
from datetime import datetime
# from pymongo import MongoClient
import json

import pymongo
from settings import db, mongo
from resources import config
# import models
# db.users.create_index([('user_id', pymongo.ASCENDING),('phone_number', pymongo.ASCENDING)],unique=True)
db.users.create_index([('phone_number', pymongo.ASCENDING)],unique=True)


class TransactionBase(Resource):
    def __init__(self):
        #init field for input
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'amount',
            required = True,
            type = int,
            help     = 'amount required and must be integer',
            location = ['form', 'json']
        )
        self.reqparse.add_argument('remarks', required = False,location = ['form', 'json'])
        self.reqparse.add_argument('target_user', required = False,location = ['form', 'json'])
        super().__init__()

class TransactionTopUp(TransactionBase):
    @jwt_required
    def post(self):
        # print('topup')
        dataUser = db.users.find_one({'phone_number':get_jwt_identity()})

        args = self.reqparse.parse_args()
        #set up data top-up transaction
        dataTransaction = {
            '_id' : str(uuid4()),
            'top_up_id': str(uuid4()),
            'status': "SUCCESS",
            'user_id': dataUser['_id'],
            'transaction_type': 'CREDIT',
            'amount': args.get('amount') or None,
            'remarks': args.get('remarks') or '',
        }
        dataTransaction['balance_before'] = int(dataUser['balance'])
        dataTransaction['balance_after'] = int(dataUser['balance']) + int(dataTransaction['amount'])
        dataTransaction['created_date'] = datetime.now()

        #set up data user before and after for rollback operation
        dataUserBefore = {'balance': dataUser['balance']}
        dataUserUpdate = {'balance': dataTransaction['balance_after']}
        
        #do top-up transaction
        try:
            try:
                dbTransaction = db.transactions.insert_one(dataTransaction)
                dbUser = db.users.update_one({"phone_number": get_jwt_identity()},
                                    {"$set": dataUserUpdate})
            #rollback if fail
            except Exception as e:
                dbTransaction = db.transactions.delete_one({"top_up_id":dataTransaction['top_up_id']})
                dbUser = db.users.update_one({"phone_number": get_jwt_identity()},
                                    {"$set": dataUserBefore})

            dataTransactionCek = db.transactions.find_one({'top_up_id':dataTransaction['top_up_id']}) or None
            #validation for top-up transaction -->success
            if dataTransactionCek:
                dataOutput =  {"message":"SUCCESS", 
                    "result":{
                        "top_up_id":f"{dataTransactionCek['top_up_id']}",
                        "amount_top_up":f"{dataTransactionCek['amount']}",
                        "balance_before":f"{dataTransactionCek['balance_before']}",
                        "balance_after":f"{dataTransactionCek['balance_after']}",
                        "created_date":f"{dataTransactionCek['created_date']}",
                        }
                    }
                return config.responseJson(dataOutput,201)
            else: #-->fail
                dataOutput ={'message':"Transaction top-up gagal, silahkan coba beberapa saat lagi"}
                return config.responseJson(dataOutput,400)

        except Exception as e:
            print('error',e)
            dataOutput ={'message':e}
            return config.responseJson(dataOutput,400)

class TransactionPayment(TransactionBase):
    def __init__(self):
        super().__init__()
        #override field remarks -->  required
        self.reqparse.replace_argument('remarks', required=True,type=str, location = ['form', 'json'])
        
    @jwt_required
    def post(self):
        # print('payment')
        dataUser = db.users.find_one({'phone_number':get_jwt_identity()})

        args = self.reqparse.parse_args()
        #set up data payment transaction
        dataTransaction = {
            '_id' : str(uuid4()),
            'payment_id': str(uuid4()),
            'status': "SUCCESS",
            'user_id': dataUser['_id'],
            'transaction_type': 'DEBIT',
            'amount': args.get('amount') or None,
            'remarks': args.get('remarks') or '',
        }
        dataTransaction['balance_before'] = int(dataUser['balance'])
        dataTransaction['balance_after'] =  int(dataUser['balance']) - int(dataTransaction['amount'])  
        dataTransaction['created_date'] = datetime.now()

        if  dataTransaction['balance_after'] < 0:
            dataOutput ={'message':"Balance is not enough"}
            return config.responseJson(dataOutput,400)

        #set up data user before and after for rollback operation
        dataUserBefore = {'balance': dataUser['balance']}
        dataUserUpdate = {'balance': dataTransaction['balance_after']}
        
        #do payment transaction
        try:
            try:
                dbTransaction = db.transactions.insert_one(dataTransaction)
                dbUser = db.users.update_one({"phone_number": get_jwt_identity()},
                                    {"$set": dataUserUpdate})
            #rollback if fail
            except Exception as e:
                dbTransaction = db.transactions.delete_one({"payment_id":dataTransaction['payment_id']})
                dbUser = db.users.update_one({"phone_number": get_jwt_identity()},
                                    {"$set": dataUserBefore})

            dataTransactionCek = db.transactions.find_one({'payment_id':dataTransaction['payment_id']}) or None
            #validation for payment transaction -->success
            if dataTransactionCek:
                dataOutput =  {"message":"SUCCESS", 
                    "result":{
                        "payment_id":f"{dataTransactionCek['payment_id']}",
                        "amount":f"{dataTransactionCek['amount']}",
                        "remarks":f"{dataTransactionCek['remarks']}",
                        "balance_before":f"{dataTransactionCek['balance_before']}",
                        "balance_after":f"{dataTransactionCek['balance_after']}",
                        "created_date":f"{dataTransactionCek['created_date']}",
                        }
                    }
                return config.responseJson(dataOutput,201)
            else: #-->fail
                dataOutput ={'message':"Transaction payment gagal, silahkan coba beberapa saat lagi"}
                return config.responseJson(dataOutput,400)

        except Exception as e:
            print('error',e)
            dataOutput ={'message':e}
            return config.responseJson(dataOutput,400)

class TransactionTransfer(TransactionBase):
    def __init__(self):
        super().__init__()
        #override field remarks -->  required
        self.reqparse.replace_argument('remarks', required=True,type=str, location = ['form', 'json'])
        self.reqparse.replace_argument('target_user', required=True,type=str, location = ['form', 'json'])
        
    @jwt_required
    def post(self):
        # print('transfer')
        args = self.reqparse.parse_args()
        dataUser = db.users.find_one({'phone_number':get_jwt_identity()})
        
        dataUserTarget = db.users.find_one({'_id': args.get('target_user')}) or None
        if dataUserTarget == None:
            dataOutput ={'message':"Target User not registered, please fill correctly"}
            return config.responseJson(dataOutput,400)

        #set up data transfer transaction
        dataTransaction = {
            '_id' : str(uuid4()),
            'transfer_id': str(uuid4()),
            'status': "SUCCESS",
            'user_id': dataUser['_id'],
            'target_user': dataUserTarget['_id'],
            'transaction_type': 'DEBIT',
            'amount': args.get('amount') or None,
            'remarks': args.get('remarks') or '',
        }
        dataTransaction['balance_before'] = int(dataUser['balance'])
        dataTransaction['balance_after'] =  int(dataUser['balance']) - int(dataTransaction['amount']) 
        dataTransaction['created_date'] = datetime.now()

        if  dataTransaction['balance_after'] < 0:
            dataOutput ={'message':"Balance is not enough"}
            return config.responseJson(dataOutput,400)

        #set up data user before and after for rollback operation
        dataUserBefore = {'balance': dataUser['balance']}
        dataUserUpdate = {'balance': dataTransaction['balance_after']}

        #set up data user target before and after for rollback operation
        dataUserTargetBefore = {'balance': dataUserTarget['balance']}
        dataUserTargetUpdate = {'balance': int(dataUserTarget['balance']) + int(dataTransaction['amount']) }
        
        #do transfer transaction
        try:
            try:
                dbTransaction = db.transactions.insert_one(dataTransaction)
                dbUser = db.users.update_one({"phone_number": get_jwt_identity()},{"$set": dataUserUpdate})
                dbUserTarget = db.users.update_one({"_id": dataUserTarget['_id']}, {"$set": dataUserTargetUpdate})
            #rollback if fail
            except Exception as e:
                dbTransaction = db.transactions.delete_one({"transfer_id":dataTransaction['transfer_id']})
                dbUser = db.users.update_one({"phone_number": get_jwt_identity()}, {"$set": dataUserBefore})
                dbUserTarget = db.users.update_one({"_id": dataUserTarget['_id']},  {"$set": dataUserTargetBefore})

            dataTransactionCek = db.transactions.find_one({'transfer_id':dataTransaction['transfer_id']}) or None
            #validation for transfer transaction -->success
            if dataTransactionCek:
                dataOutput =  {"message":"SUCCESS", 
                    "result":{
                        "transfer_id":f"{dataTransactionCek['transfer_id']}",
                        "amount":f"{dataTransactionCek['amount']}",
                        "remarks":f"{dataTransactionCek['remarks']}",
                        "balance_before":f"{dataTransactionCek['balance_before']}",
                        "balance_after":f"{dataTransactionCek['balance_after']}",
                        "created_date":f"{dataTransactionCek['created_date']}",
                        }
                    }
                return config.responseJson(dataOutput,201)
            else: #-->fail
                dataOutput ={'message':"Transaction transfer gagal, silahkan coba beberapa saat lagi"}
                return config.responseJson(dataOutput,400)

        except Exception as e:
            print('error',e)
            dataOutput ={'message':e}
            return config.responseJson(dataOutput,400)

class TransactionHistory(TransactionBase):
    @jwt_required
    def get(self):
        # print('transactions')
        try:
            dataUser = db.users.find_one({'phone_number':get_jwt_identity()})
            dataTransactionList = db.transactions.find({'user_id':dataUser['_id']}) or None
            # validation for transaction history user-->success
            if dataTransactionList:
                #extract transaction list data history
                list_result = []
                for dataTransaction in dataTransactionList:
                    # print(dataTransaction)
                    data = {}
                    if "top_up_id" in dataTransaction : data['top_up_id'] = dataTransaction['top_up_id']
                    elif "payment_id" in dataTransaction : data['payment_id'] = dataTransaction['payment_id']
                    elif "transfer_id" in dataTransaction : data['transfer_id'] = dataTransaction['transfer_id']
                    data['status'] = dataTransaction['status']
                    data['user_id'] = dataTransaction['user_id']
                    data['transaction_type'] = dataTransaction['transaction_type']
                    data['amount'] = dataTransaction['amount']
                    data['remarks'] = dataTransaction['remarks']
                    data['balance_before'] = dataTransaction['balance_before']
                    data['balance_after'] = dataTransaction['balance_after']
                    data['created_date'] = dataTransaction['created_date']

                    list_result.append(data)

                dataOutput =  {"message":"SUCCESS", 
                    "result": list_result[::-1]
                    }
                return config.responseJson(dataOutput,200)
            else: #-->fail
                dataOutput ={'message':"Transaction history gagal, silahkan coba beberapa saat lagi"}
                return config.responseJson(dataOutput,400)

        except Exception as e:
            print('error',e)
            dataOutput ={'message':e}
            return config.responseJson(dataOutput,400)

        # return{'bismillah':'allahumma shalli ala muhammad'}

#----------------------------------------------------------------------------------routing
transactions_api = Blueprint('resources.transactions', __name__)
api       = Api(transactions_api)

api.add_resource(TransactionTopUp, '/topup', endpoint='transaction/top-up')
api.add_resource(TransactionPayment, '/payment', endpoint='transaction/payment')
api.add_resource(TransactionTransfer, '/transfer', endpoint='transaction/transfer')
api.add_resource(TransactionHistory, '/transactions', endpoint='transaction/history')
