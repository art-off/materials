import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # дирректория для файлов
    UPLOAD_FOLDER = 'files'
    # допустимые типы для загрузки файлов
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'mp3', 'gif', 'mp4']

    # НАСТРОЙКА ПОЧТОВОГО СЕРВЕРА
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'transneft.materials@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'transneft.materials1234'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'transneft.materials@gmail.com'
    ADMINS = ['transneft.materials@gmail.com']
