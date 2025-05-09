from flask_restful import Resource, reqparse
from data.books import Book
from flask import jsonify
from flask import request
import os
from werkzeug.utils import secure_filename
from data.db_session import create_session
from server import allowed_file

book_parser = reqparse.RequestParser()
book_parser.add_argument('holder', type=int, required=True, help='holder (user ID) is required')
book_parser.add_argument('author', type=str, required=True, help='Author is required')
book_parser.add_argument('title', type=str, required=True, help='Title is required')
book_parser.add_argument('genre', type=str, required=True, help='Genre is required')
book_parser.add_argument('age', type=int, required=True, help='Age is required')
book_parser.add_argument('cover', type=str, required=True, help='Cover URL is required')


class BookResource(Resource):
    def get(self, book_id=None):
        session = create_session()
        if book_id:
            book = session.get(Book, book_id)
            if book:
                return jsonify(book.to_dict())
            return {'message': 'Book not found'}, 404
        else:
            books = session.query(Book).all()
            return jsonify([book.to_dict() for book in books])

    def post(self):
        args = book_parser.parse_args()
        session = create_session()

        book = Book(
            holder=args['holder'],
            author=args['author'],
            title=args['title'],
            genre=args['genre'],
            age=args['age'],
            cover=args['cover']
        )

        session.add(book)
        session.commit()
        return jsonify(book.to_dict())

    def put(self, book_id):
        session = create_session()
        book = session.get(Book, book_id)
        if not book:
            return {'message': 'Book not found'}, 404

        args = book_parser.parse_args()
        for key, value in args.items():
            setattr(book, key, value)

        session.commit()
        return jsonify(book.to_dict())

    def delete(self, book_id):
        session = create_session()
        book = session.get(Book, book_id)
        if not book:
            return {'message': 'Book not found'}, 404

        session.delete(book)
        session.commit()
        return {'message': 'Book deleted successfully'}


class BookCoverUpload(Resource):
    def post(self, book_id):
        session = create_session()
        book = session.get(Book, book_id)
        if not book:
            return {'message': 'Book not found'}, 404

        if 'cover' not in request.files:
            return {'message': 'No file part in request'}, 400

        file = request.files['cover']
        if file.filename == '':
            return {'message': 'No file selected'}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join('static', 'covers', f'book_{book_id}_{filename}')
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            book.cover = filepath
            session.commit()
            return {'message': 'Cover uploaded', 'cover_path': filepath}

        return {'message': 'Invalid file type'}, 400
