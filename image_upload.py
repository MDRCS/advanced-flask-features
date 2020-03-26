import os
import re
from typing import Union
from werkzeug.datastructures import FileStorage
from flask_uploads import UploadSet, IMAGES

IMAGE_SET = UploadSet("images", IMAGES)  # IMAGES Contains the basic image types that are viewable from most browsers
# (.jpg, .jpe, .jpeg, .png, .gif, .svg, and .bmp).


def save_image(image: FileStorage, folder: str = None, name: str = None):
    """ Get FileStorage and Put it in a Folder  """
    return IMAGE_SET.save(image, folder, name)


def get_path(filename: str = None, folder: str = None):
    """ Take Image Name and Folder and return full Path """
    return IMAGE_SET.path(filename, folder)


def find_image_any_format(filename: str = None, folder: str = None):
    """ Take a filename and returns an image of any accepted formats """
    for _format in IMAGES:
        image = f'{filename}.{_format}'
        image_path = IMAGE_SET.path(image, folder)
        if os.path.isfile(image_path):
            return image_path
    return None


def _retreive_filename(file: Union[str, FileStorage]):
    """ Take the file storage and return teh filename """
    if isinstance(file, FileStorage):
        return file.filename
    return file


def is_filename_safe(file: Union[str, FileStorage]):
    """ Check our regex with filename, and see if it matches or not """
    filename = _retreive_filename(file)
    allowed_format = "|".join(IMAGES)
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$"
    return re.match(regex, filename) is not None


def get_basename(file: Union[str, FileStorage]):
    """ Return fullname of the image from the path """
    filename = _retreive_filename(file)
    return os.path.split(filename)[1]


def get_extension(file: Union[str, FileStorage]):
    """ Return The file extension """
    filename = _retreive_filename(file)
    return os.path.splitext(filename)[1]
