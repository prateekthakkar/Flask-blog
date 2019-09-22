from flask import Flask,render_template,request,session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail 
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
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
    return render_template('index.html',params=params)

@app.route('/post/')
def Post():
    return render_template('post.html',params=params)

@app.route('/contacts',methods=['POST','GET'])
def Contact():
    if request.method == 'POST' :
        name = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        message = request.form.get('message')
      
        insert = contact(name=name,email=email,phone_number=phone_number,message=message,date=datetime.now())
        db.session.add(insert)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone_number
                          )

    return render_template('contact.html',params=params)

@app.route('/about/')
def About():
    return render_template('about.html',params=params)

if __name__ == "__main__":
    app.run(debug=True)