from flask import Flask,render_template,request,session,redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail 
import json
import smtplib
import math
import os
from werkzeug import secure_filename

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] =params['upload_location']
'''
#Mail Sending Error Occure
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
'''

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

#create class and clasa define database table 

class contact(db.Model):
	
	#contact table fileds name
    cid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),nullable=False)
    email = db.Column(db.String(50),nullable=False)
    phone_number = db.Column(db.String(15),nullable=False)
    message = db.Column(db.String(150),nullable=False)
    date  = db.Column(db.String(150),nullable=False)


    def __init__(self,name,email,phone_number,message,date):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.message = message
        self.date = date



@app.route('/')
def Home():
	posts = Posts.query.filter_by().all()
	last = math.ceil(len(posts)/int(params['no_of_posts']))
	page = request.args.get('page')
	if(not str(page).isnumeric()):
		page=1
	page= int(page)
	posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
	if(page==1):
		prev= "#"
		next = "/?page=" + str(page+1)
	elif(page==last):
		prev = "/?page=" + str(page-1)
		next= "#"

	else:
		prev= "/?page=" + str(page-1)
		next = "/?page=" + str(page+1)

	
	return render_template('index.html',params=params,posts=posts,prev=prev,next=next)


class Posts(db.Model):
	pid = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(30),nullable=False)
	content = db.Column(db.String(1500),nullable=False)
	date  = db.Column(db.String(30),nullable=False)
	slug = db.Column(db.String(30),nullable=False)
	img_file = db.Column(db.String(30),nullable=False)
	subtitle = db.Column(db.String(50),nullable=False)
	author = db.Column(db.String(15),nullable=False)

	def __init__(self,title,content,date,slug,img_file,subtitle,author):
		self.title = title
		self.content = content
		self.date = date
		self.slug  = slug
		self.img_file = img_file
		self.subtitle = subtitle
		self.author = author

@app.route("/post/<string:post_slug>",methods=["GET"])
def post_route(post_slug):
	post = Posts.query.filter_by(slug=post_slug).first()
	return render_template('post.html',params=params,post=post)

@app.route('/contacts',methods=['POST','GET'])
def Contact():
	if request.method == 'POST' :
		name = request.form.get('name')
		email = request.form.get('email')
		phone_number = request.form.get('phone_number')
		message = request.form.get('message')
		#insert Data Into Database 
		insert = contact(name=name,email=email,phone_number=phone_number,message=message,date=datetime.now())
		db.session.add(insert)
		db.session.commit()
		
		'''
		#mail error occure avoid
		mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message  + phone_number)'''

	return render_template('contact.html',params=params)

@app.route('/about/')
def About():
	return render_template('about.html',params=params)


@app.route('/dashboard/',methods=["POST","GET"])
def Dashboard():

	if 'user' in session and session['user'] == params['admin_user']:
		post = Posts.query.all()
		return render_template('dashboard.html',params=params,post=post)

	if request.method == "POST":
		username = request.form.get('uname')
		password = request.form.get('password')
		if (username == params['admin_user'] and password == params['admin_password']):
			#set session variable
			session['user'] = username
			post = Posts.query.all()
			return render_template('dashboard.html',params=params,post=post)
		#Redirect To Admin Login Page

	return render_template('login.html',params=params)


@app.route("/edit/<string:pid>",methods=["GET","POST"])
def Edit(pid):
	if ('user' in session and session['user'] == params['admin_user']):
		if request.method == "POST":
			box_title = request.form.get('title')
			content = request.form.get('content')
			date = datetime.now()
			slug = request.form.get('slug')
			img_file = request.form.get('img_file')
			subtitle = request.form.get('subtitle')
			author = request.form.get('author')

				
			if pid == '0':
				post = Posts(title=box_title,content=content,date=date,slug=slug,img_file=img_file,subtitle=subtitle,author=author)
				db.session.add(post)
				db.session.commit()
			else:
				post = Posts.query.filter_by(pid=pid).first()
				post.title = box_title
				post.content = content
				post.slug = slug
				post.img_file = img_file
				post.subtitle = subtitle
				post.author = author
				db.session.commit()
				return redirect('/edit/'+pid)
		post = Posts.query.filter_by(pid=pid).first()
		return render_template('edit.html',params=params,post=post,pid=pid)
	

@app.route("/login/")
def Login():
	return redirect('/dashboard')

@app.route("/logout/")
def Logout():
	session.pop("user")
	return redirect('/dashboard/')

@app.route("/Logout/")
def Logout2():
	session.pop("user")
	return redirect('/')

@app.route("/delete/<string:pid>",methods=["POST","GET"])
def Delete(pid):
	if 'user' in session and session['user'] == params['admin_user']:
		post = Posts.query.filter_by(pid=pid).first()
		db.session.delete(post)
		db.session.commit()
	return redirect('/dashboard/')



if __name__ == "__main__":
	app.run(debug=True)
