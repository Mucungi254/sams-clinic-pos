import os

class Config:
    SECRET_KEY = 'sams-clinic-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sams_clinic_pos.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')