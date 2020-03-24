from flask_restful import Resource, request
from flask import render_template, make_response
import traceback
from schemas.user import UserSchema
from models.confirmation import ConfirmationModel
from models.user import UserModel, MailGunException


class Confirmation(Resource):
    def get(self, confirmation_id):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        print(confirmation)
        if not confirmation:
            return {"message": "Not found Confirmation"}, 404

        if confirmation.expired:
            return {"message": "Confirmation is Already expired"}, 400

        if confirmation.confirmed:
            return {"message": "Confirmation is Already confirmed"}, 400

        confirmation.confirmed = True
        confirmation.save_database()
        print("jsjsjjs")
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation_page.html", email=confirmation.user.email), 200, headers)


class ConfirmationByUser(Resource):
    def post(self, user_id):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": "User not FOUND"}, 404

        try:
            recent_confirmation = user.most_recent_confirmation

            if recent_confirmation:
                if not recent_confirmation.confirmed:
                    return {"message": "The User is not yet Confirmed"}
                recent_confirmation.force_to_expire()

            confirmation = ConfirmationModel(user_id=user_id)
            confirmation.save_database()
            user.send_confirmation_email()
            return {"message": "RESEND Confirmation SUCCESSFULLY "}, 201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": "Failed RESEND Confirmation"}, 500
