from datetime import date
from flask_login import UserMixin
from flask import url_for
# from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import re
import os
from app import db, login, app



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    surname = db.Column(db.String(64), index=True)
    patronymic = db.Column(db.String(64), index=True)
    position = db.Column(db.String(128))
    organization = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    materials = db.Column(db.String(4096), default='') # тут будет храниться такое: material_id:date,  НАДА БОЛЬШЕ МЕСТА
    tmp = db.Column(db.Integer, default=0)        # всякие временные значения (правильно отвеченные тесты)

    def parse_materials(self):
        materials = re.findall(r'[^, ]+', self.materials)
        tmp = {}
        for mat in materials:
            m = re.findall(r'[^:]+', mat)
            tmp[int(m[0])] = m[1]
        return tmp

    def add_material(self, material_id, date):
        material_id = int(material_id)
        if User.query.get(material_id) is not None and material_id not in self.parse_materials():
            self.materials += f'{material_id}:{date}' + ', '
            db.session.commit()
            return 'good'
        return 'error'

    def __repr__(self):
        return f'<User {self.id} {self.name} {self.surname} {self.patronymic}>'

    def set_password(self, password):
        # self.password_hash = generate_password_hash(password)
        bytes_password = bytes(password, encoding='utf-8')
        self.password_hash = md5(bytes_password).hexdigest()

    def check_password(self, password):
        # return check_password_hash(self.password_hash, password)
        bytes_password = bytes(password, encoding='utf-8')
        return self.password_hash == md5(bytes_password).hexdigest()

    # для апишки
    def check_password_hash(self, password_hash):
        return self.password_hash == password_hash

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'patronymic': self.patronymic,
            'position': self.position,
            'organization': self.organization,
            'email': self.email,
            'materials': self.parse_materials()
        }
        return data


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    section = db.Column(db.String(128))
    date = db.Column(db.String(32), default=date.today().isoformat())
    keywords = db.Column(db.String(256), default='') # тут будук ключевые слова через запятую
    files = db.Column(db.String(512), default='')  # все файлы, принадлещащие этому материалу
    tests = db.Column(db.String(1028), default='')  # все id тесты, принадлещащие этому материалу

    def __repr__(self):
        return f'<Material {self.id} {self.name} {self.section}>'

    def parse_files(self):
        '''Спикос файлов находиться в виде строки, с разделителем - запятая и пробел
        Эта функция возвращает массив всех названий файлов'''
        return re.findall(r'[^, ]+', self.files)

    def add_files(self, filename):
        if filename not in self.parse_files():
            self.files += f'{filename}' + ', '
            db.session.commit()

    def parse_tests(self):
        '''Спикос id тестов находиться в виде строки, с разделителем - запятая и пробел
        Эта функция возвращает массив всех id тестов'''
        result = []
        for test in re.findall(r'[^, ]+', self.tests):
            result.append(int(test))
        return result

    def add_tests(self, test_id):
        if test_id not in self.parse_tests():
            self.tests += f'{test_id}' + ', '
            db.session.commit()

    def parse_keywords(self):
        '''Спикос ключевых слов находиться в виде строки, с разделителем - запятая и пробел
        Эта функция возвращает массив всех ключевых слов'''
        keywords = []
        keywords += re.findall(r'[^, ]+', self.name)
        keywords += re.findall(r'[^, ]+', self.section)
        keywords += [self.name]
        keywords += [self.section]
        keywords += re.findall(r'[^ ,][^,]+', self.keywords)
        for i in range(len(keywords)):
            keywords[i] = keywords[i].lower()
        return keywords

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'section': self.section,
            'date': self.date,
            'keywords': self.parse_keywords(),
            'files': {
            },
            'tests': []
        }
        all_files = self.parse_files()
        doc = all_files[0]
        all_files.remove(doc)
        data['files']['doc'] = doc
        data['files']['add'] = all_files
        for test_id in self.parse_tests():
            test = Test.query.get(test_id)
            data['tests'].append(test.to_dict())
        return data

    @staticmethod
    def to_collection_dict():
        data = {
            'items': [],
            '_meta': {
                'count': 0
            }
        }
        # changes
        materials = Material.query.all()[::-1]
        for material in materials:
            data['items'].append(material.to_dict())
            data['_meta']['count'] += 1
        return data



# содержим адреса для отправки эл писем
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(120), index=True, unique=True)

    @staticmethod
    def add(e):
        email = Email.query.filter_by(value=e).first()
        if email is None:
            email = Email(value=e)
            db.session.add(email)
            db.session.commit()

    @staticmethod
    def delete(e):
        email = Email.query.filter_by(value=e).first()
        if email is None:
            return
        db.session.delete(email)
        db.session.commit()

    def __repr__(self):
        return f'<Email {self.value}>'


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(2048))
    answer1 = db.Column(db.String(2048))
    answer2 = db.Column(db.String(2048))
    answer3 = db.Column(db.String(2048))
    answer4 = db.Column(db.String(2048))
    correct_answer = db.Column(db.String(5))

    def __repr__(self):
        return f'<Test {self.question}>'

    def to_dict(self):
        data = {
            'question': self.question,
            'answer1': self.answer1,
            'answer2': self.answer2,
            'answer3': self.answer3,
            'answer4': self.answer4,
            'correct_answer': self.correct_answer
        }
        return data
