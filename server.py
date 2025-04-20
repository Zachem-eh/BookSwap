from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.fields.simple import EmailField, BooleanField
from wtforms.validators import DataRequired
from werkzeug.utils import redirect
from data import db_session
from data.books import Book
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

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


from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired

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
        book = Book(
            title=form.title.data,
            author=form.author.data,
            genre=form.genre.data,
            age=form.age.data,
            holder=current_user.id
        )
        db_sess.add(book)
        db_sess.commit()
        return redirect('/books')
    return render_template('add_book.html', form=form)


if __name__ == '__main__':
    db_session.global_init('database/book_swap.db')
    app.run(host='127.0.0.1', port=8080)
