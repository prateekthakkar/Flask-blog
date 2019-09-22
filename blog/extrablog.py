from flask import Flask,render_template,request,session,json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

#open Json file in read mode only

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True #Create local_server Varible And give equalto True

app = Flask(__name__)

#check condition if you are working in local server or not
if(local_server): 
	#coonect with mysql database
	app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri'] #using parameter access local server uri 
#condition is  false then it will take production server uri
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = params['production_uri'] #using parameter access production server uri
db = SQLAlchemy(app) #initialize db 

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
	return render_template('index.html')

@app.route('/post/')
def Post():
	return render_template('post.html')

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

	return render_template('contact.html')

@app.route('/about/')
def About():
	return render_template('about.html')

if __name__ == "__main__":
	app.run(debug=True)