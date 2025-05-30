from flask import Flask, render_template, request, flash, url_for
from flask_restful import Api
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, IntegerField
from wtforms.fields.simple import EmailField, BooleanField
from wtforms.validators import DataRequired
from werkzeug.utils import redirect
from data import db_session
from data.books import Book
from data.users import User
from data.relationships import Relationship
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from user_resourse import UserResource, UserListResource
from book_resource import BookResource, BookListResource
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum'

login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)
api.add_resource(UserResource, '/api/users/<int:user_id>')
api.add_resource(UserListResource, '/api/users')
api.add_resource(BookResource, '/api/books/<int:book_id>')
api.add_resource(BookListResource, '/api/books')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class RegisterForm(FlaskForm):
    email = EmailField('Ваш email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Подтвердите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться', validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class BookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    genre = SelectField('Жанр', choices=[
        ('Фэнтези', 'Фэнтези'),
        ('Научная фантастика', 'Научная фантастика'),
        ('Детектив', 'Детектив'),
        ('Роман', 'Роман'),
        ('Приключения', 'Приключения'),
        ('Ужасы', 'Ужасы'),
        ('Биография', 'Биография'),
        ('История', 'История')
    ], validators=[DataRequired()])
    age = SelectField('Возрастное ограничение', choices=[
        ('0+', '0+'),
        ('6+', '6+'),
        ('12+', '12+'),
        ('16+', '16+'),
        ('18+', '18+')
    ], validators=[DataRequired()])
    cover = FileField('Выберите изображение',
                      validators=[DataRequired()],
                      render_kw={'accept': 'image/*'})
    submit = SubmitField('Добавить книгу')


class BookFormRedactor(BookForm):
    cover = FileField('Выберите изображение (необязательно)', render_kw={'accept': 'image/*'})


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        try:
            if sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html',
                                       form=form,
                                       message="Этот email уже зарегистрирован")

            user = User()
            user.email = form.email.data
            user.password = form.password.data
            user.surname = form.surname.data
            user.name = form.name.data
            user.age = form.age.data
            sess.add(user)
            sess.commit()
            return redirect('/login')
        finally:
            sess.close()
    return render_template('register.html', form=form)


@app.route('/books')
@login_required
def books():
    db_sess = db_session.create_session()
    try:
        genre_filter = request.args.get('genre')

        if genre_filter:
            all_books = db_sess.query(Book).filter(Book.genre == genre_filter).all()
        else:
            all_books = db_sess.query(Book).all()

        genres = db_sess.query(Book.genre).distinct().all()
        genres = [g[0] for g in genres]
        return render_template('books.html', books=all_books, genres=genres, selected_genre=genre_filter)
    finally:
        db_sess.close()


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            file = form.cover.data
            filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join('static/images', filename)
            file.save(save_path)
            book = Book(
                title=form.title.data,
                author=form.author.data,
                genre=form.genre.data,
                age=form.age.data,
                holder=current_user.id,
                cover=f'images/{filename}'
            )
            db_sess.add(book)
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            if not user.books:
                user.books = str(book.id)
            else:
                user.books += f', {book.id}'
            db_sess.commit()

            return redirect('/books')
        finally:
            db_sess.close()
    return render_template('add_book.html', form=form)


@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    db_sess = db_session.create_session()
    try:
        book = db_sess.query(Book).filter(Book.id == book_id, Book.holder == current_user.id).first()
        db_sess.query(Relationship).filter(Relationship.book == book_id).delete()
        if book:
            if book.cover and os.path.exists(os.path.join('static', book.cover)):
                os.remove(os.path.join('static', book.cover))

            holder = db_sess.query(User).filter(User.id == book.holder).first()
            holder_books = [int(x) for x in holder.books.split(', ')]
            ind = holder_books.index(book.id)
            del holder_books[ind]
            holder_books = ', '.join([str(x) for x in holder_books])
            holder.books = holder_books

            db_sess.delete(book)
            db_sess.commit()
            flash('Книга успешно удалена', 'success')
        else:
            flash('Книга не найдена или у вас нет прав на её удаление', 'danger')

        return redirect(url_for('profile'))
    finally:
        db_sess.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/books")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/book/<int:id_book>')
def book(id_book):
    sess = db_session.create_session()
    try:
        right_book = sess.query(Book).filter(Book.id == id_book).first()
        return render_template('book.html', book=right_book)
    finally:
        sess.close()


@app.route('/profile')
@login_required
def profile():
    sess = db_session.create_session()
    try:
        curr_books = sess.query(Book).filter(Book.holder == current_user.id).all()
        return render_template('profile.html', books=curr_books)
    finally:
        sess.close()


@app.route('/take_book/<int:book_id>', methods=['POST'])
@login_required
def take_book(book_id):
    sess = db_session.create_session()
    try:
        taken_book = sess.query(Book).filter(Book.id == book_id).first()
        holder = taken_book.holder
        relationship = Relationship()
        relationship.holder = holder
        relationship.book = taken_book.id
        relationship.taker = current_user.id
        sess.add(relationship)
        sess.commit()

        return redirect(f'/books')
    finally:
        sess.close()


@app.route('/check_take', methods=['GET', 'POST'])
@login_required
def check_take():
    sess = db_session.create_session()
    try:
        relationships = sess.query(Relationship).filter(Relationship.holder == current_user.id).all()
        flag_rl = False
        if relationships:
            flag_rl = True
        taker_dict = dict()
        for relationship in relationships:
            taker = sess.query(User).filter(User.id == relationship.taker).first()
            book_take = sess.query(Book).filter(Book.id == relationship.book).first()
            if taker not in taker_dict.keys():
                taker_dict[taker] = [book_take]
            else:
                taker_dict[taker].append(book_take)

        return render_template('check_take.html', takers=taker_dict, flag_rl=flag_rl)
    finally:
        sess.close()


@app.route('/replace_book/<int:book_id>/<int:taker_id>', methods=['POST'])
@login_required
def replace_book(book_id, taker_id):
    sess = db_session.create_session()
    try:
        sess.query(Relationship).filter(Relationship.book == book_id).delete()

        book_replace = sess.query(Book).filter(Book.id == book_id).first()
        holder = sess.query(User).filter(User.id == book_replace.holder).first()
        taker = sess.query(User).filter(User.id == taker_id).first()

        holder_books = [int(x) for x in holder.books.split(', ')]
        ind = holder_books.index(book_replace.id)
        del holder_books[ind]
        holder_books = ', '.join([str(x) for x in holder_books])
        holder.books = holder_books

        if not taker.books:
            taker.books = str(book_replace.id)
        else:
            taker.books += f', {book_replace.id}'
        book_replace.holder = taker.id

        sess.commit()
        return redirect('/check_take')
    finally:
        sess.close()


@app.route('/refuse_book/<int:book_id>/<int:taker_id>', methods=['POST'])
@login_required
def refuse_book(book_id, taker_id):
    sess = db_session.create_session()
    try:
        sess.query(Relationship).filter(Relationship.taker == taker_id, Relationship.book == book_id).delete()
        sess.commit()
        return redirect('/check_take')
    finally:
        sess.close()


@app.route('/redactor/<int:book_id>', methods=['GET', 'POST'])
@login_required
def redactor(book_id):
    sess = db_session.create_session()
    try:
        form = BookFormRedactor()
        curr_book = sess.query(Book).filter(Book.id == book_id).first()
        if form.validate_on_submit():
            file = form.cover.data
            if file:
                filename = secure_filename(file.filename)
                filename = f"{uuid.uuid4().hex}_{filename}"
                save_path = os.path.join('static/images', filename)
                if curr_book.cover and os.path.exists(os.path.join('static', curr_book.cover)):
                    os.remove(os.path.join('static', curr_book.cover))
                file.save(save_path)
                curr_book.cover = f'images/{filename}'
            curr_book.title = form.title.data
            curr_book.author = form.author.data
            curr_book.genre = form.genre.data
            curr_book.age = form.age.data
            sess.commit()
            return redirect('/books')

        form.title.data = curr_book.title
        form.author.data = curr_book.author
        form.genre.data = curr_book.genre
        form.age.data = curr_book.age
        return render_template('redactor.html', form=form, book_id=book_id)
    finally:
        sess.close()


if __name__ == '__main__':
    db_session.global_init('database/book_swap.db')
    app.run(host='127.0.0.1', port=8080)
