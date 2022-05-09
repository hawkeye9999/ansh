from flask import Blueprint, request, render_template, abort, session, redirect, url_for,jsonify
from app import mysql,app_root
from werkzeug.utils import secure_filename
import MySQLdb.cursors
from datetime import date
import datetime
import json,pytz,requests, base64, math, random, os, shutil
from pathlib import Path 
from check_login import login_required

student = Blueprint('student', __name__,template_folder='templates')
IST = pytz.timezone('Asia/Kolkata')

@student.route('/quiz_attempt/')
@login_required
def student_quiz():
    # if session.get("quiz_id") is not None:
    print("QUiz Attempt")
    print(session)
    print("\n")
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT \
        det.quiz_started,det.quiz_id,det.q_title,det.q_sub,det.q_date,det.q_time_start,det.q_time_end,det.show_answer,det.quiz_type,ques.total_question\
         FROM \
         (SELECT \
         quiz_started,quiz_id,q_title,q_sub,q_date,q_time_start,q_time_end,show_answer,quiz_type \
          FROM quiz_det \
           WHERE quiz_id=%s AND quiz_status=1)\
           as det \
            INNER JOIN \
            (SELECT \
             quiz_id,COUNT(q_no) AS total_question \
              FROM questions WHERE quiz_id=%s)as ques \
               on det.quiz_id = ques.quiz_id ",(session['quiz_id'],session['quiz_id']))
    quiz_det = cur.fetchone()
    cur.close()
    # # #print(quiz_det)
    if quiz_det:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT switch_limit FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])
        temp = cur.fetchone()
        cur.close()
        session['max_limit'] = int(temp['switch_limit'])
        dt = datetime.datetime.strptime(quiz_det['q_date'], '%Y-%m-%d').strftime('%d/%m/%y')
        db_date = datetime.datetime.strptime(quiz_det['q_date'], '%Y-%m-%d').date()
        session['quiz_show'] = quiz_det['show_answer']
        session['quiz_end'] = quiz_det['q_time_end']
        session['quiz_date'] = quiz_det['q_date']
        session['quiz_type'] = quiz_det['quiz_type']
        # #print("Show:")
        dt1 = datetime.datetime.strptime(datetime.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d').date()
        # #print(dt)
        # #print(type(dt))
        today_time = datetime.datetime.now(IST).strftime('%H:%M')
        st=datetime.datetime.strptime(quiz_det['q_time_start'],'%H:%M').time()
        end=datetime.datetime.strptime(quiz_det['q_time_end'],'%H:%M').time()
        t_time=datetime.datetime.strptime(today_time,'%H:%M').time()
        # # #print(dt == db_d)
        # # #print(t_time)
        # # #print(st)
        # # #print(end)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT quiz_attempted FROM score WHERE quiz_id = %s AND user=%s",(session['quiz_id'],session['svv']))
        rec = cur.fetchone()
        if dt1 < db_date or (dt1 == db_date and t_time<st and quiz_det['quiz_started']==0) and not rec:
            print("IF1")
            return render_template('attempt_quiz.html',message="",q_details=quiz_det,date=dt)
        elif dt1 > db_date or (dt1 == db_date and  (t_time>=end) and quiz_det['quiz_started']==0) or rec:
            print("IF2")
            return redirect(url_for('student.score_quiz'))
        elif dt1 == db_date and t_time>st and quiz_det['quiz_started']==0:
        # if dt1 < db_date or (dt1 == db_date and t_time<st):
            # return render_template('attempt_quiz.html',message="",q_details="",date="",points="")
            print("IF3")
            return render_template('attempt_quiz.html',message="Quiz not started yet!",q_details="",date="")
        elif dt1 == db_date and quiz_det['quiz_started']==1:
        # elif dt1 == db_date and  (t_time>=st and t_time<end):
            print("IF4")
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT quiz_attempted FROM score WHERE quiz_id = %s AND user=%s",(session['quiz_id'],session['svv']))
            rec = cur.fetchone()
            # #print(rec)
            cur.close()
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT ques_type,selected_opt,one_line_ans,ques_id FROM quiz_responses WHERE quiz_id = %s AND user_inserted = %s",(session['quiz_id'],session['svv']))
            user_attempt_ques = cur.fetchone()
            cur.close()
            if rec is None:
                if session.get('submitted_ques') is None or session.get('q_nos') is None:
                    # #print(session)
                    if user_attempt_ques is None:
                        session['quiz_start'] = datetime.datetime.now(IST).strftime('%H:%M:%S')   
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("SELECT * FROM questions WHERE quiz_id = %s",[session['quiz_id']])
                    records = cur.fetchall()
                    cur.close()
                    qts = list()
                    question_nos = list()
                    ques_index = 0
                    session['submitted_ques'] = 0
                    session['ques_submitted'] = list()                
                    if user_attempt_ques is None:
                        for row in records:
                            qts.append(row)
                            question_nos.append(row['q_id'])
                        random.shuffle(question_nos)
                        print(question_nos)
                    else:
                        session.get('submitted_ques')
                        questions_attempted = user_attempt_ques['ques_id'].split(',')
                        print(questions_attempted)
                        session['submitted_ques'] = len(questions_attempted)
                        session['ques_submitted'] = [int(i) for i in questions_attempted]
                        print("session['submitted_ques']:",session['submitted_ques'])
                        print("session['ques_submitted']:",session['ques_submitted'])
                        for row in records:
                            if str(row['q_id']) in questions_attempted:
                                qts.append(row)
                                question_nos.append(row['q_id'])
                        for row in records:
                            print(row['q_id'])
                            if str(row['q_id']) not in questions_attempted:
                                qts.append(row)
                                question_nos.append(row['q_id'])
                        ques_type = [int(x) for x in user_attempt_ques['ques_type'].split(',')]
                        one_line_ans_st = user_attempt_ques['one_line_ans']
                        mcq_st = user_attempt_ques['selected_opt']
                        if user_attempt_ques['one_line_ans']:
                            one_line_ans_st = user_attempt_ques['one_line_ans'].split(',')
                        if user_attempt_ques['selected_opt']:
                            mcq_st = user_attempt_ques['selected_opt'].split(',')
                        print("Attempted:",questions_attempted)
                        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                        cur.execute("SELECT * FROM questions WHERE quiz_id = %s AND q_id = %s",(session['quiz_id'],int(questions_attempted[0])))
                        records_pr = cur.fetchone()
                        cur.close()
                        records_pr['submitted'] = 1
                        answers = list()
                        mcq_ct = 0
                        one_line_ct = 0
                        user_submit_ques_splt_index = 0
                        for i in range(len(ques_type)):
                            if ques_type[i] == 0:
                                answers.append(mcq_st[mcq_ct])
                                mcq_ct += 1
                            elif ques_type[i] == 1:
                                answers.append(one_line_ans_st[one_line_ct])
                                one_line_ct += 1
                        print("answers:",answers)
                        records_pr['submitted_answer'] = answers[user_submit_ques_splt_index]
                        print("Records:",records)
                    print("qts",qts)
                    print("question_nos",question_nos)
                    for row in records:
                        if question_nos[0] == row['q_id']:
                            ques_index = records.index(row)
                    print('Question Index:')
                    print(ques_index)
                    session['total_ques'] = len(records)
                    session['q_nos'] = question_nos
                    session['current_ques'] = question_nos[0]
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("SELECT q_timer,q_time_division,q_time_end FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])
                    records2 = cur.fetchone()
                    cur.close()
                    session['q_timer'] = records2['q_timer']
                    session['q_time_division'] = records2['q_time_division']
                    time = ""
                    if records2['q_timer'] == 1 and records2['q_time_division'] == 'm':
                        time = datetime.datetime.strptime(qts[ques_index]['q_time'],"%H:%M:%S")
                        # #print("Time:",time)
                        a_timedelta = time - datetime.datetime(1900, 1, 1)
                        seconds = a_timedelta.total_seconds()
                        # #print("Total Time:",time)
                        # #print('seconds',seconds)
                        total_time = int(math.ceil(seconds))
                        # time_per_ques = seconds / session['total_ques']
                        time_per_ques = seconds
                        # #print("Time Per Question:",seconds)
                        time = int(math.ceil(time_per_ques))
                        session['time_per_ques'] = time
                        dt_time_now = datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                        # #print(dt_time_now)
                        now = datetime.datetime.strptime(dt_time_now,'%Y-%m-%d %H:%M:%S')
                        # # #print("now",n)
                        added_seconds = datetime.timedelta(0, time)
                        session['question_timer_finish'] = now + added_seconds
                        # #print("session['question_timer_finish']",session['question_timer_finish'])
                    elif records2['q_timer'] == 1 and records2['q_time_division'] == 'eq':
                        end_time = datetime.datetime.strptime(qts[ques_index]['q_time'],"%H:%M:%S")
                        a_timedelta = end_time - datetime.datetime(1900, 1, 1)
                        seconds = a_timedelta.total_seconds()
                        # #print("Total Time:",end_time)
                        total_time = int(math.ceil(seconds))
                        time_per_ques = seconds / session['total_ques']
                        # #print("Time Per Question:",seconds)
                        time = int(math.ceil(time_per_ques))
                        session['time_per_ques'] = time
                        now = datetime.datetime.now(IST)
                        # #print("now",now)
                        added_seconds = datetime.timedelta(0, time)
                        session['question_timer_finish'] = now + added_seconds
                        # #print("session['question_timer_finish']",session['question_timer_finish'])
                        dt_time_now = datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                        # #print(dt_time_now)
                        now = datetime.datetime.strptime(dt_time_now,'%Y-%m-%d %H:%M:%S')
                        # # #print("now",n)
                        added_seconds = datetime.timedelta(0, time)
                        session['question_timer_finish'] = now + added_seconds
                        # #print("session['question_timer_finish']",session['question_timer_finish'])
                    # #print("Time:",time)

                # # #print(questions[1])
                    if user_attempt_ques is None:
                        print("Question  Not Attempted")
                        print(session)
                        return render_template('quiz.html',message="",questions=qts[ques_index],ques_no=session['submitted_ques']+1,total=0,time_per_ques=time,attempted=0)
                    else:
                        print("Question Attempted")
                        print(session)
                        return render_template('quiz.html',message="",questions=records_pr,ques_no=1,total=0,time_per_ques=time,attempted=0)
                elif session.get('submitted_ques') > 0 and session.get('submitted_ques') < session.get('total_ques'):
                    # #print(session)
                    question_for_no = session['q_nos']
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("SELECT * FROM questions WHERE quiz_id = %s AND q_id = %s",(session['quiz_id'],question_for_no[session['submitted_ques']]))
                    records = cur.fetchone()
                    time = ""
                    current_ques = session['current_ques']
                    q_nos = session['q_nos']
                    question_number = q_nos.index(current_ques)
                    if session['q_timer'] == 1 and session['q_time_division'] == 'm':
                        end_time = datetime.datetime.strptime(records['q_time'],"%H:%M:%S")
                        a_timedelta = end_time - datetime.datetime(1900, 1, 1)
                        seconds = a_timedelta.total_seconds()
                        # #print("Total Time:",end_time)
                        total_time = int(math.ceil(seconds))
                        # time_per_ques = seconds / session['total_ques']
                        time_per_ques = seconds
                        # #print("Time Per Question:",seconds)
                        time = int(math.ceil(time_per_ques))
                        session['time_per_ques'] = time
                        # #print("session['time_per_ques']:",session['time_per_ques'])
                        now = datetime.datetime.now(IST)
                        # #print("now",now)
                        added_seconds = datetime.timedelta(0, time)
                        session['question_timer_finish'] = now + added_seconds
                        # #print("session['question_timer_finish']",session['question_timer_finish'])
                        dt_time_now = datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                        # #print(dt_time_now)
                        now = datetime.datetime.strptime(dt_time_now,'%Y-%m-%d %H:%M:%S')
                        # # #print("now",n)
                        added_seconds = datetime.timedelta(0, time)
                        session['question_timer_finish'] = now + added_seconds
                        # #print("session['question_timer_finish']",session['question_timer_finish'])
                    elif session['q_timer'] == 1 and session['q_time_division'] == 'eq':
                        # session['quiz_end'] = session['quiz_end']+':00'
                        end_time = datetime.datetime.strptime(records['q_time'],"%H:%M:%S")
                        a_timedelta = end_time - datetime.datetime(1900, 1, 1)
                        # #print(type(a_timedelta))
                        seconds = a_timedelta.total_seconds()
                        # #print("Total Time:",end_time)
                        total_time = int(math.ceil(seconds))
                        time_per_ques = seconds / session['total_ques']
                        # #print("Time Per Question:",seconds)
                        time = int(math.ceil(time_per_ques))
                        session['time_per_ques'] = time
                        # #print("session['time_per_ques']:",session['time_per_ques'])
                        now = datetime.datetime.now(IST)
                        # #print("now",now)
                        added_seconds = datetime.timedelta(0, time)
                        session['question_timer_finish'] = now + added_seconds
                        # #print("session['question_timer_finish']",session['question_timer_finish'])
                        dt_time_now = datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                        # #print(dt_time_now)
                        now = datetime.datetime.strptime(dt_time_now,'%Y-%m-%d %H:%M:%S')
                        # # #print("now",n)
                        added_seconds = datetime.timedelta(0, time)
                        session['question_timer_finish'] = now + added_seconds
                        # #print("session['question_timer_finish']",session['question_timer_finish'])

                    # #print("The time Per Question:",time)
                    return render_template('quiz.html',message="",questions=records,ques_no=question_number+1,total=0,time_per_ques=time,attempted=0)
                elif session.get('submitted_ques')==0 :
                    question_for_no = session['q_nos']
                    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("SELECT * FROM questions WHERE quiz_id = %s AND q_id = %s",(session['quiz_id'],question_for_no[0]))
                    records = cur.fetchone()
                    time = ""
                    if session['q_timer'] == 1 and session['q_time_division'] == 'm':
                        time = records['q_time']
                    elif session['q_timer'] == 1 and session['q_time_division'] == 'eq':
                        time = session['time_per_ques']
                    # #print("The time Per Question:",time)
                    return render_template('quiz.html',message="",questions=records,ques_no=int(session['submitted_ques']+1),total=0,time_per_ques=time,attempted=0,max_limit = session['max_limit'])
                else:
                    return render_template('attempt_quiz.html',message="Sorry Quiz is Already Filled!",q_details="",date="",max_limit = session['max_limit'])
            else:
                return redirect(url_for('student.score_quiz'))
        elif dt1 > db_date or (dt1 == db_date and  (t_time>=end)):
            print("IF5")
            return redirect(url_for('student.score_quiz'))
        else:
            print("IF6")
            return render_template('attempt_quiz.html',message="Quiz Not Found",q_details="",date="",max_limit="")
    else:
        return render_template('attempt_quiz.html',message="Quiz Not Saved By Faculty!",q_details="",date="",max_limit="")

@student.route('/submit_question_old/',methods=['POST', 'GET'])
@login_required
def question_submit_old():
    if session.get('submitted_ques') is not None or session.get('q_nos') is not None:
        ques_id = request.form['question_id']
        ans_type = int(request.form['ans_type'])
        # #print("Answer Type is:",type(ans_type))
        if ans_type==0:
            if 'option_select' in request.form:
                opt_select = 'option'+request.form['option_select']
            else:
                opt_select = ''
            # #print("selected_opt:")
            # #print(opt_select)
        elif ans_type==1:
            one_line_ans = request.form['one_line_ans']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT ques_id FROM quiz_responses WHERE quiz_id = %s AND user_inserted = %s",(session['quiz_id'],session['svv']))
        user_attempt_ques = cur.fetchone()
        cur.close()
        if user_attempt_ques is not None:
            user_attempt_ques = len(user_attempt_ques['ques_id'].split(","))
        else:
            user_attempt_ques = 0
        # print("attempt:",user_attempt_ques)
        if user_attempt_ques == 0:
            if session.get('quiz_start') is not None:
                end_time = datetime.datetime.now(IST).strftime("%H:%M:%S")
                start_time = session['quiz_start']
            else:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("SELECT q_time_start FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])
                rec = cur.fetchone()
                cur.close()
                rec['q_time_start'] = rec['q_time_start']+':00'
                start_dt = datetime.datetime.strptime(rec['q_time_start'], '%H:%M:%S')
                time_per_ques = datetime.datetime.now(IST).strftime("%H:%M:%S")
                end_time = datetime.datetime.strptime(time_per_ques,'%H:%M:%S')
                diff = (end_time - start_dt)
                hours, remainder = divmod(diff.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                start_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
                print(start_time)
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if ans_type==0:
                cur.execute("INSERT INTO quiz_responses (selected_opt,user_inserted,ques_id,ques_type,quiz_id,time_per_ques,quiz_start) VALUES (%s,%s,%s,%s,%s,%s,%s)",(opt_select,session['svv'],ques_id,ans_type,session['quiz_id'],end_time,start_time))    
            elif ans_type==1:
                cur.execute("INSERT INTO quiz_responses (one_line_ans,user_inserted,ques_id,ques_type,quiz_id,time_per_ques,quiz_start) VALUES (%s,%s,%s,%s,%s,%s,%s)",(one_line_ans,session['svv'],ques_id,ans_type,session['quiz_id'],end_time,start_time))    
        elif user_attempt_ques > 0:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT selected_opt,one_line_ans,ques_type,ques_id,time_per_ques FROM quiz_responses WHERE quiz_id = %s AND user_inserted=%s",(session['quiz_id'],session['svv']))
            record = cur.fetchone()
            cur.close()
            updt_ques_id = record['ques_id']+','+ques_id
            updt_ques_type = str(record['ques_type'])+','+str(ans_type)
            end_time = datetime.datetime.now(IST).strftime("%H:%M:%S")
            end_time = record['time_per_ques']+','+end_time
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if ans_type==0:
                if record['selected_opt'] is not None:
                    updt_opt = record['selected_opt']+','+opt_select
                else:
                    updt_opt = opt_select
                cur.execute("UPDATE quiz_responses SET selected_opt = %s , ques_type = %s , ques_id  = %s , time_per_ques = %s  WHERE quiz_id = %s AND user_inserted=%s" ,(updt_opt,updt_ques_type,updt_ques_id,end_time,session['quiz_id'],session['svv']))
            elif ans_type==1:
                if record['one_line_ans'] is not None:
                    updt_ans = record['one_line_ans']+'$,'+one_line_ans
                else:
                    updt_ans = one_line_ans
                cur.execute("UPDATE quiz_responses SET one_line_ans = %s , ques_type = %s , ques_id  = %s , time_per_ques = %s WHERE quiz_id = %s AND user_inserted=%s" ,(updt_ans,updt_ques_type,updt_ques_id,end_time,session['quiz_id'],session['svv']))
        mysql.connection.commit()
        session['submitted_ques'] = int(session['submitted_ques'])+1
        ques_submitted = session['ques_submitted']
        print("ques_submitted:",ques_submitted)
        print("ques_id:",ques_id)
        if ques_submitted is not None:
            ques_submitted.append(int(ques_id))
            session['ques_submitted'] = ques_submitted
        else:
            ques_submitted = list()
            ques_submitted.append(int(ques_id))
            session['ques_submitted'] = ques_submitted
        if session.get('submitted_ques') ==  session.get('total_ques'):
            return redirect(url_for('student.finish_quiz'))
            # print(session)
        else:
            q_nos = session['q_nos']
            q_nos_index = q_nos.index(session['current_ques'])
            if(len(q_nos)==(q_nos_index+1)):
                session['current_ques'] = q_nos[q_nos_index]
            else:
                session['current_ques'] = q_nos[q_nos_index+1]
            # print(session)
            return redirect(url_for('student.student_quiz'))

@student.route('/submit_question/',methods=['POST', 'GET'])
@login_required
def question_submit():
    if session.get('submitted_ques') is not None or session.get('q_nos') is not None:
        ques_id = request.form['question_id']
        ans_type = int(request.form['ans_type'])
        # #print("Answer Type is:",type(ans_type))
        if ans_type==0:
            if 'option_select' in request.form:
                opt_select = 'option'+request.form['option_select']
            else:
                opt_select = ''
            # #print("selected_opt:")
            # #print(opt_select)
        elif ans_type==1:
            one_line_ans = request.form['one_line_ans']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT ques_id FROM quiz_responses WHERE quiz_id = %s AND user_inserted = %s",(session['quiz_id'],session['svv']))
        user_attempt_ques = cur.fetchone()
        cur.close()
        if user_attempt_ques is not None:
            user_attempt_ques = len(user_attempt_ques['ques_id'].split(","))
        else:
            user_attempt_ques = 0
        # print("attempt:",user_attempt_ques)
        if user_attempt_ques == 0:
            if session.get('quiz_start') is not None:
                end_time = datetime.datetime.now(IST).strftime("%H:%M:%S")
                start_time = session['quiz_start']
            else:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("SELECT q_time_start FROM quiz_det WHERE quiz_id = %s",[session['quiz_id']])
                rec = cur.fetchone()
                cur.close()
                rec['q_time_start'] = rec['q_time_start']+':00'
                start_dt = datetime.datetime.strptime(rec['q_time_start'], '%H:%M:%S')
                time_per_ques = datetime.datetime.now(IST).strftime("%H:%M:%S")
                end_time = datetime.datetime.strptime(time_per_ques,'%H:%M:%S')
                diff = (end_time - start_dt)
                hours, remainder = divmod(diff.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                start_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
                # print(start_time)
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if ans_type==0:
                cur.execute("INSERT INTO quiz_responses (selected_opt,user_inserted,ques_id,ques_type,quiz_id,time_per_ques,quiz_start) VALUES (%s,%s,%s,%s,%s,%s,%s)",(opt_select,session['svv'],ques_id,ans_type,session['quiz_id'],end_time,start_time))    
            elif ans_type==1:
                cur.execute("INSERT INTO quiz_responses (one_line_ans,user_inserted,ques_id,ques_type,quiz_id,time_per_ques,quiz_start) VALUES (%s,%s,%s,%s,%s,%s,%s)",(one_line_ans,session['svv'],ques_id,ans_type,session['quiz_id'],end_time,start_time))    
        elif user_attempt_ques > 0:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT selected_opt,one_line_ans,ques_type,ques_id,time_per_ques FROM quiz_responses WHERE quiz_id = %s AND user_inserted=%s",(session['quiz_id'],session['svv']))
            record = cur.fetchone()
            cur.close()
            print("record['ques_id']",record['ques_id'])
            user_submit_ques_splt = [int(x) for x in record['ques_id'].split(',')]
            # print("user_submit_ques_splt:",user_submit_ques_splt)
            # print("user_attempt_ques:",user_attempt_ques)
            
            if int(ques_id) not in user_submit_ques_splt:
                updt_ques_id = record['ques_id']+','+ques_id
                updt_ques_type = str(record['ques_type'])+','+str(ans_type)
                end_time = datetime.datetime.now(IST).strftime("%H:%M:%S")
                end_time = record['time_per_ques']+','+end_time
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                if ans_type==0:
                    if record['selected_opt'] is not None:
                        updt_opt = record['selected_opt']+','+opt_select
                    else:
                        updt_opt = opt_select
                    cur.execute("UPDATE quiz_responses SET selected_opt = %s , ques_type = %s , ques_id  = %s , time_per_ques = %s  WHERE quiz_id = %s AND user_inserted=%s" ,(updt_opt,updt_ques_type,updt_ques_id,end_time,session['quiz_id'],session['svv']))
                elif ans_type==1:
                    if record['one_line_ans'] is not None:
                        updt_ans = record['one_line_ans']+'$,'+one_line_ans
                    else:
                        updt_ans = one_line_ans
                    cur.execute("UPDATE quiz_responses SET one_line_ans = %s , ques_type = %s , ques_id  = %s , time_per_ques = %s WHERE quiz_id = %s AND user_inserted=%s" ,(updt_ans,updt_ques_type,updt_ques_id,end_time,session['quiz_id'],session['svv']))
            
            elif int(ques_id) in user_submit_ques_splt: # finding index and removing item from the answer submitted list
                ques_type = [int(x) for x in record['ques_type'].split(',')]
                one_line_ans_st = record['one_line_ans']
                end_time = record['time_per_ques'].split(',')
                mcq_st = record['selected_opt']
                if record['one_line_ans']:
                    one_line_ans_st = record['one_line_ans'].split(',')
                if record['selected_opt']:
                    mcq_st = record['selected_opt'].split(',')
                answers = list()
                mcq_ct = 0
                one_line_ct = 0
                for i in range(len(ques_type)):
                    if ques_type[i] == 0:
                        answers.append(mcq_st[mcq_ct])
                        mcq_ct += 1
                    elif ques_type[i] == 1:
                        answers.append(one_line_ans_st[one_line_ct])
                        one_line_ct += 1
                print("answers:",answers)
                user_submit_ques_splt_index = user_submit_ques_splt.index(int(ques_id))  
                print("Index to pop",user_submit_ques_splt_index)
                mcq_ct = 0
                one_line_ct = 0
                for i in range(len(ques_type)):
                    if i==user_submit_ques_splt_index:
                        if ques_type[i] == 0:
                           mcq_st.pop(mcq_ct)
                        elif ques_type[i] == 1:
                            one_line_ans_st.pop(one_line_ct)
                    if ques_type[i] == 0:
                        mcq_ct += 1
                    elif ques_type[i] == 1:
                        one_line_ct += 1
                answers.pop(user_submit_ques_splt_index)
                ques_type.pop(user_submit_ques_splt_index)
                user_submit_ques_splt.pop(user_submit_ques_splt_index)
                end_time.pop(user_submit_ques_splt_index)
                updt_mcq = ""
                updt_one_line = ""
                if mcq_st:
                    updt_mcq = ','.join(mcq_st)
                    print("updt_mcq:",updt_mcq)
                if one_line_ans_st:
                    updt_one_line = ','.join(one_line_ans_st)
                    print("updt_one_line:",updt_one_line)
                if ans_type==0:
                    if updt_mcq == "":
                        updt_mcq += opt_select
                    else:
                        updt_mcq += ','+opt_select
                elif ans_type==1:
                    if updt_one_line == "":
                        updt_one_line += one_line_ans
                    else:
                        updt_one_line += ','+one_line_ans
                user_submit_ques_splt = [str(x) for x in user_submit_ques_splt]
                updt_ques_id = ','.join(user_submit_ques_splt)
                updt_ques_id += ','+ques_id
                ques_type = [str(x) for x in ques_type]
                updt_ques_type = ','.join(ques_type)
                updt_ques_type += ','+str(ans_type)
                now_time = datetime.datetime.now(IST).strftime("%H:%M:%S")
                end_time = ','.join(end_time)
                end_time += ','+now_time
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                if ans_type==0:
                    cur.execute("UPDATE quiz_responses SET selected_opt = %s , ques_type = %s , ques_id  = %s , time_per_ques = %s  WHERE quiz_id = %s AND user_inserted=%s" ,(updt_mcq,updt_ques_type,updt_ques_id,end_time,session['quiz_id'],session['svv']))
                elif ans_type==1:                
                    cur.execute("UPDATE quiz_responses SET one_line_ans = %s , ques_type = %s , ques_id  = %s , time_per_ques = %s WHERE quiz_id = %s AND user_inserted=%s" ,(updt_one_line,updt_ques_type,updt_ques_id,end_time,session['quiz_id'],session['svv']))

        mysql.connection.commit()
        ques_submitted = session['ques_submitted']
        print("ques_submitted:",ques_submitted)
        print("ques_id:",ques_id)
        if ques_submitted is not None:
            if int(ques_id) not in ques_submitted:
                ques_submitted.append(int(ques_id))
                session['ques_submitted'] = ques_submitted
                session['submitted_ques'] = int(session['submitted_ques'])+1
        else:
            ques_submitted = list()
            ques_submitted.append(int(ques_id))
            session['ques_submitted'] = ques_submitted
            session['submitted_ques'] = int(session['submitted_ques'])+1

        q_nos = session['q_nos']
        q_nos_index = q_nos.index(session['current_ques'])
        print('q_nos_index:',q_nos_index)
        print(session.get('submitted_ques'),session.get('total_ques'),q_nos_index+1,'fffffff')
        
        if (session.get('submitted_ques') ==  session.get('total_ques')) or ((q_nos_index+1)==session.get('total_ques')):
            print("quiz finished")
            return jsonify({"msg":"end"}) 
            # return redirect(url_for('student.finish_quiz'))
        else:
            d = {"question_status":"saved"}
            return jsonify(d)
            # if(len(q_nos)==(q_nos_index+1)):
            #     session['current_ques'] = q_nos[q_nos_index]
            # else:
            #     session['current_ques'] = q_nos[q_nos_index+1]
            # print(session)
            # return redirect(url_for('student.question_submit_mode',mode="next"))

@student.route('/submit_question_mode',methods=['POST', 'GET'])
@login_required
def question_submit_mode():
    if request.method == "POST" or request.method == "GET" :
        if request.method == "POST":
            ques_no = request.form['ques_no'] 
            mode = request.args.get('mode')
            ques_id = request.form['question_id']
            #way is for from where this function is called 0- left right button
            way = 0
            print("Ques-ID:")
            print(ques_id)
            ans_type = int(request.form['ans_type'])
            # #print("Answer Type is:",type(ans_type))
            if ans_type==0:
                if 'option_select' in request.form:
                    opt_select = 'option'+request.form['option_select']
                else:
                    opt_select = ''
                # #print("selected_opt:")
                # #print(opt_select)
            elif ans_type==1:
                one_line_ans = request.form['one_line_ans']
        else:
            mode = request.args['mode']
            ques_no = request.args.get('ques_no')
            print(request.args,'argsss')
            print(session) 
            ques_id = session['current_ques']
            #way is for from where this function is called 1- After Submitting or Updating
            way = 1
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT ques_type,selected_opt,one_line_ans,ques_id FROM quiz_responses WHERE quiz_id = %s AND user_inserted = %s",(session['quiz_id'],session['svv']))
        user_submit_ques = cur.fetchone()
        user_attempt_ques = user_submit_ques
        cur.close()
        if user_attempt_ques is not None:
            user_attempt_ques = len(user_attempt_ques['ques_id'].split(","))
            user_submit_ques_splt = [int(x) for x in user_submit_ques['ques_id'].split(',')]
            print("user_submit_ques_splt:",user_submit_ques_splt)
            print("user_attempt_ques:",user_attempt_ques)
            ques_type = [int(x) for x in user_submit_ques['ques_type'].split(',')]
            one_line_ans_st = user_submit_ques['one_line_ans']
            mcq_st = user_submit_ques['selected_opt']
            if user_submit_ques['one_line_ans']:
                one_line_ans_st = user_submit_ques['one_line_ans'].split(',')
            if user_submit_ques['selected_opt']:
                mcq_st = user_submit_ques['selected_opt'].split(',')
            print("ques_type:",ques_type)
            print("one_line_ans_st:",one_line_ans_st)
            print("mcq_st:",mcq_st)
        else:
            user_submit_ques_splt = []
            user_attempt_ques = 0
        
        if mode=="next" or mode=="prev":
            q_nos = session['q_nos']
            current_ques_index = q_nos.index(session['current_ques'])
            print("Current ques index:",current_ques_index)
        if mode=="next":
            session['current_ques'] = q_nos[current_ques_index+1]

        elif mode=="prev":
            session['current_ques'] = q_nos[current_ques_index-1]
        
        if mode=="next" or mode=="prev":
            if session.get('to_be_submitted_answer') is None or session.get('not_submitted_ques_id') is None:
                print("Navigation First Time")
                session['to_be_submitted_answer'] = list()
                session['not_submitted_ques_id'] = list()
            print("not_submitted_ques_id:",session['not_submitted_ques_id'])
            if int(ques_id) not in session['not_submitted_ques_id'] and int(ques_id) not in session['ques_submitted']:
                print("Attempting a new question not in not_submitted_ques_id and not submitted")
                not_submitted_ques_id = session['not_submitted_ques_id']
                not_submitted_ques_id.append(q_nos[current_ques_index])
                session['not_submitted_ques_id'] = not_submitted_ques_id
                if ans_type==0:
                    session['to_be_submitted_answer'].append(opt_select)
                elif ans_type==1:
                    session['to_be_submitted_answer'].append(one_line_ans)
                prev_attempt = 0
            elif int(ques_id) in session['ques_submitted'] and int(ques_id) not in session['not_submitted_ques_id']:
                print("Question submitted checking if answer is changed or not")
                answers = list()
                mcq_ct = 0
                one_line_ct = 0
                for i in range(len(ques_type)):
                    if ques_type[i] == 0:
                        answers.append(mcq_st[mcq_ct])
                        mcq_ct += 1
                    elif ques_type[i] == 1:
                        answers.append(one_line_ans_st[one_line_ct])
                        one_line_ct += 1
                print("answers:",answers)
                user_submit_ques_splt_index = user_submit_ques_splt.index(int(ques_id))
                prev_submittted_ans  = answers[user_submit_ques_splt_index]
                print("prev_submittted_ans:",prev_submittted_ans)
                if way == 0:
                    if ans_type==0:
                        new_answer = opt_select
                    elif ans_type==1:
                        new_answer = one_line_ans
                    print("new_answer:",new_answer)
                    if prev_submittted_ans != new_answer:
                        not_submitted_ques_id = session['not_submitted_ques_id']
                        not_submitted_ques_id.append(q_nos[current_ques_index])
                        session['not_submitted_ques_id'] = not_submitted_ques_id
                        if ans_type==0:
                            session['to_be_submitted_answer'].append(opt_select)
                        elif ans_type==1:
                            session['to_be_submitted_answer'].append(one_line_ans)
                        ques_submitted = session['ques_submitted']
                        print(ques_submitted)
                        print(int(ques_id))
                        ques_submitted.remove(int(ques_id))
                        session['ques_submitted'] = ques_submitted
                        session['submitted_ques'] = session['submitted_ques']-1
                # prev_attempt = 0
            else:
                print("QUestion attempted before replacing by new value in the session")
                not_submitted_ques_id_index = session['not_submitted_ques_id'].index(int(ques_id))
                print('not_submitted_ques_id_index:',not_submitted_ques_id_index)
                if way==0:
                    to_be_submitted_answer = session['to_be_submitted_answer']
                    if ans_type== 0:
                        to_be_submitted_answer[not_submitted_ques_id_index] = opt_select
                    elif ans_type== 1:
                        to_be_submitted_answer[not_submitted_ques_id_index] = one_line_ans
                    session['to_be_submitted_answer'] = to_be_submitted_answer
                # prev_attempt = 1
            print(session)
            if session['current_ques'] in session['not_submitted_ques_id'] and session['current_ques'] not in session['ques_submitted']:
                print("Have attempted before")
                not_submitted_ques_id_index = session['not_submitted_ques_id'].index(session['current_ques'])
                print('not_submitted_ques_id_index:',not_submitted_ques_id_index)
                prev_attempt = 1
            else:
                print("Not attempted before")
                prev_attempt = 0

        if mode=="next":
            current_ques_index += 1

        elif mode=="prev":
            current_ques_index -= 1

        print("current_ques_index",current_ques_index)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM questions WHERE quiz_id = %s AND q_id = %s",(session['quiz_id'],session['current_ques']))
        records = cur.fetchone()
        print(records)
        # print(type(records))
        print("Prev attempt:",prev_attempt)
        if prev_attempt == 1:
            to_be_submitted_answer = session['to_be_submitted_answer']
            print(to_be_submitted_answer)
            if mode=="next":
                # records['session_answer'] = to_be_submitted_answer[not_submitted_ques_id_index+1]
                records['session_answer'] = to_be_submitted_answer[not_submitted_ques_id_index]
            elif mode=="prev":
                # records['session_answer'] = to_be_submitted_answer[not_submitted_ques_id_index-1]
                records['session_answer'] = to_be_submitted_answer[not_submitted_ques_id_index]
            print(records)
        if way==1:        
        ################ Removing question ID's from the session when it is submitted
            if ques_id in session['not_submitted_ques_id'] and ques_id in session['ques_submitted']:
                not_submitted_ques_id = session['not_submitted_ques_id']
                to_be_submitted_answer = session['to_be_submitted_answer']
                to_be_submitted_answer.pop(not_submitted_ques_id.index(ques_id))
                not_submitted_ques_id.pop(not_submitted_ques_id.index(ques_id))
                session['not_submitted_ques_id'] = not_submitted_ques_id
                session['to_be_submitted_answer'] = to_be_submitted_answer
        ##############
        if session['current_ques'] in user_submit_ques_splt and session['current_ques'] not in session['not_submitted_ques_id']:    
            records['submitted'] = 1
            answers = list()
            mcq_ct = 0
            one_line_ct = 0
            user_submit_ques_splt_index = user_submit_ques_splt.index(session['current_ques'])
            for i in range(len(ques_type)):
                if ques_type[i] == 0:
                    answers.append(mcq_st[mcq_ct])
                    mcq_ct += 1
                elif ques_type[i] == 1:
                    answers.append(one_line_ans_st[one_line_ct])
                    one_line_ct += 1
            print("answers:",answers)
            records['submitted_answer'] = answers[user_submit_ques_splt_index]            
            print("Previous /Next Question is Submitted:",records)
        else:
            records['submitted'] = 0
        time = ""
        print(session)
        if(ques_no == session['total_ques']):
            return redirect(url_for('student.finish_quiz'))   

        # return render_template('quiz.html',message="",questions=records,ques_no=current_ques_index+1,total=0,time_per_ques=time,attempted=prev_attempt)
        send = {}
        send['message'] = ""
        send['questions'] = records
        send['ques_no'] = (current_ques_index+1)
        send['total'] = 0
        send['time_per_ques'] = time
        send['attempted'] = prev_attempt
        send['total_ques'] = session['total_ques']
        print(send)
        return jsonify(send)
        
    else:
        send = {}
        send['message'] = ""
        send['questions'] = ""
        send['ques_no'] = ""
        send['total'] = 0
        send['time_per_ques'] = ""
        send['attempted'] = ""
        send['total_ques'] = ""
        print(send)
        return jsonify(send)

@student.route('/submit_question_mode_old',methods=['POST', 'GET'])
@login_required
def question_submit_mode_old():
    if request.method == "POST" or request.method == "GET" :
        if request.method == "POST":
            mode = request.args.get('mode')
            ques_id = request.form['question_id']
            print("Ques-ID:")
            print(ques_id)
            ans_type = int(request.form['ans_type'])
            # #print("Answer Type is:",type(ans_type))
            if ans_type==0:
                if 'option_select' in request.form:
                    opt_select = 'option'+request.form['option_select']
                else:
                    opt_select = ''
                # #print("selected_opt:")
                # #print(opt_select)
            elif ans_type==1:
                one_line_ans = request.form['one_line_ans']
        else:
            mode = request.args['mode']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT ques_type,selected_opt,one_line_ans,ques_id FROM quiz_responses WHERE quiz_id = %s AND user_inserted = %s",(session['quiz_id'],session['svv']))
        user_submit_ques = cur.fetchone()
        user_attempt_ques = user_submit_ques
        cur.close()
        if user_attempt_ques is not None:
            user_attempt_ques = len(user_attempt_ques['ques_id'].split(","))
            user_submit_ques_splt = [int(x) for x in user_submit_ques['ques_id'].split(',')]
            print("user_submit_ques_splt:",user_submit_ques_splt)
            print("user_attempt_ques:",user_attempt_ques)
            ques_type = [int(x) for x in user_submit_ques['ques_type'].split(',')]
            one_line_ans_st = user_submit_ques['one_line_ans']
            mcq_st = user_submit_ques['selected_opt']
            if user_submit_ques['one_line_ans']:
                one_line_ans_st = user_submit_ques['one_line_ans'].split(',')
            if user_submit_ques['selected_opt']:
                mcq_st = user_submit_ques['selected_opt'].split(',')
            print("ques_type:",ques_type)
            print("one_line_ans_st:",one_line_ans_st)
            print("mcq_st:",mcq_st)
        else:
            user_submit_ques_splt = []
            user_attempt_ques = 0
        if mode=="next":
            q_nos = session['q_nos']
            current_ques_index = q_nos.index(session['current_ques'])
            print("Current ques index")
            print(current_ques_index)
            session['current_ques'] = q_nos[current_ques_index+1]
            if session.get('to_be_submitted_answer') is None or session.get('not_submitted_ques_id') is None:
                session['to_be_submitted_answer'] = list()
                session['not_submitted_ques_id'] = list()
            if request.method=="POST":
                if int(ques_id) in session['ques_submitted'] and int(ques_id) not in session['not_submitted_ques_id']:
                    answers = list()
                    mcq_ct = 0
                    one_line_ct = 0
                    for i in range(len(ques_type)):
                        if ques_type[i] == 0:
                            answers.append(mcq_st[mcq_ct])
                            mcq_ct += 1
                        elif ques_type[i] == 1:
                            answers.append(one_line_ans_st[one_line_ct])
                            one_line_ct += 1
                    print("answers:",answers)
                    user_submit_ques_splt_index = user_submit_ques_splt.index(int(ques_id))
                    prev_submittted_ans  = answers[user_submit_ques_splt_index]
                    if ans_type==0:
                        new_answer = opt_select
                    elif ans_type==1:
                        new_answer = one_line_ans
                    if prev_submittted_ans != new_answer:
                        not_submitted_ques_id = session['not_submitted_ques_id']
                        not_submitted_ques_id.append(q_nos[current_ques_index])
                        session['not_submitted_ques_id'] = not_submitted_ques_id
                        if ans_type==0:
                            session['to_be_submitted_answer'].append(opt_select)
                        elif ans_type==1:
                            session['to_be_submitted_answer'].append(one_line_ans)
                        ques_submitted = session['ques_submitted']
                        print(ques_submitted)
                        print(int(ques_id))
                        ques_submitted.remove(int(ques_id))
                        session['ques_submitted'] = ques_submitted
                        session['submitted_ques'] = session['submitted_ques']-1
                    prev_attempt = 0
                elif int(ques_id) not in session['not_submitted_ques_id']:
                    not_submitted_ques_id = session['not_submitted_ques_id']
                    not_submitted_ques_id.append(q_nos[current_ques_index])
                    session['not_submitted_ques_id'] = not_submitted_ques_id
                    if ans_type==0:
                        session['to_be_submitted_answer'].append(opt_select)
                    elif ans_type==1:
                        session['to_be_submitted_answer'].append(one_line_ans)
                    prev_attempt = 0
                else:
                    not_submitted_ques_id_index = session['not_submitted_ques_id'].index(int(ques_id))
                    print('not_submitted_ques_id_index:',not_submitted_ques_id_index)
                    to_be_submitted_answer = session['to_be_submitted_answer']
                    if ans_type== 0:
                        to_be_submitted_answer[not_submitted_ques_id_index] = opt_select
                    elif ans_type== 1:
                        to_be_submitted_answer[not_submitted_ques_id_index] = one_line_ans
                    session['to_be_submitted_answer'] = to_be_submitted_answer
                    prev_attempt = 1
            else:
                if session['current_ques'] not in session['not_submitted_ques_id']:
                    prev_attempt = 0
                else:
                    not_submitted_ques_id_index = session['not_submitted_ques_id'].index(session['current_ques'])-1
                    prev_attempt = 1
            if session['current_ques'] in user_submit_ques_splt:
                print("q_nos:",q_nos)
                print("user_submit_ques['ques_id']:",user_submit_ques['ques_id'])
                user_submit_ques_splt_index = user_submit_ques_splt.index(session['current_ques'])
                print("user_submit_ques_splt_index",user_submit_ques_splt_index)

                # not_submitted_ques = list(set(q_nos) - set(user_submit_ques_splt))
                # print("not_submitted_ques:",not_submitted_ques)
            print(session)
            current_ques_index += 1
            question_for_no = session['q_nos']

        elif mode=="prev":
            q_nos = session['q_nos']
            current_ques_index = q_nos.index(session['current_ques'])
            print("Current ques index")
            print(current_ques_index)
            session['current_ques'] = q_nos[current_ques_index-1]
            print(session['not_submitted_ques_id'])
            if int(ques_id) in session['ques_submitted'] and int(ques_id) not in session['not_submitted_ques_id']:
                answers = list()
                mcq_ct = 0
                one_line_ct = 0
                for i in range(len(ques_type)):
                    if ques_type[i] == 0:
                        answers.append(mcq_st[mcq_ct])
                        mcq_ct += 1
                    elif ques_type[i] == 1:
                        answers.append(one_line_ans_st[one_line_ct])
                        one_line_ct += 1
                print("answers:",answers)
                user_submit_ques_splt_index = user_submit_ques_splt.index(int(ques_id))
                prev_submittted_ans  = answers[user_submit_ques_splt_index]
                if ans_type==0:
                    new_answer = opt_select
                elif ans_type==1:
                    new_answer = one_line_ans
                if prev_submittted_ans != new_answer:
                    not_submitted_ques_id = session['not_submitted_ques_id']
                    not_submitted_ques_id.append(q_nos[current_ques_index])
                    session['not_submitted_ques_id'] = not_submitted_ques_id
                    if ans_type==0:
                        session['to_be_submitted_answer'].append(opt_select)
                    elif ans_type==1:
                        session['to_be_submitted_answer'].append(one_line_ans)
                    ques_submitted = session['ques_submitted']
                    ques_submitted.remove(int(ques_id))
                    session['ques_submitted'] = ques_submitted
                    session['submitted_ques'] = session['submitted_ques']-1
                    print("session for question submitted updated",session)
                prev_attempt = 0
            elif int(ques_id) not in session['not_submitted_ques_id']:
                print("Not Present")
                not_submitted_ques_id = session['not_submitted_ques_id']
                not_submitted_ques_id.append(q_nos[current_ques_index])
                session['not_submitted_ques_id'] = not_submitted_ques_id
                if ans_type==0:
                    session['to_be_submitted_answer'].append(opt_select)
                elif ans_type==1:
                    session['to_be_submitted_answer'].append(one_line_ans)
                prev_attempt = 0
            else:
                print("Present")
                not_submitted_ques_id_index = session['not_submitted_ques_id'].index(int(ques_id))
                print('not_submitted_ques_id_index:',not_submitted_ques_id_index)
                to_be_submitted_answer = session['to_be_submitted_answer']
                if ans_type== 0:
                    to_be_submitted_answer[not_submitted_ques_id_index] = opt_select
                elif ans_type== 1:
                    to_be_submitted_answer[not_submitted_ques_id_index] = one_line_ans
                session['to_be_submitted_answer'] = to_be_submitted_answer
                prev_attempt = 1
            print("user_submit_ques_splt:",user_submit_ques_splt)
            if session['current_ques'] in user_submit_ques_splt:
                print("q_nos:",q_nos)
                print("user_submit_ques['ques_id']:",user_submit_ques['ques_id'])
                user_submit_ques_splt_index = user_submit_ques_splt.index(session['current_ques'])
                print("user_submit_ques_splt_index",user_submit_ques_splt_index)
                # not_submitted_ques = list(set(q_nos) - set(user_submit_ques_splt))
                # print("not_submitted_ques:",not_submitted_ques)
                    
            print(session)
            current_ques_index -= 1
            print('current_ques_index:',current_ques_index)
            question_for_no = session['q_nos']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM questions WHERE quiz_id = %s AND q_id = %s",(session['quiz_id'],session['current_ques']))
        records = cur.fetchone()
        print(records)
        # print(type(records))
        print("Prev attempt:",prev_attempt)
        if prev_attempt == 1:
            to_be_submitted_answer = session['to_be_submitted_answer']
            print(to_be_submitted_answer)
            if mode=="next":
                records['session_answer'] = to_be_submitted_answer[not_submitted_ques_id_index+1]
            elif mode=="prev":
                records['session_answer'] = to_be_submitted_answer[not_submitted_ques_id_index-1]
            print(records)
            prev_ques_id = q_nos[not_submitted_ques_id_index]    
            ################ Removing question ID's from the session when it is submitted
            if prev_ques_id in session['not_submitted_ques_id'] and prev_ques_id in session['ques_submitted']:
                not_submitted_ques_id = session['not_submitted_ques_id']
                to_be_submitted_answer = session['to_be_submitted_answer']
                to_be_submitted_answer.pop(not_submitted_ques_id.index(prev_ques_id))
                not_submitted_ques_id.pop(not_submitted_ques_id.index(prev_ques_id))
                session['not_submitted_ques_id'] = not_submitted_ques_id
                session['to_be_submitted_answer'] = to_be_submitted_answer
            ##############
        if session['current_ques'] in user_submit_ques_splt and session['current_ques'] not in session['not_submitted_ques_id']:    
            records['submitted'] = 1
            answers = list()
            mcq_ct = 0
            one_line_ct = 0
            for i in range(len(ques_type)):
                if ques_type[i] == 0:
                    answers.append(mcq_st[mcq_ct])
                    mcq_ct += 1
                elif ques_type[i] == 1:
                    answers.append(one_line_ans_st[one_line_ct])
                    one_line_ct += 1
            print("answers:",answers)
            records['submitted_answer'] = answers[user_submit_ques_splt_index]            
            print("Previous /Next Question is Submitted:",records)
        else:
            records['submitted'] = 0
        time = ""
        if session['q_timer'] == 1 and session['q_time_division'] == 'm':
            end_time = datetime.datetime.strptime(records['q_time'],"%H:%M:%S")
            a_timedelta = end_time - datetime.datetime(1900, 1, 1)
            seconds = a_timedelta.total_seconds()
            # #print("Total Time:",end_time)
            total_time = int(math.ceil(seconds))
            # time_per_ques = seconds / session['total_ques']
            time_per_ques = seconds
            # #print("Time Per Question:",seconds)
            time = int(math.ceil(time_per_ques))
            session['time_per_ques'] = time
            # #print("session['time_per_ques']:",session['time_per_ques'])
            now = datetime.datetime.now(IST)
            # #print("now",now)
            added_seconds = datetime.timedelta(0, time)
            session['question_timer_finish'] = now + added_seconds
            # #print("session['question_timer_finish']",session['question_timer_finish'])
            dt_time_now = datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            # #print(dt_time_now)
            now = datetime.datetime.strptime(dt_time_now,'%Y-%m-%d %H:%M:%S')
            # # #print("now",n)
            added_seconds = datetime.timedelta(0, time)
            session['question_timer_finish'] = now + added_seconds
            # #print("session['question_timer_finish']",session['question_timer_finish'])
        elif session['q_timer'] == 1 and session['q_time_division'] == 'eq':
            # session['quiz_end'] = session['quiz_end']+':00'
            end_time = datetime.datetime.strptime(records['q_time'],"%H:%M:%S")
            a_timedelta = end_time - datetime.datetime(1900, 1, 1)
            # #print(type(a_timedelta))
            seconds = a_timedelta.total_seconds()
            # #print("Total Time:",end_time)
            total_time = int(math.ceil(seconds))
            time_per_ques = seconds / session['total_ques']
            # #print("Time Per Question:",seconds)
            time = int(math.ceil(time_per_ques))
            session['time_per_ques'] = time
            # #print("session['time_per_ques']:",session['time_per_ques'])
            now = datetime.datetime.now(IST)
            # #print("now",now)
            added_seconds = datetime.timedelta(0, time)
            session['question_timer_finish'] = now + added_seconds
            # #print("session['question_timer_finish']",session['question_timer_finish'])
            dt_time_now = datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            # #print(dt_time_now)
            now = datetime.datetime.strptime(dt_time_now,'%Y-%m-%d %H:%M:%S')
            # # #print("now",n)
            added_seconds = datetime.timedelta(0, time)
            session['question_timer_finish'] = now + added_seconds
            # #print("session['question_timer_finish']",session['question_timer_finish'])
        # #print("The time Per Question:",time)
        return render_template('quiz.html',message="",questions=records,ques_no=current_ques_index+1,total=0,time_per_ques=time,attempted=prev_attempt)
    else:
        return redirect(request.url+'#')
    

@student.route('/browser_switch/',methods=['POST'])
@login_required
def switch_browser():
    # #print("Swicthing Browser!")
    # session.pop("switch",None)
    # #print(session)
    # return json.dumps("1");
    if session.get('switch') is not None:
        # #print("Switch Times:")
        # #print(session['switch'])
        if session['switch'] < session['max_limit']:
            ok = request.form['get_focus']
            session['switch'] = session['switch']+1
            return json.dumps(session['switch'])
        else:
            if session['switch'] == session['max_limit']:
                session.pop("switch",None)
            return json.dumps(session['max_limit'])
    else:
        session['switch'] = 0
        return json.dumps(session['switch'])


@student.route('/questions_view/')
@login_required
def view_questions():
    mode = session['mode']    
    if mode=="Faculty":
        session['over_access'] = 1
        return redirect(url_for('dashboard'))
    elif mode=="Student":
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT user_score,ques_points FROM score WHERE user = %s AND quiz_id = %s AND pending_chk = 0",(session['svv'],session['quiz_id']))
        student = cur.fetchone()
        cur.close()
        # #print(student)
        ques_points = student['ques_points'].split(",")
        total_score = {}
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT SUM(points) AS total_points FROM questions WHERE quiz_id =%s', [session['quiz_id']])
        total_pts = cursor.fetchone()
        total_score['total_points'] = int(total_pts['total_points'])
        total_score['score'] = student['user_score']
        # total_score['total_points'] = student['total_points']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT selected_opt,ques_id,ques_type,one_line_ans FROM quiz_responses WHERE quiz_id = %s AND user_inserted = %s",(session['quiz_id'],session['svv']))
        quiz_response = cur.fetchone()
        cur.close()
        if quiz_response:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM questions WHERE quiz_id = %s",[session['quiz_id']])
            records = cur.fetchall()
            cur.close()
            questions = list()
            for row in records:
                questions.append(row)
            ques_index = quiz_response['ques_id'].split(",")
            if quiz_response['one_line_ans'] is not None:
                res_one_line = quiz_response['one_line_ans'].split("$,")
            else:
                res_one_line = []
            if quiz_response['selected_opt'] is not None:               
                res_select_opt_mcq = quiz_response['selected_opt'].split(",")
            else:
                res_select_opt_mcq = []
            ques_type = quiz_response['ques_type'].split(",")
            # #print("ques_type",ques_type)
            answers = list()
            mcq_ct = 0
            one_line_ct = 0
            # #print("res_select_opt_mcq",res_select_opt_mcq)
            for i in range(len(questions)):
                # #print("i",i)
                # #print("len(ques_type)",len(ques_type))
                if len(ques_type)>i:
                    if ques_type[i] == '0':
                        answers.append(res_select_opt_mcq[mcq_ct])
                        mcq_ct += 1
                        # #print("mcq_ct",mcq_ct)
                    elif ques_type[i] == '1':
                        answers.append(res_one_line[one_line_ct])
                        one_line_ct += 1
                        # #print("one_line_ct",one_line_ct)
                else:
                    # #print(type(questions[i]['ans_type']))
                    if questions[i]['ans_type'] == 0:
                        answers.append("")
                        mcq_ct += 1
                        # #print("mcq_ct",mcq_ct)
                    elif questions[i]['ans_type'] == 1:
                        answers.append("")
                        one_line_ct += 1
                        # #print("one_line_ct",one_line_ct)
            # #print("answers",answers)


            op = list()
            # #print("ques_index",ques_index)
            # #print("ques_points",ques_points)
            for i in range(len(questions)):
                # #print("I:",i," type is :",type(i))
                # #print("str(questions[i][q_id]",str(questions[i]['q_id']))
                op1 = {}
                op1['ques'] = questions[i]['question']
                op1['point'] = questions[i]['points']
                op1['ans_type'] = questions[i]['ans_type']
                op1['opt1'] = questions[i]['opt1']
                op1['opt2'] = questions[i]['opt2']
                op1['opt3'] = questions[i]['opt3']
                op1['opt4'] = questions[i]['opt4']
                if str(questions[i]['q_id']) in ques_index:
                    index = ques_index.index(str(questions[i]['q_id']))
                    # #print("index:",index)
                    op1['answered'] = answers[index]
                    op1['got_point'] = ques_points[index]
                else:
                    op1['answered'] = answers[i]
                    op1['got_point'] = '0'
                op1['correct_opt'] = questions[i]['correct_opt']
                
                # #print(op)
                op.append(op1)
            return render_template('check_ques_score.html',msg = "",ques=op,len = len(op), score=total_score,attempted=1)
        else:
            option_select = list()
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT ans_type,opt1,opt2,opt3,opt4,q_id,question AS ques,correct_opt,points FROM questions WHERE quiz_id = %s",[session['quiz_id']])
            records = cur.fetchall()
            questions = list()
            points = []
            for row in records:
                questions.append(row)
                points.append(row['points'])
            total_score = {}
            total_score['score'] = 0
            total_score['total_points'] = sum(points)
            # #print(questions)
            return render_template('check_ques_score.html',msg = "",ques=questions,len = len(questions),score=total_score,attempted=0)
        


@student.route('/quiz_finish/',methods=['POST', 'GET'])
@login_required
def finish_quiz():
    # #print(session)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT selected_opt,ques_id,ques_type,quiz_start,time_per_ques,q_time_start FROM quiz_responses,quiz_det WHERE quiz_responses.quiz_id = %s AND quiz_responses.quiz_id = quiz_det.quiz_id AND user_inserted=%s",(session['quiz_id'],session['svv']))
    record_user = cur.fetchone()
    cur.close()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT ans_type FROM questions WHERE quiz_id = %s",[session['quiz_id']])
    question_ans_type = cur.fetchall()
    cur.close()
    if record_user is not None:
        ans_type = record_user['ques_type'].split(",")
        time_per_ques = record_user['time_per_ques'].split(',')
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
    # #print("quiz_end_time:",quiz_end_time)
    # #print("user_quiz_start:",user_quiz_start)
    ttl_time_taken = str(datetime.datetime.strptime(quiz_end_time, '%H:%M:%S') - datetime.datetime.strptime(user_quiz_start, '%H:%M:%S'))
    ttl_time_taken = datetime.datetime.strptime(ttl_time_taken, '%H:%M:%S')
    # #print(ttl_time_taken.time())
    ttl_time_taken = ttl_time_taken.time()
    pending = 0
    for row in question_ans_type:
        if row['ans_type']==1:
            pending = 1
    # #print('pending',pending)
    diff_time = list()
    for i in range(len(time_per_ques)):
        if i==0:
            start_time = datetime.datetime.strptime(record_user['quiz_start'],"%H:%M:%S")
            end_time = datetime.datetime.strptime(time_per_ques[i],"%H:%M:%S")
        else:
            start_time = datetime.datetime.strptime(time_per_ques[i-1],"%H:%M:%S")
            end_time = datetime.datetime.strptime(time_per_ques[i],"%H:%M:%S")
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
        print('')
    print("MCQ:",mcq)
    #print("Answer Type List:",ans_type)
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
        #print(question_ids)
        # #print(option_selected)
        #print(record_og)
        count = 0
        ind = 0
        for row in record_og:
            #print("Database Question Id:")
            print(row['q_id'])
            if str(row['q_id']) in question_ids:
                i = question_ids.index(str(row['q_id']))
            if str(row['q_id']) in mcq:
                i = mcq.index(str(row['q_id']))
                print("Index:",str(i))
                print("row['correct_opt']:",row['correct_opt'])
                if row['correct_opt'] == option_selected[i]:
                    count = count+int(row['points'])
                    mcq_ques_list.append(row['q_id'])
                    #print(row['points'])
                    mcq_score_list.append(row['points'])
                else:
                    i = -1
                    mcq_score_list.append(0)
                    mcq_ques_list.append(row['q_id'])
            else:
                mcq_score_list.append(0)
                mcq_ques_list.append(row['q_id'])
            # #print(ind)
            #print("Count:")
            # #print(count)
            print("mcq_score_list",mcq_score_list)
            print("mcq_ques_list",mcq_ques_list)
            ind += 1
        mcq_lst = 0
        #print("MCQ score List:",mcq_score_list)
        for i in range(len(question_ids)):
            #print('i',i)
            #print('mcq_lst',mcq_lst)
            if ans_type[i]=='1':
                score_list += '0,'
            elif ans_type[i]=='0':
                #print('question_ids[i]',question_ids[i])
                ind = mcq_ques_list.index(int(question_ids[i]))
                #print('ind',ind)
                score_list += str(mcq_score_list[ind])+','
                # mcq_lst += 1
                # #print('mcq_lst',mcq_lst)
        if score_list[-1] == ',':
            score_list = score_list[:-1]
        #print("Score List:",score_list)

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

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("UPDATE quiz_responses SET time_per_ques = %s WHERE quiz_id = %s AND user_inserted=%s" ,(diff_time_str,session['quiz_id'],session['svv']))
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
        cur.execute("UPDATE quiz_responses SET time_per_ques = %s WHERE quiz_id = %s AND user_inserted=%s" ,(diff_time_str,session['quiz_id'],session['svv']))
        mysql.connection.commit()

        if pending==0:
            session['quiz_score'] = count
    return redirect(url_for('student.score_quiz'))

@student.route('/quiz_score/',methods=['POST', 'GET'])
@login_required
def score_quiz():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT quiz_attempted,user_score,total_points,show_answer,pending_chk FROM score,quiz_det WHERE score.quiz_id = %s AND score.user = %s AND quiz_det.quiz_id = %s",(session['quiz_id'],session['svv'],session['quiz_id']))
    rec = cur.fetchone()
    cur.close()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT SUM(points) AS total_points FROM questions WHERE quiz_id =%s', [session['quiz_id']])
    total_pts = cursor.fetchone()
    total_points = int(total_pts['total_points'])
    # #print(rec)
    # #print(session)  
    # session['quiz_show'] = 1
    if rec:
        if rec['quiz_attempted']=='1':
            if rec['show_answer']==1 and rec['pending_chk']==0:
                return render_template('quiz_submit.html',msg="",score=rec['user_score'],total=total_points)
            else:
                 return render_template('quiz_submit.html',msg="",score="",total="")       
        else:
            return render_template('quiz_submit.html',msg="You havent't Filled the quiz yet!",score="",total="")    
    else:
        return render_template('quiz_submit.html',msg="You havent't Filled the quiz yet!",score="",total="")

@student.route('/close_quiz/',methods=['POST', 'GET'])
@login_required
def quiz_close():
    if session.get('q_nos') is not None:
        session.pop('q_nos',None)
    if session.get('quiz_id') is not None:
        session.pop('quiz_id',None)
    if session.get('quiz_score') is not None:
        session.pop('quiz_score',None)
    if session.get('quiz_show') is not None:
        session.pop('quiz_show',None)
    if session.get('total_ques') is not None:
        session.pop('total_ques',None)
    return redirect(url_for('dashboard'))