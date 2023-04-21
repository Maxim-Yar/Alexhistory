from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField


class NewsForm(FlaskForm):
    content = TextAreaField("Содержание")
    submit = SubmitField('Добавить')
