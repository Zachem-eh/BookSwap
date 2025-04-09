from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.simple import EmailField, BooleanField
from wtforms.validators import DataRequired

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
