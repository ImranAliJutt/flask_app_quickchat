import base64
import io
from flask import Flask, Response, render_template, request, session, url_for
from flask_mysqldb import MySQL
import datetime 
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'your_secret_key_here'

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "root"
app.config['MYSQL_DB'] = "connection" 
app.config['UPLOAD_FOLDER'] = 'uploads'

mysql = MySQL(app)


@app.route('/')
@app.route('/login',methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        try:
            username = request.form['username']
            session['emailuser'] = username

            password = request.form['password']
            cur = mysql.connection.cursor()
            user1 = cur.execute("SELECT * FROM register WHERE username = %s AND password = %s", (username, password))
            if user1 > 0:
                userdetails = cur.fetchall()
                cur = mysql.connection.cursor()
                cur.execute("SELECT username, course.course_date, course.timing, course.coursedec FROM register INNER JOIN course ON regid = registerid")  # Fetch all courses from the course table
                course_data = cur.fetchall()
                cur.close()
                return render_template('navbar.html', emailuser=session['emailuser'], course_data= course_data )
            else:
                cur.close()  
                return render_template('login.html')
            
        except Exception as e:
            return f"An error occurred: {str(e)}"

        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        try:
            username=request.form['username']
            email = request.form['email']
            password = request.form['password']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO register (email, password,username) VALUES (%s, %s,%s)", (email, password,username))
            mysql.connection.commit()
            cur.close()
            return render_template('login.html')
        except Exception as e:
            return f"An error occurred: {str(e)}"
        
    return render_template('register.html')

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        try:
            post = request.form['post']
            current_date = datetime.date.today()
            current_time = datetime.datetime.now().time()
            
            cur = mysql.connection.cursor()
            emailuser = session['emailuser']
            cur.execute("SELECT regid FROM register WHERE username = %s", (emailuser,))
            user2id = cur.fetchone()[0]  
            cur.execute("INSERT INTO course (registerid, course_date, timing, coursedec) VALUES (%s, %s, %s, %s)", (user2id, current_date, current_time, post))
            mysql.connection.commit()
            cur.close()

            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM course") 
            course_data = cur.fetchall()
            cur.close()

            return render_template('navbar.html', emailuser=session.get('emailuser'), course_data=course_data)
        except Exception as e:
            return f"An error occurred: {str(e)}"
    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM course")  
            course_data = cur.fetchall()
            cur.close()
            return render_template('navbar.html', emailuser=session.get('emailuser'), course_data=course_data)
        except Exception as e:
            return f"An error occurred: {str(e)}"




@app.route('/user')
def user(debug='true'):
    try:
        cur = mysql.connection.cursor()
        user = cur.execute("SELECT * from register")
        if user > 0:
            userdetails = cur.fetchall()
            cur.close() 
            return render_template('user.html', userdetails=userdetails)
        else:
            cur.close()  
            return "No users found"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/')
def l():
    render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/checking')
def check():
    if 'emailuser' in session:
        return render_template('checking.html')
    else:
        return render_template('login.html')

@app.route('/user_profile' , methods=['GET' , 'POST'] )
def user_profile():
    session.clear()
    return render_template('login.html')


@app.route('/update_user', methods=['POST'])
def updates():
    username = request.form['username']
    emailuser = session['emailuser']
    if 'emailuser' in session:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE register SET username=%s WHERE username=%s", (username, emailuser))
        mysql.connection.commit() 
        cur.close()
        curuser= mysql.connection.cursor()
        curuser.execute("SELECT username, course.course_date, course.timing, course.coursedec FROM register INNER JOIN course ON regid = registerid") 
        course_data = curuser.fetchall()
        return render_template('navbar.html' , emailuser=session.get('emailuser'), course_data=course_data)

                




if __name__ == "__main__":
    app.secret_key = 'your_secret_key_here'
    app.run(debug=False,host='0.0.0.0')
