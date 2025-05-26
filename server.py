import os
import datetime
import numpy as np
from keras.models import load_model
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from server_functions import convert_strings_to_floats, preprocess_image, str_processing

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:meowies@localhost/Thesis'
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'cats'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
model = load_model('model_224_1861.67.h5', compile=False)

not_found_cat = jsonify({
            "id": "-1",
            "name": "not found",
            "image": "cats/not_found.png"
        })


class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)


class regions(db.Model):
    id = db.Column(db.SmallInteger, primary_key=True)
    name = db.Column(db.Text)


class shelters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    region_id = db.Column(db.Integer, db.ForeignKey(regions.id))
    address = db.Column(db.Text)

    region = db.relationship('regions', foreign_keys='shelters.region_id')


class cats(db.Model):
    id = db.Column(db.SmallInteger, primary_key=True)
    name = db.Column(db.Text)
    region_id = db.Column(db.Integer, db.ForeignKey(regions.id))
    shelter_id = db.Column(db.Integer, db.ForeignKey(shelters.id))
    status = db.Column(db.Text)
    details = db.Column(db.Text)
    phone = db.Column(db.Text)

    region = db.relationship('regions', foreign_keys='cats.region_id')
    shelter = db.relationship('shelters', foreign_keys='cats.shelter_id')


class photos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    embedding = db.Column(db.Text)
    cat_id = db.Column(db.Integer, db.ForeignKey(cats.id))
    route = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey(users.id))
    upload_date = db.Column(db.Text)

    cat = db.relationship('cats', foreign_keys='photos.cat_id')
    user = db.relationship('users', foreign_keys='photos.user_id')


@app.route("/", methods=["GET", "POST"])
def upload_file():
    return 'yep'


@app.route('/search', methods=['POST'])
def search():
    region = request.form.get('region')
    ignore = request.form.get('ignore')
    ignored_cats = ignore.rstrip().split()
    if 'image' not in request.files:
        return '', 400
    new_image = request.files['image']
    filepath = os.path.join(UPLOAD_FOLDER, new_image.filename)
    new_image.save(filepath)

    query = preprocess_image(filepath)
    suspect = model.predict(query)
    print(suspect)

    a = []

    embeddings = (
        db.session.query(photos.embedding, photos.cat_id)
        .join(cats)
        .join(regions)
        .filter(regions.name == region)
        .filter(~photos.cat_id.in_(ignored_cats))
        .all()
    )

    if len(embeddings) == 0:
        return not_found_cat

    embedding_list = [e[0] for e in embeddings]
    indexes_list = [e[1] for e in embeddings]
    print("embedding_list")
    print(embedding_list)
    print("indexes_list")
    print(indexes_list)

    for line in embedding_list:
        print("line")
        print(line)
        line = line.rstrip().split(' ')
        print(line)
        line = convert_strings_to_floats(line)
        a.append(line)

    suspect = str_processing(str(suspect))
    print("suspect")
    print(suspect)

    suspect = suspect.rstrip().split(' ')
    print(suspect)
    suspect = convert_strings_to_floats(suspect)
    print(suspect)
    suspect = np.array(suspect)
    print(suspect)

    embeddings = np.array(a)
    print(embeddings)
    print(suspect)

    distances = np.linalg.norm(embeddings - suspect, axis=1)

    min_distance = np.min(distances)
    print(min_distance)

    index = np.where(distances == min_distance)[0][0]
    found_cat_id = indexes_list[index]
    print(found_cat_id)

    found_cat_photos = (
        db.session.query(cats.name, photos.route, shelters.name, shelters.address, cats.phone, cats.details)
        .join(photos, photos.cat_id == cats.id)
        .join(shelters, cats.shelter_id == shelters.id)
        .filter(cats.id == found_cat_id)
        .all()
    )

    print(found_cat_photos)
    try:
        found_cat_name = found_cat_photos[0][0]
        found_cat_photo = found_cat_photos[0][1]
        found_cat_shelter = found_cat_photos[0][2]
        shelter_address = found_cat_photos[0][3]
        contact_phone_number = found_cat_photos[0][4]
        found_cat_details = found_cat_photos[0][5]
    except Exception as e:
        print(e)
        return not_found_cat

    return jsonify({
        "id": str(found_cat_id),
        "name": found_cat_name,
        "image": found_cat_photo,
        "shelter": found_cat_shelter,
        "address": shelter_address,
        "phone": contact_phone_number,
        "details": found_cat_details
    })


@app.route('/cats/<filename>')
def get_image(filename):
    return send_from_directory('cats', filename)


@app.route('/add_cat', methods=['POST'])
def add_cat():
    name = request.form.get('name')
    region_name = request.form.get('region')
    shelter_name = request.form.get('shelter')
    details = request.form.get('details')
    user_id = request.form.get('user')
    address = request.form.get('address')
    phone = request.form.get('phone')

    if 'image' not in request.files:
        return '', 400
    new_image = request.files['image']
    now = datetime.datetime.now()
    time = str(now.time())
    time = time.replace(":", "")
    time = time.replace(".", "")
    filepath = os.path.join(UPLOAD_FOLDER, f'{time}.jpg')
    new_image.save(filepath)

    try:
        region = db.session.query(regions).filter_by(name=region_name).first()
        region_id = region.id if region else None

        user = db.session.query(users).filter_by(id=user_id).first()
        if not user:
            user = users(id=user_id, name='', password='', email='')
            db.session.add(user)
            db.session.commit()

        shelter = db.session.query(shelters).filter_by(name=shelter_name).first()
        if not shelter:
            shelter = shelters(name=shelter_name, address=address)
            db.session.add(shelter)
            db.session.commit()
        shelter_id = shelter.id

        cat = cats(name=name, region_id=region_id, shelter_id=shelter_id,
                   status='in_shelter', details=details, phone=phone)
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.id

        query = preprocess_image(filepath)
        embedding = model.predict(query)

        photo = photos(embedding=str(embedding), cat_id=cat_id, route=filepath,
                       user_id=int(user_id), upload_date=str(now))
        db.session.add(photo)
        db.session.commit()

    except Exception as e:
        print(e)

    return '', 200


@app.route('/user/<email>', methods=['GET'])
def get_user_by_email(email):
    if email is not None:
        found_user = db.session.query(users).filter(users.email == email).first()
        if found_user is not None:
            return jsonify({
                "id": str(found_user.id),
                "name": found_user.name,
                "email": found_user.email
            })
    return 404


@app.route('/user', methods=['POST'])
def add_user():
    user_name = request.form.get('name')
    email = request.form.get('name')
    password = request.form.get('name')
    result = db.session.execute(
        """
        INSERT INTO Users(
        Name, Email, Password, Birthday, ProfilePicture)
        VALUES ('%s', '%s', crypt('%s', gen_salt('bf')));
        """ % (user_name, email, password)
    )
    db.session.commit()
    if result.rowcount > 0:
        return 200
    return 404


@app.route('/user/check', methods=['POST'])
def check_password():
    email = request.form.get('email'),
    password = request.form.get('password')
    found_user = (db.session
                  .query(users)
                  .filter(users.email == email, users.password == password)
                  .first())
    if found_user is not None:
        return 200
    return 404


@app.route('/user/login', methods=['POST'])
def authorize():
    email = request.form.get('email'),
    password = request.form.get('password')
    found_user = (db.session
                  .query(users)
                  .filter(users.email == email, users.password == password)
                  .first())
    if found_user is not None:
        return jsonify({
            "id": str(found_user.id),
            "name": found_user.name,
            "email": found_user.email
        })
    return 404


@app.route('/user/change/password', methods=['POST'])
def change_password():
    email = request.form.get('email'),
    password = request.form.get('password')

    result = db.session.execute(
        """
        UPDATE users
        SET password = crypt('%s', gen_salt('bf'))
        WHERE email = '%s'
        """ % (password, email)
    )
    db.session.commit()
    if result.rowcount > 0:
        return 200
    return 404


@app.route('/user/change/name')
def change_name():
    email = request.form.get('email'),
    name = request.form.get('name')
    result = db.session.query(users).filter_by(email=email).update({"name": name})
    db.session.commit()
    if result.rowcount > 0:
        return 200
    return 404


@app.route('/user/change/email')
def change_email():
    old_email = request.form.get('old_email'),
    new_email = request.form.get('new_email')
    result = db.session.query(users).filter_by(email=old_email).update({"email": new_email})
    db.session.commit()
    if result.rowcount > 0:
        return 200
    return 404


if __name__ == '__main__':
    app.run(host='192.168.1.16', port=5000, debug=True)
