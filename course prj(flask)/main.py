from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user #новое
from werkzeug.security import check_password_hash, generate_password_hash #новое


app = Flask(__name__)
app.secret_key = 'master temo 1'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db' # Создание бд использующихся в проекте
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)
manager.login_view = 'login'


 


class Item(db.Model): # Таблица со всеми товарами
    iditem = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(40), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    describtion = db.Column(db.Text, nullable = True)
    text = db.Column(db.String(40), nullable = True)
    isActive = db.Column (db.Boolean, default = True)

    def __repr__(self):
        return self.title


class User(db.Model, UserMixin):# Таблица со всеми пользователями 
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(40), nullable = False)
    password = db.Column(db.String(40), nullable = False)
    #userrole = db.Column(db.Integer, nullable = False) # 1 - админ, 2 - модератор, 3 - обычный пользователь        


@manager.user_loader # новое
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/') #Главная страница
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template("base.html", data = items)


@app.route('/create', methods = ['POST', 'GET']) #Добавление товара
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        describtion = request.form['describtion']
        text = request.form['text']
        
        item = Item(title = title, price = price, describtion = describtion, text = text)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return redirect('/')
    return render_template('create.html')


@app.route('/profile') # Страница юзера
@login_required
def about():
    return render_template('profile.html')


@app.route('/login', methods = ['GET','POST']) # Страница с логином (Возможно нужно будет переделать/удалить)
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


@app.route('/register', methods = ['GET','POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    
    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('passwords are not equal')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password = hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            
            return redirect(url_for('login'))
    return render_template('register.html')




@app.route('/logout', methods = ['GET','POST']) # Страница с выходом из своего профиля
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


@app.route('/product/<id>')
def product(id):
    desc = Item.query.filter_by(iditem = id)
    return render_template('viewitem.html', data = desc)


if __name__ == "__main__":
    app.run(debug=True)