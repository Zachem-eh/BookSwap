from flask_restful import Resource, reqparse
from data.db_session import create_session
from data.users import User
from data.books import Book
from data.relationships import Relationship
from flask import jsonify, make_response
from re import match

parser = reqparse.RequestParser()
parser.add_argument('surname', required=False)
parser.add_argument('name', required=False)
parser.add_argument('age', required=False, type=int)
parser.add_argument('email', required=False)
parser.add_argument('password', required=False)


# /api/users/<id>
class UserResource(Resource):
    def get(self, user_id):
        sess = create_session()
        try:
            user = sess.query(User).filter(User.id == user_id).first()
            if not user:
                return make_response(jsonify({"error": "Not found"}), 404)
            return jsonify(user.to_dict(only=('id', 'surname', 'name', 'age', 'email', 'books')))
        finally:
            sess.close()

    def delete(self, user_id):
        sess = create_session()
        try:
            user = sess.query(User).filter(User.id == user_id).first()
            if not user:
                return make_response(jsonify({"error": "Not found"}), 404)
            sess.query(Book).filter(Book.holder == user_id).delete()
            sess.query(Relationship).filter(
                (Relationship.holder == user_id) | (Relationship.taker == user_id)).delete()
            sess.delete(user)
            sess.commit()
            return jsonify({'status': 'ok'})
        except Exception as e:
            sess.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
        finally:
            sess.close()

    def put(self, user_id):
        sess = create_session()
        args = parser.parse_args()
        try:
            user = sess.query(User).filter(User.id == user_id).first()

            if not user:
                return make_response(jsonify({"error": "Not found"}), 404)

            required_fields = ['surname', 'name', 'email']
            if all(args[field] is None for field in required_fields):
                return make_response(jsonify({"error": "Missing required fields"}), 400)

            if args['email'] and sess.query(User).filter(User.email == args['email'], User.id != user_id).first():
                return make_response(jsonify({"error": "Email already exists"}), 400)

            if user.email == args['email']:
                return make_response(jsonify({"error": "Replacing the e-mail with the same one"}), 400)

            if match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+", args['email']) is None:
                return make_response(jsonify({"error": "Wrong email"}), 400)

            user.surname = args['surname'] if args['surname'] else user.surname
            user.name = args['name'] if args['name'] else user.name
            user.age = args['age'] if args['age'] else user.age
            user.email = args['email'] if args['email'] else user.email
            sess.commit()
            return jsonify({str(user_id): 'changed'})
        except Exception as e:
            sess.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
        finally:
            sess.close()


class UserListResource(Resource):
    def get(self):
        sess = create_session()
        try:
            users = sess.query(User).all()
            return jsonify([user.to_dict(only=('id', 'surname', 'name', 'age', 'email', 'books')) for user in users])
        finally:
            sess.close()

    def post(self):
        args = parser.parse_args()
        sess = create_session()
        try:
            required_fields = ['surname', 'name', 'email', 'password']
            if not all(args[field] for field in required_fields):
                return make_response(jsonify({"error": "Missing required fields"}), 400)

            if sess.query(User).filter(User.email == args['email']).first():
                return make_response(jsonify({"error": "Email already registered"}), 400)

            user = User(
                surname=args['surname'],
                name=args['name'],
                age=args['age'],
                email=args['email'],
                password=args['password']
            )
            sess.add(user)
            sess.commit()
            return jsonify({'user_id': user.id})
        except Exception as e:
            sess.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
        finally:
            sess.close()
