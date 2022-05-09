from flask import Blueprint, request, render_template, abort, session, redirect, url_for
from app import mysql,app_root
from werkzeug.utils import secure_filename
import MySQLdb.cursors
from datetime import date
import datetime
import json,pytz,requests, base64, math,os
from check_login import login_required, check_message, hash_password, check_password
from app import page_not_found
from pathlib import Path
import xlrd, xlwt, openpyxl
# from openpyxl_image_loader import SheetImageLoader
import xlsxwriter

admin = Blueprint('admin', __name__,template_folder='templates')
IST = pytz.timezone('Asia/Kolkata')

# COMMON FOR STUDENT AND FACULTY START #

@admin.route('/master_data',methods=['POST','GET'])
@login_required
def get_master_mode():
    mode = request.args.get('mode')
    if mode=="Student":
        qs = []
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(S_id) as Total_Stud FROM student where current_sem=1 OR current_sem=2')
        fy_students = cursor.fetchone()
        fy = {}
        fy['batch'] = 'First-Year'
        fy['Total_Stud'] = fy_students['Total_Stud']
        qs.append(fy)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(S_id) as Total_Stud FROM student where current_sem=3 OR current_sem=4')
        sy_students = cursor.fetchone()
        sy = {}
        sy['batch'] = 'Second-Year'
        sy['Total_Stud'] = sy_students['Total_Stud']
        qs.append(sy)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(S_id) as Total_Stud FROM student where current_sem=5 OR current_sem=6')
        ty_students = cursor.fetchone()
        ty = {}
        ty['batch'] = 'Third-Year'
        ty['Total_Stud'] = ty_students['Total_Stud']
        qs.append(ty)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(S_id) as Total_Stud FROM student where current_sem=7 OR current_sem=8')
        ly_students = cursor.fetchone()
        ly = {}
        ly['batch'] = 'Last-Year'
        ly['Total_Stud'] = ly_students['Total_Stud']
        qs.append(ly)
        print(qs)
        if session.get('data_master_mode') is None:
            session['data_master_mode'] = "student"
        else:
            if session['data_master_mode'] != "student":
                session['data_master_mode'] = "student"
        colors = ['bg-gradient-primary2','bg-gradient-success','bg-gradient-info','bg-gradient-warning','bg-gradient-danger','bg-gradient-dark']
        return render_template('student/student_types.html', stud = qs, color=colors)
    elif mode=="Faculty":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if session.get('data_master_mode') is None:
            session['data_master_mode'] = "faculty"
        else:
            if session['data_master_mode'] != "faculty":
                session['data_master_mode'] = "faculty"
        print(session['dept'])
        cursor.execute('SELECT dept_name FROM department where dept_short = %s',[session['dept']])
        department = cursor.fetchone()
        dept = department['dept_name']
        cursor.execute('SELECT F_id, Designation, L_name, F_name, M_name, F_email, F_num, gender FROM faculty where dept = %s',[dept])
        faculty = cursor.fetchall()
        cursor.close()
        msg = check_message()
        return render_template('faculty_master_data.html',mode=mode, faculties=faculty, faclen=len(faculty),msg=msg)
    elif mode=="Subject":
        qs = []
        print(session['dept'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for sem_num in range(1,9):
            db_sem = "sem"+str(sem_num)
            cursor.execute('SELECT COUNT(subject.course_code) as Total_comp_Sub FROM subject INNER JOIN department ON department.dept_id=subject.dept_id AND department.dept_short=%s AND subject.sem=%s',(session['dept'],db_sem))
            sem_com_subjects = cursor.fetchone()
            print(sem_com_subjects)
            cursor.execute('SELECT COUNT(electives.course_code) as Total_elect_Sub FROM electives INNER JOIN department ON department.dept_id=electives.dept_id AND department.dept_short=%s AND electives.sem=%s',(session['dept'],db_sem))
            sem_elect_subjects = cursor.fetchone()
            print(sem_elect_subjects)
            sem = {}
            sem['batch'] = 'Semester-'+str(sem_num)
            sem['Total_Sub'] = sem_com_subjects['Total_comp_Sub'] + sem_elect_subjects['Total_elect_Sub']
            qs.append(sem)
        print(qs)
        if session.get('data_master_mode') is None:
            session['data_master_mode'] = "subject"
        else:
            if session['data_master_mode'] != "subject":
                session['data_master_mode'] = "subject"
        colors = ['bg-gradient-primary2','bg-gradient-success','bg-gradient-info','bg-gradient-warning','bg-gradient-danger','bg-gradient-dark']
        return render_template('subject/subject_types.html', sub = qs, color=colors)
    elif mode=="Electives":
        qs = []
        print(session['dept'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for sem_num in range(1,9):
            db_sem = "sem"+str(sem_num)
            cursor.execute('SELECT COUNT(electives.course_code) as Total_Sub FROM electives \
                INNER JOIN department ON department.dept_id=electives.dept_id \
                    AND department.dept_short=%s AND electives.sem=%s',(session['dept'],db_sem))
            sem_subjects = cursor.fetchone()
            sem = {}
            sem['batch'] = 'Semester-'+str(sem_num)
            sem['Total_Sub'] = sem_subjects['Total_Sub']
            qs.append(sem)
        print(qs)
        if session.get('data_master_mode') is None:
            session['data_master_mode'] = "electives"
        else:
            if session['data_master_mode'] != "electives":
                session['data_master_mode'] = "electives"
        colors = ['bg-gradient-primary2','bg-gradient-success','bg-gradient-info','bg-gradient-warning','bg-gradient-danger','bg-gradient-dark']
        return render_template('electives/electives_types.html', elective_sub = qs, color=colors)


@admin.route('/check_record_present/',methods=['POST','GET'])
@login_required
def check_record_entry():
    # #print(session)
    data_edit_mode = request.form['data_edit_mode']
    print("check_record_present")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    res = {}
    if data_edit_mode == "student":
        email = request.form['mail']
        print("Email:",email)
        s_id = request.form['stud_id']
        print("S_ID:",s_id)
        cursor.execute("SELECT F_name, M_name, L_name FROM student WHERE S_id=%s OR S_email=%s",(s_id,email))
        student = cursor.fetchone()
        cursor.close()
        if student:
            name = student['F_name']+" "+student['M_name']+" "+student['L_name']
            res['present'] = 1
            res['stud_name'] = name
            print(res)
            return json.dumps(res)
        else:
            res['present'] = 0
            return json.dumps(res)
    elif data_edit_mode == "faculty":
        email = request.form['mail']
        print("Email:",email)
        f_id = request.form['fac_id']
        cursor.execute("SELECT F_name, M_name, L_name FROM faculty WHERE F_id=%s OR F_email=%s",(f_id,email))
        student = cursor.fetchone()
        cursor.close()
        if student:
            name = student['F_name']+" "+student['M_name']+" "+student['L_name']
            res['present'] = 1
            res['stud_name'] = name
            print(res)
            return json.dumps(res)
        else:
            res['present'] = 0
            return json.dumps(res)
    elif data_edit_mode == "subject":
        sub_code = request.form['sub_code']
        print("sub_code:",sub_code)
        cursor.execute("SELECT sub_name_long FROM subject WHERE course_code=%s",[sub_code])
        subject = cursor.fetchone()
        cursor.close()
        if subject:
            res['present'] = 1
            res['sub_name'] = subject['sub_name_long']
            print(res)
            return json.dumps(res)
        else:
            res['present'] = 0
            return json.dumps(res)
    elif data_edit_mode == "electives_subject":
        sub_code = request.form['sub_code']
        print("sub_code:",sub_code)
        cursor.execute("SELECT sub_name_long FROM electives WHERE course_code=%s",[sub_code])
        subject = cursor.fetchone()
        cursor.close()
        if subject:
            res['present'] = 1
            res['sub_name'] = subject['sub_name_long']
            print(res)
            return json.dumps(res)
        else:
            res['present'] = 0
            return json.dumps(res)
    elif data_edit_mode == "electives_category":
        category = request.form['category']
        sem = request.form['sem']
        print("sub_code:",category)
        cursor.execute('SELECT dept_id FROM department where dept_short = %s',[session['dept']])
        department = cursor.fetchone()
        dept_id = department['dept_id']
        cursor.execute("SELECT cat_name FROM electives_category WHERE cat_name=%s AND sem=%s AND dept_id=%s ",(category,sem,dept_id))
        elective_category = cursor.fetchone()
        cursor.close()
        if elective_category:
            res['present'] = 1
            print(res)
            return json.dumps(res)
        else:
            res['present'] = 0
            print(res)
            return json.dumps(res)


@admin.route('/check_excel_sheet/',methods=['POST'])
@login_required
def check_excel_sheet_subject():
    category_directory = os.path.join(app_root,"static/db_format",session['data_master_mode'])
    category_file = category_directory+'/'+session['data_master_mode'].title()+'_master.xlsx'
    res = {}
    if not os.path.exists(category_file):
        Path(category_directory).mkdir(parents=True, exist_ok=True)
        workbook =xlsxwriter.Workbook(category_file)
        worksheet = workbook.add_worksheet(session['data_master_mode'])
        if session['data_master_mode'] == 'student':
            field_names = ['Student ID','Student Last Name','Student First Name','Student Middle Name','Roll Number','Batch Number','Student Email','KT','Type: Diploma (1: yes;0:no)','Student Mobile Number','Parents Email Id','Parents Mobile Number','Current Semester','Gender (M:Male, F:Female, O:others)']
        elif session['data_master_mode'] == 'faculty':
            field_names = ['Faculty ID','Designation','Faculty Last Name','Faculty First Name','Faculty Middle Name','Faculty Email','Faculty Mobile Number','Gender (M:Male, F:Female, O:others)']
        elif session['data_master_mode'] == 'subject':
            field_names = ['Subject Code','Subject Name','Short Subject Name','Subject Type: 1-Theory, 0- Practical','Marks (0- no marks, 1- marks)']
        elif session['data_master_mode'] == 'electives_subject':
            field_names = ['Subject Code','Subject Name','Short Subject Name','Subject Type: 1-Theory, 0- Practical','Elective Category','Marks (0- no marks, 1- marks)']
        elif session['data_master_mode'] == 'electives_category':
            field_names = ['Category Name']
        for i in range(len(field_names)):
            worksheet.write(0,i,field_names[i])
        workbook.close()
        res['created'] = 1
    else:
        res['created'] = 1
    return json.dumps(res)

@admin.route('/upload_excel/',methods=['POST'])
@login_required
def upload_excel_add_records():
    dept= ""
    data_master_mode = ""
    print(request.form)    
    if session.get('dept') is not None:
        dept = session['dept']
    if session.get('data_master_mode') is not None:
        data_master_mode = session['data_master_mode']
    print(request.files)
    ajax_response = {}
    if len(request.files) != 0:
        up_rec_excel = request.files["excel_file"]
        up_rec_excel_filename =  up_rec_excel.filename.strip()
        up_rec_excel_filename = up_rec_excel_filename.replace(" ", "")
        print(up_rec_excel_filename)
        if up_rec_excel_filename!='':
            if data_master_mode == "student" or data_master_mode == "subject" or data_master_mode == "electives_category" or data_master_mode == "electives_subject":
                mode = request.form['mode_ex_up']
                # print("mode",mode)
                excel_directory = os.path.join(app_root,"static/spreadsheets",dept,data_master_mode,mode)
            elif data_master_mode == "faculty":
                excel_directory = os.path.join(app_root,"static/spreadsheets",dept,data_master_mode)
            # s_photo_file = os.path.join(directory,s_photo)
            print(excel_directory)
            Path(excel_directory).mkdir(parents=True, exist_ok=True)
            for f in os.listdir(excel_directory):
                os.remove(os.path.join(excel_directory, f))
            up_rec_excel.save(os.path.join(excel_directory,secure_filename(up_rec_excel_filename)))
            excel_sheet = xlrd.open_workbook(os.path.join(excel_directory,up_rec_excel_filename))
            excel_sheet_names = excel_sheet.sheet_names()
            load_sheet_name = ""
            for i in range(len(excel_sheet_names)):
                if excel_sheet_names[i].lower() == data_master_mode.lower():
                    load_sheet_name = excel_sheet_names[i]
            sheet = excel_sheet.sheet_by_name(load_sheet_name)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sheet_create = 0
            row_insrt = 0
            category_correct = 0
            if data_master_mode == "student":
                query = """INSERT IGNORE INTO student (S_id,S_pass,image,L_name,F_name,M_name,roll,batch,S_email,KT,S_num,Type,P_email,P_num,current_sem,gender,dept) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                for r in range(1, sheet.nrows):
                    stud_id = int(sheet.cell(r,0).value)
                    lname = sheet.cell(r,1).value
                    fname = sheet.cell(r,2).value
                    mname = sheet.cell(r,3).value
                    year = mode
                    print(year)
                    roll = int(sheet.cell(r,4).value)
                    batch = int(sheet.cell(r,5).value)
                    email = sheet.cell(r,6).value
                    kts = int(sheet.cell(r,7).value)
                    dipl_type = int(sheet.cell(r,8).value)
                    mob_num = int(sheet.cell(r,9).value)
                    p_email	= sheet.cell(r,10).value
                    if sheet.cell(r,11).value != '':
                        p_mob_num = int(sheet.cell(r,11).value) 
                    else:
                        p_mob_num = sheet.cell(r,11).value
                    sem	= int(sheet.cell(r,12).value)
                    gender	= sheet.cell(r,13).value
                    stud_dept = session['dept']
                    s_pass = hash_password(str(p_mob_num))
                    pxl_doc = openpyxl.load_workbook(os.path.join(excel_directory,up_rec_excel_filename))
                    img_sheet = pxl_doc[load_sheet_name]
                    # image_loader = SheetImageLoader(img_sheet)
                    # if image_loader.image_in('B'+str((r+1))):
                    #     s_photo =  image_loader.get('B'+str((r+1)))
                    #     s_photo_name = str(stud_id)+'.png'
                    #     image_present = 1
                    # else:
                    image_present = 0
                    s_photo_name = ''
                    values = (stud_id, s_pass, s_photo_name, lname, fname, mname, roll, batch, email, kts, mob_num, dipl_type, p_email, p_mob_num, sem, gender, stud_dept)
                    print(values)
                    # Execute sql Query
                    cursor.execute(query, values)                    
                    if cursor.rowcount == 1:
                        img_directory = os.path.join(app_root,"static/profile_pics/student_images",dept,mode,str('semester_'+str(sem)),str(stud_id))
                        print(img_directory)
                        Path(img_directory).mkdir(parents=True, exist_ok=True)
                        for f in os.listdir(img_directory):
                            os.remove(os.path.join(img_directory, f))
                        # if image_present == 1:
                        #     s_photo.save(os.path.join(img_directory,s_photo_name))
                    elif cursor.rowcount == 0:
                        if sheet_create == 0:
                            workbook_err = xlwt.Workbook(encoding='utf-8')
                            worksheet_err = workbook_err.add_sheet(data_master_mode,cell_overwrite_ok=True)
                            worksheet_err.Title = "Failed Records to Insert";     
                            cols = ['Student ID', 'Student Last Name', 'Student First Name', 'Student Middle Name', 'Roll Number', 'Year', 'Student Email', 'Reason']
                            sheet_create = 1
                            for items in range(0,len(cols)):
                                worksheet_err.write(0,items,cols[items])                                   
                            rows = [stud_id,lname,fname,mname,roll,year,email,'Record Already Present']
                        for items in range(0,len(rows)):
                            worksheet_err.write((row_insrt+1),items,rows[items])
                        row_insrt += 1
            elif data_master_mode == "faculty":
                query = """INSERT IGNORE INTO faculty (F_id,Designation,L_name,F_name,M_name,F_email,F_password,dept,F_num,gender,img) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                for r in range(1, sheet.nrows):
                    fac_id = int(sheet.cell(r,0).value)
                    desg = str(sheet.cell(r,1).value)
                    lname = sheet.cell(r,2).value
                    fname = sheet.cell(r,3).value
                    mname = sheet.cell(r,4).value
                    email = sheet.cell(r,5).value
                    mob_num	 = int(sheet.cell(r,6).value)
                    gender	= sheet.cell(r,7).value
                    fac_dept = session['dept']
                    f_pass = hash_password(str(mob_num))
                    pxl_doc = openpyxl.load_workbook(os.path.join(excel_directory,up_rec_excel_filename))
                    # img_sheet = pxl_doc[data_master_mode.capitalize()]
                    # image_loader = SheetImageLoader(img_sheet)
                    # if image_loader.image_in('B'+str((r+1))):
                    #     f_photo =  image_loader.get('B'+str((r+1)))
                    #     f_photo_name = str(fac_id)+'.png'
                    #     image_present = 1
                    # else:
                    image_present = 0
                    f_photo_name = ''
                    cursor.execute('SELECT dept_name FROM department where dept_short = %s',[fac_dept])
                    department = cursor.fetchone()
                    fac_dept = department['dept_name']
                    values = (fac_id, desg, lname, fname, mname, email, f_pass, fac_dept, mob_num, gender, f_photo_name)
                    # print(values)
                    # Execute sql Query
                    cursor.execute(query, values)
                    if cursor.rowcount == 1:
                        img_directory = os.path.join(app_root,"static/profile_pics/faculty_images",dept,str(fac_id))
                        print(img_directory)
                        Path(img_directory).mkdir(parents=True, exist_ok=True)
                        for f in os.listdir(img_directory):
                            os.remove(os.path.join(img_directory, f))
                        # if image_present == 1:
                        #     f_photo.save(os.path.join(img_directory,f_photo_name))
                    elif cursor.rowcount == 0 :
                        if sheet_create == 0:
                            workbook_err = xlwt.Workbook(encoding='utf-8')
                            worksheet_err = workbook_err.add_sheet(data_master_mode,cell_overwrite_ok=True)
                            worksheet_err.Title = "Failed Records to Insert";     
                            cols = ['College ID', 'Last Name', 'First Name', 'Middle Name', 'Email Address', 'Reason']
                            sheet_create = 1
                            for items in range(0,len(cols)):
                                worksheet_err.write(0,items,cols[items])           
                            rows = [fac_id,lname,fname,mname,email,'Record already present!']
                        for items in range(0,len(rows)):
                            worksheet_err.write((row_insrt+1),items,rows[items])
                        row_insrt += 1
            elif data_master_mode == "subject":
                query = """INSERT IGNORE INTO subject (course_code,sub_name_long,sub_name_short,sem,sub_type,marks,dept_id) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
                print("sheet.nrows",sheet.nrows)
                for r in range(1, sheet.nrows):
                    course_code = str(sheet.cell(r,0).value)
                    long_sub_name = str(sheet.cell(r,1).value).upper()
                    short_sub_name = str(sheet.cell(r,2).value).upper()
                    sem = mode
                    dept = session['dept']
                    sub_type_string = str(sheet.cell(r,3).value)
                    if isinstance(sub_type_string, float):
                        sub_type_string = str(int(sub_type_string))
                        sub_type=''.join(i for i in sub_type_string if i.isdigit())
                    else:
                        sub_type=sub_type_string    
                    print("sub_type_string:",sub_type_string," ",type(sub_type_string))
                    m_string = str(sheet.cell(r,4).value)
                    if isinstance(m_string, float):
                        m_string = str(int(m_string))
                        print("m_string:",m_string," ",type(m_string))
                        marks=''.join(i for i in m_string if i.isdigit())
                    else:
                        marks = m_string
                    print("marks:",marks)
                    cursor.execute('SELECT dept_id FROM department where dept_short = %s',[dept])
                    department = cursor.fetchone()
                    dept_id = department['dept_id']
                    values = (course_code, long_sub_name, short_sub_name, sem, sub_type, marks, dept_id)
                    # print(values)
                    # Execute sql Query
                    cursor.execute(query, values)
                    if cursor.rowcount == 0:
                        if sheet_create == 0:
                            workbook_err = xlwt.Workbook(encoding='utf-8')
                            worksheet_err = workbook_err.add_sheet(data_master_mode,cell_overwrite_ok=True)
                            worksheet_err.Title = "Failed Records to Insert";     
                            cols = ['Subject Code', 'Subject Full Name', 'Subject Short Name','Semester','Department', 'Reason']
                            sheet_create = 1
                            for items in range(0,len(cols)):
                                worksheet_err.write(0,items,cols[items])
                        reason = "Record already present"
                        rows = [course_code,long_sub_name,short_sub_name,sem,dept,reason]
                        for items in range(0,len(rows)):
                            worksheet_err.write((row_insrt+1),items,rows[items])
                        row_insrt += 1
            elif data_master_mode == "electives_category":
                cursor.execute('SELECT dept_id FROM department where dept_short = %s',[session['dept']])
                department = cursor.fetchone()
                dept_id = department['dept_id']
                query = """INSERT IGNORE INTO electives_category (cat_name,sem,dept_id) VALUES (%s,%s,%s)"""
                for r in range(1, sheet.nrows):
                    cat_name = (str(sheet.cell(r,0).value).lower()).capitalize()
                    values = (cat_name,mode,dept_id)
                    cursor.execute(query, values)
                    if cursor.rowcount == 0:
                        if sheet_create == 0:
                            workbook_err = xlwt.Workbook(encoding='utf-8')
                            worksheet_err = workbook_err.add_sheet(data_master_mode,cell_overwrite_ok=True)
                            worksheet_err.Title = "Failed Records to Insert"
                            cols = ['Category Name', 'Reason']
                            sheet_create = 1
                            for items in range(0,len(cols)):
                                worksheet_err.write(0,items,cols[items])
                        rows = [cat_name,"Record already present"]
                        for items in range(0,len(rows)):
                            worksheet_err.write((row_insrt+1),items,rows[items])
                        row_insrt += 1
            elif data_master_mode == "electives_subject":
                query = """INSERT IGNORE INTO electives (course_code,sub_name_long,sub_name_short,sem,sub_type,elective_category,marks,dept_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute('SELECT dept_id FROM department where dept_short = %s',[dept])
                department = cursor.fetchone()
                dept_id = department['dept_id']
                cursor.execute('SELECT category_id,cat_name FROM electives_category where dept_id = %s AND sem = %s',(dept_id,mode))
                electives_category = cursor.fetchall()
                print(electives_category)
                elect_cat_id = []
                elect_cat_name = []
                for i in range(len(electives_category)):
                    e_cat = electives_category[i] 
                    elect_cat_id.append(int(e_cat['category_id']))
                    elect_cat_name.append(e_cat['cat_name'].strip())
                print(elect_cat_id)
                print(elect_cat_name)
                for r in range(1, sheet.nrows):
                    course_code = str(sheet.cell(r,0).value)
                    long_sub_name = str(sheet.cell(r,1).value).upper()
                    short_sub_name = str(sheet.cell(r,2).value).upper()
                    sem = mode
                    dept = session['dept']
                    sub_type_string = str(sheet.cell(r,3).value)
                    if isinstance(sub_type_string, float):
                        sub_type_string = str(int(sub_type_string))
                        sub_type=''.join(i for i in sub_type_string if i.isdigit())
                    else:
                        sub_type=sub_type_string    
                    print("sub_type_string:",sub_type_string," ",type(sub_type_string))
                    elective = ((str(sheet.cell(r,4).value)).strip()).title()
                    m_string = sheet.cell(r,5).value
                    if isinstance(m_string, float):
                        m_string = str(int(m_string))
                    marks=''.join(i for i in m_string if i.isdigit())
                    print("marks:",marks)
                    cat_id = elective
                    category_correct = 0
                    if len(elect_cat_name)!= 0:
                        if elective in elect_cat_name:
                            category_correct = 1
                            cat_id = elect_cat_id[elect_cat_name.index(elective)]
                    print("cat_id",cat_id)
                    values = (course_code, long_sub_name, short_sub_name, sem, sub_type, cat_id,int(marks), dept_id)
                    print(query,values)
                    cursor.execute(query, values)
                    print("rowcount:",cursor.rowcount)
                    if cursor.rowcount == 0:
                        if sheet_create == 0:
                            workbook_err = xlwt.Workbook(encoding='utf-8')
                            worksheet_err = workbook_err.add_sheet(data_master_mode,cell_overwrite_ok=True)
                            worksheet_err.Title = "Failed Records to Insert";     
                            cols = ['Subject Code', 'Subject Full Name', 'Subject Short Name','Semester','Department', 'Reason']
                            sheet_create = 1
                            for items in range(0,len(cols)):
                                worksheet_err.write(0,items,cols[items])
                        reason = ""
                        if category_correct == 0:
                            reason = "Elective Category Not Found, Please Check the Master!"
                        else:
                            reason = "Record already present"
                        rows = [course_code,long_sub_name,short_sub_name,sem,dept,reason]
                        for items in range(0,len(rows)):
                            worksheet_err.write((row_insrt+1),items,rows[items])
                        row_insrt += 1
            cursor.close()
            mysql.connection.commit()
            if sheet_create == 1:
                file_name = data_master_mode+"_master_records_addition_failed.xlsx"
                for f in os.listdir(excel_directory):
                    os.remove(os.path.join(excel_directory, f))
                workbook_err.save(os.path.join(excel_directory,file_name))
            ajax_response['file_error'] = 0
            ajax_response['total_rec'] = (sheet.nrows - 1)
            ajax_response['failed_rec'] = row_insrt
        else:
            ajax_response['file_error'] = 1
        ajax_response['file_recieved'] = 1
    else:
        ajax_response['file_recieved'] = 0
    print(ajax_response)
    return json.dumps(ajax_response)
    

@admin.route('/export_excel/',methods=['POST'])
@login_required
def upload_excel_export_records():
    data_master_mode = request.form['data_master_mode']
    ajax_response = {}
    if session.get('dept') is not None:
        dept = session['dept']
    if data_master_mode != "":
        download_directory = os.path.join(app_root,"static/spreadsheets/Download")
        print(download_directory)
        Path(download_directory).mkdir(parents=True, exist_ok=True)
        for f in os.listdir(download_directory):
            os.remove(os.path.join(download_directory, f))
        if data_master_mode == "student":
            mode = request.form['mode']
            if mode != "" :
                workbook =xlsxwriter.Workbook(os.path.join(download_directory,dept+'_'+data_master_mode+'_'+mode+'_master.xlsx'))
                worksheet = workbook.add_worksheet(data_master_mode)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                if mode=="First-Year":
                    cursor.execute('SELECT S_id,image,L_name,F_name, M_name,roll,batch,S_email,KT,Type,S_num,P_email,P_num,current_sem,gender FROM student where current_sem=1 OR current_sem=2 ORDER BY current_sem ASC, roll ASC')
                elif mode=="Second-Year":
                    cursor.execute('SELECT S_id,image,L_name,F_name, M_name,roll,batch,S_email,KT,Type,S_num,P_email,P_num,current_sem,gender FROM student where current_sem=3 OR current_sem=4 ORDER BY current_sem ASC, roll ASC')
                elif mode=="Third-Year":
                    cursor.execute('SELECT S_id,image,L_name,F_name, M_name,roll,batch,S_email,KT,Type,S_num,P_email,P_num,current_sem,gender FROM student where current_sem=5 OR current_sem=6 ORDER BY current_sem ASC, roll ASC')
                elif mode=="Last-Year":
                    cursor.execute('SELECT S_id,image,L_name,F_name, M_name,roll,batch,S_email,KT,Type,S_num,P_email,P_num,current_sem,gender FROM student where current_sem=7 OR current_sem=8 ORDER BY current_sem ASC, roll ASC')
                
                field_names = ['Student ID','Student Last Name','Student First Name','Student Middle Name','Year','Roll Number','Batch Number','Student Email','KT','Type: Diploma (1: yes;0:no)','Student Mobile Number','Parents Email Id','Parents Mobile Number','Current Semester','Gender (M:Male, F:Female, O:others)']
                records = cursor.fetchall()
                # print(records)
                cursor.close()
                print(field_names)
                for items in range(0,len(field_names)):
                    worksheet.write(0,items,field_names[items])
                row_insert = 1
                # img_directory = os.path.join(app_root,"static/profile_pics/student_images",dept,mode)
                # img_directory = os.path.join(app_root,"static/profile_pics/student_images",dept,mode,str('semester_'+str(sem)),str(stud_id))
                for row in records:
                    print(row)
                    worksheet.write(row_insert,0,row['S_id'])
                    worksheet.write(row_insert,1,row['L_name'])
                    worksheet.write(row_insert,2,row['F_name'])
                    worksheet.write(row_insert,3,row['M_name'])
                    worksheet.write(row_insert,4,mode)
                    worksheet.write(row_insert,5,row['roll'])
                    worksheet.write(row_insert,6,row['batch'])
                    worksheet.write(row_insert,7,row['S_email'])
                    worksheet.write(row_insert,8,row['KT'])
                    worksheet.write(row_insert,9,row['Type'])
                    worksheet.write(row_insert,10,row['S_num'])
                    worksheet.write(row_insert,11,row['P_email'])
                    worksheet.write(row_insert,12,row['P_num'])
                    worksheet.write(row_insert,13,row['current_sem'])
                    worksheet.write(row_insert,14,row['gender'])
                    row_insert += 1
                workbook.close()
                ajax_response['file_created'] = 1
                ajax_response['data_got'] = 1
            else:
                ajax_response['data_got'] = 0
        elif data_master_mode == "faculty": 
            workbook =xlsxwriter.Workbook(os.path.join(download_directory,dept+'_'+data_master_mode+'_master.xlsx'))
            worksheet = workbook.add_worksheet(data_master_mode)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT dept_name FROM department where dept_short = %s',[dept])
            department = cursor.fetchone()
            dept_full = department['dept_name']
            cursor.execute('SELECT F_id,Designation,img,L_name,F_name, M_name,F_email,F_num,gender FROM faculty where dept = %s ORDER BY F_name ASC', [dept_full])
            records = cursor.fetchall()
            cursor.close()
            field_names = ['College ID','Designation','First Name','Middle Name','Last Name','Email address','Mobile Number','Gender (M:Male, F:Female, O:others)']
            # print(records)
            print(field_names)
            for items in range(0,len(field_names)):
                worksheet.write(0,items,field_names[items])
            row_insert = 1
            for row in records:
                    # print(row)
                worksheet.write(row_insert,0,row['F_id'])
                worksheet.write(row_insert,1,row['Designation'])
                worksheet.write(row_insert,2,row['F_name'])
                worksheet.write(row_insert,3,row['M_name'])
                worksheet.write(row_insert,4,row['L_name'])
                worksheet.write(row_insert,5,row['F_email'])
                worksheet.write(row_insert,6,row['F_num'])
                worksheet.write(row_insert,7,row['gender'])
                row_insert += 1
            workbook.close()
            ajax_response['file_created'] = 1
            ajax_response['data_got'] = 1
        elif data_master_mode == "subject": 
            mode = request.form['mode']
            if mode != "" :
                workbook =xlsxwriter.Workbook(os.path.join(download_directory,dept+'_'+data_master_mode+'_'+mode+'_master.xlsx'))
                worksheet = workbook.add_worksheet(data_master_mode)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT subject.course_code,subject.sub_name_long,subject.sub_name_short,subject.sub_type,subject.marks,subject.sem, department.dept_short FROM subject INNER JOIN department ON subject.dept_id = department.dept_id AND subject.sem = %s AND department.dept_short = %s ORDER BY subject.course_code ASC',(mode,session['dept']))
                field_names = ['Subject Code','Subject Name','Short Subject Name','Semester','Department','Marks (0- no marks, 1- marks)']
                records = cursor.fetchall()
                # print(records)
                cursor.close()
                print(field_names)
                for items in range(0,len(field_names)):
                    worksheet.write(0,items,field_names[items])
                row_insert = 1
                for row in records:
                    # print(row)
                    worksheet.write(row_insert,0,row['course_code'])
                    worksheet.write(row_insert,1,row['sub_name_long'])
                    worksheet.write(row_insert,2,row['sub_name_short'])
                    worksheet.write(row_insert,3,row['sem'][-1])
                    worksheet.write(row_insert,4,row['dept_short'])
                    worksheet.write(row_insert,5,row['sub_type'])
                    worksheet.write(row_insert,6,row['marks'])
                    row_insert += 1
                workbook.close()
                ajax_response['file_created'] = 1
                ajax_response['data_got'] = 1
            else:
                ajax_response['data_got'] = 0
        elif data_master_mode == "electives_category": 
            mode = request.form['mode']
            if mode != "" :
                workbook =xlsxwriter.Workbook(os.path.join(download_directory,dept+'_'+data_master_mode+'_'+mode+'_master.xlsx'))
                worksheet = workbook.add_worksheet(data_master_mode)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT electives_category.cat_name FROM electives_category INNER JOIN department ON electives_category.dept_id = department.dept_id AND electives_category.sem = %s AND department.dept_short = %s ORDER BY electives_category.cat_name ASC',(mode,session['dept']))
                field_names = ['Category Name']
                records = cursor.fetchall()
                cursor.close()
                worksheet.write(0,0,field_names[0])
                row_insert = 1
                for row in records:
                    worksheet.write(row_insert,0,row['cat_name'])
                    row_insert += 1
                workbook.close()
                ajax_response['file_created'] = 1
                ajax_response['data_got'] = 1
            else:
                ajax_response['data_got'] = 0
        elif data_master_mode == "electives_subject": 
            print(data_master_mode,":")
            mode = request.form['mode']
            if mode != "" :
                workbook =xlsxwriter.Workbook(os.path.join(download_directory,dept+'_'+data_master_mode+'_'+mode+'_master.xlsx'))
                worksheet = workbook.add_worksheet(data_master_mode)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT electives.course_code,electives.sub_name_long,electives.sub_name_short,electives.sem,electives.sub_type,electives.marks,electives_category.cat_name,department.dept_short FROM electives INNER JOIN department ON electives.dept_id = department.dept_id INNER JOIN electives_category ON electives.elective_category = electives_category.category_id AND department.dept_short = %s AND electives.sem = %s ORDER BY electives.course_code ASC',(session['dept'],mode))
                field_names = ['Subject Code','Subject Name','Short Subject Name','Semester','Department','Subject Type (1-theory, 0-Practical)','Elective Category','Marks (0- no marks, 1- marks)']
                records = cursor.fetchall()
                # print(records)
                cursor.close()
                print(field_names)
                for items in range(0,len(field_names)):
                    worksheet.write(0,items,field_names[items])
                row_insert = 1
                for row in records:
                    # print(row)
                    worksheet.write(row_insert,0,row['course_code'])
                    worksheet.write(row_insert,1,row['sub_name_long'])
                    worksheet.write(row_insert,2,row['sub_name_short'])
                    worksheet.write(row_insert,3,row['sem'][-1])
                    worksheet.write(row_insert,4,row['dept_short'])
                    worksheet.write(row_insert,5,row['sub_type'])
                    worksheet.write(row_insert,6,row['cat_name'])
                    worksheet.write(row_insert,7,row['marks'])
                    row_insert += 1
                workbook.close()
                ajax_response['file_created'] = 1
                ajax_response['data_got'] = 1
            else:
                ajax_response['data_got'] = 0
    else:
        ajax_response['data_got'] = 0
    return json.dumps(ajax_response)


# COMMON FOR STUDENT , FACULTY AND SUBJECTS END #

# FOR STUDENT ONLY START #

@admin.route('/student_master',methods=['POST','GET'])
@login_required
def student_master_mode():
    mode = request.args.get('mode')
    print(session)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if mode=="First-Year":
        mode_num = 1
        cursor.execute('SELECT S_id, L_name, F_name, M_name, roll, batch, S_email, KT, S_id, S_num, gender FROM student where current_sem=1 OR current_sem=2 ORDER BY roll ASC')
    elif mode=="Second-Year":
        mode_num = 2
        cursor.execute('SELECT S_id, L_name, F_name, M_name, roll, batch, S_email, KT, S_id, S_num, gender FROM student where current_sem=3 OR current_sem=4 ORDER BY roll ASC')
    elif mode=="Third-Year":
        mode_num = 3
        cursor.execute('SELECT S_id, L_name, F_name, M_name, roll, batch, S_email, KT, S_id, S_num, gender FROM student where current_sem=5 OR current_sem=6 ORDER BY roll ASC')
    elif mode=="Last-Year":
        mode_num = 4
        cursor.execute('SELECT S_id, L_name, F_name, M_name, roll, batch, S_email, KT, S_id, S_num, gender FROM student where current_sem=7 OR current_sem=8 ORDER BY roll ASC')
    student = cursor.fetchall()
    cursor.close()
    # print(student)
    msg = check_message()
    return render_template('student_master.html',stud_type=mode, students=student,stdlen=len(student), stud_type_num=mode_num,msg=msg)


@admin.route('/add_student/',methods=['POST'])
@login_required
def insert_student_entry():
    # #print(session)
    print(request.form)
    email = request.form['mail']
    fname = request.form['fname'].upper()
    lname = request.form['lname'].upper()
    mname = request.form['mname'].upper()
    kts = request.form['kt']
    gender = request.form['gender']
    roll = request.form['roll']
    batch = request.form['batch']
    mob_num = request.form['mob_num']
    sem = request.form['semester']
    p_email = request.form['p_mail']
    p_mob_num = request.form['p_mob_num']
    s_pass = hash_password(str(p_mob_num))
    stud_id = request.form['stud_id']
    mode = request.form['mode']
    dept= ""
    dept = session['dept']
    s_photo = ''
    print(request.files)
    if request.files['s_photo'].filename != '':
        s_photo = request.files["s_photo"]
        print(request.files["s_photo"])
        s_photo_name =  s_photo.filename
        directory = os.path.join(app_root,"static/profile_pics/student_images",dept,mode,str('semester_'+sem),stud_id)
        # s_photo_file = os.path.join(directory,s_photo)
        print(directory)
        Path(directory).mkdir(parents=True, exist_ok=True)
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))
        s_photo.save(os.path.join(directory,secure_filename(s_photo_name)))
    else:
        s_photo_name = ''
    print(s_photo)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO student (S_id,S_pass,L_name,F_name,M_name,roll,batch,S_email,KT,S_num,P_email,P_num,current_sem,image,gender,dept) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(stud_id,s_pass,lname,fname,mname,roll,batch,email,kts,mob_num,p_email,p_mob_num,sem,s_photo_name,gender,dept))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Student Entry Successfully Inserted!"
        msg['mode'] = 1
    else:
        msg = {}
        msg['title'] = "Student Entry Insertion Failed!"
        msg['mode'] = 0
    cursor.close()
    msg['there'] = 1
    session['message'] = msg    
    return redirect('/admin/student_master?mode='+mode)


@admin.route('/fetch_student/',methods=['POST'])
@login_required
def fetch_student_entry():
    stud_id = request.form['stud_id']
    dept = session['dept']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM student WHERE S_id = %s",[stud_id])
    result = cursor.fetchone()
    result['there'] = 1
    # print(result)
    # print(type(result))
    if result == None:
        result['there'] = 0
    else:
        session['email_edit'] = result['S_email']
        session['stud_id_edit'] = result['S_id']
    return json.dumps(result)


@admin.route('/check_student_present_edit/',methods=['POST'])
@login_required
def check_student_entry_edit():
    print("check_student_present_edit")
    print(session)
    email = request.form['mail']
    s_id = request.form['stud_id']
    print("Email:",email)
    print("S_ID:",s_id)
    check_counter = {'email':0,'stud_id':0}
    if email != session['email_edit']:
        check_counter['email'] += 1
    if s_id != session['stud_id_edit']:
        check_counter['stud_id'] += 1
    print(check_counter)
    res = {}
    if check_counter['email'] == 1 and check_counter['stud_id'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT S_id FROM student WHERE S_id=%s AND S_email=%s",(s_id,email))
        student = cursor.fetchone()
        cursor.close()
        if student:
            res['s_id_present'] = 1
            res['mail_present'] = 1
        else:
            res['s_id_present'] = 0
            res['mail_present'] = 0
    elif check_counter['email'] == 1 and check_counter['stud_id'] == 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT S_id FROM student WHERE S_email=%s",[email])
        student = cursor.fetchone()
        cursor.close()
        res['s_id_present'] = 0
        if student:
            res['mail_present'] = 1
        else:
            res['mail_present'] = 0
    elif check_counter['email'] == 0 and check_counter['stud_id'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT S_id FROM student WHERE S_id=%s",[s_id])
        student = cursor.fetchone()
        cursor.close()
        res['mail_present'] = 0 
        if student:
            res['s_id_present'] = 1
        else:
            res['s_id_present'] = 0
    else:
        res['s_id_present'] = 0
        res['mail_present'] = 0
    print(res)
    return json.dumps(res)


@admin.route('/update_student/',methods=['POST'])
@login_required
def update_student_entry():
    print(request.form)
    email = request.form['e_mail']
    fname = request.form['e_fname'].upper()
    lname = request.form['e_lname'].upper()
    mname = request.form['e_mname'].upper()
    kts = request.form['e_kt']
    gender = request.form['e_gender']
    roll = request.form['e_roll']
    batch = request.form['e_batch']
    mob_num = request.form['e_mob_num']
    sem = request.form['e_semester']
    p_email = request.form['e_p_mail']
    p_mob_num = request.form['e_p_mob_num']
    first_login = request.form['e_first_login']
    s_pass = hash_password(str(p_mob_num))
    stud_id = request.form['e_stud_id']
    mode = request.form['e_mode']
    dept= session['dept']
    s_photo = ''
    s_photo_name = ''
    print(request.files)
    if len(request.files) != 0:
        s_photo = request.files["e_s_photo"]
        print(s_photo)
        s_photo_name =  s_photo.filename
        print(s_photo_name)
        if s_photo_name != '':
            directory = os.path.join(app_root,"static/profile_pics/student_images",dept,mode,str('semester_'+sem),stud_id)
            # s_photo_file = os.path.join(directory,s_photo)
            print(directory)
            Path(directory).mkdir(parents=True, exist_ok=True)
            for f in os.listdir(directory):
                os.remove(os.path.join(directory, f))
            s_photo.save(os.path.join(directory,secure_filename(s_photo_name)))
    print(s_photo_name)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if s_photo_name == '':
        if first_login == 0:
            cursor.execute("UPDATE student SET S_id = %s, S_pass = %s, L_name = %s, F_name = %s, M_name = %s, roll = %s, batch = %s, S_email = %s, KT = %s, S_num = %s, P_email = %s, P_num = %s, current_sem = %s, gender = %s WHERE S_id = %s or S_email = %s",(stud_id,s_pass,lname,fname,mname,roll,batch,email,kts,mob_num,p_email,p_mob_num,sem,gender,stud_id,email))
        else:
            cursor.execute("UPDATE student SET S_id = %s, L_name = %s, F_name = %s, M_name = %s, roll = %s, batch = %s, S_email = %s, KT = %s, S_num = %s, P_email = %s, P_num = %s, current_sem = %s, gender = %s WHERE S_id = %s or S_email = %s",(stud_id,lname,fname,mname,roll,batch,email,kts,mob_num,p_email,p_mob_num,sem,gender,stud_id,email))
    else:
        if first_login == 0:
            cursor.execute("UPDATE student SET S_id = %s, S_pass = %s, L_name = %s, F_name = %s, M_name = %s, roll = %s, batch = %s, S_email = %s, KT = %s, S_num = %s, P_email = %s, P_num = %s, current_sem = %s, image = %s, gender = %s WHERE S_id = %s or S_email = %s",(stud_id,s_pass,lname,fname,mname,roll,batch,email,kts,mob_num,p_email,p_mob_num,sem,s_photo_name,gender,stud_id,email))
        else:
            cursor.execute("UPDATE student SET S_id = %s, L_name = %s, F_name = %s, M_name = %s, roll = %s, batch = %s, S_email = %s, KT = %s, S_num = %s, P_email = %s, P_num = %s, current_sem = %s, image = %s, gender = %s WHERE S_id = %s or S_email = %s",(stud_id,lname,fname,mname,roll,batch,email,kts,mob_num,p_email,p_mob_num,sem,s_photo_name,gender,stud_id,email))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Student Entry Successfully Updated!"
        msg['mode'] = 1
    else:
        msg['title'] = "No Update in Student Entry!"
        msg['mode'] = 2
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/student_master?mode='+mode)


@admin.route('/delete_student/',methods=['POST'])
@login_required
def delete_student_entry():
    # #print(session)
    print(request.form)
    stud_id = request.form['stud_id']
    dept = session['dept']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT image,current_sem FROM student WHERE S_id = %s",[stud_id])
    result = cursor.fetchone()
    print(result)
    year = ''
    res = {}
    if result['current_sem'] == 1 or result['current_sem'] == 2:
        year = "First-Year"
    elif result['current_sem'] == 3 or result['current_sem'] == 4:
        year = "Second-Year"
    elif result['current_sem'] == 5 or result['current_sem'] == 6:
        year = "Third-Year"
    elif result['current_sem'] == 7 or result['current_sem'] == 8:
        year = "Last-Year"
    filename =  result['image']
    
    dir = os.getcwd()
    print('Present DIR is : ',dir)
    myfile = dir+"/static/profile_pics/student_images/"+dept+"/"+year+"/semester_"+str(result['current_sem'])+"/"+stud_id
    print(str(myfile))
    print("Image url:",result['image'])
    if result['image'] is not None:
        path = os.path.join(str(myfile), result['image']) 
    else:
        path = str(myfile)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    msg = {}
    if cursor.execute("DELETE FROM student WHERE S_id = %s",[stud_id]):    
        mysql.connection.commit()
        res['deleted'] = 1
        if os.path.isfile(path):
            try:
                os.remove(path)
                res['deleted'] = 1
            except OSError as e:  ## if failed, report it back to the user ##
                print ("Error: %s - %s." % (e.filename, e.strerror))
            try:
                os.rmdir(myfile)
                res['deleted'] = 1
            except OSError as e:  ## if failed, report it back to the user ##
                print ("Error: %s - %s." % (e.filename, e.strerror))            
        else:
            print("Not Found!")
    else:
        res['deleted'] = 0
    print(res)
    msg = {}
    if res['deleted'] == 1:
        mysql.connection.commit()
        msg['title'] = "Student Entry Successfully Deleted!"
        msg['mode'] = 1
    else:
        msg['title'] = "Failed to Delete Record!"
        msg['mode'] = 0
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return json.dumps(res)

# FOR STUDENT ONLY END #

# FOR FACULTY ONLY START #

@admin.route('/add_faculty/',methods=['POST'])
@login_required
def insert_faculty_entry():
    print(request.form)
    desgn = request.form['desg'].capitalize()+"."
    email = request.form['mail']
    fname = request.form['fname'].upper()
    lname = request.form['lname'].upper()
    mname = request.form['mname'].upper()
    gender = request.form['gender']
    mob_num = request.form['mob_num']
    f_pass = hash_password(mob_num)
    fac_id = request.form['fac_id']
    dept= ""
    dept = session['dept']
    f_photo = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT dept_name FROM department where dept_short = %s',[dept])
    department = cursor.fetchone()
    dept = department['dept_name']
    if request.files['f_photo'].filename != '':
        f_photo = request.files["f_photo"]
        f_photo_name =  f_photo.filename
        directory = os.path.join(app_root,"static/profile_pics/faculty_images",session['dept'],fac_id)
        # s_photo_file = os.path.join(directory,s_photo)
        print(directory)
        Path(directory).mkdir(parents=True, exist_ok=True)
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))
        f_photo.save(os.path.join(directory,secure_filename(f_photo_name)))
    else:
        f_photo_name = ''
    print(f_photo)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # print(fac_id,desgn,lname,fname,mname,email,mob_num,dept,mob_num,gender,f_photo_name)
    cursor.execute("INSERT INTO faculty (F_id,Designation,L_name,F_name,M_name,F_email,F_password,dept,F_num,gender,img) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (fac_id,desgn,lname,fname,mname,email,f_pass,dept,mob_num,gender,f_photo_name))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Faculty Entry Successfully Inserted!"
        msg['mode'] = 1
    else:
        msg = {}
        msg['title'] = "Faculty Entry Insertion Failed!"
        msg['mode'] = 0
    cursor.close()
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/master_data?mode='+session['data_master_mode'].capitalize())


@admin.route('/fetch_faculty/',methods=['POST'])
@login_required
def fetch_faculty_entry():
    fac_id = request.form['fac_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM faculty WHERE F_id = %s",[fac_id])
    result = cursor.fetchone()
    print(cursor.rowcount)
    # print(type(result))
    if cursor.rowcount == 0:
        result['there'] = 0
    else:
        result['there'] = 1
        session['email_edit'] = result['F_email']
        session['fac_id_edit'] = result['F_id']
    print(result)
    return json.dumps(result)


@admin.route('/check_faculty_present_edit/',methods=['POST'])
@login_required
def check_faculty_entry_edit():
    print("check_faculty_present_edit")
    print(session)
    email = request.form['mail']
    fac_id = request.form['fac_id']
    print("Email:",email)
    print("F_ID:",fac_id,type(fac_id))
    print("session['fac_id_edit']:",session['fac_id_edit'],type(session['fac_id_edit']))
    check_counter = {'email':0,'fac_id':0}
    if email != session['email_edit']:
        check_counter['email'] = 1
    if fac_id != session['fac_id_edit']:
        check_counter['fac_id'] = 1
    print(check_counter)
    res = {}
    if check_counter['email'] == 1 and check_counter['fac_id'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT F_id FROM faculty WHERE F_id=%s AND F_email=%s",(fac_id,email))
        faculty = cursor.fetchone()
        if faculty:
            res['f_id_present'] = 1
            res['mail_present'] = 1
        else:
            res['f_id_present'] = 0
            res['mail_present'] = 0
        cursor.close()
    elif check_counter['email'] == 1 and check_counter['fac_id'] == 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT F_id FROM faculty WHERE F_email=%s",[email])
        faculty = cursor.fetchone()
        cursor.close()
        res['f_id_present'] = 0
        if faculty:
            res['mail_present'] = 1
        else:
            res['mail_present'] = 0
    elif check_counter['email'] == 0 and check_counter['fac_id'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT F_id FROM faculty WHERE F_id=%s",[fac_id])
        faculty = cursor.fetchone()
        cursor.close()
        res['mail_present'] = 0 
        if faculty:
            res['f_id_present'] = 1
        else:
            res['f_id_present'] = 0
    else:
        res['f_id_present'] = 0
        res['mail_present'] = 0
    print(res)
    return json.dumps(res)


@admin.route('/update_faculty/',methods=['POST'])
@login_required
def update_faculty_entry():
    print(request.form)
    desg = request.form['e_desg'].capitalize()
    email = request.form['e_mail']
    fname = request.form['e_fname'].upper()
    lname = request.form['e_lname'].upper()
    mname = request.form['e_mname'].upper()
    gender = request.form['e_gender']
    mob_num = request.form['e_mob_num']
    fac_id = request.form['e_fac_id']
    first_login = request.form['e_first_login']
    print("first_login",first_login)
    f_pass = hash_password(str(mob_num))
    dept= session['dept']
    f_photo = ''
    f_photo_name = ''
    print("request.files",request.files)
    if len(request.files) != 0:
        f_photo = request.files["e_f_photo"]
        print(f_photo)
        f_photo_name =  f_photo.filename
        print(f_photo_name)
        if f_photo_name != '':
            directory = os.path.join(app_root,"static/profile_pics/faculty_images",dept,fac_id)
            # s_photo_file = os.path.join(directory,s_photo)
            print(directory)
            Path(directory).mkdir(parents=True, exist_ok=True)
            for f in os.listdir(directory):
                os.remove(os.path.join(directory, f))
            f_photo.save(os.path.join(directory,secure_filename(f_photo_name)))
    print("f_photo_name:",f_photo_name)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if f_photo_name == '':
        if first_login == 0:
            cursor.execute("UPDATE faculty SET Designation = %s, F_id = %s, F_password = %s, L_name = %s, F_name = %s, M_name = %s, F_email = %s, F_num = %s,gender = %s WHERE F_id = %s or F_email = %s",(desg,fac_id,f_pass,lname,fname,mname,email,mob_num,gender,fac_id,email))
        else:
            cursor.execute("UPDATE faculty SET Designation = %s, F_id = %s, L_name = %s, F_name = %s, M_name = %s, F_email = %s, F_num = %s,gender = %s WHERE F_id = %s or F_email = %s",(desg,fac_id,lname,fname,mname,email,mob_num,gender,fac_id,email))
    else:
        if first_login == 0:
            cursor.execute("UPDATE faculty SET Designation = %s, F_id = %s, F_password = %s, L_name = %s, F_name = %s, M_name = %s, F_email = %s, F_num = %s, img = %s, gender = %s  WHERE F_id = %s or F_email = %s",(desg,fac_id,f_pass,lname,fname,mname,email,mob_num,f_photo_name,gender,fac_id,email))
        else:
            cursor.execute("UPDATE faculty SET Designation = %s, F_id = %s, L_name = %s, F_name = %s, M_name = %s, F_email = %s, F_num = %s, img = %s, gender = %s  WHERE F_id = %s or F_email = %s",(desg,fac_id,lname,fname,mname,email,mob_num,f_photo_name,gender,fac_id,email))
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg = {}
        msg['title'] = "Faculty Entry Successfully Updated!"
        msg['mode'] = 1
    else:
        msg = {}
        msg['title'] = "No Update in Faculty Entry!"
        msg['mode'] = 2
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/master_data?mode='+session['data_master_mode'].capitalize())


@admin.route('/delete_faculty/',methods=['POST'])
@login_required
def delete_faculty_entry():
    # #print(session)
    print(request.form)
    fac_id = request.form['fac_id']
    dept = session['dept']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT img FROM faculty WHERE F_id = %s",[fac_id])
    result = cursor.fetchone()
    print(result)
    year = ''
    res = {}
    filename =  result['img']
    dir = os.getcwd()
    print('Present DIR is : ',dir)
    myfile = dir+"/static/profile_pics/faculty_images/"+dept+"/"+fac_id
    print(str(myfile))
    print("Image url:",result['img'])
    if result['img'] is not None:
        path = os.path.join(str(myfile), result['img']) 
    else:
        path = str(myfile)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if cursor.execute("DELETE FROM faculty WHERE F_id = %s",[fac_id]):    
        mysql.connection.commit()
        res['deleted'] = 1
        if os.path.isfile(path):
            try:
                os.remove(path)
                res['deleted'] = 1
            except OSError as e:  ## if failed, report it back to the user ##
                print ("Error: %s - %s." % (e.filename, e.strerror))
            try:
                os.rmdir(myfile)
                res['deleted'] = 1
            except OSError as e:  ## if failed, report it back to the user ##
                print ("Error: %s - %s." % (e.filename, e.strerror))            
        else:
            print("Not Found!")
    else:
        res['deleted'] = 0
    print(res)    
    cursor.close()
    return json.dumps(res)

# FOR FACULTY ONLY END #

# FOR SUBJECTS ONLY START #

@admin.route('/subject_choice',methods=['POST','GET'])
@login_required
def subject_type_mode():
    sem = request.args.get('sem_mode')
    print(sem)
    print(session)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if sem != "" and sem=='sem1' or sem=='sem2' or sem=='sem3' or sem=='sem4' or sem=='sem5' or sem=='sem6' or sem=='sem7' or sem=='sem8':
        sem_num = int(sem[-1])
        print(sem_num)
        cursor.execute('SELECT COUNT(electives.course_code) as total_subjects FROM electives INNER JOIN department ON electives.dept_id = department.dept_id AND department.dept_short=%s AND electives.sem=%s',(session['dept'],sem))
        total_elect_sub = cursor.fetchone()
        cursor.execute('SELECT COUNT(subject.course_code) as total_subjects FROM subject INNER JOIN department ON subject.dept_id = department.dept_id AND department.dept_short=%s AND subject.sem=%s',(session['dept'],sem))
        total_norm_sub = cursor.fetchone()
        cursor.close()
        return render_template('subject/subject_mode.html',sub_type=sem, total_elect_sub=total_elect_sub['total_subjects'],total_norm_sub=total_norm_sub['total_subjects'], sem=sem)
    else:
        return redirect('/admin/master_data?mode=Subject')


@admin.route('/subject_master',methods=['POST','GET'])
@login_required
def subject_master_mode():
    sem = request.args.get('sem_mode')
    print(sem)
    print(session)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if sem != "" and sem=='sem1' or sem=='sem2' or sem=='sem3' or sem=='sem4' or sem=='sem5' or sem=='sem6' or sem=='sem7' or sem=='sem8':
        sem_num = int(sem[-1])
        print(sem_num)
        cursor.execute('SELECT subject.course_code,subject.sub_name_short, subject.sub_name_long, subject.sub_type, subject.marks FROM subject INNER JOIN department ON subject.dept_id = department.dept_id AND department.dept_short=%s AND subject.sem=%s ORDER BY subject.course_code ASC',(session['dept'],sem))
        subject = cursor.fetchall()
        print(cursor.rowcount)
        cursor.close()
        msg = check_message()
        
        return render_template('subject_master_data.html',sub_type=sem, subjects=subject,sublen=len(subject), stud_type_num=sem_num,msg=msg)
    else:
        return redirect('/admin/master_data?mode=Subject')

@admin.route('/fetch_subject/',methods=['POST'])
@login_required
def fetch_subject_entry():
    sub_id = request.form['sub_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM subject WHERE course_code = %s",[sub_id])
    result = cursor.fetchone()
    print(cursor.rowcount)
    # print(type(result))
    if cursor.rowcount == 0:
        result['there'] = 0
    else:
        result['there'] = 1
        session['sub_id_edit'] = result['course_code']
        session['sub_short_edit'] = result['sub_name_short']
    print(result)
    return json.dumps(result)


@admin.route('/add_subject/',methods=['POST'])
@login_required
def insert_subject_entry():
    # #print(session)
    print(request.form)
    sub_full_name = request.form['sub_full_name'].upper()
    sub_short_name = request.form['sub_short_name'].upper()
    sub_code = request.form['sub_code'].upper()
    sub_type = int(request.form['sub_type'])
    marks = int(request.form['marks'])
    sem = request.form['mode']
    dept= ""
    dept = session['dept']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT dept_id FROM department where dept_short = %s',[session['dept']])
    department = cursor.fetchone()
    dept_id = department['dept_id']
    cursor.execute("INSERT INTO subject (course_code,sub_name_long,sub_name_short,sem,sub_type,marks,dept_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",(sub_code,sub_full_name,sub_short_name,sem,sub_type,marks,dept_id))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Subject Entry Successfully Updated!"
        msg['mode'] = 1
    else:
        msg = {}
        msg['title'] = "Subject Entry Updating Failed!"
        msg['mode'] = 0
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/subject_master?sem_mode='+sem)


@admin.route('/check_subject_present_edit/',methods=['POST'])
@login_required
def check_subject_entry_edit():
    print(session)
    sub_id = request.form['sub_code']
    short_name = request.form['short_name']
    print("session['sub_id_edit']:",session['sub_id_edit'])
    print("session['sub_short_edit']:",session['sub_short_edit'])
    check_counter = {'sub_id':0,'short_name':0}
    if sub_id != session['sub_id_edit']:
        check_counter['sub_id'] = 1
    if short_name != session['sub_short_edit']:
        check_counter['short_name'] = 1
    print(check_counter)
    res = {}
    if check_counter['sub_id'] == 1 and check_counter['short_name'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT subject.course_code FROM subject INNER JOIN department ON subject.dept_id = department.dept_id WHERE subject.course_code=%s AND department.dept_short=%s AND subject.sub_name_short=%s",(sub_id,session['dept'],short_name))
        subject = cursor.fetchone()
        if subject:
            res['sub_id'] = 1
            res['short_name'] = 1
        else:
            res['sub_id'] = 0
            res['short_name'] = 0
        cursor.close()
    elif check_counter['sub_id'] == 1 and check_counter['short_name'] == 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT subject.course_code FROM subject INNER JOIN department ON subject.dept_id = department.dept_id WHERE subject.course_code=%s AND department.dept_short=%s",(sub_id,session['dept']))
        subject = cursor.fetchone()
        cursor.close()
        res['short_name'] = 0
        if subject:
            res['sub_id'] = 1
        else:
            res['sub_id'] = 0
    elif check_counter['sub_id'] == 0 and check_counter['short_name'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT subject.course_code FROM subject INNER JOIN department ON subject.dept_id = department.dept_id WHERE department.dept_short=%s AND subject.sub_name_short=%s",(session['dept'],short_name))
        faculty = cursor.fetchone()
        cursor.close()
        res['sub_id'] = 0 
        if faculty:
            res['short_name'] = 1
        else:
            res['short_name'] = 0
    else:
        res['sub_id'] = 0
        res['short_name'] = 0
    print(res)
    return json.dumps(res)


@admin.route('/update_subject/',methods=['POST'])
@login_required
def update_subject_entry():
    print(request.form)
    sub_full_name = request.form['e_sub_full_name'].upper()
    sub_short_name = request.form['e_sub_short_name'].upper()
    sub_code = request.form['e_sub_code'].upper()
    sub_type = int(request.form['e_sub_type'])
    marks = int(request.form['e_marks'])
    sem = request.form['e_mode']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE subject \
        SET course_code = %s, sub_name_long = %s, sub_name_short = %s, sem = %s, sub_type = %s, marks = %s \
            WHERE course_code = %s or sub_name_short = %s",(sub_code,sub_full_name,sub_short_name,sem,sub_type,marks,sub_code,sub_short_name))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Subject Entry Successfully Updated!"
        msg['mode'] = 1
    else:
        msg['title'] = "No Update in Subject!"
        msg['mode'] = 2
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/subject_master?sem_mode='+sem)


@admin.route('/delete_subject/',methods=['POST'])
@login_required
def delete_subject_entry():
    # #print(session)
    print(request.form)
    sub_id = request.form['sub_id']
    res = {}
    if sub_id !='':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if cursor.execute("DELETE subject FROM subject INNER JOIN department ON department.dept_id = subject.dept_id WHERE department.dept_short=%s AND subject.course_code = %s",(session['dept'],sub_id)):
            mysql.connection.commit()
            cursor.close()
            res['deleted'] = 1
        else:
            res['deleted'] = 0
        res['error'] = 0
    else:
        res['error'] = 1
    print(res)        
    return json.dumps(res)


# FOR SUBJECTS ONLY STOP #

# FOR ELECTIVES SUBJECT START #

@admin.route('/elective_choice',methods=['POST','GET'])
@login_required
def elective_mode():
    sem = request.args.get('sem_mode')
    choice = request.args.get('elect_mode')
    print(sem)
    print(session)
    print("choice",choice)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if sem != "" and sem=='sem1' or sem=='sem2' or sem=='sem3' or sem=='sem4' or sem=='sem5' or sem=='sem6' or sem=='sem7' or sem=='sem8':
        if choice != "" and choice=='subject' or choice=='category':
            sem_num = int(sem[-1])
            print(sem_num)
            if session['data_master_mode'] != "electives_"+choice :
                session['data_master_mode'] = "electives_"+choice
            if choice == 'subject':
                cursor.execute('SELECT course_code, sub_name_short, sub_name_long, sub_type, elective_category, marks, cat_name FROM electives INNER JOIN department ON electives.dept_id = department.dept_id INNER JOIN electives_category ON elective_category = category_id AND department.dept_short=%s AND electives.sem=%s ORDER BY course_code ASC',(session['dept'],sem))
                subject = cursor.fetchall()
                print(cursor.rowcount)
                cursor.close()
                msg = check_message()
                return render_template('elective_subject_master_data.html',sub_type=sem, subjects=subject,sublen=len(subject), stud_type_num=sem_num,msg=msg)
            else:
                cursor.execute('SELECT electives_category.cat_name,electives_category.category_id FROM electives_category INNER JOIN department ON electives_category.dept_id = department.dept_id AND department.dept_short=%s AND electives_category.sem=%s ORDER BY electives_category.cat_name ASC',(session['dept'],sem))
                category = cursor.fetchall()
                print(cursor.rowcount)
                cursor.close()
                msg = check_message()
                return render_template('electives/elective_category_master_data.html',sem=sem, categories=category,catlen=len(category),msg=msg)
        else:
            sem_num = int(sem[-1])
            print(sem_num)
            cursor.execute('SELECT COUNT(electives.course_code) as total_subjects FROM electives INNER JOIN department ON electives.dept_id = department.dept_id AND department.dept_short=%s AND electives.sem=%s',(session['dept'],sem))
            total_sub = cursor.fetchone()
            cursor.execute('SELECT COUNT(electives_category.cat_name) as total_category FROM electives_category INNER JOIN department ON electives_category.dept_id  = department.dept_id AND department.dept_short=%s AND electives_category.sem=%s',(session['dept'],sem))
            total_cat = cursor.fetchone()
            cursor.close()
            return render_template('electives/elective_mode.html',sub_type=sem, total_subjects=total_sub['total_subjects'],total_category=total_cat['total_category'], sem=sem)

    else:
        return redirect('/admin/master_data?mode=Subject')


# ELECTIVE SUBJECT STARTS #

@admin.route('/elective_subject_master',methods=['POST','GET'])
@login_required
def elective_subject_master_mode():
    sem = request.args.get('sem_mode')
    print(sem)
    print(session)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if sem != "" and sem=='sem1' or sem=='sem2' or sem=='sem3' or sem=='sem4' or sem=='sem5' or sem=='sem6' or sem=='sem7' or sem=='sem8':
        sem_num = int(sem[-1])
        print(sem_num)
        cursor.execute('SELECT electives.course_code,electives.sub_name_short, electives.sub_name_long, electives.sub_type,electives.elective_of, electives.marks FROM electives INNER JOIN department ON electives.dept_id = department.dept_id AND department.dept_short=%s AND electives.sem=%s ORDER BY electives.course_code ASC',(session['dept'],sem))
        subject = cursor.fetchall()
        print(cursor.rowcount)
        cursor.close()
        msg = check_message()
        
        return render_template('elective_subject_master_data.html',sub_type=sem, subjects=subject,sublen=len(subject), stud_type_num=sem_num,msg=msg)
    else:
        return redirect('/admin/master_data?mode=Subject')


@admin.route('/check_elective_subject_present_edit/',methods=['POST'])
@login_required
def check_elective_subject_entry_edit():
    print(session)
    sub_id = request.form['sub_code']
    short_name = request.form['short_name']
    print("session['sub_id_edit']:",session['el_sub_id_edit'])
    print("session['sub_short_edit']:",session['el_sub_short_edit'])
    check_counter = {'sub_id':0,'short_name':0}
    if sub_id != session['el_sub_id_edit']:
        check_counter['sub_id'] = 1
    if short_name != session['el_sub_short_edit']:
        check_counter['short_name'] = 1
    print(check_counter)
    res = {}
    if check_counter['sub_id'] == 1 and check_counter['short_name'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT electives.course_code FROM electives INNER JOIN department ON electives.dept_id = department.dept_id WHERE electives.course_code=%s AND department.dept_short=%s AND electives.sub_name_short=%s",(sub_id,session['dept'],short_name))
        subject = cursor.fetchone()
        if subject:
            res['sub_id'] = 1
            res['short_name'] = 1
        else:
            res['sub_id'] = 0
            res['short_name'] = 0
        cursor.close()
    elif check_counter['sub_id'] == 1 and check_counter['short_name'] == 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT electives.course_code FROM electives INNER JOIN department ON electives.dept_id = department.dept_id WHERE electives.course_code=%s AND department.dept_short=%s",(sub_id,session['dept']))
        subject = cursor.fetchone()
        cursor.close()
        res['short_name'] = 0
        if subject:
            res['sub_id'] = 1
        else:
            res['sub_id'] = 0
    elif check_counter['sub_id'] == 0 and check_counter['short_name'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT electives.course_code FROM electives INNER JOIN department ON electives.dept_id = department.dept_id WHERE department.dept_short=%s AND electives.sub_name_short=%s",(session['dept'],short_name))
        faculty = cursor.fetchone()
        cursor.close()
        res['sub_id'] = 0 
        if faculty:
            res['short_name'] = 1
        else:
            res['short_name'] = 0
    else:
        res['sub_id'] = 0
        res['short_name'] = 0
    print(res)
    return json.dumps(res)

@admin.route('/fetch_elective_subject/',methods=['POST'])
@login_required
def fetch_elective_subject_entry():
    sub_id = request.form['sub_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM electives WHERE course_code = %s",[sub_id])
    result = cursor.fetchone()
    print(cursor.rowcount)
    # print(type(result))
    if cursor.rowcount == 0:
        result['there'] = 0
    else:
        result['there'] = 1
        session['el_sub_id_edit'] = result['course_code']
        session['el_sub_short_edit'] = result['sub_name_short']
    print(result)
    return json.dumps(result)


@admin.route('/add_elective_subject/',methods=['POST'])
@login_required
def insert_elective_subject_entry():
    # #print(session)
    print(request.form)
    sub_full_name = request.form['sub_full_name'].upper()
    sub_short_name = request.form['sub_short_name'].upper()
    sub_code = request.form['sub_code'].upper()
    sub_type = int(request.form['sub_type'])
    category = int(request.form['category'])
    marks = int(request.form['marks'])
    sem = request.form['mode']
    dept= ""
    dept = session['dept']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT dept_id FROM department where dept_short = %s',[session['dept']])
    department = cursor.fetchone()
    dept_id = department['dept_id']
    cursor.execute("INSERT INTO electives (course_code,sub_name_long,sub_name_short,sem,sub_type,elective_category,marks,dept_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(sub_code,sub_full_name,sub_short_name,sem,sub_type,category,marks,dept_id))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Subject Entry Successfully Inserted!"
        msg['mode'] = 1
    else:
        msg = {}
        msg['title'] = "Subject Entry Insertion Failed!"
        msg['mode'] = 0
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/elective_choice?sem_mode='+sem+'&elect_mode=subject')


@admin.route('/update_elective_subject/',methods=['POST'])
@login_required
def update_elective_subject_entry():
    print(request.form)
    sub_full_name = request.form['e_sub_full_name'].upper()
    sub_short_name = request.form['e_sub_short_name'].upper()
    sub_code = request.form['e_sub_code'].upper()
    sub_type = int(request.form['e_sub_type'])
    category = int(request.form['e_category'])
    marks = int(request.form['e_marks'])
    sem = request.form['e_mode']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE electives \
        SET course_code = %s, sub_name_long = %s, sub_name_short = %s, sem = %s, sub_type = %s, elective_category = %s, marks = %s \
            WHERE course_code = %s or sub_name_short = %s",(sub_code,sub_full_name,sub_short_name,sem,sub_type,category,marks,sub_code,sub_short_name))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Subject Entry Successfully Updated!"
        msg['mode'] = 1
    else:
        msg['title'] = "No Update in Subject Entry!"
        msg['mode'] = 2
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/elective_choice?sem_mode='+sem+'&elect_mode=subject')


@admin.route('/delete_elective_subject/',methods=['POST'])
@login_required
def delete_elective_subject_entry():
    # #print(session)
    print(request.form)
    sub_id = request.form['sub_id']
    res = {}
    if sub_id !='':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if cursor.execute("DELETE electives FROM electives INNER JOIN department ON department.dept_id = electives.dept_id WHERE department.dept_short=%s AND electives.course_code = %s",(session['dept'],sub_id)):
            mysql.connection.commit()
            cursor.close()
            res['deleted'] = 1
        else:
            res['deleted'] = 0
        res['error'] = 0
    else:
        res['error'] = 1
    print(res)        
    return json.dumps(res)

# ELECTIVE SUBJECT ENDS #

# ELECTIVE CATEGORY STARTS #

@admin.route('/fetch_elective_categories/',methods=['POST'])
@login_required
def fetch_electives_category_entry():
    mode = request.form['sem_mode']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT dept_id FROM department where dept_short = %s',[session['dept']])
    department = cursor.fetchone()
    dept_id = department['dept_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT category_id, cat_name FROM electives_category WHERE sem = %s AND dept_id = %s",(mode,dept_id))
    categories = cursor.fetchall()
    print(categories)
    print(type(categories))
    res = {}
    if cursor.rowcount == 0:
        res['there'] = 0
    else:
        cat_name = []
        cat_ids = []
        for i in range(len(categories)):
            cat_single = categories[i] 
            cat_name.append(cat_single['cat_name'])
            cat_ids.append(cat_single['category_id'])
        res['there'] = 1
        res['cat_name'] =  cat_name
        res['cat_id'] = cat_ids
    print(res)
    return json.dumps(res)

@admin.route('/fetch_category/',methods=['POST'])
@login_required
def fetch_category_entry():
    cat_id = request.form['cat_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM electives_category WHERE category_id = %s",[cat_id])
    result = cursor.fetchone()
    print(cursor.rowcount)
    # print(type(result))
    if cursor.rowcount == 0:
        result['there'] = 0
    else:
        result['there'] = 1
        session['cat_sem_edit'] = result['sem']
        session['cat_name_edit'] = result['cat_name']
    print(result)
    return json.dumps(result)


@admin.route('/add_category/',methods=['POST'])
@login_required
def insert_category_entry():
    # #print(session)
    print(request.form)
    cat_name = request.form['cat_name'].title()
    sem = request.form['mode']
    dept= ""
    dept = session['dept']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT dept_id FROM department where dept_short = %s',[session['dept']])
    department = cursor.fetchone()
    dept_id = department['dept_id']
    cursor.execute("INSERT INTO electives_category (cat_name,sem,dept_id) VALUES (%s,%s,%s)",(cat_name,sem,dept_id))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Category Entry Successfully Inserted!"
        msg['mode'] = 1
    else:
        msg = {}
        msg['title'] = "Category Entry Insertion Failed!"
        msg['mode'] = 0
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/elective_choice?sem_mode='+sem+'&elect_mode=category')


@admin.route('/check_category_present_edit/',methods=['POST'])
@login_required
def check_category_entry_edit():
    print(session)
    sem = request.form['sem']
    category_name = request.form['category'].capitalize()
    print("form sem:",sem)
    print("form category name:",category_name)
    check_counter = {'sem':0,'category_name':0}
    print("session['cat_sem_edit']",session['cat_sem_edit'])
    print("session['cat_name_edit']",session['cat_name_edit'])
    if sem != session['cat_sem_edit']:
        check_counter['sem'] = 1
    if category_name != session['cat_name_edit']:
        check_counter['category_name'] = 1
    print(check_counter)
    res = {}
    if check_counter['sem'] == 1 or check_counter['category_name'] == 1:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT electives_category.category_id FROM electives_category INNER JOIN department ON electives_category.dept_id = department.dept_id WHERE electives_category.cat_name = %s AND electives_category.sem = %s AND department.dept_short=%s",(category_name,sem,session['dept']))
        category = cursor.fetchone()
        if category:
            res['sem'] = 1
            res['cat_name_edit'] = 1
        else:
            res['sem'] = 0
            res['cat_name_edit'] = 0
        cursor.close()
    else:
        res['sem'] = 0
        res['cat_name_edit'] = 0
    print(res)
    return json.dumps(res)


@admin.route('/update_category/',methods=['POST'])
@login_required
def update_category_entry():
    print(request.form)
    sem = request.form['e_mode']
    cat_id = request.form['e_cat_id']
    cat_name = request.form['e_cat_name'].title()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE electives_category\
        SET cat_name = %s, sem = %s  \
            WHERE category_id = %s ",(cat_name,sem,cat_id))
    msg = {}
    if cursor.rowcount == 1:
        mysql.connection.commit()
        msg['title'] = "Category Entry Successfully Updated!"
        msg['mode'] = 1
    else:
        msg['title'] = "No Update in Category Entry!"
        msg['mode'] = 2
    msg['there'] = 1
    session['message'] = msg
    cursor.close()
    return redirect('/admin/elective_choice?sem_mode='+sem+'&elect_mode=category')


@admin.route('/delete_category/',methods=['POST'])
@login_required
def delete_category_entry():
    # #print(session)
    print(request.form)
    cat_id = request.form['cat_id']
    res = {}
    if cat_id !='':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if cursor.execute("DELETE electives_category FROM electives_category INNER JOIN department ON department.dept_id = electives_category.dept_id WHERE department.dept_short=%s AND electives_category.category_id = %s",(session['dept'],cat_id)):
            mysql.connection.commit()
            cursor.execute("DELETE electives FROM electives INNER JOIN department ON department.dept_id = electives.dept_id WHERE department.dept_short=%s AND electives.elective_category = %s",(session['dept'],cat_id))
            mysql.connection.commit()
            cursor.close()
            res['deleted'] = 1
        else:
            res['deleted'] = 0
        res['error'] = 0
    else:
        res['error'] = 1
    print(res)        
    return json.dumps(res)

# ELECTIVE CATEGORY ENDS #