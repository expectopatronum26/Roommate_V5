
# profile/__init__.py
from flask import Blueprint

profile_bp = Blueprint('profile', __name__, template_folder='../templates/profile')

from profile import routes

