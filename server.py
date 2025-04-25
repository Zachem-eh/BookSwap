from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField
from wtforms.fields.simple import EmailField, BooleanField
from wtforms.validators import DataRequired
from werkzeug.utils import redirect
from data import db_session
from data.books import Book
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class RegisterForm(FlaskForm):
    email = EmailField('Ваш email')
    password = PasswordField('Пароль')
    repeat_password = PasswordField('Подтвердите пароль')
    surname = StringField('Фамилия')
    name = StringField('Имя')
    age = StringField('Возраст')
    submit = SubmitField('Зарегистрироваться')


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


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        sess = db_session.create_session()
        user = User()
        user.email = form.email.data
        user.password = form.password.data
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = int(form.age.data)
        sess.add(user)
        sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/books')
@login_required
def books():
    db_sess = db_session.create_session()
    genre_filter = request.args.get('genre')

    if genre_filter:
        all_books = db_sess.query(Book).filter(Book.genre == genre_filter).all()
    else:
        all_books = db_sess.query(Book).all()

    genres = db_sess.query(Book.genre).distinct().all()
    genres = [g[0] for g in genres]

    return render_template('books.html', books=all_books, genres=genres, selected_genre=genre_filter)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        file = form.cover.data
        filename = secure_filename(file.filename)
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
        db_sess.commit()
        return redirect('/books')
    return render_template('add_book.html', form=form)


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
    right_book = sess.query(Book).filter(Book.id == id_book).first()
    return render_template('book.html', book=right_book)


@app.route('/profile')
@login_required
def profile():
    sess = db_session.create_session()
    curr_books = sess.query(Book).filter(Book.holder == current_user.id).all()
    return render_template('profile.html', books=curr_books)


if __name__ == '__main__':
    db_session.global_init('database/book_swap.db')
    app.run(host='127.0.0.1', port=8080)
