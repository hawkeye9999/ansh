
from logging import debug
import os,time
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import json
from flask_mysqldb import MySQL
from check_login import hash_password, check_password, check_message
import MySQLdb.cursors
# from flask_oauthlib.client import OAuth
from pathlib import Path
import gc
from datetime import date
import datetime, base64, requests, pytz, jwt
from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY")
app.config['MYSQL_HOST'] = os.environ.get("HOST")
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'exam_portal'
# app.config['MYSQL_PASSWORD'] = 'Hp6J$BpGhe^{'
# app.config['MYSQL_DB'] = 'kjsieitexamportal'
app.config['GOOGLE_ID'] = "940087145192-fsbm0se399b5o2fjo01n95p81mr77vv5.apps.googleusercontent.com"
app.config['GOOGLE_SECRET'] = "w8z2AkmdFE4GvVa8O9dZ60YP"

#sending mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
mail = Mail(app)




# oauth = OAuth(app)
# google = oauth.remote_app(
#     'google',
#     consumer_key=app.config.get('GOOGLE_ID'),
#     consumer_secret=app.config.get('GOOGLE_SECRET'),
#     request_token_params={
#         'scope': 'email'
#     },
#     base_url='https://www.googleapis.com/oauth2/v1/',
#     request_token_url=None,
#     access_token_method='POST',
#     access_token_url='https://accounts.google.com/o/oauth2/token',
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
# )

mysql = MySQL(app)
app_root = app.root_path 
IST = pytz.timezone('Asia/Kolkata')

@app.route("/")
def load():
    return redirect(url_for('show_login'))
    # return render_template("home.html",message="")
    

################################## Login ##########################################

# @app.route('/google_login/')
# def login2():
#     return google.authorize(callback=url_for('authorized', _external=True))
     

# @app.route('/google_login/authorized')
# def authorized():
#     resp = google.authorized_response()
#     if resp is None:
#         return 'Access denied: reason=%s error=%s' % (
#             request.args['error_reason'],
#             request.args['error_description']
#         )
#     session['google_token'] = (resp['access_token'], '')
#     me = google.get('userinfo')
#     return redirect(url_for('show_login'))

# @google.tokengetter
# def get_google_oauth_token():
#     return session.get('google_token')

@app.route('/login/')
def show_login():

    # #print(session)
    try:
        assert session["flash_msg"]
    except (KeyError,AssertionError):
        session["flash_msg"] = ""
        
    if session.get("login") is not None:
        if session['login'] != 0:
            return redirect(url_for('dashboard'))
    elif 'google_token' in session:
        me = google.get('userinfo')
        personal_data = jsonify({"data": me.data})
        response = me.data        
        # msg = verify_email(response['email'])
        msg=""
        # #print(msg)
        if msg=="0":
            
            return render_template("login.html",message="Email ID does not exists in the database!")
        else:
            return redirect(url_for('dashboard'))
        # return personal_data
    else:
        msg = session["flash_msg"]
        session["flash_msg"] = ""
        return render_template("login.html",message=msg)

@app.route('/google_signin/', methods=['POST', 'GET'])
def google_login():
    return render_template("google_login.html")


def auth_encode(email,pwd,token_version,role):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=600),
        'iat': datetime.datetime.utcnow(),
        'email': email,
        'pass':pwd,
        'role':role,
        'token_version':token_version
    }
    token = jwt.encode(
        payload,
        app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )
    return token

def auth_decode(token,url,pwd):
    try:
        payload = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms=["HS256"])
        email = payload["email"]
        role = payload["role"]
        token_version = payload["token_version"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if url=="login.html":
            if role == "student":
                cursor.execute("UPDATE student SET S_pass = %s , first_login = %s WHERE S_email = %s",[pwd,1,email])
            elif role == "faculty":
                cursor.execute("UPDATE faculty SET F_password = %s , first_login = %s WHERE F_email = %s",[pwd,1,email])
            elif role == "admin":
                cursor.execute("UPDATE admin SET A_pass = %s , first_login = %s WHERE A_email = %s",[pwd,1,email])
            mysql.connection.commit()
            session["token_version"]+=1
            session["flash_msg"] = "Password Changed Successfully"

            return redirect(url_for("show_login"))
        else:
            try:
                if session["token_version"] == token_version:
                    return render_template(url,message="")
            except KeyError:
                return render_template("reset_password.html",err_msg_head="Cross Browser Access Unauthorized" ,err_msg="Go to the reset link from the same window or generate a new one.")
            else:
                raise jwt.ExpiredSignatureError
            
    except jwt.ExpiredSignatureError:
        return render_template("reset_password.html",err_msg_head = "Token Expired" ,err_msg="Please Try Resetting Your Password...")
    except jwt.InvalidTokenError:
        return render_template("reset_password.html",err_msg_head="Invalid Token" ,err_msg="Please Try Resetting Your Password...")      


def send_verification_mail(email,pwd,role,called_from):
    try:
        assert session["token_version"]
    except KeyError:
        session["token_version"] = 0
    print("Email:",email)
    print("role:",role)
    role = role.lower()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    flag = 0
    if role == "student":
        cursor.execute("Select * from student Where S_email = %s",[email])
        student = cursor.fetchone()
        flag = 1 if student else 0
    elif role == "faculty":
        cursor.execute("Select * from faculty Where F_email = %s",[email])
        faculty = cursor.fetchone()
        flag = 1 if faculty else 0
    elif role == "admin":
        cursor.execute("Select * from admin Where A_email = %s",[email])
        admin = cursor.fetchone()
        flag = 1 if admin else 0
            
    if flag == 0 and called_from == "Login":
        print("MAIL NOT SENT")
        session["flash_msg"] = "ERROR:  Provided Email ID does not exist under the selected role, please try again..."
        return redirect(url_for("show_login"))
    elif flag == 0 and called_from == "Pass_Change":
        f_msg = {}
        f_msg['title'] = "Provided Email ID does not exist under the selected role, please try again..." 
        f_msg['there'] = 1
        f_msg['mode'] = 0
        session['message'] = f_msg
        return redirect(url_for("show_profile"))
    session["token_version"] += 1
    token = auth_encode(email,pwd,session["token_version"],role)
    if called_from == "Login" or called_from=="Pass_Change":
        msg = Message(
            'Exam Portal Reset Password',
            sender = app.config["MAIL_USERNAME"],
            recipients = [email]
            )
        msg.html = f"Set your new login password <a href='{os.environ.get('DOMAIN')}/resetpassword?token={token}'> here </a>"
        mail.send(msg)
        print("MAIL SENT")
        if called_from == "Login":
            session["flash_msg"] = "Password reset mail sent if the email address provided is valid..."
            return redirect(url_for("show_login"))
        elif called_from == "Pass_Change":
            f_msg = {}
            f_msg['title'] = "Password reset mail sent if the email address provided is valid..." 
            f_msg['there'] = 1
            f_msg['mode'] = 1
            session['message'] = f_msg
            print("from pass changeeeee")
            return redirect(url_for("show_profile"))
        else:
            return redirect(url_for("show_login"))

@app.route('/form_login/', methods=['POST', 'GET'])
def login():
    # #print(session)
    name1 = request.form['username']
    pwd = request.form['pass']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM faculty WHERE F_email = %s', [name1])
    account = cursor.fetchone()
    if account:
        if check_password(pwd, account['F_password']):
            if account['first_login'] == 0:
                return send_verification_mail(name1,pwd,"faculty","Login")
            else:
                msg = 'Logged in successfully !'
                session['username'] = account['Designation'].upper()+" "+account['F_name'] +" "+ account['L_name']
                session['svv'] = account['F_id']
                session['gender'] = account['gender']
                session['login'] = 1
                session['mode'] = "Faculty"
                session['login_mode'] = "SVV"
                cursor.execute('SELECT dept_short FROM department where dept_name = %s',[account['dept']])
                department = cursor.fetchone()
                cursor.close()
                dept_short = department['dept_short']
                session['dept'] = dept_short
                img_found = 0
                if account['img'] != '':
                    img_file = os.path.join(app_root,"static/profile_pics/faculty_images/",dept_short,account['F_id'],account['img'])
                    # print(img_file)
                    print(os.path.exists(img_file))
                    if os.path.exists(img_file):
                        img_found = 1
                        session['img'] = os.path.join("/static/profile_pics/faculty_images/",dept_short,account['F_id'],account['img'])
                if img_found == 0:
                    if account['gender']=='F':
                        session['img'] = "/static/images/woman.png"
                    elif account['gender']=='M':
                        session['img'] = "/static/images/man.png"
                    else:
                        session['img'] = "images/user.png"
                return redirect(url_for('dashboard'))
        else:
            session["flash_msg"] = 'Incorrect Credentials !'
    else:        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE S_email = %s', [name1])
        student = cursor.fetchone()
        print("Student")
        print()
        if student :
            print("student['first_login']",student['first_login'])
            if check_password(pwd, student['S_pass']):
                if student['first_login'] == 0:
                    return send_verification_mail(name1,pwd,"student","Login")
                else:
                    msg = 'Logged in successfully !'
                    cursor.close()            
                    session['username'] = student['F_name'] +" "+ student['L_name']
                    session['svv'] = student['S_id']
                    session['gender'] = student['gender']
                    session['dept'] = student['dept']
                    session['sem'] = student['current_sem']
                    session['batch'] = student['batch']
                    session['roll'] = student['roll']
                    session['login'] = 1
                    session['mode'] = "Student"
                    session['login_mode'] = "SVV"
                    img_found = 0
                    year = ""
                    if student['current_sem'] == 1 or student['current_sem'] == 2:
                        year = "First-Year"
                    elif student['current_sem'] == 3 or student['current_sem'] == 4:
                        year = "Second-Year"
                    elif student['current_sem'] == 5 or student['current_sem'] == 6:
                        year = "Third-Year"
                    elif student['current_sem'] == 7 or student['current_sem'] == 8:
                        year = "Last-Year"
                    semester = "semester_"+str(student['current_sem'])
                    if student['image'] != '':
                        img_file = os.path.join(app_root,"static/profile_pics/student_images/",student['dept'],year,semester,student['S_id'],student['image'])
                        # print(img_file)
                        print(os.path.exists(img_file))
                        if os.path.exists(img_file):
                            img_found = 1
                            session['img'] = os.path.join("/static/profile_pics/student_images/",student['dept'],year,semester,student['S_id'],student['image'])
                    if img_found == 0:
                        if student['gender']=='F':
                            session['img'] = "/static/images/woman.png"
                        elif student['gender']=='M':
                            session['img'] = "/static/images/man.png"
                        else:
                            session['img'] = "images/user.png"
                    return redirect(url_for('dashboard'))
            else:
                session["flash_msg"] = "Incorrect Credentials!"
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM admin WHERE A_email = %s', [name1])
            admin = cursor.fetchone()

            # if admin:
            #     if not check_password(pwd,admin["A_pass"]):
            #         session["flash_msg"] = "Invalid Credentials!"
            #         return redirect(url_for("show_login"))
            #     else:
            #         if admin['first_login'] == 0:
            #             return send_verification_mail(name1,pwd,"admin","Login")

            if admin:
                msg = 'Logged in successfully !'
                cursor.close()            
                session['username'] = admin['F_name'] +" "+ admin['L_name']
                session['svv'] = admin['A_id']
                session['gender'] = admin['A_gender']
                if admin['dept'] == 'Information Technology':
                    session['dept'] = 'IT'
                session['login'] = 1
                session['mode'] = "Admin"
                session['login_mode'] = "SVV"
                if admin['A_gender']=='F':
                    session['img'] = "/static/images/woman.png"
                elif admin['A_gender']=='M':
                    session['img'] = "/static/images/man.png"
                else:
                    session['img'] = "images/user.png"
                return redirect(url_for('dashboard'))
            else:
                session["flash_msg"] = 'Incorrect Credentials !'
    return redirect(url_for("show_login"))

@app.route('/resetpassword/',methods=['GET','POST'])
def resetpassword():
        
    if request.method == "GET":
        try:
            assert request.args.get("forgotpassword")
            return render_template("reset_password.html",enter_email="true")
        except (KeyError,AssertionError):
            token = request.args.get("token")
            session["token"] = token
            return auth_decode(session["token"],url="reset_password.html",pwd="")
        
    if request.method == "POST":
        try:
            email = request.form["reset_pass_email"]
            role = request.form["options"]
            return send_verification_mail(email,"",role,"Login")
        except KeyError:
            pwd = hash_password(request.form["password"])
            return auth_decode(session["token"],url = "login.html",pwd = pwd)


def verify_email(email):
    # #print(email)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM faculty WHERE F_email= %s', [email])
    account = cursor.fetchone()
    cursor.close()
    if account:
        msg = 'Logged in successfully !'
        session.permanent = True
        session['username'] = account['F_name'] +" "+ account['L_name']
        session['fullname'] = account['F_namse'] +" "+ account['M_name']+" "+ account['L_name']
        session['svv'] = account['F_id']
        session['gender'] = account['gender']
        session['login'] = 2
        session['mode'] = "Faculty"
        session['login_mode'] = "google"
        session['img'] = account['img']
        session['dept'] = account['dept']
        session['num'] = account['F_num']
        
        # redirect(url_for('dashboard'))
        return "1"
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE S_email= %s', [email])
        student = cursor.fetchone()
        if student:
            msg = 'Logged in successfully !'
            cursor.close()            
            session['username'] = student['F_name'] +" "+ student['L_name']
            session['svv'] = student['S_id']
            session['dept'] = student['dept']
            session['sem'] = student['current_sem']
            session['batch'] = student['batch']
            session['roll'] = student['roll']
            session['login'] = 1
            session['mode'] = "Student"
            session['login_mode'] = "google"
            me = google.get('userinfo')
            response = me.data
            session['img'] = response['picture']
            # redirect(url_for('dashboard'))
            return "2"
        else:
            return "0"

from check_login import login_required

@app.route('/index/')
@login_required
def dashboard():
    print(session)
    if session['login'] == 1:
        msg = {}
        msg['title'] = "Welcome Back "+ session['username']
        msg['there'] = 1
        msg['mode'] = 2
        print(msg)
        session['message'] = msg
        session['login'] = 2
    else :
        msg=""
        if not session.get("message") is None:
            msg=session['message']
            session.pop('message',None)
    mode = session['mode']
    svv = session['svv']
    dt = datetime.datetime.today().strftime('%Y-%m-%d')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    qs = list()
    if mode=="Faculty":
        # cursor.execute('SELECT quiz_id,q_title,q_sub,q_date,q_time_start,q_time_end FROM quiz_det WHERE fac_inserted =%s AND q_date >= %s ORDER BY quiz_id DESC', (svv,dt))
        cursor.execute('SELECT quiz_id,q_title,q_sub,q_date,q_time_start,q_time_end,quiz_type FROM quiz_det WHERE fac_inserted =%s ORDER BY quiz_id DESC', [svv])
        records = cursor.fetchall()
        for row in records:
            row['q_date'] = datetime.datetime.strptime(row['q_date'], '%Y-%m-%d').strftime('%d/%m/%y')
            qs.append(row)
        print(qs)
    elif mode=="Admin":
        cursor.execute('SELECT COUNT(S_id) as Total_Stud FROM student')
        students = cursor.fetchone()
        qs.append(students)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(F_id) as Total_Fac FROM faculty')
        faculty = cursor.fetchone()
        qs.append(faculty)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) as Total_Sub FROM subject')
        subject = cursor.fetchone()
        qs.append(subject)
        print(qs)
    elif mode=="Student":
        if session.get('time_per_ques') is not None:
            session.pop('time_per_ques',None)
        if session.get('total_ques') is not None:
            session.pop('total_ques',None)
        if session.get('quiz_id') is not None:
            session.pop('quiz_id',None)
        if session.get('quiz_show') is not None:
            session.pop('quiz_show',None)
        if session.get('q_nos') is not None:
            session.pop('q_nos',None)
        if session.get('q_time_division') is not None:
            session.pop('q_time_division',None)
        if session.get('q_timer') is not None:
            session.pop('q_timer',None)
        if session.get('quiz_date') is not None:
            session.pop('quiz_date',None)
        if session.get('quiz_end') is not None:
            session.pop('quiz_end',None)
        if session.get('quiz_show') is not None:
            session.pop('quiz_show',None)
        if session.get('question_timer_finish') is not None:
            session.pop('question_timer_finish',None)
        if session.get('attempt_ques') is not None:
            session.pop('attempt_ques',None)
        if session.get('quiz_start') is not None:
            session.pop('quiz_start',None)
        if session.get('switch') is not None:
            session.pop('switch',None)
        if session.get('quiz_score') is not None:
            session.pop('quiz_score',None)
        if session.get('submitted_ques') is not None:
            session.pop('submitted_ques',None)            
        if session.get('ques_submitted') is not None:
            session.pop('ques_submitted',None)
        if session.get('not_submitted_ques_id') is not None:
            session.pop('not_submitted_ques_id',None)
        if session.get('current_ques') is not None:
            session.pop('current_ques',None)
        if session.get('q_nos') is not None:
            session.pop('q_nos',None)
        if session.get('to_be_submitted_answer') is not None:
            session.pop('to_be_submitted_answer',None)
        if session.get('total_ques') is not None:
            session.pop('total_ques',None)

        dept = session['dept']
        sem = session['sem']
        batch = session['batch']
        cursor.execute('SELECT quiz_type,quiz_id,q_title,q_sub,q_date,q_time_start,q_time_end,quiz_started FROM quiz_det WHERE q_date >= %s AND q_dept = %s AND q_sem = %s AND q_batch="All" OR  q_batch=%s ORDER BY quiz_id DESC', (dt,dept,sem,batch))
        records = cursor.fetchall()
        cursor.close()
        # #print(len(records))
        now = datetime.datetime.now(IST)
        today_time = now.strftime('%H:%M')
        # #print(today_time)
        # #print(dt)
        if len(records)>0:
            for row in records:
                st=datetime.datetime.strptime(row['q_time_start'],'%H:%M').time()
                end=datetime.datetime.strptime(row['q_time_end'],'%H:%M').time()
                t_time=datetime.datetime.strptime(today_time,'%H:%M').time()
                # #print(row)
                # #print(type(row))
                db_date = datetime.datetime.strptime(row['q_date'], '%Y-%m-%d').date()
                row['q_date'] = datetime.datetime.strptime(row['q_date'], '%Y-%m-%d').strftime('%d/%m/%y')
                # #print('db_date:',db_date)
                # #print('type(db_date):',type(db_date))
                dt1 = datetime.datetime.strptime(dt, '%Y-%m-%d').date()
                # #print('dt:',dt)
                # #print('type(dt):',type(dt))

                # subject = 'WN'
                # # #print(subject)
                sem = 'sem'+str(session['sem'])
                # #print(sem)
                if row['quiz_type']=='0':
                    subject = row['q_sub']
                    print(subject)
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('SELECT subject.course_code,subject.sub_name_long,subject.is_elective FROM subject INNER JOIN department ON department.dept_id = subject.dept_id AND subject.sem = %s AND subject.sub_name_long = %s AND department.dept_short = %s', (sem,subject,session['dept']))
                    elective_sub = cursor.fetchone()
                    if cursor.rowcount == 0:
                        cursor.execute('SELECT electives.course_code,electives.sub_name_long FROM electives INNER JOIN department ON department.dept_id = electives.dept_id AND electives.sem = %s AND electives.sub_name_long = %s AND department.dept_short = %s', (sem,subject,session['dept']))
                        elective_sub = cursor.fetchone()
                        if cursor.rowcount > 0:
                            elective_sub['is_elective'] = 1
                else:
                    elective_sub = {}
                    elective_sub['is_elective'] = 0
                    subject = 'Non-Subjective'
                # #print(elective_sub)
                subject_check = 0
                if elective_sub['is_elective'] == 1:
                    # #print("checking user elective")
                    cursor.execute('SELECT electives FROM student WHERE dept = %s AND S_id = %s', (session['dept'],session['svv']))
                    selected_electives = cursor.fetchone()
                    cursor.close()
                    if selected_electives['electives'] is not None:
                        sel_elect = selected_electives['electives'].split(",")
                        if sel_elect[-1] == '':
                            del sel_elect[-1]
                    else:
                        sel_elect = []
                    
                    if elective_sub['course_code'] in sel_elect:
                        subject_check = 1
                    else:
                        subject_check = 0
                else:
                    # #print("No need to check elective")
                    subject_check = 1
                # #print('subject_check:',subject_check)
                # db_date = datetime.date(row['q_date'], '%Y-%m-%d')
                if dt1 < db_date and subject_check==1:
                    # # #print("Appended1")
                    qs.append(row)
                elif (subject_check==1 and dt == db_date.strftime("%Y-%m-%d")) and  ((t_time<=st or t_time<end) or row['quiz_started']==1):
                    # # #print("Appended2")
                    qs.append(row)

    
    cursor.close()
    # #print(session)
    # if len(records)>0:
    #     return render_template('index.html', message=msg,quizes = qs,total_q = len(records))
    # else:
    colors = ['bg-gradient-primary2','bg-gradient-success','bg-gradient-info','bg-gradient-warning','bg-gradient-danger','bg-gradient-dark']
    msg = {}
    if mode=="Admin":
        msg = check_message()
        return render_template('index.html', message=msg, quizes = qs,total_q = len(qs),color=colors,mode = mode)
    elif mode=="Faculty":
        msg = check_message()
        if session.get('overtime') is not None:
            session.pop('overtime',None)
            msg['title'] = "You Can Edit the Quiz only before Quiz start Time!"
            msg['mode'] = 0
            msg['there'] = 1
            return render_template('index.html', message=msg, quizes = qs,total_q = len(records),color=colors,mode = mode)
    elif mode=="Student":
        if session.get('over_access') is not None:
            session.pop('over_access',None)
            msg['title'] = "Student Can't Access this Page, only accessible by Faculty!"
            msg['mode'] = 0
            msg['there'] = 1
            return render_template('index.html', message=msg, quizes = qs,total_q = len(records),color=colors,mode = mode)
    return render_template('index.html', message=msg, quizes = qs,total_q = len(records),color=colors,mode = mode)


@app.route('/profile/')
@login_required
def show_profile():
    # #print(session)
    mode = session['mode']
    svv = session['svv']
    login_mode = session['mode']
    msg = {}
    if session.get('message') is not None:
        msg = session['message']
        if msg['there'] == 1:
            msg = check_message()
    s_info = {'Name':'','roll':'','batch':'','num':'','sem':'','dept':'','gender':'','img':''}
    f_info = {'Name':'','num':'','dept':'','gender':'','img':''}
    a_info = {'Name':'','num':'','dept':'','gender':'','img':''}
    info = {}
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if mode=="Faculty":
        cursor.execute('SELECT * FROM faculty WHERE F_id = % s', [svv])
    elif mode=="Student":
        cursor.execute('SELECT * FROM student WHERE S_id = % s', [svv])
    elif mode=="Admin":
        cursor.execute('SELECT * FROM admin WHERE A_id = % s', [svv])

    account = cursor.fetchone()
    if account:
        cursor.close()
        if mode=="Faculty":
            f_info['Name'] = account['F_name'] +" "+ account['M_name'] + " " + account['L_name']
            f_info['num'] = account['F_num']
            f_info['dept'] = account['dept']
            f_info['gender'] = account['gender']
            f_info['img'] = account['img']
            f_info['mail'] = account['F_email']
            info = f_info
        elif mode=="Student":
            s_info['Name'] = account['F_name'] +" "+ account['M_name'] + " " + account['L_name']
            s_info['num'] = account['S_num']
            s_info['dept'] = account['dept']
            s_info['gender'] = account['gender']
            s_info['roll'] = account['roll']
            s_info['batch'] = account['batch']
            s_info['img'] = account['image']
            s_info['mail'] = account['S_email']
            s_info['sem'] = account['current_sem']
            info = s_info
        elif mode=="Admin":
            a_info['Name'] = account['F_name'] +" "+ account['M_name'] + " " + account['L_name']
            a_info['num'] = account['A_num']
            a_info['dept'] = account['dept']
            a_info['gender'] = account['A_gender']
            a_info['img'] = account['img']
            info = a_info
    else:
        msg['title'] = "Error while fetching data"
        msg['there'] = 1
        msg['mode'] = 0
    print("msg",msg)
    # print(info)
    # print(session)
    if mode=="Student":
        print(session)
        sem = 'sem'+str(session['sem'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT electives_category.category_id,electives_category.cat_name FROM electives_category \
             INNER JOIN department ON electives_category.dept_id = department.dept_id \
                 AND department.dept_short = %s AND electives_category.sem = %s",(session['dept'],sem))
        elective_categories = cursor.fetchall()
        print(elective_categories)
        cursor.execute("SELECT electives.sub_name_long,electives.course_code,electives.elective_category FROM electives \
             INNER JOIN department ON electives.dept_id = department.dept_id \
                 AND department.dept_short = %s AND electives.sem = %s",(session['dept'],sem))
        elective_subjects = cursor.fetchall()
        print(elective_subjects)
        cursor.execute("SELECT electives FROM student WHERE S_id = %s AND dept = %s",(session['svv'],session['dept']))
        selected_electives = cursor.fetchone()
        print(selected_electives)
        if selected_electives['electives'] is not None:
            sel_elect = selected_electives['electives'].split(",")
        else:
            sel_elect = []
        print(sel_elect)
        elective_cat = dict()
        for i in range(len(elective_categories)):
            e_cat = elective_categories[i]
            # elective_cat[i] = dict()
            all_dict = dict()
            all_dict['cat_name'] = e_cat['cat_name']
            elect_subs = list()
            elect_cat_id = list()
            elect_selected = 0
            for j in range(len(elective_subjects)):
                e_sub = elective_subjects[j]
                if e_sub['elective_category'] == e_cat['category_id']:
                    if e_sub['course_code'] in sel_elect:
                        print("Yes present")
                        if elect_selected == 0:
                            all_dict['selected_sub'] = e_sub['sub_name_long']
                            all_dict['selected'] = 1
                            elect_selected = 1
                        break
                    else:
                        elect_subs.append(e_sub['sub_name_long'])
                        elect_cat_id.append(e_sub['course_code'])
                        if elect_selected == 0:
                            all_dict['selected'] = 0
                    
            all_dict['categories'] = elect_subs
            all_dict['course_code'] = elect_cat_id
            elective_cat[i] = all_dict
        print(elective_cat)
        cursor.close()
        return render_template("profile.html",data=info,message=msg,elective = elective_cat)
    else:
        return render_template("profile.html",data=info,message=msg)

@app.route('/change_password/',methods=['POST'])
@login_required
def password_change():
    print("password change",session)
    name1 = request.form['email']
    pwd = ""
    return send_verification_mail(name1,pwd,session['mode'],"Pass_Change")


@app.route('/change_profile_pic/',methods=['POST'])
@login_required
def profile_photo_change():
    print(session)
    print(request.files)
    print(len(request.files))
    image = request.files['user_image']
    image_name =  image.filename.strip()
    print(image_name)
    mode = session['mode']
    if mode=="Faculty":
        dir_url = os.path.join("static/profile_pics/faculty_images",session['dept'],session['svv'])
        directory = os.path.join(app_root,dir_url)
        query = "UPDATE faculty SET img = %s WHERE F_id = %s"
        image_format = image_name.partition(".")
        image_name = session['svv']+'.'+image_format[-1]
        values = (image_name,session['svv'])
    elif mode=="Student":
        if session['sem'] == 1 or session['sem'] == 2:
            year = 'First-Year'
        elif session['sem'] == 3 or session['sem'] == 4:
            year = 'Second-Year'
        elif session['sem'] == 5 or session['sem'] == 6:
            year = 'Third-Year'
        elif session['sem'] == 7 or session['sem'] == 8:
            year = 'Last-Year'
        dir_url = os.path.join("static/profile_pics/student_images",session['dept'],year,'semester_'+str(session['sem']),session['svv'])
        directory = os.path.join(app_root,dir_url)
        # s_photo_file = os.path.join(directory,s_photo)
        query = "UPDATE student SET image = %s WHERE S_id = %s"
        image_format = image_name.partition(".")
        image_name = session['svv']+'.'+image_format[-1]
        values = (image_name,session['svv'])
    
    elif mode=="Admin":
        directory = os.path.join(app_root,"static/profile_pics/admin_images"+mode+"_images",session['dept'])
        # s_photo_file = os.path.join(directory,s_photo)
    # print(directory)
    Path(directory).mkdir(parents=True, exist_ok=True)
    for f in os.listdir(directory):
        os.remove(os.path.join(directory, f))
    image.save(os.path.join(directory,secure_filename(image_name)))
    session['img'] = os.path.join("/",dir_url,image_name)
    # print("session['img']",session['img'])
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, values)
    mysql.connection.commit()
    ajax_response = {}
    if os.path.exists(directory+'/'+image_name):
        ajax_response['uploaded'] = 1
    else:
        ajax_response['uploaded'] = 0
    return json.dumps(ajax_response)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.route('/signout/')
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('show_login'))

################################## Login ##########################################

if __name__ == "__main__":
    import logging
    # logging.basicConfig(filename='./error.log',level=logging.DEBUG)
    # print(USKS)
    app.run()

from sample import sample
from quiz.quiz import quiz
from student.student import student
app.register_blueprint(sample,url_prefix="/sample")
app.register_blueprint(quiz,url_prefix="/quiz")
app.register_blueprint(student,url_prefix="/student")

from admin import admin
app.register_blueprint(admin.admin,url_prefix="/admin")

