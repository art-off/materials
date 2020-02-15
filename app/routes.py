from flask import render_template, flash, redirect, url_for, request, send_from_directory, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import date
from functools import wraps
import os
import re
import docx
from app import app, db
from app.forms import (LoginForm, RegistrationForm, AddMaterialForm,
                       AddTxtFilesForm, AddFilesForm, EditMaterialForm,
                       SearchUserForm, AddTestForm, ChoiceAnswerForm)
from app.models import User, Material, Email, Test
from app.email import send_email_to_everyone


def for_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id != 1:
            return render_template('no_access_rights.html')
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
@app.route('/index')
@login_required
def index():
    send = request.args.get('send_email_to_everyone')
    if send == '1':
        material_id = int(request.args.get('material_id'))
        material = Material.query.get_or_404(material_id)
        send_email_to_everyone(material)
    materials = Material.query.all()[::-1]
    return render_template('index.html', title='Home', materials=materials)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный email или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=re.sub(r'\s', '', form.name.data),
                    surname=re.sub(r'\s', '', form.surname.data),
                    patronymic=re.sub(r'\s', '', form.patronymic.data),
                    email=re.sub(r'\s', '', form.email.data),
                    materials='')
        user.set_password(form.password.data)
        email = Email(value=form.email.data)
        db.session.add(user)
        db.session.add(email)
        db.session.commit()
        flash('Вы зарегистрированы')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/add_material', methods=['GET', 'POST'])
@login_required
@for_admin
def add_material():
    form = AddMaterialForm()
    if form.validate_on_submit():
        material = Material(name=form.name.data,
                            section=form.section.data.lower(),
                            keywords=form.keywords.data,
                            files='')
        db.session.add(material)
        db.session.commit()
        #send_email_to_everyone(material)
        return redirect(url_for('add_files',id=material.id, text='txt', num=0))
    return render_template('add_material.html', form=form)



@app.route('/add_files', methods=['GET', 'POST'])
@login_required
@for_admin
def add_files():
    id = request.args.get('id')
    text = request.args.get('text')
    num = request.args.get('num')
    material = Material.query.get_or_404(id)
    if text == 'txt':
        form = AddTxtFilesForm()
    else:
        form = AddFilesForm()
    if form.validate_on_submit():
        file = request.files['file']
        filename = f'{material.id}({num}).{file.filename.rsplit(".", 1)[1]}'
        material.add_files(filename)
        db.session.commit()
        file.save(os.path.join('app', app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('add_files', id=id, text='add', num=int(num)+1))
    return render_template('add_files.html', text=text, form=form, material_id=id)


@app.route('/add_tests', methods=['GET', 'POST'])
@login_required
@for_admin
def add_tests():
    id = request.args.get('id')
    num = request.args.get('num')
    material = Material.query.get_or_404(id)
    form = AddTestForm()
    if form.validate_on_submit():
        test = Test(question=form.question.data,
                    answer1=form.answer1.data,
                    answer2=form.answer2.data,
                    answer3=form.answer3.data,
                    answer4=form.answer4.data,
                    correct_answer=form.correct_answer.data)
        db.session.add(test)
        # берем id последнего теста
        test_id = Test.query.all()[-1].id
        material.add_tests(str(test_id))
        db.session.commit()
        return redirect(url_for('add_tests', id=id, num=int(num)+1))
    return render_template('add_tests.html', text='Добавление вопроса', form=form, material_id=id, num=num)


@app.route('/edit_material/<id>', methods=['GET', 'POST'])
@login_required
@for_admin
def edit_material(id):
    material = Material.query.get_or_404(id)
    files = material.parse_files()
    form = EditMaterialForm(material.name)
    if form.validate_on_submit():
        material.name = form.name.data
        material.section = form.section.data.lower()
        material.keywords = form.keywords.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('edit_material', id=id))
    elif request.method == 'GET':
        form.name.data = material.name
        form.section.data = material.section
        form.keywords.data = material.keywords
    return render_template('edit_material.html', form=form, material=material, files=files, count_tests=len(material.parse_tests()))


@app.route('/edit_tests/<id>', methods=['GET', 'POST'])
@login_required
@for_admin
def edit_tests(id):
    count = request.args.get('count')
    num = request.args.get('num')
    if num == count:
        return redirect(url_for('index'))
    material_tests = Material.query.get_or_404(id).parse_tests()
    test = Test.query.get(material_tests[int(num)])
    form = AddTestForm()
    if form.validate_on_submit():
        test.question = form.question.data
        test.answer1 = form.answer1.data
        test.answer2 = form.answer2.data
        test.answer3 = form.answer3.data
        test.answer4 = form.answer4.data
        test.correct_answer = form.correct_answer.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('edit_tests', id=id, num=int(num)+1, count=count))
    elif request.method == 'GET':
        form.question.data = test.question
        form.answer1.data = test.answer1
        form.answer2.data = test.answer2
        form.answer3.data = test.answer3
        form.answer4.data = test.answer4
        form.correct_answer.data = test.correct_answer
    return render_template('add_tests.html', text='Редактирование вопроса', form=form, material_id=id, num=num)


def delete_files(material_files):
    for file in material_files:
        path_to_file = os.path.join('app', app.config['UPLOAD_FOLDER'], file)
        if os.path.isfile(path_to_file):
            os.remove(path_to_file)

def delete_tests(material_tests_id):
    for test_id in material_tests_id:
        test = Test.query.get(test_id)
        if test is not None:
            db.session.delete(test)

@app.route('/delete_material/<id>')
@login_required
@for_admin
def delete_material(id):
    material = Material.query.get_or_404(id)
    files = re.findall(r'[^, ]+', material.files)
    tests = material.parse_tests()
    delete_files(files)
    delete_tests(tests)
    db.session.delete(material)
    db.session.commit()
    flash('Материал и тесты удалены')
    return redirect(url_for('index'))


@app.route('/donwload/<filename>')
@login_required
def donwload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/check_progress', methods=['GET', 'POST'])
@login_required
@for_admin
def check_progress():
    form = SearchUserForm()
    if form.validate_on_submit():
        users = User.query.order_by(User.surname)
        if form.name.data != '':
            tmp = []
            for u in users:
                if u.name == form.name.data:
                    tmp.append(u)
            users = tmp
        if form.surname.data != '':
            tmp = []
            for u in users:
                if u.surname == form.surname.data:
                    tmp.append(u)
            users = tmp
        if form.patronymic.data != '':
            tmp = []
            for u in users:
                if u.patronymic == form.patronymic.data:
                    tmp.append(u)
            users = tmp
        return render_template('check_progress.html', title='Проверка прогресса', form=form, users=users)
    return render_template('check_progress.html', title='Проверка прогресса', form=form)

@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.get_or_404(id)
    mat_and_dates = user.parse_materials()
    material_and_dates = []
    for mat_id, date in mat_and_dates.items():
        material = Material.query.get(mat_id)
        if material is not None:
            material_and_dates.append((material, date))
    material_and_dates = material_and_dates[::-1]
    return render_template('user.html', title='Проверка прогресса', user=user, material_and_dates=material_and_dates)



@app.route('/material/<id>')
@login_required
def material(id):
    material = Material.query.get_or_404(id)
    files = material.parse_files()
    doc = docx.Document(os.path.join('app', app.config['UPLOAD_FOLDER'], files[0]))
    del files[0]
    text_doc = []
    for paragraph in doc.paragraphs:
        text_doc.append(paragraph.text)
    text_doc = '\n'.join(text_doc)
    return render_template('material.html', material=material, text_doc=text_doc, files=files,
                            count_tests=len(material.parse_tests()))



@app.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    material_id = int(request.args.get('material_id'))
    count = int(request.args.get('count'))
    num = int(request.args.get('num'))
    if num == 0:
        # если num = 0 (начальная точка входа в тесты), то обнуляем tmp (он будет использоваться в качестве счетчика)
        current_user.tmp = 0
        db.session.commit()
    elif num == count:
        if current_user.tmp == count:
            current_user.add_material(material_id, date.today().isoformat())
            flash('Вы прошли тестирование по материалу')
        else:
            flash('Вы не прошли тестирование по материалу, попробуйте еще раз')
        current_user.tmp = 0
        db.session.commit()
        return redirect(url_for('index'))
    material_tests = Material.query.get_or_404(material_id).parse_tests()
    curr_test = Test.query.get(material_tests[num])
    form = ChoiceAnswerForm()
    if form.validate_on_submit():
        if int(form.answer.data) == int(curr_test.correct_answer):
            current_user.tmp += 1
            db.session.commit()
        return redirect(url_for('test', material_id=material_id, count=count, num=num+1))
    return render_template('test.html', form=form, test=curr_test)
