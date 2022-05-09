from flask import Blueprint, request, render_template, abort, session, redirect, url_for
from app import mysql
import MySQLdb.cursors
from datetime import date
from decimal import Decimal
import datetime
import json,pytz,requests, base64, math
from check_login import login_required

quiz = Blueprint('quiz', __name__,template_folder='templates')
IST = pytz.timezone('Asia/Kolkata')
# @quiz.route('/home')
# @quiz.route('/')
# def quizes_all_a():
#     return render_template('all_quizes.html',message = "", quizes = "",total_q = len(0),color=[])
    

@quiz.route('/all_quizes/')
@login_required
def quizes_all():
    mode = session['mode']
    svv = session['svv']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    qs = list()
    colors = ['bg-gradient-primary2','bg-gradient-success','bg-gradient-info','bg-gradient-warning','bg-gradient-danger','bg-gradient-dark']
    if mode=="Faculty":
        cursor.execute('SELECT quiz_id,q_title,q_sub,q_date,q_time_start,q_time_end FROM quiz_det WHERE fac_inserted =%s ORDER BY quiz_id DESC', [svv])
        records = cursor.fetchall()
        cursor.close()
        for row in records:
            row['q_date'] = datetime.datetime.strptime(row['q_date'], '%Y-%m-%d').strftime('%d/%m/%y')
            qs.append(row)
        return render_template('all_quizes.html', message="", quizes = qs,total_q = len(records),color=colors)
    elif mode=="Student":
        dept = session['dept']
        sem = session['sem']
        batch = session['batch']
        cursor.execute('SELECT quiz_id,q_title,q_sub,q_date,q_time_start,q_time_end FROM quiz_det WHERE q_dept = %s AND q_sem = %s AND q_batch="All" OR  q_batch=%s ORDER BY quiz_id DESC', (dept,sem,batch))
        records = cursor.fetchall()
        cursor.close()
        for row in records:
            row['q_date'] = datetime.datetime.strptime(row['q_date'], '%Y-%m-%d').strftime('%d/%m/%y')
            qs.append(row)
        return render_template('all_quizes.html', message="", quizes = qs,total_q = len(records),color=colors)

@quiz.route('/CreateQuiz/')
@login_required
def create_quiz():
    if not session.get("mode") is None:
        if session['mode']=="Faculty":
            return render_template("create_quiz.html")
        return redirect(url_for('bad_request'))

@quiz.route('/check_others_time/',methods=['POST'])
def check_other_quiz_time():
    dept =  request.form['dept']
    sem = request.form['sem']
    batch =  request.form['batch']
    if session.get('quiz_id') is not None:
        quiz_id = session['quiz_id']
    date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    print("Date:",date)
    print("dept:",dept)
    print("sem:",sem)
    print("batch:",batch)
    s_time =  datetime.datetime.strptime(request.form['s_time'],'%H:%M').time()
    e_time =  datetime.datetime.strptime(request.form['e_time'],'%H:%M').time()
    # #print("s_time:",s_time)
    # #print("e_time:",e_time)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if session.get('quiz_id') is None:
        cursor.execute('SELECT q_title,quiz_started,q_time_start,q_time_end,fac_inserted FROM quiz_det WHERE q_date = %s AND q_dept = %s AND q_sem = %s AND q_batch = %s', (date,dept,sem,batch))
    else:
        cursor.execute('SELECT q_title,quiz_started,q_time_start,q_time_end,fac_inserted FROM quiz_det WHERE q_date = %s AND q_dept = %s AND q_sem = %s AND q_batch = %s AND quiz_id!=%s', (date,dept,sem,batch,quiz_id))
    # # #print(cursor._last_executed)
    records = cursor.fetchall()
    cursor.close()
    print(records)
    i = 0
    quiz_another_running = 0
    if records:    
        for row in records:
            f_stime = datetime.datetime.strptime(row['q_time_start'],'%H:%M').time()
            f_etime = datetime.datetime.strptime(row['q_time_end'],'%H:%M').time()
            print("s_time")
            print("f_stime:",f_stime)
            print("f_etime:",f_etime)
            if s_time >= f_stime and s_time<= f_etime:
                value_present = 1
                break
            elif row['q_time_start']==1:
                quiz_another_running = 1
                break
            elif e_time >= f_stime and e_time<= f_etime:
                value_present = 1
                break
            else:
                value_present = 0
                quiz_another_running = 0
            i += 1
    else:
        value_present = 0
        quiz_another_running = 0
    # #print("Value present:",value_present)
    rt_str = ''
    res = {}
    if quiz_another_running == 1 or value_present==1:
        print(records[i])
        row = records[i]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT Designation, F_name, L_name FROM faculty WHERE F_id = %s',[row['fac_inserted']])
        fac_det = cursor.fetchone()
        res['quiz_name'] = row['q_title']
        res['fac_det'] = fac_det['Designation'] +' '+ fac_det['F_name'] + ' ' + fac_det['L_name'] 
    if quiz_another_running == 1:
        res['msg'] = 'Started'
    elif value_present==1:
        res['msg'] = 'Yes'
    elif value_present==0:
        res['msg'] = 'No'
    print(res)
    return json.dumps(res)


@quiz.route('/getsubjects/',methods=['POST'])
def get_subjects():
    dept =  request.form['dept']
    print("dept:",dept)
    sem = 'sem'+request.form['sem']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT \
        electives.sub_name_long AS s_name \
        FROM electives \
        INNER JOIN department ON electives.dept_id = department.dept_id \
        WHERE department.dept_short = %s AND electives.sem = %s', (dept,sem))
    electives = cursor.fetchall()
    cursor.execute('SELECT \
        subject.sub_name_long AS s_name \
        FROM subject \
        INNER JOIN department ON subject.dept_id = department.dept_id \
        WHERE department.dept_short = %s AND subject.sem = %s', (dept,sem))
    records = cursor.fetchall()
    # #print(records)
    subjects = list()    
    for row in records:
        subjects.append(row['s_name'])
    for row in electives:
        subjects.append(row['s_name'])
    cursor.close()
    return json.dumps(subjects)

@quiz.route('/add_quiz_info/',methods=['POST'])
@login_required
def add_quiz_information():
    title =  request.form['quiz_title']
    dept =  request.form['dept']
    sem =  request.form['sem']
    batch =  request.form['batch']
    date =  request.form['date']
    s_time =  request.form['s_time']
    e_time =  request.form['e_time']
    fac_inserted = session['svv']
    view_score =  request.form['view_score']
    if "ques_timer" in request.form:
        ques_timer =  request.form['ques_timer']
    else:
        ques_timer = 0
    quiz_type = request.form['quiz_type']
    switch_limit = request.form['switch_limit']
    # #print(quiz_type)
    # #print('Ques Time:',ques_timer)
    if view_score=='Yes':
        view_score = 1
    else:
        view_score = 0
    if ques_timer=='Yes':
        ques_timer = 1
        q_time_divide =  request.form['q_time_divide']
    else:
        ques_timer = 0
        q_time_divide = '-'
    if quiz_type=='1':
        sub = ''
    else:
        sub =  request.form['sub']
    # #print('sub',sub)
    # #print('quiz_type',quiz_type)
    # preview_quiz_questiont(q_date)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    result = cur.execute("INSERT INTO quiz_det (q_title,q_dept,q_sem,q_sub,q_batch,q_date,q_time_start,q_time_end,show_answer,fac_inserted,q_timer,q_time_division,quiz_type,switch_limit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(title,dept,sem,sub,batch,date,s_time,e_time,view_score,fac_inserted,ques_timer,q_time_divide,quiz_type,switch_limit))
    session.pop("quiz_id",None)
    session.pop("ques_no",None)
    session['quiz_id'] = str(cur.lastrowid)
    session['ques_timer'] = ques_timer
    if q_time_divide!='-':
        session['q_time_division'] = q_time_divide
        # #print(session['q_time_division'])
    # #print("QUiz ID:",session['quiz_id'])
    # #print("QUiz Timer:",session['ques_timer'])
    mysql.connection.commit()
    return redirect(url_for('quiz.add_quiz_details'))    

@quiz.route('/add_quiz_det/')
@login_required
def add_quiz_details():
    if not session.get("ques_no") is None:
        print('')
        # #print("ques_no in add quiz det:"+str(session['ques_no']))
        # session['ques_no'] = int(session['ques_no'])+1
    else:
        session['ques_no'] = 1
        
    # # #print("question_timer:",session['ques_timer'])
    # # #print("question time division mode:",session['q_time_division'])
    return render_template('add_question.html',msg = "",option=1,ques=session['ques_no'])

@quiz.route('/add_question/',methods=['POST'])
@login_required
def add_questions():
    
    # session.pop('ques_no', None)
    # #print(session)
    if not session.get("ques_no") is None:
        print('')
        # #print("ques_no in add question:"+str(session['ques_no']))
        # if session['ques_no']!=1:
        #     session['ques_no'] = int(session['ques_no'])+1
    else:
        session['ques_no'] = 1
    # #print("ques_no in add question2:"+str(session['ques_no']))
    ques_no = str(session['ques_no'])
    # #print(type(ques_no))
    ques = request.form['ques'+ques_no]
    pts = request.form['points']
    ans_type = request.form['answ_type']
    if session['ques_timer']==1 and session['q_time_division']=='m':
        if ans_type == 'mcq':
            mins = int(request.form['mcq_mins'])
            secs = int(request.form['mcq_secs'])
        elif ans_type =='one_line':
            mins = int(request.form['one_mins'])
            secs = int(request.form['one_secs'])

        # #print("Mins:",mins)
        # #print("Secs:",secs)
            
        hour = 0
        ques_time = "%d:%02d:%02d" % (hour, mins, secs) 
         
    else:
        ques_time = ''
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if ans_type=='mcq':
        ans_type = 0
        ttloptions = int(request.form['ttloptions'])
        correct_option = request.form['correct_opt']
        options= list()
        # #print(ttloptions)
        # # #print(request.form["opt"+ques_no])
        for i in range(1,5):
            # #print("I value:"+str(i))#
            j = "opt"+str(i) 
            if j in request.form:
                options.append(request.form["opt"+str(i)])
            else:
                # #print("Value Not present")
                options.append("-")

        result = cur.execute("INSERT INTO questions (q_no,question,ans_type,opt1,opt2,opt3,opt4,correct_opt,q_time,points,quiz_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(ques_no,ques,ans_type,options[0],options[1],options[2],options[3],correct_option,ques_time,pts,session["quiz_id"]))
    elif ans_type=='one_line':
        ans_type = 1
        result = cur.execute("INSERT INTO questions (q_no,question,ans_type,q_time,points,quiz_id) VALUES (%s,%s,%s,%s,%s,%s)",(ques_no,ques,ans_type,ques_time,pts,session["quiz_id"]))
    
    
    # questions = {
    # 'question': ques,
    # 'total_options': ttloptions,
    # 'options':options,
    # 'correct_option':correct_option
    # }
 
    mysql.connection.commit()

    session['ques_no'] = int(session['ques_no'])+1
    # session['total_questions'] = total_questions
    # # #print(questions)
    # # #print(total_questions)
    # # #print("Size of Session:"+str(sys.getsizeof(session)))
    return redirect(url_for('quiz.add_quiz_details'))
    # return render_template('add_question.html',msg = "",ques=ques_no)

@quiz.route('/cancel_quiz/',methods=['POST', 'GET'])
@login_required
def quiz_cancel():
    if not session.get("quiz_id") is None:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        result = cur.execute("DELETE FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])    
        mysql.connection.commit()
        session.pop("quiz_id",None)
        session.pop("ques_no",None)
    return redirect(url_for('dashboard'))

@quiz.route('/complete_quiz/',methods=['POST', 'GET'])
@login_required
def quiz_completion():
    if session.get("quiz_id") is not None:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        result = result = cur.execute("UPDATE quiz_det SET quiz_status = 1 WHERE quiz_id = %s" ,[session['quiz_id']])
        mysql.connection.commit()
        session.pop("quiz_id",None)
        session.pop("ques_no",None)
    return redirect(url_for('dashboard'))

@quiz.route('/cancel_quiz_quest/',methods=['POST', 'GET'])
@login_required
def quiz_cancel_quest():
    if session.get("quiz_id") is not None and session.get("ques_no") is not None:
        # #print("exists")
        # #print("Quiz ID:"+session['quiz_id'])
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("DELETE FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])    
        mysql.connection.commit()
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("DELETE FROM questions WHERE quiz_id = %s",[session['quiz_id']])    
        mysql.connection.commit()
        session.pop("quiz_id",None)
        session.pop("ques_no",None)
    else:
        print('')
        # #print("Not Exists!")
    return redirect(url_for('dashboard'))

@quiz.route('/start_quiz',methods=['POST','GET'])
@login_required
def quiz_start():
    qid = request.args.get('quiz_id')
    return render_template('start_quiz.html',qid=qid)

@quiz.route('/get_quiz', methods=['POST', 'GET'])
@login_required
def quiz_get():
    qt = request.args.get('quiz_id')
    session['quiz_id'] = qt
    mode = session['mode']    
    if mode=="Faculty":
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT COUNT(q_no) AS total_question FROM questions WHERE quiz_id = %s",[qt])
        record = cur.fetchone()
        # #print(record)
        if record:
            session['ques_no'] = int(record['total_question'])+1
        cur.execute("SELECT * FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])
        quiz = cur.fetchone()
        db_date = datetime.datetime.strptime(quiz['q_date'], '%Y-%m-%d').date()
        dt1 = datetime.datetime.strptime(datetime.datetime.now(IST).strftime('%Y-%m-%d'), '%Y-%m-%d').date()
        today_time = datetime.datetime.now(IST).strftime('%H:%M')
        st=datetime.datetime.strptime(quiz['q_time_start'],'%H:%M').time()
        t_time=datetime.datetime.strptime(today_time,'%H:%M').time()
        session['ques_timer']=quiz['q_timer']
        session['q_time_division']=quiz['q_time_division']
        # #print(db_date)
        # #print(dt1)
        # #print(t_time)
        # #print(st)
        
        # if dt1 < db_date or (dt1 == db_date and t_time<st):
        #     return redirect(url_for('quiz_preview'))
        # else:
        #     session['overtime'] = 1
        #     return redirect(url_for('dashboard'))
        return redirect(url_for('quiz.quiz_preview'))
    elif mode=="Student":
        if session.get('switch') is not None:
            session.pop('switch',None)
        if session.get('attempt_ques') is not None:
            session.pop('attempt_ques',None)
        return redirect(url_for('student.student_quiz'))

@quiz.route('/preview_quiz/',methods=['POST', 'GET'])
@login_required
def quiz_preview():
    # #print(session)
    if session.get("quiz_id") is not None:
        # # #print("exists")
        # #print("Quiz ID:"+session['quiz_id'])
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])
        quiz = cur.fetchone()
        quiz_start_time = quiz['q_time_start']+':00'
        if len(quiz['q_time_start']) == 5:
            quiz_start_time = quiz['q_time_start']+':00'
        else:
            quiz_stop_time = quiz['q_time_start']        
        quiz_stop_time = quiz['q_time_end']+':00'
        quiz_stop_time = datetime.datetime.strptime(quiz_stop_time, '%H:%M:%S').time()
        print(quiz_stop_time)
        quiz_start_time = datetime.datetime.strptime(quiz_start_time, '%H:%M:%S')
        quiz_start_time_pre = quiz_start_time - datetime.timedelta(minutes = 10)
        quiz_start_time_pre = quiz_start_time_pre.strftime('%H:%M:%S')
        quiz_start_time_pre = datetime.datetime.strptime(quiz_start_time_pre, '%H:%M:%S').time()
        print("Quiz start pre time:",quiz_start_time_pre)
        now_time = datetime.datetime.now(IST).strftime('%H:%M:%S')
        now_time = datetime.datetime.strptime(now_time,'%H:%M:%S').time()
        dt1 = datetime.datetime.strptime(datetime.datetime.now(IST).strftime('%Y-%m-%d'), '%Y-%m-%d').date()
        db_date = datetime.datetime.strptime(quiz['q_date'], '%Y-%m-%d').date()
        perm_start = 0
        if quiz['quiz_started']==0 and now_time >= quiz_start_time_pre and now_time < quiz_stop_time and dt1 == db_date:
            print("Now time less than stop time and greater than start time - 10 mins")
            perm_start = 1
        elif now_time < quiz_start_time_pre or now_time > quiz_stop_time:
            print("Now time greater than stop time or less than start time - 10 mins")
        # #print("Found QUiz:")
        # #print(quiz)
        cur.close()
        dept =  quiz['q_dept']
        sem = 'sem'+quiz['q_sem']
        # #print(dept)
        # #print(sem)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT \
            electives.sub_name_long AS s_name \
            FROM electives \
            INNER JOIN department ON electives.dept_id = department.dept_id \
            WHERE department.dept_short = %s AND electives.sem = %s', (dept,sem))
        electives = cursor.fetchall()
        cursor.execute('SELECT \
            subject.sub_name_long AS s_name \
            FROM subject \
            INNER JOIN department ON subject.dept_id = department.dept_id \
            WHERE department.dept_short = %s AND subject.sem = %s', (dept,sem))
        records = cursor.fetchall()
        # #print(records)
        subjects = list()    
        for row in records:
            subjects.append(row['s_name'])
        for row in electives:
            subjects.append(row['s_name'])
        cursor.close()
        return render_template('preview_quiz.html',msg = "",quiz_det = quiz,sub = subjects,permission_to_start=perm_start)
    else:
        return render_template('preview_quiz.html',msg = "Quiz Not Created Yet!")

@quiz.route('/preview_quiz_question/',methods=['POST', 'GET'])
@login_required
def quiz_preview_question():
    # #print(session)
    if session.get("ques_no") is not None and session.get("ques_no")!=1:
        # # #print("exists")
        # #print("Quiz ID:"+session['quiz_id'])
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if session['ques_timer']==1 and session['q_time_division']=='eq':
            cur.execute("SELECT q_time_start,q_time_end FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])
            result = cur.fetchone()
            q_time_start = result['q_time_start']
            q_time_end = result['q_time_end']
            cur.execute("SELECT COUNT(question) AS ques_len FROM questions WHERE quiz_id = %s",[session['quiz_id']])
            result = cur.fetchone()
            ttl_ques = result['ques_len']
            ttl_ques = int(ttl_ques)
            FMT = '%H:%M'
            delta = datetime.datetime.strptime(q_time_end, FMT) - datetime.datetime.strptime(q_time_start, FMT)
            time_diff = delta.seconds/60
            # #print("The time difference is :",time_diff)
            diff = time_diff / ttl_ques
            t_per_question = datetime.timedelta(minutes = diff)
            time_per_question = (datetime.datetime.min + t_per_question).time()
            # time_per_question = str(t_per_question).strftime('%H:%M:%S')
            # #print("The time per question is :",time_per_question)
            result = cur.execute("UPDATE questions SET q_time = %s  WHERE quiz_id = %s" ,(time_per_question,session['quiz_id']))
            mysql.connection.commit()

        cur.execute("SELECT * FROM questions WHERE quiz_id = %s",[session['quiz_id']])
        records = cur.fetchall()
        questions = list()
        mode = 0
        for row in records:
            questions.append(row)
        # #print(questions)
        cur.close()
        return render_template('preview_quiz_ques.html',msg = "",ques=questions,len = len(questions),ques_no=1)
    else:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT q_timer,q_time_division FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])
        records = cur.fetchone()
        session['ques_timer'] = records['q_timer']
        if records['q_time_division']!='-':
            session['q_time_division'] = records['q_time_division']
            # #print(session['q_time_division'])
        # #print(session['quiz_id'])
        # #print(session['ques_timer'])
        # # #print("Time per Question:",session['q_time_division'])
        cur.close()
        return render_template('preview_quiz_ques.html',msg = "No Questions Added Yet!")


@quiz.route('/edit_quiz_quest',methods=['POST','GET'])
@login_required
def edit_question():
    qt = request.args.get('q')
    # #print(type(qt))
    # if request.method == 'POST':
    q_id =  request.form.get('question_no'+qt)
    # #print(request.form.get('question_no'+qt))
    # # #print("got this shit:"+q_id)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM questions WHERE q_id = %s AND quiz_id = %s",(q_id,session['quiz_id']))
    question = cur.fetchone()
    if question:
        msg = 'Got data successfully !'
        cur.close()
        # ed_ques = list(question)
        # # #print(ed_ques)
        # for row in question:
        #     ed_ques.append(row)
        return render_template('edit_quiz.html',msg = "",ques_det=question,ques_no=qt)
    return render_template('edit_quiz.html',msg = "",ques_det=question,ques_no=qt)
    # else:
    #     cur.close()
    #     msg="Could not Edit the question!"
    #     return redirect(url_for('quiz_preview'))        

@quiz.route('/update_question/',methods=['POST'])
@login_required
def update_questions():
    q_no = request.form['ques_no']
    ques = request.form['ques'+q_no]
    pts = request.form['ed_points']
    ans_type = request.form['ed_answ_type']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    q_index = request.form['ques_index']

    if ans_type=='mcq':
        ans_type = 0
        correct_option = request.form['correct_opt']
        ttloptions = int(request.form['ttloptions'])
        options= list()
        if session['ques_timer']==1 and session['q_time_division']=='m':
            mins = int(request.form['ed_mcq_mins'])
            secs = int(request.form['ed_mcq_secs'])
            # #print("Mins:",mins)
            # #print("Secs:",secs)
            hour = 0
            ques_time = "%d:%02d:%02d" % (hour, mins, secs) 
             
        else:
            ques_time = ''


        for i in range(1,5):
            # # #print("I value:"+str(i))#
            j = "opt"+str(i) 
            if j in request.form:
                options.append(request.form["opt"+str(i)])
            else:
                # #print("Value Not present")
                options.append("-")
        result = cur.execute("UPDATE questions SET question = %s , opt1  = %s , opt2 = %s , opt3 = %s , opt4 = %s , correct_opt = %s , ans_type = %s , points = %s, q_time = %s WHERE q_id = %s" ,(ques,options[0],options[1],options[2],options[3],correct_option,ans_type,pts,ques_time,q_index))
    elif ans_type=='one_line' or ans_type=='desc':
        if ans_type=='one_line':
            ans_type = 1
        elif ans_type=='desc':
            ans_type = 2

        if session['ques_timer']==1 and session['q_time_division']=='m':
            mins = int(request.form['ed_one_mins'])
            secs = int(request.form['ed_one_secs'])
            # #print("Mins:",mins)
            # #print("Secs:",secs)
            hour = 0
            ques_time = "%d:%02d:%02d" % (hour, mins, secs) 
             
        else:
            ques_time = ''
        # #print("Question Time:",ques_time)
        result = cur.execute("UPDATE questions SET question = %s , opt1  = '-' , opt2 = '-' , opt3 = '-' , opt4 = '-' , correct_opt = '-' , ans_type = %s , points = %s, q_time = %s WHERE q_id = %s" ,(ques,ans_type,pts,ques_time,q_index))    

    mysql.connection.commit()
    return redirect(url_for('quiz.quiz_preview_question'))

@quiz.route('/update_quiz_det/',methods=['POST'])
@login_required
def quiz_update_details():
    title =  request.form['quiz_title']
    dept =  request.form['dept']
    sem =  request.form['sem']
    quiz_type = request.form['quiz_type']
    if quiz_type=='1':
        sub = ''
    else:
        sub =  request.form['sub']
    batch =  request.form['batch']
    date =  request.form['date']
    s_time =  request.form['s_time']
    e_time =  request.form['e_time']
    view_score =  request.form['view_score']
    ques_timer =  request.form['up_ques_timer']
    switch_limit =  request.form['switch_limit']
    desc_time =  request.form['desc_time']
    # #print('Ques Time:',ques_timer)

    if view_score=='Yes':
        view_score = 1
        
    else:
        view_score = 0

    if ques_timer=='Yes':
        ques_timer = 1
        if 'up_q_time_divide' in request.form:
            q_time_divide =  request.form['up_q_time_divide']
        else:
            q_time_divide = '-'

    else:
        ques_timer = 0
        q_time_divide = '-'

    # #print('sub',sub)
    # #print('quiz_type',quiz_type)

    session['q_time_division'] = q_time_divide
    session['ques_timer'] = ques_timer

    q_index = request.form['quiz_index']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    result = cur.execute("UPDATE quiz_det SET q_title = %s ,q_dept = %s ,q_sem = %s ,q_sub = %s ,q_batch = %s ,q_date = %s ,q_time_start = %s ,q_time_end = %s ,show_answer= %s,q_timer=%s,q_time_division=%s,quiz_type=%s,quiz_started=%s WHERE quiz_id = %s" ,(title,dept,sem,sub,batch,date,s_time,e_time,view_score,ques_timer,q_time_divide,quiz_type,0,q_index))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('quiz.quiz_preview_question'))

@quiz.route('/del_question/',methods=['POST'])
@login_required
def question_delete():
    # #print(session)
    q_index = request.form['index']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM questions WHERE q_id = %s",[q_index])
    mysql.connection.commit()
    session['ques_no'] = int(session['ques_no'])-1
    return json.dumps("Deleted successfully")

@quiz.route('/del_quiz/',methods=['POST'])
@login_required
def quiz_delete():
    #print(session)
    q_index = request.form['index']
    # #print("exists")
    #print("Quiz ID:"+session['quiz_id'])
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM quiz_responses WHERE quiz_id = %s",[session['quiz_id']])    
    mysql.connection.commit()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM score WHERE quiz_id = %s",[session['quiz_id']])    
    mysql.connection.commit()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])    
    mysql.connection.commit()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM questions WHERE quiz_id = %s",[session['quiz_id']])    
    mysql.connection.commit()
    
    # cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur.execute("DELETE t1, t2, t3, t4 FROM \
    #       score as t1 \
    #       INNER JOIN  quiz_responses as t2 on t1.quiz_id = t2.quiz_id \
    #       INNER JOIN  questions as t3 on t1.quiz_id=t3.quiz_id \
    #       INNER JOIN  quiz_det as t4 on t1.quiz_id=t4.quiz_id \
    #       WHERE  t1.quiz_id = %s",[session['quiz_id']])    
    # mysql.connection.commit()
    session.pop("quiz_id",None)
    session.pop("ques_no",None)
    # #print("Not Exists!")
    session['message'] = 'Quiz Deleted Successfully!'
    return redirect(url_for('quiz.quizes_all'))
    # return json.dumps("Deleted successfully")

@quiz.route('/get_response', methods=['POST', 'GET'])
@login_required
def responses_get():
    qt = request.args.get('quiz_id')
    session['quiz_id'] = qt
    mode = session['mode']    
    if mode=="Faculty":
        return redirect(url_for('quiz.response'))
    elif mode=="Student":
        session['over_access'] = 1
        return redirect(url_for('dashboard'))


def floorDecimal(number, decimal):
    return math.floor(number * pow(10, decimal))/pow(10, decimal)

def add_one(v):
    after_comma = Decimal(v).as_tuple()[-1]*-1
    add = Decimal(1) / Decimal(10**after_comma)
    return Decimal(v) + add

@quiz.route('/show_responses/')
@login_required
def response():
    if session.get('quiz_id') is not None:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(user) AS user_attempt FROM score WHERE quiz_id =%s AND quiz_attempted=1', [session['quiz_id']])
        records = cursor.fetchone()
        # #print(records)
        if records['user_attempt'] is not None or records['user_attempt'] != 0:
            user_quiz_attempt = records['user_attempt']
            cursor.execute('SELECT user_score,total_points FROM score WHERE quiz_id =%s AND quiz_attempted=1', [session['quiz_id']])
            rd = cursor.fetchall()
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT SUM(points) AS total_points FROM questions WHERE quiz_id =%s', [session['quiz_id']])
            total_pts = cursor.fetchone()
            total_points = total_pts['total_points']
            cursor.close()
            print(total_points)
            distinction = 0.75*float(total_points)
            print(distinction)
            pass_marks = 0.35*float(total_points)
            print(pass_marks)
            
            stud_correct_opt = list()
            distinct = 0
            pass_mark_got = 0
            fail_mark_got = 0
            for row in rd:
                # #print("present")
                # #print(row)
                percent = round((int(row['user_score']) / int(row['total_points']))*100,0)
                if int(row['user_score']) >= (0.75*float(total_points)):
                    distinct += 1
                elif int(row['user_score']) >= (0.35*float(total_points)) and int(row['user_score']) < (0.75*float(total_points)):
                    pass_mark_got += 1
                elif int(row['user_score']) < (0.35*float(total_points)):
                    fail_mark_got += 1
                # #print(percent)
                stud_correct_opt.append(percent)  
            # print(len(rd))
            # print(distinct)
            # print(pass_mark_got)
            # print(fail_mark_got)
            test_list = list()
            for i in range(3):
                test_list.append(0)
            print(test_list)
            if len(rd) > 0:
                test_list[0] = floorDecimal(((distinct / len(rd))*100), 2)
                test_list[1] = floorDecimal(((pass_mark_got / len(rd))*100), 2)
                test_list[2] = floorDecimal(((fail_mark_got / len(rd))*100), 2)
            max = 0
            percent_send = dict()
            percent_send['distinct'] = test_list[0]
            percent_send['pass'] = test_list[1]
            percent_send['fail'] = test_list[2]
            print(percent_send)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT q_date,q_time_start,q_sub,q_title,q_sem,q_dept,q_batch,quiz_start FROM quiz_det,quiz_responses WHERE quiz_det.quiz_id = %s', [session['quiz_id']])
            r_quiz = cursor.fetchone()
            cursor.close()
            print(r_quiz)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if r_quiz is not None and r_quiz['q_batch']=="All":
                cursor.execute('SELECT COUNT(S_id) AS total_stud FROM student WHERE current_sem =%s AND dept= %s', (r_quiz['q_sem'],r_quiz['q_dept']))
            else:
                cursor.execute('SELECT COUNT(S_id) AS total_stud FROM student WHERE current_sem =%s AND dept= %s AND batch=%s', (r_quiz['q_sem'],r_quiz['q_dept'],r_quiz['q_batch']))
            quiz_responses = cursor.fetchone()
            print(quiz_responses)
            # quiz_responses = {'total_stud': 72}
            # print(quiz_responses)
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT username,roll,stud_img,user_score,total_points,total_time_taken FROM score WHERE quiz_id =%s ORDER BY cast(user_score as unsigned) DESC,total_time_taken ASC LIMIT 5', [session['quiz_id']])
            records = cursor.fetchall()
            cursor.close()
            rankers = list()
            for row in records:
                if row['stud_img']=="":
                    row['stud_img'] = 'images/man.png'
                rankers.append(row)
            total_points = int(total_points)
            cursor.close()
            
            # for row in records:
            #     if row['image']=="":
            #         if row['gender']=='M':
            #             row['image'] = 'images/man.png'
            #         elif row['gender'] == 'F':
            #             row['image'] = 'images/woman.png'
                # if row['time_submitted'] !='':
                #     time_submit = datetime.datetime.strptime(row['time_submitted'], '%H:%M:%S')
                # else:
                #     time_submit = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                # # #print(r_quiz['quiz_start'])
                # if r_quiz['quiz_start']!='' and r_quiz['quiz_start'] is not None:
                #     quiz_time = datetime.datetime.strptime(r_quiz['quiz_start'], '%H:%M:%S')
                # else:
                #     quiz_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S')   
                # # #print(time_submit)
                # # #print(quiz_time)
                # row['time_submitted'] = (time_submit - quiz_time)
                # # #print(row['time_submitted'])
                # rankers.append(row)
            return render_template('response.html',avg_correct=percent_send,qz_rsp=user_quiz_attempt,total_stud=quiz_responses['total_stud'],quiz_name=r_quiz['q_title'],quiz_sub=r_quiz['q_sub'],toppers=rankers,tplen= len(rankers),total_points=total_points)
        else:
            cursor.execute('SELECT q_sub,q_title,q_sem,q_dept,q_batch FROM quiz_det WHERE quiz_id =%s', [session['quiz_id']])
            r_quiz = cursor.fetchone()
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if r_quiz['q_batch']=="All":
                cursor.execute('SELECT COUNT(S_id) AS total_stud FROM student WHERE current_sem =%s AND dept= %s', (r_quiz['q_sem'],r_quiz['q_dept']))
            else:
                cursor.execute('SELECT COUNT(S_id) AS total_stud FROM student WHERE current_sem =%s AND dept= %s AND batch=%s', (r_quiz['q_sem'],r_quiz['q_dept'],r_quiz['q_batch']))
            quiz_responses = cursor.fetchone()
            cursor.close()
            percent_send = dict()
            percent_send['distinct'] = 0
            percent_send['pass'] = 0
            percent_send['fail'] = 0
            return render_template('response.html',avg_correct=percent_send,qz_rsp=0,total_stud=quiz_responses['total_stud'],quiz_name=r_quiz['q_title'],quiz_sub=r_quiz['q_sub'],toppers=0,tplen=0)
    else:
        return redirect(url_for('quiz.quizes_all')) 

@quiz.route('/mark_graph_value', methods=['POST', 'GET'])
@login_required
def mark_response():
    label = request.args.get('label')
    print(label)
    if label=='Avg. % Students Passed Distinction' or label=='Avg. % Students Passed' or label=='Avg. % Students Failed':
        print(session)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT q_sub,q_title,q_sem,q_dept,q_batch FROM quiz_det WHERE quiz_id =%s', [session['quiz_id']])
        r_quiz = cursor.fetchone()
        cursor.execute('SELECT dept_id FROM department WHERE dept_short = %s', [session['dept']])
        dept_id = cursor.fetchone()
        cursor.execute('SELECT course_code FROM subject WHERE sub_name_long =%s AND dept_id = %s ', (r_quiz['q_sub'],dept_id['dept_id']))
        sub_code = cursor.fetchone()
        sub_elective = 0
        if cursor.rowcount == 0:
            cursor.execute('SELECT course_code FROM electives WHERE sub_name_long =%s AND dept_id = %s', (r_quiz['q_sub'],dept_id['dept_id']))
            sub_code = cursor.fetchone()
            sub_elective = 1
        print("Sub_elective",sub_elective)
        print("sub_code",sub_code)
        cursor.close() 
        semester = r_quiz['q_sem']
        subject = r_quiz['q_sub']
        dept = r_quiz['q_dept']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT SUM(points) AS total_points FROM questions WHERE quiz_id =%s', [session['quiz_id']])
        total_pts = cursor.fetchone()
        total_points = total_pts['total_points']
        comp_score = total_points
        send_label = ""
        if label=='Avg. % Students Passed Distinction':
            comp_score = (0.75*float(total_points))
            if r_quiz['q_batch'] == 'All':
                cursor.execute('SELECT F_name, L_name, roll, electives FROM student WHERE current_sem = %s AND student.dept = %s AND S_id IN (SELECT user FROM score WHERE quiz_id = %s AND user_score >= %s) ORDER BY roll ASC', (semester,dept,session['quiz_id'],comp_score))
            else:
                cursor.execute('SELECT F_name, L_name, roll, electives FROM student WHERE current_sem = %s AND dept = %s AND batch = %s AND S_id IN (SELECT user FROM score WHERE quiz_id = %s AND user_score >= %s) ORDER BY roll ASC', (semester,dept,r_quiz['q_batch'],session['quiz_id'],))
            send_label = "Students Passed with Distinction"
        elif label == 'Avg. % Students Passed':
            high_score = (0.75*float(total_points))
            comp_score = (0.35*float(total_points))
            if r_quiz['q_batch'] == 'All':
                cursor.execute('SELECT F_name, L_name, roll, electives FROM student WHERE current_sem = %s AND student.dept = %s AND S_id IN (SELECT user FROM score WHERE quiz_id = %s AND user_score >= %s AND user_score < %s) ORDER BY roll ASC', (semester,dept,session['quiz_id'],comp_score,high_score))
            else:
                cursor.execute('SELECT F_name, L_name, roll, electives FROM student WHERE current_sem = %s AND dept = %s AND batch = %s AND S_id IN (SELECT user FROM score WHERE quiz_id = %s AND user_score >= %s AND user_score < %s) ORDER BY roll ASC', (semester,dept,r_quiz['q_batch'],session['quiz_id'],comp_score,high_score))
            send_label = "Students Passed"
        else:
            comp_score = (0.35*float(total_points))
            if r_quiz['q_batch'] == 'All':
                cursor.execute('SELECT F_name, L_name, roll, electives FROM student WHERE current_sem = %s AND student.dept = %s AND S_id IN (SELECT user FROM score WHERE quiz_id = %s AND user_score < %s) ORDER BY roll ASC', (semester,dept,session['quiz_id'],comp_score))
            else:
                cursor.execute('SELECT F_name, L_name, roll, electives FROM student WHERE current_sem = %s AND dept = %s AND batch = %s AND S_id IN (SELECT user FROM score WHERE quiz_id = %s AND user_score < %s) ORDER BY roll ASC', (semester,dept,r_quiz['q_batch'],session['quiz_id'],comp_score))
            send_label = "Students Failed"
        total_students_participants = cursor.fetchall()
        not_attempted = list(total_students_participants)
        print(not_attempted)
        for i in range(len(not_attempted)):
            row = not_attempted[i]
            if sub_elective ==1:
                electives = row['electives'].split(",")
                print(electives)
                if sub_code['course_code'] not in electives:
                    not_attempted.pop(i)    
        total_students_participants = tuple(not_attempted)
        print(total_students_participants)
        cursor.close()
        return render_template('mark_graph.html',msg={},msg_color="",label=send_label,toppers=total_students_participants ,quiz_name=r_quiz['q_title'],quiz_sub=r_quiz['q_sub'],tplen= len(total_students_participants),notattempt=1)
    else:
        return redirect('/quiz/show_responses/')
        
@quiz.route('/show_graph_value', methods=['POST', 'GET'])
@login_required
def graph_response():
    label = request.args.get('label')
    if label=='Quiz Attempted in %:' :
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT q_date,q_time_end,q_time_start,q_sub,q_title,q_sem,q_dept,q_batch,show_answer,quiz_started FROM quiz_det WHERE quiz_id =%s', [session['quiz_id']])
        r_quiz = cursor.fetchone()
        # #print("quiz_det",r_quiz)
        if r_quiz['q_batch']=="All":
            # cursor.execute('SELECT user,time_submitted,username,roll,stud_img,user_score,total_points,pending_chk,total_time_taken FROM score WHERE quiz_id =%s ORDER BY user_score DESC,time_submitted ASC', [session['quiz_id']])
            cursor.execute('SELECT user,time_submitted,username,roll,stud_img,user_score,total_points,pending_chk,total_time_taken FROM score WHERE quiz_id =%s ORDER BY roll ASC', [session['quiz_id']])
        else:
            # cursor.execute('SELECT user,time_submitted,username,roll,stud_img,user_score,total_points,pending_chk,total_time_taken FROM score WHERE quiz_id =%s ORDER BY user_score DESC,time_submitted ASC', [session['quiz_id']]) 
            cursor.execute('SELECT user,time_submitted,username,roll,stud_img,user_score,total_points,pending_chk,total_time_taken FROM score WHERE quiz_id =%s ORDER BY roll ASC', [session['quiz_id']]) 

        records = cursor.fetchall()
        cursor.execute('SELECT quiz_start FROM quiz_responses WHERE quiz_id = %s', [session['quiz_id']])
        r2_quiz = cursor.fetchone()
        # #print("Quiz Start:",r2_quiz)
        # #print("Quiz Start Type:",type(r2_quiz))
        students_attempt = list()
        pending_chk = 0
        chk = 0
        for row in records:
            # #print(row)
            if row['pending_chk']==1 and chk==0:
                pending_chk = 1
                chk=1
            if row['time_submitted'] is None and r2_quiz is None:
                row['time_submitted'] = '00:00:00'
                r2_quiz = {}
                r2_quiz['quiz_start'] = '00:00:00'
            elif row['time_submitted'] is None:
                row['time_submitted'] = '00:00:00'
            elif r2_quiz is None or r2_quiz['quiz_start'] is None :
                r2_quiz = {}
                r_quiz['q_time_start'] = r_quiz['q_time_start']+':00'
                r2_quiz['quiz_start'] = datetime.datetime.strptime(r_quiz['q_time_start'], '%H:%M:%S')
                r2_quiz['quiz_start'] = r2_quiz['quiz_start'].strftime('%H:%M:%S')
            # #print("R2 quiz",r2_quiz)
            # #print("The time started:",row['time_submitted'])
            row['time_submitted'] = datetime.datetime.strptime(row['time_submitted'], '%H:%M:%S') - datetime.datetime.strptime(r2_quiz['quiz_start'], '%H:%M:%S')
            # row['time_submitted'] = row['total_time_taken']
            students_attempt.append(row)
        cursor.close()
        # print(students_attempt)
        # #print("pending_chk:",pending_chk)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT SUM(points) AS total_points FROM questions WHERE quiz_id =%s', [session['quiz_id']])
        total_pts = cursor.fetchone()
        total_pts['total_points'] = int(total_pts['total_points'])
        if len(r_quiz['q_time_end']) == 5:
            quiz_stop_time = r_quiz['q_time_end']+':00'
        else:
            quiz_stop_time = r_quiz['q_time_end']
        quiz_stop_time = datetime.datetime.strptime(quiz_stop_time, '%H:%M:%S')
        # quiz_stop_time_post = quiz_stop_time + datetime.timedelta(minutes = 30)
        quiz_stop_time_post = quiz_stop_time
        quiz_stop_time_post = quiz_stop_time_post.strftime('%H:%M:%S')
        quiz_stop_time_post = datetime.datetime.strptime(quiz_stop_time_post, '%H:%M:%S').time()
        print("Quiz stop post time:",quiz_stop_time_post)
        now_time = datetime.datetime.now(IST).strftime('%H:%M:%S')
        now_time = datetime.datetime.strptime(now_time,'%H:%M:%S').time()
        dt1 = datetime.datetime.strptime(datetime.datetime.now(IST).strftime('%Y-%m-%d'), '%Y-%m-%d').date()
        db_date = datetime.datetime.strptime(r_quiz['q_date'], '%Y-%m-%d').date()
        perm_stop = 0
        release_score = 0
        print(now_time)
        print(quiz_stop_time_post)
        
        # if r_quiz['quiz_started']==1 and now_time < quiz_stop_time_post and dt1 == db_date:
        #     print("Now time lesser than stop time")
        #     perm_stop = 1
        if r_quiz['quiz_started']==1:
            print("Now time lesser than stop time")
            perm_stop = 1
        elif now_time > quiz_stop_time_post:
            print("Now time greater than stop time")
        if r_quiz['quiz_started']==0 and ((dt1 == db_date  and now_time > quiz_stop_time_post) or dt1 > db_date):
            print("release score allowed")
            release_score = 1
        print("perm_stop:",perm_stop)
        return render_template('response_graph.html',label="Student's Submitted Quiz",quiz_name=r_quiz['q_title'],quiz_sub=r_quiz['q_sub'],toppers=students_attempt,tplen= len(students_attempt),notattempt=0,check=pending_chk,total_points=total_pts['total_points'],show_answer=r_quiz['show_answer'],quiz_started=r_quiz['quiz_started'],permission_to_stop=perm_stop,enable_release_score=release_score)
    elif label=='Quiz Not Attempted in %:':
        print(session)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT q_sub,q_title,q_sem,q_dept,q_batch,quiz_type,q_sem FROM quiz_det WHERE quiz_id =%s', [session['quiz_id']])
        r_quiz = cursor.fetchone()
        # print("r_quiz",r_quiz)
        if int(r_quiz['quiz_type']) == 0:
            cursor.execute('SELECT dept_id FROM department WHERE dept_short = %s', [session['dept']])
            dept_id = cursor.fetchone()
            cursor.execute('SELECT course_code FROM subject WHERE sub_name_long =%s AND dept_id = %s ', (r_quiz['q_sub'],dept_id['dept_id']))
            sub_code = cursor.fetchone()
            print("sub_code",sub_code)
            subcode_from = 0
            if cursor.rowcount == 0:
                cursor.execute('SELECT course_code FROM electives WHERE sub_name_long =%s AND dept_id = %s', (r_quiz['q_sub'],dept_id['dept_id']))
                sub_code = cursor.fetchone()
                subcode_from = 1
            print("sub_code",sub_code)
            cursor.close() 
            semester = r_quiz['q_sem']
            subject = r_quiz['q_sub']
            dept = r_quiz['q_dept']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if r_quiz['q_batch'] == 'All':
                cursor.execute('SELECT F_name, L_name, roll, electives FROM student WHERE current_sem = %s AND student.dept = %s AND S_id NOT IN (SELECT user FROM score WHERE quiz_id = %s) ORDER BY roll ASC', (semester,dept,session['quiz_id']))
            else:
                cursor.execute('SELECT F_name, L_name, roll, electives FROM student WHERE current_sem = %s AND dept = %s AND batch = %s AND S_id NOT IN (SELECT user FROM score WHERE quiz_id = %s) ORDER BY roll ASC', (semester,dept,r_quiz['q_batch'],session['quiz_id']))
            total_students_participants = cursor.fetchall()
            not_attempted = list(total_students_participants)
            not_attempted_cpy = list(total_students_participants)
            print("not_attempted",not_attempted_cpy)
            if subcode_from == 1:
                for i in range(len(not_attempted_cpy)):
                    print(i)
                    row = not_attempted_cpy[i]
                    print(row['electives'])
                    if row['electives'] is not None:
                        electives = row['electives'].split(",")
                    else:
                        electives = ['']
                    print(electives)
                    print(not_attempted)
                    if sub_code['course_code'] not in electives :
                        not_attempted.pop(i)
                total_students_participants = tuple(not_attempted)
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if r_quiz['q_batch'] == 'All':
                cursor.execute('SELECT F_name, L_name, roll FROM student WHERE current_sem = %s AND student.dept = %s AND S_id NOT IN (SELECT user FROM score WHERE quiz_id = %s) ORDER BY roll ASC', (r_quiz['q_sem'],r_quiz['q_dept'],session['quiz_id']))
            else:
                cursor.execute('SELECT F_name, L_name, roll FROM student WHERE current_sem = %s AND dept = %s AND batch = %s AND S_id NOT IN (SELECT user FROM score WHERE quiz_id = %s) ORDER BY roll ASC', (r_quiz['q_sem'],r_quiz['q_dept'],r_quiz['q_batch'],session['quiz_id']))
            total_students_participants = cursor.fetchall()            
        print(total_students_participants)
        cursor.close()
        return render_template('response_graph.html',msg={},msg_color="",label="Student's Not Submitted Quiz",toppers=total_students_participants ,quiz_name=r_quiz['q_title'],quiz_sub=r_quiz['q_sub'],tplen= len(total_students_participants),notattempt=1)
    else:
        return Response("Page Doesnt Exists!",status=400,)

@quiz.route('/start_stop_quiz/',methods=['POST'])
@login_required
def start_stop_quiz_status():
    start_stop = int(request.form['start'])
    print("start_stop",start_stop)
    print("session['quiz_id']",session['quiz_id'])
    if start_stop == 0 or start_stop == 1:
        # start - 1 , stop- 0
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("UPDATE quiz_det SET quiz_started = %s WHERE quiz_id = %s AND fac_inserted=%s" ,(start_stop,session['quiz_id'],session['svv']))    
        cur.execute("SELECT * from quiz_responses")
        if (start_stop == 0):
            # cur.execute("SELECT q.user_inserted FROM quiz_responses q LEFT JOIN score s ON q.user_inserted = s.user WHERE s.user IS NULL AND q.quiz_id=%s AND s.quiz_id=%s;",(session['quiz_id'],session['quiz_id']))
            cur.execute("SELECT user_inserted from quiz_responses where quiz_responses.quiz_id = %s AND user_inserted NOT IN (select user from score WHERE score.quiz_id = %s)",(session['quiz_id'],session['quiz_id']))
            temp = cur.fetchall()
            print(temp)
            if temp is not None:
                # print("temp",temp["user_inserted"])
                for i in temp:
                    quiz_end_scores(i['user_inserted'])
        print("done!")        
        mysql.connection.commit()
        cur.close()
        return json.dumps(1)
    else:
        return json.dumps(0)

# def quiz_end_scores():
def quiz_end_scores(user):
    # #
    print("user",user)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT selected_opt,ques_id,ques_type,quiz_start,time_per_ques,q_time_start FROM quiz_responses,quiz_det WHERE quiz_responses.quiz_id = %s AND quiz_responses.quiz_id = quiz_det.quiz_id AND user_inserted=%s",[session['quiz_id'],user])
    record_user = cur.fetchone()
    cur.execute("Select F_name , L_name, roll, image from student where S_id = %s",[user])
    user_details = cur.fetchone()
    print("user_details",user_details)
    cur.close()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT ans_type FROM questions WHERE quiz_id = %s",[session['quiz_id']])
    question_ans_type = cur.fetchall()
    print("question_ans_type",question_ans_type)
    cur.close()
    print("record_user",record_user)
    if record_user is not None:
        ans_type = record_user['ques_type'].split(",")
        time_per_ques = record_user['time_per_ques'].strip().split(',')
        quiz_end_time = time_per_ques[-1]
        user_quiz_start = record_user['quiz_start']
    else:
        ans_type = []
        time_per_ques = []
        now = datetime.datetime.now(IST)
        quiz_end_time = now.strftime('%H:%M:%S')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cur.execute("SELECT selected_opt,ques_id,ques_type,quiz_start,time_per_ques FROM quiz_responses WHERE quiz_id = %s AND user_inserted=%s",(session['quiz_id'],session['svv']))
        # record_user = cur.fetchone()
        # user_quiz_start = record_user['q_time_start']+':00'
        user_quiz_start = session['quiz_start']
    # #
    # #
    
    ttl_time_taken = str(datetime.datetime.strptime(quiz_end_time, '%H:%M:%S') - datetime.datetime.strptime(user_quiz_start, '%H:%M:%S'))
    # print(str(datetime.datetime.strptime(quiz_end_time, '%H:%M:%S')))
    # print(datetime.datetime.strptime(user_quiz_start, '%H:%M:%S'))
    ttl_time_taken = datetime.datetime.strptime(ttl_time_taken, '%H:%M:%S')
    # #
    ttl_time_taken = ttl_time_taken.time()
    pending = 0
    for row in question_ans_type:
        if row['ans_type']==1:
            pending = 1
    # #
    diff_time = list()
    for i in range(len(time_per_ques)):
        if i==0:
            
            start_time = datetime.datetime.strptime(record_user['quiz_start'],"%H:%M:%S")
            end_time = datetime.datetime.strptime(time_per_ques[i].strip(),"%H:%M:%S")
        else:
            start_time = datetime.datetime.strptime(time_per_ques[i-1],"%H:%M:%S")
            end_time = datetime.datetime.strptime(time_per_ques[i].strip(),"%H:%M:%S")
        diff = (end_time - start_time)
        diff_time.append(diff)
    diff_time_str = ','.join(map(str, diff_time))
    mcq = list()
    if record_user is not None:
        ques_ids = record_user['ques_id'].split(",")
    for i in range(len(ans_type)):
        if ans_type[i]=='0':
            mcq.append(ques_ids[i])
    if record_user is not None:
        pass 
    
    #
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT correct_opt,q_id,points FROM questions WHERE quiz_id = %s AND correct_opt !='-' OR correct_opt != NULL",[session['quiz_id']])
    record_og = cur.fetchall()
    cur.close()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT SUM(points) AS total_points FROM questions WHERE quiz_id =%s', [session['quiz_id']])
    total_pts = cursor.fetchone()
    total_pts['total_points'] = int(total_pts['total_points'])
    cursor.close()
    ct = datetime.datetime.now(IST)
    if record_user:
        if record_user['ques_id'] is not None:
            question_ids = record_user['ques_id'].split(',')
        else:
            question_ids = []
        if record_user['selected_opt'] is not None:
            option_selected = record_user['selected_opt'].split(',')
        else:
            option_selected = []
        
        mcq_score_list = list()
        mcq_ques_list = list()
        score_list = ''
        #
        # #
        #
        count = 0
        ind = 0
        for row in record_og:
            #
            
            if str(row['q_id']) in question_ids:
                i = question_ids.index(str(row['q_id']))
            if str(row['q_id']) in mcq:
                i = mcq.index(str(row['q_id']))
                
                
                if row['correct_opt'] == option_selected[i]:
                    count = count+int(row['points'])
                    mcq_ques_list.append(row['q_id'])
                    #
                    mcq_score_list.append(row['points'])
                else:
                    i = -1
                    mcq_score_list.append(0)
                    mcq_ques_list.append(row['q_id'])
            else:
                mcq_score_list.append(0)
                mcq_ques_list.append(row['q_id'])
            # #
            #
            # #
            
            
            ind += 1
        mcq_lst = 0
        #
        for i in range(len(question_ids)):
            #
            #
            if ans_type[i]=='1':
                score_list += '0,'
            elif ans_type[i]=='0':
                #
                ind = mcq_ques_list.index(int(question_ids[i]))
                #
                score_list += str(mcq_score_list[ind])+','
                # mcq_lst += 1
                # #
        if score_list[-1] == ',':
            score_list = score_list[:-1]
        #

        user_img = ''
        username = ''
        roll = ''
        if user_details["F_name"] is not None and user_details["roll"] is not None:
            if user_details["image"] is not None:
                user_img = user_details["image"]
            username = user_details["F_name"] + " " + user_details["L_name"]
            roll = user_details["roll"]

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO score (time_submitted,user,user_score,ques_points,total_points,quiz_id,quiz_attempted,pending_chk,total_time_taken,stud_img,username,roll) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(quiz_end_time,user,count,score_list,total_pts['total_points'],session['quiz_id'],1,pending,ttl_time_taken,user_img,username,roll))
        mysql.connection.commit()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("UPDATE quiz_responses SET time_per_ques = %s WHERE quiz_id = %s AND user_inserted=%s" ,(diff_time_str,session['quiz_id'],user))
        mysql.connection.commit()

        if pending==0:
            session['quiz_score'] = count
    else:
        count = 0
        score_list = ''
        for i in range(len(ans_type)):
            score_list += '0,'
        if score_list!='':
            if score_list[-1] == ',':
                score_list = score_list[:-1]

        user_img = ''
        username = ''
        roll = ''
        if session.get('img') is not None and session.get('username') is not None and session.get('roll') is not None:
            user_img = session['img']
            username = session['username']
            roll = session['roll']


        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO score (time_submitted,user,user_score,ques_points,total_points,quiz_id,quiz_attempted,pending_chk,total_time_taken,stud_img,username,roll) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(quiz_end_time,session['svv'],count,score_list,total_pts['total_points'],session['quiz_id'],1,pending,ttl_time_taken,user_img,username,roll))
        mysql.connection.commit()
        diff_time_str = "00:00:00"
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("UPDATE quiz_responses SET time_per_ques = %s WHERE quiz_id = %s AND user_inserted=%s" ,(diff_time_str,session['quiz_id'],user))
        mysql.connection.commit()
        if pending==0:
            session['quiz_score'] = count
        
        session['q_nos'] = []
        session['not_submitted_ques_id'] = []
        session['submitted_ques'] = []
        session['to_be_submitted_answer'] = []
        session['ques_submitted'] = []

@quiz.route('/release_score/',methods=['POST', 'GET'])
@login_required
def score_release():
    # #print('session',session)
    if request.form['send_value'] is not None:
        quiz_id = str(request.form['send_value'])
        # #print(quiz_id)
        # #print(type(quiz_id))
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("UPDATE quiz_det SET show_answer = %s WHERE quiz_id = %s AND fac_inserted=%s" ,(1,quiz_id,session['svv']))    
        mysql.connection.commit()
        cur.close()
        session['message'] = 'Successfully Marked!'
        session['message_color'] = 1
        return redirect('/quiz/show_graph_value?label=Quiz Attempted in %:')
    else:
        session['message'] = 'Session Destroyed , Go to Dashboard'
        session['message_color'] = 1
        return redirect('/quiz/show_graph_value?label=Quiz Attempted in %:')

@quiz.route('/check_answer/',methods=['POST', 'GET'])
@login_required
def mark_answer():
    stud_id = request.form['send_value']
    # # #print(stud_id)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT user,user_score,ques_points,pending_chk,total_points FROM score WHERE user = %s AND quiz_id = %s",(stud_id,session['quiz_id']))
    student = cur.fetchone()
    cur.close()
    # #print(student)
    # #print(student['ques_points'])
    if student['ques_points'] != '':
        ques_points = student['ques_points'].split(",")
    else:
        ques_points = [0]
    #print("Question Points:",ques_points)
    score = list(map(float, ques_points))
    score = sum(score)
    # #print("Score:",score)
    total_score = {}
    total_score['score'] = int(math.ceil(score))
    total_score['total_points'] = student['total_points']
    # #print("Total Points:",total_score['total_points'])
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT F_name,L_name,roll FROM student WHERE S_id = %s",[student['user']])
    stud_info = cur.fetchone()
    cur.close()
    # #print(session)
    if student is not None:
        # # #print("exists")
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM questions WHERE quiz_id = %s",[session['quiz_id']])
        records = cur.fetchall()
        questions = list()
        question_index = list()
        for row in records:
            questions.append(row)
            if row['ans_type']==1:
                question_index.append(str(row['q_id']))
        # #print(questions[0]['q_id'])
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT selected_opt,ques_id,ques_type,one_line_ans,desc_ans_name,time_per_ques FROM quiz_responses WHERE quiz_id = %s AND user_inserted=%s",(session['quiz_id'],stud_id))
        quiz_response = cur.fetchone()
        # # #print(type(quiz_response))
        cur.close()

        if quiz_response is not None:
            ques_index = quiz_response['ques_id'].split(",")
            if quiz_response['one_line_ans'] is not None:
                res_one_line = quiz_response['one_line_ans'].split("$,")
            else:
                res_one_line = []
            if quiz_response['ques_id'] is not None:
                ques_index = quiz_response['ques_id'].split(",")
            else:
                ques_index = []
            if quiz_response['selected_opt'] is not None:
                res_select_opt_mcq = quiz_response['selected_opt'].split(",")
            else:
                res_select_opt_mcq = []
            if quiz_response['desc_ans_name'] is not None:
                res_select_desc_ans = quiz_response['desc_ans_name'].split(",")
            else:   
                res_select_desc_ans = []

            ques_type = quiz_response['ques_type'].split(",")
            time_per_ques = quiz_response['time_per_ques'].split(",")
            copy = 0
        else:
            ques_index = question_index
            res_one_line = []
            res_select_opt_mcq = []
            ques_type = []
            time_per_ques = []
            copy = 1

        
        answers = list()
        mcq_ct = 0
        one_line_ct = 0
        # #print(ques_type)
        # #print(ques_index)
        # #print(res_one_line)
        # #print(res_select_opt_mcq)
        if len(ques_type)>0:
            for i in range(len(ques_type)):
                if ques_type[i] == '0':
                    answers.append(res_select_opt_mcq[mcq_ct])
                    mcq_ct += 1
                elif ques_type[i] == '1':
                    answers.append(res_one_line[one_line_ct])
                    one_line_ct += 1
        else:
            answers = []
        #print("Answers:",answers)
        op = list()
        for i in range(len(questions)):
            #print("I:",i," type is :",type(i))
            op1 = {}
            op1['ques'] = questions[i]['question']
            op1['point'] = questions[i]['points']
            op1['ans_type'] = questions[i]['ans_type']
            op1['opt1'] = questions[i]['opt1']
            op1['opt2'] = questions[i]['opt2']
            op1['opt3'] = questions[i]['opt3']
            op1['opt4'] = questions[i]['opt4']
            op1['correct_opt'] = questions[i]['correct_opt']
            #print('ques_index',ques_index)
            if str(questions[i]['q_id']) in ques_index :
                index = ques_index.index(str(questions[i]['q_id']))
                #print("index:",index)
                if quiz_response is not None:
                    op1['answered'] = answers[index]
                    op1['got_point'] = ques_points[index]
                    op1['time_per_ques'] = time_per_ques[index]
                else:
                    op1['answered'] = ''
                    op1['got_point'] = ques_points[index]
                    op1['time_per_ques'] = ''
            else:
                op1['answered'] = ""
                op1['got_point'] = "0"
                op1['time_per_ques'] = "00:00:00"
            #print('op1',op1)
            #print(op)
            op.append(op1)
        #print(op)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT SUM(points) AS total_points FROM questions WHERE quiz_id =%s', [session['quiz_id']])
        total_pts = cursor.fetchone()
        total_pts['total_points'] = int(total_pts['total_points'])
        return render_template('mark_answer.html',msg = "",ques=op,len = len(questions),ques_no=1,checked=student['pending_chk'],stud=stud_info,score=total_score,student_id=stud_id,tried_copy=copy,total_points=total_pts['total_points'])
    else:
        return render_template('mark_answer.html',msg = "Not Attempted The Quiz!")

@quiz.route('/mark_student/',methods=['POST', 'GET'])
@login_required
def update_marks_student():
    stud_id = request.form['stud_id']
    # #print("STudent ID:",stud_id)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT q_id,ans_type FROM questions WHERE quiz_id = %s",[session['quiz_id']])
    total_ques_one_line = cur.fetchall()
    cur.close()
    marks = list()
    ques_index = list()
    for i in range(len(total_ques_one_line)):
        if total_ques_one_line[i]['ans_type']==1:
            marks.append(request.form['ans'+str(i+1)])
            ques_index.append(str(total_ques_one_line[i]['q_id']))
    # #print("Marks got :",marks)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT ques_id FROM quiz_responses WHERE quiz_id = %s AND user_inserted =%s ",(session['quiz_id'],stud_id))
    question_shuffle = cur.fetchone()
    cur.close()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT ques_points FROM score WHERE quiz_id = %s AND user =%s AND quiz_attempted=1 AND (pending_chk=1 OR pending_chk=0)",(session['quiz_id'],stud_id))
    user_ques_points = cur.fetchone()
    cur.close()
    # #print(user_ques_points)
    if question_shuffle is not None:
        questions_id = question_shuffle['ques_id'].split(",")
    else:
        questions_id = ques_index
    # #print('questions_id',questions_id)
    if user_ques_points['ques_points']!='':
        points = user_ques_points['ques_points'].split(",")
    else:
        points = [0]
    # #print('points',points)
    # #print(total_ques_one_line)
    mcq_ct = 0
    # #print('user_ques_points',user_ques_points)
    if user_ques_points['ques_points']!='' or user_ques_points['ques_points'] is not None:
        for i in range(len(total_ques_one_line)):
            # #print(total_ques_one_line[i]['q_id'])
            if total_ques_one_line[i]['ans_type']==1:
                if str(total_ques_one_line[i]['q_id']) in questions_id :
                    q_ind = questions_id.index(str(total_ques_one_line[i]['q_id']))
                    # #print("Q_ind:",q_ind)
                    points[q_ind] = marks[mcq_ct]
                    mcq_ct += 1

            # #print(points)
        points = list(map(float, points))
        total_points = sum(points)
        total_points = int(math.ceil(total_points))
        # #print(total_points)
        # #print(points)
        str_usr_points = ['{:.1f}'.format(x) for x in points]
        # #print(str_usr_points)
        str_usr_points = ','.join(str_usr_points)
        # #print(str_usr_points)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("UPDATE score SET ques_points = %s , user_score = %s , pending_chk  = 0 WHERE quiz_id = %s AND user=%s" ,(str_usr_points,total_points,session['quiz_id'],stud_id))    
        mysql.connection.commit()
        session['message'] = 'Successfully Marked!'
        session['message_color'] = 1
        return redirect('/quiz/show_graph_value?label=Quiz Attempted in %:')
    else:
        session['message'] = 'Failed to Marked!'
        session['message_color'] = 0
        return redirect(url_for('quiz.response')) 

@quiz.route('/del_response/',methods=['POST'])
@login_required
def response_delete():
    #print(session)
    q_index = request.form['index']
    # #print("exists")
    #print("Quiz ID:"+session['quiz_id'])
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM quiz_responses WHERE quiz_id = %s",[session['quiz_id']])    
    mysql.connection.commit()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM score WHERE quiz_id = %s",[session['quiz_id']])    
    mysql.connection.commit()
    session.pop("quiz_id",None)
    session.pop("ques_no",None)
    # #print("Not Exists!")
    session['message'] = 'Quiz Deleted Successfully!'
    return redirect(url_for('quiz.quizes_all'))