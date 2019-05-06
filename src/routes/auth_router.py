from flask import request, Blueprint, json, Response, redirect, url_for
from flask_dance.contrib.facebook import facebook
from flask_dance.contrib.google import google

from ..models.UserModel import UserModel, UserSchema
from ..shared.FacebookSocial import facebook_bp as facebook_blueprint
from ..shared.GoogleSocial import google_bp as google_blueprint

from ..shared.Authentication import Auth

auth_api = Blueprint('', __name__)
user_schema = UserSchema()


@auth_api.route("/google")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    account_info = google.get("/oauth2/v2/userinfo")
    if account_info.ok:
        account_info_json = account_info.json()
        user = UserModel()
        user.email = account_info_json['email']
        user.save()
        
        ser_data = user_schema.dump(user).data
        token = Auth.generate_token(ser_data.get('id'))
        return custom_response({'jwt_token': token}, 200)

    return custom_response('Resigter facebook failed', 500)


@auth_api.route('/facebook')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    account_info = facebook.get('/me?fields=id,email,name')

    if account_info.ok:
        account_info_json = account_info.json()
        user = UserModel()
        user.email = account_info_json['email']
        user.save()

        ser_data = user_schema.dump(user).data
        token = Auth.generate_token(ser_data.get('id'))
        return custom_response({'jwt_token': token}, 200)

    return custom_response('Resigter facebook failed', 500)


def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
