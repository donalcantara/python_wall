from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app, 'wall')

app.secret_key = "ThisIsSecret!"

@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	password = request.form['password']
	query = "SELECT * FROM users WHERE users.username = :username LIMIT 1"
	data = {'username': username}
	user = mysql.query_db(query, data)
	session['id'] = user[0]['id']
	session['username'] = user[0]['username']
	if len(user) == 0:
		flash('There is no account with that username!')
		return redirect('/')
	if user[0]:
		if user[0]['password'] == password:
			session['username'] = request.form['username']
			return redirect('/wall')
		else:
			flash("Incorrect email and/or password!")
			return redirect('/')

@app.route('/register', methods=['POST'])
def submit():
	email = request.form['email']
	username = request.form['user']
	session['name'] = request.form['name']
	session['user'] = request.form['user']
	session['email'] = request.form['email']
	session['password'] = request.form['password']
	error = 0
	if session['name'].isalpha() == True:
		flash("Name cannot contain numbers!")
		error += 1
	if len(request.form['user']) < 1:
		flash("User name cannot be blank!")
		error += 1
	if len(request.form['name']) < 1:
		flash("Name cannot be blank!")
		error += 1
	if len(request.form['email']) < 1:
		flash("Email cannot be blank!")
		error += 1
	if len(request.form['password']) < 8:
		flash("Password cannot be less than 8 characters!")
		error += 1
	if len(request.form['password']) != len(request.form['confirm']):
		flash("Confirmed password doesn't match!")
		error += 1
	if error > 0:
		print error
		return redirect('/')
	user = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
	data = {'email': email}
	user = mysql.query_db(user, data)
	if len(user) > 0:
		flash('That email is already registered!')
		return redirect('/')
	user = "SELECT * FROM users WHERE users.username = :user LIMIT 1"
	data = {'user': username}
	user = mysql.query_db(user, data)
	if len(user) > 0:
		flash('That username is already taken!')
		return redirect('/')
	if error == 0:
		query = "INSERT INTO users(name, username, email, password, created_at, updated_at) VALUES (:name, :user, :email, :password, NOW(), NOW())"
		data = {
			'name': request.form['name'],
			'user': request.form['user'],
			'email': request.form['email'],
			'password': request.form['password']
			}
		user = mysql.query_db(query, data)
		flash("Great!  Now log in below!")
		return redirect('/')

@app.route('/')
def index():
	query = "SELECT * FROM users"
	users = mysql.query_db(query)
	session['id'] = users[0]['id']
	return render_template('index.html', users = users)

@app.route('/wall')
def wall():
	posts = mysql.query_db("SELECT posts.content, posts.created_at, users.name, users.username, users.id, posts.id AS pos_id FROM posts join users ON users.id = posts.user_id")
	comments = mysql.query_db("SELECT * FROM users JOIN comments on users.id = comments.user_id")
	return render_template('wall.html', posts=posts, comments=comments)

@app.route('/post/<user_id>', methods=['POST'])
def post(user_id):
	message = request.form['message']
	query = 'INSERT INTO posts (user_id, content, created_at, updated_at) VALUES (:id, :post, NOW(), NOW())'
	data = {
		'id': user_id,
		'post': message
		}
	posts = mysql.query_db(query, data)
	return redirect('/wall')

@app.route('/comment/<post_id>/<user_id>', methods=["POST"])
def comment(post_id, user_id):
	comm = request.form['comment']
	print comm
	query = 'INSERT INTO comments (user_id, post_id, content, created_at, updated_at) VALUES (:user_id, :post_id, :comment, NOW(), NOW())'
	data = {
		'user_id': user_id,
		'post_id': post_id,
		'comment': comm
		}
	mysql.query_db(query, data)
	return redirect('/wall')


@app.route('/logout')
def logout():
	session['email'] = []
	session['username'] = []
	session['password'] = []
	return redirect('/')

@app.route('/delete/<user_id>')
def delete(user_id):
	query = "DELETE FROM users WHERE id = :id" #this is the query
	data = {'id': user_id} #this is the data
	mysql.query_db(query, data) #this is the result from the query with the data from the db
	return redirect('/') #redirect back to the front page

# @app.route('/update/<friend_id>', methods=['POST'])
# def update(friend_id):
# 	query = "UPDATE friends SET first_name = :first_name, last_name = :last_name, occupation = :occupation, updated_at = NOW() WHERE id = :id" #the query that you're updating info from the db back to the db
# 	data = { #this is the data you'll be updating in the db
# 		'first_name': request.form['first_name'], 
# 		'last_name':  request.form['last_name'],
# 		'occupation': request.form['occupation'],
# 		'id': friend_id
# 		}
# 	mysql.query_db(query, data)
# 	return redirect('/')

# @app.route('/edit/<friend_id>', methods=['POST'])
# def show(friend_id): #friend_id is the variable that you're passing
# 	query = "SELECT * FROM friends WHERE id = :specific_id" #this is the query you're sending to the database
# 	data = {'specific_id': friend_id} # this is the data you're sending to the datbase
# 	friends = mysql.query_db(query, data) #combine the query with the data and you'll get back data from the database
# 	return render_template('edit.html', friends=friends) #this sends you to the edit.html page with friends being the data you requested

app.run(debug=True)















