from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import traceback
from schemas.image import ImageSchema
from flask import request, send_file
import image_upload

imageschema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required
    def post(self):

        data = imageschema.load(request.files)
        user_id = get_jwt_identity()
        image = data["image"]
        folder = f"user_{user_id}"  # static/images/user_1

        try:
            filename = image_upload.save_image(image, folder)
            basename = image_upload.get_basename(filename)
            return {"message": "The Image {} is uploaded succefully.".format(basename)}, 201
        except UploadNotAllowed:
            extension = image_upload.get_extension(filename)
            return {"message": "This extension {} is not allowed".format(extension)}, 400


class Image(Resource):
    @jwt_required
    def get(self, filename):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_upload.is_filename_safe(filename):
            extension = image_upload.get_extension(filename)
            return {"message": "This Extension {} is not accepted.".format(extension)}, 400

        try:
            return send_file(image_upload.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": "File not found"}, 404

    @jwt_required
    def delete(self, filename):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_upload.is_filename_safe(filename):
            extension = image_upload.get_extension(filename)
            return {"message": "This Extension {} is not accepted.".format(extension)}, 400

        try:
            image_path = image_upload.get_path(filename, folder)
            basename = image_upload.get_basename(image_path)
            os.remove(image_path)
            return {"message": "The Image {} has been deleted succefully.".format(basename)}, 200
        except FileNotFoundError:
            return {"message": "File not found"}, 404
        except:
            traceback.print_exc()
            return {"message": "Error Will deleting the image file."}, 500


class AvatarImage(Resource):

    @jwt_required
    def put(self):
        data = imageschema.load(request.files)
        folder = "avatars"
        filename = f"user_{get_jwt_identity()}"
        avatar_path = image_upload.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": "Failed Deleting Avatar Image."}, 500

        try:
            ext = image_upload.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = image_upload.save_image(data["image"], folder, avatar)
            basename = image_upload.get_basename(avatar_path)
            return {"message": "Avatar Image {} Uploaded Succefully.".format(basename)}, 200
        except UploadNotAllowed:
            return {"message": "{} is an Illegal Extension Format".format(ext)}



