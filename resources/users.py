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
from settings import db
from resources import config
# import models
# db.users.create_index([('user_id', pymongo.ASCENDING),('phone_number', pymongo.ASCENDING)],unique=True)
db.users.create_index([('phone_number', pymongo.ASCENDING)],unique=True)


class UserBase(Resource):
    def __init__(self):
        #init field for input 
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'phone_number',
            required = True,
            type=int,
            help     = 'phone_number required and must be integer',
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'pin',
            required = True,
            help     = 'pin required',
            location = ['form', 'json']
        )
        self.reqparse.add_argument( 'first_name', required = False,location = ['form', 'json'] )
        self.reqparse.add_argument( 'last_name', required = False,location = ['form', 'json'] )
        self.reqparse.add_argument(  'address', required = False,location = ['form', 'json'] )

        super().__init__()

class UserRegister(UserBase):
    def post(self):
        args = self.reqparse.parse_args()
        data = {
            '_id' : str(uuid4()),
            'first_name': args.get('first_name') or None,
            'last_name': args.get('last_name') or None,
            'address': args.get('address') or None,
            'phone_number': args.get('phone_number') or None,
            'pin':  md5(args.get('pin').encode('utf-8')).hexdigest()  or None,
            'balance': 0,
            'created_date': datetime.now(),
            'updated_date': datetime.now(),
        }

        try:
            #validate phone number have registered or not
            if db.users.count_documents({'phone_number':data['phone_number']}) == 0 : 
                dbResponse = db.users.insert_one(data)
                #validate register user --> success
                if dbResponse.acknowledged:
                    dataResponse = db.users.find_one({'_id':dbResponse.inserted_id})
                    dataOutput =  {"message":"SUCCESS", 
                                "result":{
                                    "user_id":f"{dataResponse['_id']}",
                                    "first_name":f"{dataResponse['first_name']}",
                                    "last_name":f"{dataResponse['last_name']}",
                                    "phone_number":f"{dataResponse['phone_number']}",
                                    "address":f"{dataResponse['address']}",
                                    "created_date":f"{dataResponse['created_date']}",
                                    }
                                }
                    return config.responseJson(dataOutput,201)
                else:
                    dataOutput ={'message':"Register user gagal, silahkan coba beberapa saat lagi"}
                    return config.responseJson(dataOutput,400)
            else:
                dataOutput ={'message':"Phone Number already registered"}
                return config.responseJson(dataOutput,400)

        except Exception as e:
            print('error',e)
            dataOutput ={'message':e}
            return config.responseJson(dataOutput,400)

class UserLogin(UserBase):
    def post(self):
        args = self.reqparse.parse_args()
        phone_number = args.get('phone_number') or None
        pin = args.get('pin') or None
        try:
            #hash pin number
            hashPin = md5(pin.encode('utf-8')).hexdigest()
            #get data user
            dataResponse = db.users.find_one({'phone_number':phone_number,'pin':hashPin}) or None
            #validate get data user --> success
            if dataResponse:
                dataOutput = {"message":"SUCCESS", 
                            "result":{
                                "access_token":create_access_token(identity=phone_number, fresh=True),
                                "refresh_token":create_refresh_token(identity=phone_number)
                                }
                            }
                return config.responseJson(dataOutput,200)
            else:
                dataOutput ={"message":"Phone number and pin doesn’t match."}
                return config.responseJson(dataOutput,400)

        except Exception as e:
            print('error',e)
            dataOutput ={'message':e}
            return config.responseJson(dataOutput,400)

class UserUpdateProfile(UserBase):
    
    def __init__(self):
        super().__init__()
        #override field phone_number and pin --> not required
        self.reqparse.replace_argument('phone_number', required=False, location = ['form', 'json'])
        self.reqparse.replace_argument('pin', required=False, location = ['form', 'json'])

    @jwt_required
    def put(self):
        args = self.reqparse.parse_args()
        data = {
            'first_name': args.get('first_name') or None,
            'last_name': args.get('last_name') or None,
            'address': args.get('address') or None,
            'updated_date': datetime.now(),
        }
        try:
            #update data user 
            dbResponse = db.users.update_one({'phone_number':get_jwt_identity()},{"$set": data}) or None
            #validate update data user --> success
            if dbResponse.acknowledged and dbResponse.modified_count == 1:
                dataResponse = db.users.find_one({'phone_number':get_jwt_identity()})
                dataOutput =  {"message":"SUCCESS", 
                            "result":{
                                "user_id":f"{dataResponse['_id']}",
                                "first_name":f"{dataResponse['first_name']}",
                                "last_name":f"{dataResponse['last_name']}",
                                "address":f"{dataResponse['address']}",
                                "updated_date":f"{dataResponse['updated_date']}",
                                }
                            }
                return config.responseJson(dataOutput,200)
            else:
                dataOutput ={'message':"Update User Profile gagal, silahkan coba beberapa saat lagi"}
                return config.responseJson(dataOutput,400)

        except Exception as e:
            print('error',e)
            dataOutput ={'message':e}
            return config.responseJson(dataOutput,400)

            # return{'bismillah':'allahumma shalli ala muhammad'}


#----------------------------------------------------------------------------------routing
users_api = Blueprint('resources.users', __name__)
api       = Api(users_api)

api.add_resource(UserLogin, '/login', endpoint='user/signin')
api.add_resource(UserRegister, '/register', endpoint='user/regster')
api.add_resource(UserUpdateProfile, '/profile', endpoint='user/update-profile')
