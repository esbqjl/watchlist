from flask import Flask,render_template
from flask import url_for, request, redirect, flash
import click
from markupsafe import escape
import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
# 在扩展类实例化前加载配置

db = SQLAlchemy(app)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method== 'POST':
        title = request.form.get('title')
        year=request.form.get('year')
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input') #显示错误提示
            return redirect(url_for('index'))
        movie = Movies(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    movies = Movies.query.all()
    return render_template('index.html',movies=movies)
@app.route('/home')
@app.route('/hello')
def hello():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'
@app.route('/user/<name>')
def user_page(name):
    return f'User:{escape(name)}'
@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page',name="wenjun"))
    print(url_for('user_page',name='peter'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for',num=2))
    return 'Test_page'

@app.cli.command()
def forge():
    db.create_all()
    name = 'Wenjun'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    click.echo('Done.')
    for m in movies:
        movie = Movies(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash=db.Column(db.String(128))
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)
class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))
    
@app.cli.command()
@click.option('--drop',is_flag=True,help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

@app.context_processor
def inject_user():
    user=User.query.first()
    return dict(user=user)
@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
def edit(movie_id):
    movie = Movies.query.get_or_404(movie_id)
    if request.method=='POST':
        title=request.form['title']
        year=request.form['year']
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input')
            return redirect(url_for('edit',movie_id=movie_id))
        movie.title=title
        movie.year=year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
def delete(movie_id):
    movie=Movies.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))
import click
@app.cli.command()
@click.option('--username',prompt=True,help="The username used to login.")
@click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True,help='The password used to login.')
def admin(username, password):
    '''Create User.'''
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating User...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
        
    db.session.commit()
    click.echo('Done.')