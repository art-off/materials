from flask import send_from_directory, jsonify, request
from app import app, db
from app.models import Material, User


@app.route('/api/donwload/<filename>')
def donwload_api(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/materials', methods=['GET'])
def get_materials():
    return jsonify(Material.to_collection_dict())


@app.route('/api/get_user', methods=['POST'])
def get_user():
    if 'secret' not in request.form.keys() or \
        'email' not in request.form.keys() or \
            'password_hash' not in request.form.keys():
            return 'Invalid DATA', 418
    secret = request.form['secret']
    if secret not in app.config['SECRET_KEYS_API']:
        return 'Invalid secret key', 402
    email = request.form['email']
    password_hash = request.form['password_hash']
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password_hash(password_hash):
        return 'Invalid email or password', 403
    return jsonify(user.to_dict())


@app.route('/api/add_material', methods=['POST'])
def add_material_for_user():
    if 'secret' not in request.form.keys() or \
        'user_id' not in request.form.keys() or \
        'material_id' not in request.form.keys() or \
        'material_date' not in request.form.keys():
            return 'Invalid DATA', 418
    secret = request.form['secret']
    if secret not in app.config['SECRET_KEYS_API']:
        return 'Invalid secret key', 402
    user_id = int(request.form['user_id'])
    material_id = request.form['material_id']
    material_date = request.form['material_date']
    user = User.query.get(user_id)
    print(secret, user_id, material_id, material_date)
    if user is None:
        return 'Invalid id', 403
    if user.add_material(material_id, material_date) == 'error':
        return 'Material does not exist', 404
    return 'Added', 200
