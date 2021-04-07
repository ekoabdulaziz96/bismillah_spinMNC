# from flask import jsonify, Blueprint, abort
# from flask_restful import Resource, Api, reqparse, fields, marshal, marshal_with
# from flask_jwt_extended import (JWTManager, jwt_required,
#                                 create_access_token, get_jwt_identity)

# import models

# message_fields = {
#     'id' : fields.Integer,
#     'content' : fields.String,
#     'published_at' : fields.String
# }

# def get_or_abort(id):
#     try:
#         msg = models.Message.get_by_id(id)
#     except models.Message.DoesNotExist:
#         abort(404)
#     else:
#         return msg

# class BaseMessage(Resource):
#     def __init__(self):
#         self.reqparse = reqparse.RequestParser()
#         self.reqparse.add_argument(
#             'content',
#             required = True,
#             help     = 'konten wajib ada',
#             location = ['form', 'json']
#         )
#         super().__init__()

# class MessageList(BaseMessage):
#     # @jwt_required
#     def get(self):
#         messages = [marshal(message, message_fields)
#                     for message in models.Message.select()]
#         return {'messages' : messages}

#     @jwt_required
#     def post(self):
#         args = self.reqparse.parse_args()
#         current_user = get_jwt_identity()
#         user = models.User.select().where(models.User.username == current_user).get()

#         message = models.Message.create(
#             content = args.get('content'),
#             user_id = user
#         )

#         return marshal(message, message_fields)

# def validate_owner(msg):
#     current_user = get_jwt_identity()
#     user = models.User.select().where(models.User.username == current_user).get()

#     if msg.user_id == user:
#         return True
#     else:
#         abort(403)

# class Message(BaseMessage):
#     @marshal_with(message_fields)
#     def get(self, id):
#         return get_or_abort(id)

#     @jwt_required
#     def put(self, id):
#         args    = self.reqparse.parse_args()
#         content = args.get('content')
#         msg = get_or_abort(id)

#         if validate_owner(msg):
#             message = models.Message.update(content = content).where(models.Message.id == id).execute()
#             return 'berhasil mengupdate'

#     @jwt_required
#     def delete(self, id):
#         args    = self.reqparse.parse_args()
#         content = args.get('content')
#         msg = get_or_abort(id)

#         if validate_owner(msg):
#             message = models.Message.delete().where(models.Message.id == id).execute()
#             return 'berhasil menghapus!'

# messages_api = Blueprint('resources.messages', __name__)
# api          = Api(messages_api)

# api.add_resource(MessageList, '/messages', endpoint='messages')
# api.add_resource(Message, '/message/<int:id>', endpoint='message')
