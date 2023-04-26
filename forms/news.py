from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField

# описание формы создания и изменения комментария
class NewsForm(FlaskForm):
    # описание полей ввода и кнопок
    content = TextAreaField("Содержание")
    submit = SubmitField('Добавить')
