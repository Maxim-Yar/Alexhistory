from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.users import User
from data.news import News
from forms.user import RegisterForm, LoginForm
from forms.news import NewsForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
import json

app = Flask(__name__)
# создание ключа безопасности
app.config['SECRET_KEY'] = 'KOLASS_KUCA'
login_manager = LoginManager()
login_manager.init_app(app)

# вход в учетную запись, из которой не вышли из сессии в прошлом запуске
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# переход на главную страницу после входа
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

# создание api сервера
@app.route('/api/location', methods=['GET'])
def location():
    result = {}
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=Киров Александровский сад Кирова&format=json"
    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Печатаем извлечённые из ответа поля:
        result["address"] = toponym_address
        result["coord"] = toponym_coodrinates
    else:
        # возвращаем ощибку, если нет ответа от геокодера
        abort(504)
    # возвращаем ответ в формате json
    return json.dumps(result, sort_keys=True, ensure_ascii=False)

# переход на страницу входа в учетную запись
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # проверка введенных данных
    if form.validate_on_submit():
        # создание сессии
        db_sess = db_session.create_session()
        # проверка введкнных данных
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            # переход на главную страницу
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        # вывод предупреждения об ошибке
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

# переход главную страницу
@app.route("/")
def index():
    # создание новой формы и сессии
    form = NewsForm()
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    # переход на главную страницу
    return render_template("information.html", news=news, form=form)

# переход на форму регистрации
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    # проверка на введенные данные
    if form.validate_on_submit():
        # проверка на правильность ввода данных
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        # создание нового пользователя
        # внос нового пользователя в БД
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        # переход к странице входа в аккаунт
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

# страница создания комментария
@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    # провека на ввод данных
    if form.validate_on_submit():
        # создание нового коментария
        # внос нового комментария в БД
        db_sess = db_session.create_session()
        news = News()
        news.content = form.content.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        # переход на главную страницу
        return redirect('/')
    return render_template('news.html', title='Добавление комментария',
                           form=form)

# изменение новости
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    # проверка на запрос данных о данном коментарии
    if request.method == "GET":
        db_sess = db_session.create_session()
        # проверка на автора комментария или админа
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user or current_user.id == 0
                                          ).first()
        if news:
            form.content.data = news.content
        else:
            abort(404)
    # проверка на ввод данных
    if form.validate_on_submit():
        # проверка на автора или админа
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user or current_user.id == 0
                                          ).first()
        if news:
            # изменение и созранение нового комментария
            news.content = form.content.data
            db_sess.commit()
            # переход на главную страницу
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )

# удаление выбранного комментария
@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    # проверка на автора или админа
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user or current_user.id == 0
                                      ).first()
    if news:
        # удаление комментария и сохранение этого
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    # запуск программы
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
