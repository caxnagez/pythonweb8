from flask import Blueprint, jsonify, request
from main import Session, User
from werkzeug.security import generate_password_hash
user_api = Blueprint('user_api', __name__)

def get_users_with_details(users_list):
    result = []
    for user in users_list:
        user_dict = {
            'id': user.id,
            'surname': user.surname,
            'name': user.name,
            'age': user.age,
            'position': user.position,
            'speciality': user.speciality,
            'address': user.address,
            'email': user.email,
            'city_from': user.city_from
        }
        result.append(user_dict)
    return result

@user_api.route('/api/users', methods=['GET'])
def get_users():
    session = Session()
    users = session.query(User).all()
    session.close()
    return jsonify({'users': get_users_with_details(users)})

@user_api.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': get_users_with_details([user])[0]})

@user_api.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    session = Session()
    existing_user = session.query(User).filter(User.id == data.get('id')).first()
    if existing_user:
        session.close()
        return jsonify({'error': 'Id already exists'}), 400

    user_id = data.get('id')
    surname = data.get('surname')
    name = data.get('name')
    age = data.get('age')
    position = data.get('position')
    speciality = data.get('speciality')
    address = data.get('address')
    email = data.get('email')
    city_from = data.get('city_from')
    password = data.get('password')

    if not all([user_id, surname, name, age, position, speciality, address, email, password]):
        session.close()
        return jsonify({'error': 'Missing required fields'}), 400

    existing_email = session.query(User).filter(User.email == email).first()
    if existing_email:
        session.close()
        return jsonify({'error': 'Email already registered'}), 400

    new_user = User(
        id=user_id,
        surname=surname,
        name=name,
        age=age,
        position=position,
        speciality=speciality,
        address=address,
        email=email,
        city_from=city_from
    )
    new_user.set_password(password)

    session.add(new_user)
    session.commit()
    session.close()
    return jsonify({'success': 'User added successfully'}), 201

@user_api.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user_api(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        return jsonify({'error': 'User not found'}), 404

    session.delete(user)
    session.commit()
    session.close()
    return jsonify({'success': 'User deleted successfully'})

@user_api.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user_api(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        return jsonify({'error': 'User not found'}), 404

    if 'surname' in data:
        user.surname = data['surname']
    if 'name' in data:
        user.name = data['name']
    if 'age' in data:
        user.age = data['age']
    if 'position' in data:
        user.position = data['position']
    if 'speciality' in data:
        user.speciality = data['speciality']
    if 'address' in data:
        user.address = data['address']
    if 'email' in data:
        existing_email = session.query(User).filter(User.email == data['email'], User.id != user_id).first()
        if existing_email:
            session.close()
            return jsonify({'error': 'Email already registered by another user'}), 400
        user.email = data['email']
    if 'city_from' in data:
        user.city_from = data['city_from']
    if 'password' in data:
        user.set_password(data['password'])

    session.commit()
    session.close()
    return jsonify({'success': 'User updated successfully'})
