import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Book(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'books'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    holder = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    author = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    cover = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user = orm.relationship('User', foreign_keys=[holder], back_populates='book')