from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Email, EqualTo
from app.models import User, Material
from app import app


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class AddMaterialForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    section = StringField('Раздел', validators=[DataRequired()])
    keywords = TextAreaField('Вверите слова, по которым будет происходить поиск (через зяпятую)')
    submit = SubmitField('Перейти к добавлению файлов')

    def validate_name(self, name):
        material = Material.query.filter_by(name=name.data).first()
        if material is not None:
            raise ValidationError('Пожалуйста, используйте другое название')

class AddTxtFilesForm(FlaskForm):
    file = FileField('Добавьте файл с основным текстом в формате .docx',
        validators=[
            FileRequired(),
            FileAllowed(['docx'], 'Только .docx')
    ])
    submit = SubmitField('Отправить')

class AddFilesForm(FlaskForm):
    file = FileField('Добавьте столько дополнительных файлов, сколько нужно',
        validators=[
            FileRequired(),
            FileAllowed(app.config['ALLOWED_EXTENSIONS'], 'Только png, jpg, jpeg, mp3, gif, mp4')
    ])
    submit = SubmitField('Отправить')

class EditMaterialForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    section = StringField('Раздел', validators=[DataRequired()])
    keywords = TextAreaField('Вверите слова, по которым будет происходить поиск (через зяпятую)')
    submit = SubmitField('Редактировать')

    def __init__(self, original_name, *args, **kwargs):
        super(EditMaterialForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            material = Material.query.filter_by(name=name.data).first()
            if material is not None:
                raise ValidationError('Пожалуйста, используйте другое название')


class SearchUserForm(FlaskForm):
    surname = StringField('Фамилия')
    name = StringField('Имя')
    patronymic = StringField('Отчество')
    submit = SubmitField('Найти')


class AddTestForm(FlaskForm):
    question = TextAreaField('Вопрос', validators=[DataRequired()])
    answer1 = TextAreaField('Вариант ответа №1', validators=[DataRequired()])
    answer2 = TextAreaField('Вариант ответа №2', validators=[DataRequired()])
    answer3 = TextAreaField('Вариант ответа №3', validators=[DataRequired()])
    answer4 = TextAreaField('Вариант ответа №4', validators=[DataRequired()])
    correct_answer = RadioField(u'Правильный ответ', validators=[InputRequired()], choices=[
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4')
    ])
    submit = SubmitField('Сохранить')

class ChoiceAnswerForm(FlaskForm):
    answer = RadioField('answer', choices=[
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4')
    ])
    submit = SubmitField('Ответить')
