from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.simple import EmailField, BooleanField
from wtforms.validators import DataRequired
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum'


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


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # sess = db_session.create_session()
        # user = User()
        # user.email = form.email.data
        # user.password = form.password.data
        # user.surname = form.surname.data
        # user.name = form.name.data
        # user.age = int(form.age.data)
        # sess.add(user)
        # sess.commit()
        return redirect('/')
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
