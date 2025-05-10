from flask_restful import Resource, reqparse
from data.books import Book
from data.users import User
from flask import jsonify, make_response
from flask import request
import os
from werkzeug.utils import secure_filename
from data.db_session import create_session
from utils import allowed_file
import uuid

book_parser = reqparse.RequestParser()
book_parser.add_argument('holder', type=int, required=False)
book_parser.add_argument('author', type=str, required=False)
book_parser.add_argument('title', type=str, required=False)
book_parser.add_argument('genre', type=str, required=False)
book_parser.add_argument('age', type=str, required=False)
book_parser.add_argument('cover', type=str, required=False)

class BookResource(Resource):
    def get(self, book_id=None):
        session = create_session()
        if book_id:
            book = session.get(Book, book_id)
            if book:
                return jsonify(book.to_dict(only=('id', 'holder', 'author', 'title', 'genre', 'age', 'cover')))
            return make_response({'message': 'Book not found'}, 404)
        else:
            books = session.query(Book).all()
            return jsonify([book.to_dict(only=('id', 'holder', 'author', 'title', 'genre', 'age', 'cover')) for book in books])

    def post(self):
        args = book_parser.parse_args()
        session = create_session()

        required_fields = ['holder', 'author', 'title', 'genre', 'age', 'cover']
        if not all(args[field] for field in required_fields):
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        user_holder = session.query(User).filter(User.id == args['holder']).first()
        if not user_holder:
            return make_response(jsonify({"error": "Holder not exist"}), 400)

        genres = ['Фэнтези', 'Научная фантастика', 'Детектив', 'Роман', 'Приключения', 'Ужасы', 'Биография', 'История']
        if args['genre'] not in genres:
            return make_response(jsonify({"error": "Wrong genre"}), 400)

        ages = ['0+', '6+', '12+', '16+', '18+']
        if args['age'] not in ages:
            return make_response(jsonify({"error": "Wrong age limit"}), 400)

        with open(os.path.abspath(args['cover']), mode='rb', encoding='utf-8') as file:
            if file.name == '':
                return make_response({'message': 'No file selected'}, 400)

            if not (file and allowed_file(file.name)):
                return make_response({'message': 'Invalid file type'}, 400)

            data = file.readlines()
            filename = secure_filename(file.name)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join('static/images', unique_filename)

        with open(filepath, mode='wb', encoding='utf-8') as new_file:
            new_file.writelines(data)

        book = Book(
            holder=args['holder'],
            author=args['author'],
            title=args['title'],
            genre=args['genre'],
            age=args['age'],
            cover=f'/images/{unique_filename}'
        )

        session.add(book)
        session.commit()
        return jsonify(book.to_dict(only=('id', 'holder', 'author', 'title', 'genre', 'age', 'cover')))

    def put(self, book_id):
        session = create_session()
        book = session.get(Book, book_id)
        if not book:
            return make_response({'message': 'Book not found'}, 404)

        args = book_parser.parse_args()
        for key, value in args.items():
            if value:
                setattr(book, key, value)

        session.commit()
        return jsonify(book.to_dict(only=('id', 'holder', 'author', 'title', 'genre', 'age', 'cover')))

    def delete(self, book_id):
        session = create_session()
        book = session.get(Book, book_id)
        if not book:
            return make_response({'message': 'Book not found'}, 404)

        session.delete(book)
        session.commit()
        return jsonify({'message': 'Book deleted successfully'})


class BookCoverUpload(Resource):
    def post(self, book_id):
        session = create_session()
        book = session.get(Book, book_id)
        if not book:
            return make_response({'message': 'Book not found'}, 404)

        if 'cover' not in request.files:
            return make_response({'message': 'No file part in request'}, 400)

        file = request.files['cover']
        if file.filename == '':
            return make_response({'message': 'No file selected'}, 400)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join('static', 'covers', f'book_{book_id}_{filename}')
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            book.cover = filepath
            session.commit()
            return jsonify({'message': 'Cover uploaded', 'cover_path': filepath})

        return make_response({'message': 'Invalid file type'}, 400)
