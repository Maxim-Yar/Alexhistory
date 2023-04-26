import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# описание таблицы с пользователями в БД
class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    # описание полей таблицы
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    news = orm.relationship("News", back_populates='user')

    # возвращение данных о пользователе для последующих сравнений
    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    # хеширование паролей пользователя
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    # возвращение хешированного пароля
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
