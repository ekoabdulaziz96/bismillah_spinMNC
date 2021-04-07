from flask import Flask, request
from flask_restful import Resource, Api


from flask_jwt_extended import (JWTManager, jwt_required,
                                get_raw_jwt)

import settings
from resources.transactions import transactions_api
from resources.users import users_api


app = Flask(__name__)


#ACCESS_TOKEN_JWT
app.config['SECRET_KEY'] = 'randomString_superSecret1928390123'
app.config['JWT_BLACKLIST_ENABLED']      = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

jwt = JWTManager(app)
app.register_blueprint(transactions_api)
app.register_blueprint(users_api)

#logout
blacklist = set()
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

@app.route('/logout')
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return 'berhasil logout'

if __name__ == '__main__':
    settings.mongoDB()
    app.run(debug=True)
