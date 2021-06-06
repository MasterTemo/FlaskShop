from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update, delete, insert
from sqlalchemy.exc import InvalidRequestError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user #новое
from werkzeug.security import check_password_hash, generate_password_hash #новое
from cloudipsp import Api, Checkout


app = Flask(__name__)
app.secret_key = 'master temo 1'


# настройка конфигурации бд и логин мэнеджера
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)
manager.login_view = 'login'


# Таблица с категориями товаров
class category(db.Model):
    categid = db.Column(db.Integer, primary_key = True) 
    name = db.Column(db.Text, nullable = False)
    catedesc = db.Column(db.Text, nullable = True)


class help(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    name = db.Column(db.Text, nullable = False)
    Email = db.Column(db.Text, nullable = True)
    problem = db.Column(db.Text,nullable = False)


# Таблица со всеми товарами
class Item(db.Model): 
    iditem = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(40), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    describtion = db.Column(db.Text, nullable = True)
    text = db.Column(db.String(40), nullable = True)
    isActive = db.Column(db.Boolean, default = True)
    category = db.Column(db.Text, nullable = True)
    def __repr__(self):
        return self.title


# Таблица со всеми пользователями
class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(40), nullable = False, unique = True)
    password = db.Column(db.String(40), nullable = False)
    userpic = db.Column(db.Text, nullable = True)
    userinfo = db.Column(db.Text, nullable = True)
    #userrole = db.Column(db.Integer, nullable = False) # 1 - админ, 2 - модератор, 3 - обычный пользователь        


#Сообщения для форума
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024), nullable=False)
    def __init__(self, text, tags):
        self.text = text.strip()
        self.tags = [
            Tag(text=tag.strip()) for tag in tags.split(',')
        ]


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(32), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    message = db.relationship('Message', backref=db.backref('tags', lazy=True))


class reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024), nullable=False)
    def __init__(self, text, tagrep):
        self.text = text.strip()
        self.tagrep = [
            Tag(text=tagtagrep.strip()) for tagtagrep in tagrep.split(',')
        ]


class Tagrep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(32), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=False)
    reply = db.relationship('reply', backref=db.backref('tagrep', lazy=True))


class order(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    product = db.Column(db.Text, nullable = False)


# Логин менеджер
@manager.user_loader 
def load_user(user_id):
    return User.query.get(user_id)


#Главная страница
@app.route('/') 
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template("base.html", data = items, reply = reply.query.all())


#Маленький форум, где люди могут общаться и здававать друг-другу вопросы
@app.route('/forum', methods=['GET'])
@login_required
def forum():
    return render_template("forum.html", messages=Message.query.all())


#Станица с отзывами
@app.route('/add_reply', methods=['POST'])
@login_required
def add_reply():
    text = request.form['text']
    tag = request.form['tagrep']
    db.session.add(reply(text, tagrep))
    db.session.commit()
    return redirect(url_for('/product/<id>'))


#Страница добавления сообщений на мини-форум
@app.route('/add_message', methods=['POST'])
@login_required
def add_message():
    text = request.form['text']
    tag = request.form['tag']
    db.session.add(Message(text, tag))
    db.session.commit()
    return redirect(url_for('forum'))


@app.route('/help', methods = ['POST', 'GET'])
def helpuser():
    if request.method == "POST":
        name = request.form['name']
        Email = request.form['Email']
        problem = request.form['problem']
        me = help(name = name, Email = Email, problem = problem)
        try:
            db.session.add(me)
            db.session.commit()
            return redirect('/complete')
        except:
            return redirect('/complete')
    return render_template('help.html')


#Добавление товаров
@app.route('/create', methods = ['POST', 'GET']) 
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        describtion = request.form['describtion']
        text = request.form['text']
        category = request.form['category']
        item = Item(title = title, price = price, describtion = describtion, text = text, category = category)
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return redirect('/')
    return render_template('create.html')


@app.route('/complete')
def complete():
    return render_template('complete.html')


# Информация о товаре
@app.route('/product/<id>')
def product(id):
    desc = Item.query.filter_by(iditem = id)
    return render_template('viewitem.html', data = desc)


# Страница юзера
# Вывод минимальной информации(описание и изображение профиля)
@app.route('/profile/') 
@login_required
def about():
    return render_template('profile.html')


# Страница с логином
@app.route('/login', methods = ['GET','POST']) 
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect('/')
        else:
            flash('Неправильный логин или пароль')
            return render_template('login.html')
    else:
        flash('Добро пожаловать на наш сайт :)')
        return render_template('login.html')


#Регистрация пользователя
#Требуется ввести логин, пароль и подтверждение пароля
#Пароли хэшируются с помощью библиотеки werkzeug.security
@app.route('/register', methods = ['GET','POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    userpic = request.form.get('userpic')   
    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif InvalidRequestError:    
            flash('Логин уже использован другим пользователем')
        elif password != password2:
            flash('passwords are not equal')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password = hash_pwd, userpic = userpic)
            db.session.add(new_user)
            db.session.commit()          
            return redirect(url_for('login'))
    return render_template('register.html')


#Старница редактирования инфы о юзере 
#Отдельные страницы для редактирования описания профиля и изображения профиля
#перекинуть в осной код
@app.route('/editprofile/<id>', methods = ['GET','POST'])
@login_required
def editprofile(id):
    userinform = User.query.get(id)
    if request.method == "POST":
        if request.form['userinfo'] == "":
            userinform.userinfo =  userinform.userinfo
        else:
            userinform.userinfo = request.form['userinfo']
        if request.form['login'] == "":
            userinfom.login = userinform.login
        elif InvalidRequestError:
            flash('Логин уже используется:(')
            return redirect('/editprofile/<id>')
        else:
            userinform.login = request.form['login']
        try:
            db.session.commit()
            return redirect('/profile')
        except:
            return "Ошибка"
    else:
        return render_template('editprofile.html', userinform = userinform)


@app.route('/editpic/<id>', methods = ['GET', 'POST'])
@login_required
def editpic(id):
    userpict = User.query.get(id)
    if request.method == "POST":
        if request.form['userpic'] == "":
            userpict.userpic = userpict.userpic
        else:
            userpict.userpic = request.form['userpic']       
        try:
            db.session.commit()
            return redirect('/profile')
        except:
            return "Ошибка"
    else:
        return render_template('editpic.html', userpict = userpict)

#перекинуть в основной код
@app.route('/edititem/<id>', methods = ['GET','POST'])
def edititem(id):
    iteminform = Item.query.get(id)
    if request.method == "POST":
        if request.form['price'] == "":            
            iteminform.price = iteminform.price
        else:
            iteminform.price = request.form['price']
        if request.form['text'] == "":
            iteminform.text = iteminform.text
        else:
            iteminform.text = request.form['text']
        if request.form['title'] == "":
            iteminform.title = iteminform.title
        else:
            iteminform.title = request.form['title']
        if request.form['category'] == "":
            iteminform.category = iteminform.category
        else:
            iteminform.category = request.form['category']
        if request.form['describtion'] == "":
            iteminform.describtion = iteminform.describtion
        else:
            iteminform.describtion = request.form['describtion']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка"
    else:

        return render_template('edititem.html', iteminform = iteminform)


@app.route('/product/<iditem>/del')
@login_required
def delete(iditem):
    article = Item.query.get(iditem)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect("/")
    except:
        return "Error"


# Страница с выходом из своего профиля  (Возможно нужно будет переделать/удалить)
@app.route('/logout', methods = ['GET','POST']) 
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "Success")
    return redirect('/')


@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/supredirect')
def supredirect():
    return render_template('supredirect.html')


#Покупка товара с помощью стороннего сервиса оплаты
#пофиксить выдачу id + title в другую таблицу
@app.route('/buy/<id>')
@login_required
def item_buy(id):
    item = Item.query.get(id)
    api = Api(merchant_id=1396424,
        secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/location')
def location():
    return render_template('location.html')


@app.route('/aboutus')
@login_required
def aboutus():
    return render_template('aboutus.html')


@app.route('/FAQ')
def questions():
    return render_template('FAQ.html')


@app.route('/FAQ/FAQregister')
def questionreg():
    return render_template('FAQreg.html')


@app.route('/FAQ/FAQbuy')
def questionbuy():
    return render_template('FAQbuy.html')


@app.route('/FAQ/FAQedit')
def questionedit():
    return render_template('FAQedit.html')


if __name__ == "__main__":
    app.run(debug=True)





