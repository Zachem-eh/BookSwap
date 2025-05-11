import base64
from flask_restful import Resource, reqparse
from data.books import Book
from data.users import User
from data.relationships import Relationship
from flask import jsonify, make_response
import os
from werkzeug.utils import secure_filename
from data.db_session import create_session
import uuid

book_parser = reqparse.RequestParser()
book_parser.add_argument('holder', type=int, required=False)
book_parser.add_argument('author', type=str, required=False)
book_parser.add_argument('title', type=str, required=False)
book_parser.add_argument('genre', type=str, required=False)
book_parser.add_argument('age', type=str, required=False)
book_parser.add_argument('cover', type=str, required=False)
book_parser.add_argument('data', type=str, required=False)


class BookResource(Resource):
    def get(self, book_id):
        session = create_session()
        try:
            book = session.get(Book, book_id)
            if book:
                return jsonify(book.to_dict(only=('id', 'holder', 'author', 'title', 'genre', 'age', 'cover')))
            return make_response({'message': 'Book not found'}, 404)
        finally:
            session.close()

    def put(self, book_id):
        session = create_session()
        try:
            book = session.get(Book, book_id)
            args = book_parser.parse_args()
            genres = ['Фэнтези', 'Научная фантастика', 'Детектив', 'Роман', 'Приключения', 'Ужасы', 'Биография',
                      'История']
            ages = ['0+', '6+', '12+', '16+', '18+']
            if not book:
                return make_response({'message': 'Book not found'}, 404)

            required_fields = ['holder', 'author', 'title', 'genre', 'age', 'cover']
            if all(args[field] is None for field in required_fields):
                return make_response(jsonify({"error": "Missing required fields"}), 400)

            if (args['cover'] and (not args['data'])) or ((not args['cover']) and args['data']):
                return make_response(jsonify({"error": "Missing data or cover for image"}), 400)

            for key, value in args.items():
                if value and key == 'cover':
                    filename = secure_filename(args['cover'])
                    filename = f'{uuid.uuid4().hex}_{filename}'
                    filepath = os.path.join('static/images', filename)

                    with open(filepath, mode='wb') as new_file:
                        new_file.write(base64.b64decode(args['data']))

                    if book.cover and os.path.exists(os.path.join('static', book.cover)):
                        os.remove(os.path.join('static', book.cover))
                    book.cover = f'images/{filename}'
                elif value and key == 'holder':
                    session.query(Relationship).filter(Relationship.book == book_id).delete()

                    taker = session.get(User, value)
                    if not taker:
                        return make_response(jsonify({"error": "User not exist"}), 400)

                    holder = session.get(User, book.holder)
                    holder_books = [int(x) for x in holder.books.split(', ')]
                    ind = holder_books.index(book.id)
                    del holder_books[ind]
                    holder_books = ', '.join([str(x) for x in holder_books])
                    holder.books = holder_books

                    if not taker.books:
                        taker.books = str(book.id)
                    else:
                        taker.books += f', {book.id}'
                    book.holder = taker.id
                elif value and key == 'genre' and value not in genres:
                    return make_response(jsonify({"error": "Wrong genre"}), 400)
                elif value and key == 'age' and value not in ages:
                    return make_response(jsonify({"error": "Wrong age limit"}), 400)
                elif value and key != 'data':
                    setattr(book, key, value)

            session.commit()
            return jsonify({str(book.id): 'changed'})
        except Exception as e:
            session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
        finally:
            session.close()

