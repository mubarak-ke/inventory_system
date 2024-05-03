from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from datetime import datetime
from flask import Flask,render_template,request,redirect,url_for,flash,abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_migrate import Migrate# pip install flask-migrate
from flask_login import UserMixin,login_required,login_user,current_user,LoginManager,logout_user#pip install flask-login
from flask_wtf import FlaskForm#pip install flask-wtf
from wtforms import StringField,PasswordField,SubmitField, BooleanField
from wtforms.validators import InputRequired,Length,ValidationError,EqualTo,Email
from werkzeug.security import check_password_hash
from flask_bcrypt import Bcrypt#pip install flask-bcrypt
from database import insert_sales, sales_per_day,total_sales, todays_profit,total_profit,sales_product,profit_product,profit_day,sales_day,get_remaining_stock_per_product
app=Flask(__name__)
app.config['SQLalchemy_Track_Modification']=False
app.config['SECRET_KEY']='supersecretkey'#secret key
connection_string=app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:mubby@localhost/myduka_system'

db=SQLAlchemy(app) #import sqalchemy
engine=create_engine(connection_string)
bcrypt=Bcrypt (app)#to hash and verify passwords
app.app_context().push()

Migrate(app, db)#to use migrate open terminal and write(flask db init)after that write (flask  db migrate -m "initial migration")(then flask db upgrade)

login_manager=LoginManager(app)
login_manager.init_app(app)
login_manager.login_view="login"
#it updates the user using the user ID that stored in session
@login_manager.user_loader
def load_user(user_id):#this function will be called by login manager to load user
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    __tablename__="users"
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(64), unique=True,nullable=False)
    email=db.Column(db.String(125), unique=True, nullable=False)
    password=db.Column(db.String(120),nullable=False)
    date_created=db.Column(db.DateTime(),default=datetime.now, index=True)
   

# class UserModelView(ModelView):
#     def on

class Product(db.Model):
    __tablename__="products" 
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80))
    buying_price=db.Column(db.Numeric(10,2),nullable=False)
    selling_price=db.Column(db.Numeric(19,2),nullable=False)
    stock_quantity=db.Column(db.Integer,nullable=False)
    sales=db.relationship('Sale', backref='Product')

class Sale(db.Model):
    __tablename__="sales"
    id=db.Column(db.Integer, primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey("products.id"),nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    created_date=db.Column(db.DateTime, default=datetime.utcnow)
class registerForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(
        min=4,max=20)],render_kw={"placeholder":"Username"})
    
    email = StringField('Email', validators=[InputRequired(), Email()],render_kw= {"placeholder": "Enter Email"})#pip install email_validaor
    password = PasswordField('Password', validators=[InputRequired(),Length(
        min=4,max=20)],render_kw= {"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password',[EqualTo('password'),InputRequired()])
    submit = SubmitField('register')
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken! Please choose a different one.')
    
#login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()],render_kw= {"placeholder": "Enter Email"})
    password = PasswordField('Password', validators=[InputRequired(),Length(
        min=4,max=20)],render_kw= {"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
@app.route('/')
def home():
    return render_template('home.html') 
@app.route('/contact')
def contact():
    return render_template('contact.html')  

@app.route('/dashboard')
@login_required
def dashboard():
    spp=sales_per_day()
    ts=total_sales()
    tp= todays_profit()
    total=total_profit()
    print(total)


    
    
    sp=sales_product()
    pp=profit_product()
    sd=sales_day()
    pd=profit_day()
    pl=[]
    days=[]
    for m in pd:
        pl.append(float(m[1]))
        days.append(str(m[0]))


    sl=[]
    day=[]
    for p in sd:
        sl.append(float(p[1]))
        day.append(str(p[0]))


    name=[]
    pr=[]
    for i in pp:
        name.append(str(i[0]))
        pr.append(float(i[1]))
    names=[]
    values=[]
    for i in sp:
         names.append(str(i[0]))
         values.append(float(i[1]))

    #this query calculates the remaining stock for each productby subtractingthe total quantity sold from the total qauntity available
    remaining_stock=get_remaining_stock_per_product()
    remaining_stock_label=[]
    remaining_stock_data=[]
    for r in remaining_stock:
        remaining_stock_label.append(str(r[0]))
        remaining_stock_data.append(float(r[1]))

    return render_template( 'dashboard.html',names=names,val=values,pr=pr,name=name,sale=sl,day=day,days=days,profit=pl,spp=spp,ts=ts,tp=tp,total=total ,remaining_stock_data=remaining_stock_data ,remaining_stock_label=remaining_stock_label)

#logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out!","info")
    return redirect(url_for("login")) 
# form of sign up
#register
@app.route('/signup', methods=['GET', 'POST'])
def register():
    # form = registerForm()

    # if request.method == "POST":
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=registerForm()
    if form.validate_on_submit():
            hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}! You are now able to log in','success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)
    #     existing_user_username=user.query.filter_by(username=form.username.data).first()
    #     if existing_user_username:
    #         raise ValidationError('User already exists!','danger')
    #     if form.validate_on_submit():
    #         hashed_password=bcrypt.generate_password_hash(form.password.data)
    #         user = User(username=form.username.data, email=form.email.data, password=hashed_password)
    #         db.session.add(user)
    #         db.session.commit
    #         return redirect(url_for('login'))
    # else:
    #     return render_template('register.html', form=form)
#login
@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):#here we check if the password is correct 
            login_user(user,remember=form.remember.data) 
            next_page=request.args.get('next')#this will take us to where ever we want to go after logging in
            flash('Login successful!', 'success')
                # Here you might redirect to a profile page or another protected route
            return redirect(next_page)if next_page else redirect(url_for("home"))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html',form=form)
#route ofproducts
@app.route("/products")
def products():
    products=Product.query.all()
    return render_template("product.html",products=products)

@app.route('/insert', methods=['POST'])
@login_required
def insert():
    if request.method == 'POST':
        pname = request.form['product_name']
        b_price = request.form['buying_price']
        s_price = request.form['selling_price']
        s_quantity = request.form['stock_quantity']
        my_data = Product(name=pname, buying_price=b_price, selling_price=s_price, stock_quantity=s_quantity)
        db.session.add(my_data)
        db.session.commit()
        flash(f'Product Inserted Successfuly for:{pname}','success')
        return redirect(url_for('products'))
#update and delete
@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():

    if request.method == 'POST':
        my_data = Product.query.get(request.form.get('id'))

        my_data.name = request.form['product_name']
        my_data.buying_price = request.form['buying_price']
        my_data.selling_price = request.form['selling_price']
        my_data.stock_quantity = request.form['stock_quantity']

        db.session.commit()
        flash(f'Product Inserted Successfuly for:{my_data.name}','success')

        return redirect(url_for('products'))

@app.route('/delete/<id>/', methods = ['GET', 'POST'])
@login_required
def delete(id):
    my_data = Product.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash(f'Product Deleted Successfully For: {my_data.name}','success')

    return redirect(url_for('products'))
#sales
# creating a route for sales
@app.route("/sales")
@login_required
def sales():
    sales=Sale.query.all()
    products=Product.query.all()
    return render_template('sales.html',sales=sales,products=products,title="Sales")

# a route for adding sales
@app.route("/make_sale", methods=['POST'])
@login_required
def make_sale(): 
    try:     
        # Fetch form data
        pid = int(request.form['pid'])
        quantity = int(request.form['quantity'])

        # Fetch products and validate quantity
        product = Product.query.get(pid)
        if not product:
            flash("Invalid product ID", 'error')
            return redirect(url_for("sales"))

        stock = product.stock_quantity
        if quantity <= 0 or quantity > stock:
            flash("Invalid quantity", 'error')
            return redirect(url_for("sales"))

        # Proceed with the sale
        values = (pid, quantity)
        print("values",values)
        insert_sales(values)
        flash(f'Sales made successfully for {quantity} {product.name}', 'success')

    except ValueError: 
        flash("Invalid quantity", 'error')
    except Exception as e: 
        flash(f'Failed to make sale: {str(e)}', 'error')

    return redirect(url_for("sales"))
db.create_all()
if __name__ == '__main__':
    app.run(debug=True)

