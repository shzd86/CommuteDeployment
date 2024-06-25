from datetime import datetime
from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
home_data = []

# MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:8683@localhost/student'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.String(100), nullable=False)
    Place = db.Column(db.String(100), nullable=False)
    Time = db.Column(db.String(100), nullable=False)

class Present(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Date = db.Column(db.String(100), nullable=False)
    Present = db.Column(db.String(100), nullable=False)

class Home(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Time = db.Column(db.String(100), nullable=False)
    Date = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Reglog')
def reglog():
    return render_template('Reglog.html')
@app.route('/DriverLogin', methods=['POST'])
def DriverLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Driver.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('Driverdashboard')
        else:
            return render_template('driver_login.html', error='Invalid user')   

    


@app.route('/DriverRegister', methods=['POST'])
def DriverRegister():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = Driver.query.filter_by(email=email).first()
        if existing_user:
            return render_template('driver_login.html', error='User with this email already exists.')

        new_user = Driver(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('driver_login')

    return render_template('driver_login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session['email'] = user.email
        return redirect('/dashboard')
    else:
        return render_template('Reglog.html', error='Invalid user')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return render_template('Reglog.html', error='User with this email already exists.')

    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/Reglog')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)
    return redirect('/registration')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form.get('Name')
        phone = request.form.get('Phone')
        place = request.form.get('Place')
        time = request.form.get('Time')

        new_info = Info(Name=name, Phone=phone, Place=place, Time=time)
        db.session.add(new_info)
        db.session.commit()
        return "success"
    return render_template('registration.html')

@app.route('/prebook', methods=['GET', 'POST'])
def prebook():
    if request.method == 'POST':
        name = request.form.get('Name')
        date_str = request.form.get('Date')
        present = request.form.get('Present')

        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
        new_present = Present(Name=name, Date=date_obj, Present=present)
        db.session.add(new_present)
        db.session.commit()
        return "success"
    return render_template('prebook.html')

@app.route('/departure', methods=['GET', 'POST'])
def departure():
    if request.method == 'POST':
        name = request.form.get('Name')
        time = request.form.get('Time')
        date_str = request.form.get('Date')

        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
        new_home = Home(Name=name, Time=time, Date=date_obj)
        db.session.add(new_home)
        db.session.commit()
        return redirect('/departure')

    home_data = Home.query.order_by(Home.Date.desc(), Home.Time.asc()).all()
    return render_template('departure.html', home_data=home_data)

@app.route('/driver')
def driver():
    return render_template('driver.html')
@app.route('/Driverdashboard')
def driver_dashboard():
    home_data = Home.query.order_by(Home.Date.desc(), Home.Time.asc()).all()
    info_data = Info.query.all()
    present_data = Present.query.all()
    return render_template('DriverDashboard.html', home_data=home_data, info_data=info_data,present_data = present_data)

@app.route('/logoutt')
def logoutt():
    return render_template('login.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/driver_login')
def driver_login_page():
    return render_template('driver_login.html')

@app.route('/logout')
def logout():   
    session.pop('email', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
