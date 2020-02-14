from flask import send_from_directory, jsonify
from app import app, db
from app.models import Material


@app.route('/api/donwload/<filename>')
def donwload_api(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/materials', methods=['GET'])
def get_materials():
    return jsonify(Material.to_collection_dict())
