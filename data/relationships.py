import sqlalchemy
import sqlalchemy.orm as orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Relationship(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'relationships'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    holder = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    taker = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    book = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('books.id'))

    holder_user = orm.relationship('User', foreign_keys=[holder], backref='held_relationships')
    taker_user = orm.relationship('User', foreign_keys=[taker], backref='taken_relationships')
    book_orm = orm.relationship('Book', foreign_keys=[book], backref='book_relationships')
