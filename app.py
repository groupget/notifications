from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import jwt
from consumer import start_consuming
import OldTokenNotFoundException
from db import update_registration, save_registration
import threading
from flask_restplus import Resource, Api, fields

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
threading.Thread(target=start_consuming).start()
api = Api(app)


@api.route('/register')
class RegisterController(Resource):

    @api.response(201, 'Token successfully registered')
    @api.expect(api.model('RegisterRequest', {
        'token': fields.String(description='FCM token')
    }))
    def post(self):
        decoded_jwt = _get_decoded_jwt_from_request()
        username = decoded_jwt.get("cognito:username")
        groups = decoded_jwt.get("cognito:groups")
        group = groups[0]
        fcm_token = _get_fcm_token_from_request()
        save_registration(username, group, fcm_token)
        return make_response(
            jsonify({
                'status': 'success'
            }), 200)


@api.route('/refresh')
class RefreshController(Resource):

    @api.response(202, 'Token successfuly refreshed')
    @api.expect(api.model('RefreshRequest', {
        'old_token': fields.String(description='FCM token to refresh'),
        'new_token': fields.String(description='New FCM token to replace the old one')
    }))
    def put(self):
        json = request.json
        old_fcm_token = json['old_token']
        new_fcm_token = json['new_token']
        try:
            update_registration(old_fcm_token, new_fcm_token)
        except OldTokenNotFoundException as ex:
            return make_response(
                jsonify({
                    'status': 'old token not found'
                }), 400)
        return make_response(
            jsonify({
                'status': 'success'
            }), 200)


def _get_fcm_token_from_request():
    posted_json = request.get_json()
    token = posted_json['token']
    if token is None:
        return make_response(
            jsonify({
                'status': 'missing fcm token'
            }), 400)
    return token


def _get_decoded_jwt_from_request():
    try:
        authorization_header = str(request.headers.get("Authorization"))
        encoded_jwt = authorization_header[7:]
        return jwt.decode(jwt=encoded_jwt, verify=False)
    except Exception as ex:
        print(ex)
        return make_response(
            jsonify({
                'status': 'missing or incorrect jwt'
            }), 401)


if __name__ == '__main__':
    app.run(debug=False, threaded=True, port=5000, use_reloader=False)
