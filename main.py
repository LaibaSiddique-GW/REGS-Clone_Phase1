import sqlite3
from flask import Flask, session, render_template, redirect, request
import random # used for password randomization in userRegistration()
import string # used to simplify password randomization
from datetime import datetime, timedelta # used for automatically generating the standard grad year for students and comparing start/end times of classes during registration


""" for reference 
connection = sqlite3.connect("myDatabase.db")
connection.row_factory = sqlite3.Row
cur = connection.cursor()
"""
# Pages linked together and code snippetts (often, but not always, to fix bugs) for various places written by Laiba

# session key set up
app = Flask('app')
app.debug = True
app.secret_key = 'sessionKey'
app.config['SESSION_PERMANENT'] = False

@app.route('/', methods = ["GET", "POST"])
def login(): # written by Tabby
    if ('user' in session): # automatically redirects if already logged in
        return redirect('/account')
    
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    
    if (request.method == "POST"):
        email = request.form['email']
        password = request.form['password']
        
        # if the domain is not .edu, error. 
        if (email[-4:] != ".edu"):
            connection.commit()
            connection.close()
            return render_template('login.html', error = True)

        split = email.split('@') # splits by '@' to separate id from user type for triple checking before login
        uID = split[0]
        userType = split[1]
        userType = userType[0:split[1].index('.')] # gets rid of the email's domain
        
        cur.execute("SELECT * FROM users WHERE UID = ?", (uID,))
        row = cur.fetchone()
        
        # does the checks prior to checking the session variable
        if (row == None or len(row) == 0 or password != row['password'] or uID != row['UID'] or userType != row['user_type']): # triple checks based on uid, password, and user type
            connection.commit()
            connection.close()
            return render_template('login.html', error = True) # gives an error message when login failed
    
        # sets up session variable
        session.permanent = False
        session['user'] = row['uID']
        session['user_type'] = row['user_type'] # added from review suggestion
    
    if ('user' in session):
        connection.commit() # corrected with review
        connection.close()
        return redirect('/account') # for one unified account info page with ability to update account info
    
    connection.commit() # corrected with review
    connection.close()
    return render_template('login.html', error = False) # default rendering without an error message

@app.route('/userRegistration', methods = ["GET", "POST"])
def userRegistration(): # written by Tabby
    if ('user' not in session): # if not logged in, redirects to login page
        return redirect('/')
    elif (session['user_type'] != 'admin'): # if not admin redirects to account page
        return redirect('/account')
    
    # if user cam here from course registration without pressing "return to account" button, pop all those variables to reset them. - Laiba
    if 'registration_can_search' in session: 
        session.pop('registration_can_search')
    if 'registration_search_general' in session:
        session.pop('registration_search_general')
    if 'registration_search_capacity' in session:
        session.pop('registration_search_capacity')
    if 'registration_search_enrollment' in session:
        session.pop('registration_search_enrollment')
    if 'registration_search_professors' in session:
        session.pop('registration_search_professors')
    if 'registration_search_CRN' in session:
        session.pop('registration_search_CRN')
    if 'registration_add_CRN_list' in session:
        session.pop('registration_add_CRN_list')
    if 'registration_add_class_data' in session:
        session.pop('registration_add_class_data')
    if 'registration_drop_CRN_list' in session:
        session.pop('registration_drop_CRN_list')
    if 'registration_drop_class_data' in session:
        session.pop('registration_drop_class_data')
    
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    
    password = ""
    
    if (request.method == "POST"):
        fname = request.form['fname']
        lname = request.form['lname']
        uID = request.form['uID']
        address = request.form['address']
        userType = request.form['user_type']
        dept = request.form.get('dept')
        
        cur.execute("SELECT * FROM department WHERE dep_name = ?", (dept,))
        departments = cur.fetchall()
        if (departments == None or len(departments) == 0):
            return render_template('userRegistration.html', submitted = False, error = True)
        
        # randomization of initial password        
        characters = string.ascii_letters + string.digits # simplified password randomization
        password = ''.join(random.choices(characters, k = 10))
        
        cur.execute("SELECT COUNT(UID) FROM users WHERE UID = ?", (uID,))
        row = cur.fetchall()
        if (row == None): # error checking for repeat of a current UID
            connection.commit()
            connection.close()
            return render_template('userRegistration.html', submitted = False, error = True)
        
        try: 
            cur.execute("INSERT INTO users (UID, password, first_name, last_name, address, user_type, department) VALUES (?, ?, ?, ?, ?, ?, ?)", (uID, password, fname, lname, address, userType, dept))
        except:
            connection.commit()
            connection.close()
            return render_template('userRegistration.html', submitted = False, error = True)
        
        if (userType == "instructor"):
            cur.execute("SELECT TSID FROM time_slot WHERE start_time = '13:00:00' AND end_time = '14:00:00' AND day = 'F'") # finds the TSID for the default OH time slot
            tsID = int(cur.fetchone())
            cur.execute("SELECT MAX(room), department.building FROM department JOIN classroom ON department.building = classroom.building WHERE department.dep_name = ?", (dept,))
            office = cur.fetchone()
            building = office['office_building']
            room = int(office['MAX(room)']) + 1
            current = room
            
            # verifies that the office is open
            cur.execute("SELECT office_room FROM instructor WHERE office_room = ?", (room, ))
            if (cur.fetchall() != None):
                current = None
                while (current == None):
                    room += 1
                    cur.execute("SELECT office_room FROM instructor where office_room = ?", ((room), ))
                    if (cur.fetchone() == None):
                        current = room 
                    
            room = current 
            # offices have a default capacity of 4
            cur.execute("SELECT * FROM classroom WHERE building = ? AND room = ?", (building, room))
            if (cur.fetchall() == None): # added from review
                try: 
                    cur.execute("INSERT INTO classroom (building, room, capacity) VALUES (?, ?, ?)", (building, room, 4))
                except:
                    return render_template('userRegistration.html', submitted = False, error = True)
            
            try: 
                cur.execute("INSERT INTO instructor (IID, OH_time, office_building, office_room) VALUES (?, ?, ?, ?)", (uID, tsID, building, room))
            except: 
                return render_template('userRegistration.html', submitted = False, error = True)
        elif (userType == "gradSec"):
            cur.execute("SELECT TSID FROM time_slot WHERE start_time = '13:00:00' AND end_time = '14:00:00' AND day = 'F'") # finds the TSID for the default OH time slot
            tsID = int(cur.fetchone())
            try: 
                cur.execute("INSERT INTO grad_secretary (GID, OH_time) VALUES (?, ?)", (uID, tsID))
            except:
                return render_template('userRegistration.html', submitted = False, error = True)
        elif (userType == 'student'):
            program = request.form['program']
            if (program == 'Doctoral' or program == 'PhD'):
                try:
                    cur.execute("INSERT INTO grad_student (SID, degree_program, grad_year) VALUES (?, ?, ?)", (uID, program, (datetime.now().year + 6)))
                except:
                    return render_template('userRegistration.html', submitted = False, error = True)
            elif (program == "Masters"):
                try: 
                    cur.execute("INSERT INTO grad_student (SID, degree_program, grad_year) VALUES (?, ?, ?)", (uID, program, (datetime.now().year + 2)))
                except:
                    return render_template('userRegistration.html', submitted = False, error = True)
        else:
            cur.execute("SELECT MAX(room), department.building FROM department JOIN classroom ON department.building = classroom.building WHERE department.dep_name = ?", (dept,))
            office = cur.fetchone()
            building = office['building']
            room = int(office['MAX(room)']) + 1
            current = room
            
            # verifies that the office is open
            cur.execute("SELECT office_room FROM instructor WHERE office_room = ?", (room, ))
            if (cur.fetchall() != None):
                current = None
                while (current == None):
                    room += 1
                    cur.execute("SELECT office_room FROM instructor where office_room = ?", ((room), ))
                    if (cur.fetchone() == None):
                        current = room 
                    
            room = current 
            
            # offices have a default capacity of 4
            cur.execute("SELECT * FROM classroom WHERE building = ? AND room = ?", (building, room))
            if (cur.fetchall() == None): # added from review
                try: 
                    cur.execute("INSERT INTO classroom (building, room, capacity) VALUES (?, ?, ?)", (building, room, 4))
                except:
                    return render_template('userRegistration.html', submitted = False, error = True)
            try: 
                cur.execute("INSERT INTO administrator (AID, office_building, office_room) VALUES (?, ?, ?)", (uID, building, room))
            except: 
                return render_template('userRegistration.html', submitted = False, error = True)
        
        connection.commit()
        connection.close()
        return render_template('userRegistration.html', submitted = True, error = False, newPassword = password) # reloads page with submission confirmation
    
    connection.commit()
    connection.close()
    return render_template('userRegistration.html', submitted = False, error = False) # default with no submission confirmation
        
@app.route('/signOut')
def signOut():
    session.clear()
    return redirect('/')
  
@app.route('/account', methods = ["GET", "POST"])
def account(): # written by Tabby
    if ('user' not in session):
        return redirect('/')
    
    # if user cam here from course registration without pressing "return to account" button, pop all those variables to reset them. - Laiba
    if 'registration_can_search' in session: 
        session.pop('registration_can_search')
    if 'registration_search_general' in session:
        session.pop('registration_search_general')
    if 'registration_search_capacity' in session:
        session.pop('registration_search_capacity')
    if 'registration_search_enrollment' in session:
        session.pop('registration_search_enrollment')
    if 'registration_search_professors' in session:
        session.pop('registration_search_professors')
    if 'registration_search_CRN' in session:
        session.pop('registration_search_CRN')
    if 'registration_add_CRN_list' in session:
        session.pop('registration_add_CRN_list')
    if 'registration_add_class_data' in session:
        session.pop('registration_add_class_data')
    if 'registration_drop_CRN_list' in session:
        session.pop('registration_drop_CRN_list')
    if 'registration_drop_class_data' in session:
        session.pop('registration_drop_class_data')

    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    
    rating = None 

    cur.execute("SELECT * FROM users WHERE UID = ?", (session['user'],)) # finds all standard data on the user
    data = cur.fetchone()
    
    userType = ""
    typeSpecific = None # finds the user_type specific data to send to account 
    if (session['user_type'] == 'student'):
        cur.execute("SELECT * FROM grad_student WHERE SID = ?", (session['user'],))
        typeSpecific = cur.fetchone()
        userType = 'Graduate Student'
    elif (session['user_type'] == 'instructor'):
        cur.execute("SELECT * FROM instructor JOIN time_slot ON instructor.OH_time = time_slot.TSID WHERE IID = ?", (session['user'],))
        typeSpecific = cur.fetchone()
        userType = 'Instructor'
        
        # determines a rating
        cur.execute("SELECT AVG(rating) FROM ratings WHERE UID = ?", (session['user'],))
        rateRow = cur.fetchone()
        rating = 0
        if (rateRow != None and len(rateRow) != 0 and rateRow['AVG(rating)'] != None):
            rating = rateRow['AVG(rating)']
        rating = round(rating, 2)
    elif (session['user_type'] == 'gradSec'):
        userType = 'Graduate Secretary'
        
        # determines a rating
        cur.execute("SELECT AVG(rating) FROM ratings WHERE UID = ?", (session['user'],))
        rateRow = cur.fetchone()
        rating = 0
        if (rateRow != None and len(rateRow) != 0 and rateRow['AVG(rating)'] != None):
            rating = rateRow['AVG(rating)']
        rating = round(rating, 2)
    else: # get info for admin. - Laiba
        cur.execute("SELECT * FROM administrator WHERE AID = ?", (session['user'],))
        typeSpecific = cur.fetchone()
        userType = 'Administration'
    
    if (request.method == 'POST'): # password change
        if ("ChangePassword" in request.form):
            current = request.form['current']
            new = request.form['new']
            verify = request.form['verify']
        
            if (new != verify): # checks to make sure the password is correctly verified
                connection.commit() # could expand to show specific error messages
                connection.close()
                return render_template('account.html', userData = data, userType = session['user_type'], typeSpecific = typeSpecific, passUpdate = False, error = True, addressUpdate = False, ohUpdate = False, type = userType, rating = rating)
        
            cur.execute("SELECT UID, password FROM users WHERE UID = ?", (session['user'],))
            user = cur.fetchone()
            if (user == None):
                connection.commit()
                connection.close()
                return render_template('account.html', userData = data, userType = session['user_type'], typeSpecific = typeSpecific, passUpdate = False, error = True, addressUpdate = False, ohUpdate = False, type = userType, rating = rating)
            if (user['password'] == current):
                cur.execute("UPDATE users SET password = ? WHERE UID = ?", (new, session['user']))
                connection.commit()
            else: # fails the password update if the current password is not correct
                connection.commit()
                connection.close()
                return render_template('account.html', userData = data, userType = session['user_type'], typeSpecific = typeSpecific, passUpdate = False, error = True, addressUpdate = False, ohUpdate = False, type = userType, rating = rating)

            connection.commit()
            connection.close()
            return render_template('account.html', userData = data, userType = session['user_type'], typeSpecific = typeSpecific, passUpdate = True, error = False, addressUpdate = False, ohUpdate = False, type = userType, rating = rating)
        elif ("UpdateAddress" in request.form):
            new = request.form['address']
            cur.execute("UPDATE users SET address = ? WHERE UID = ?", (new, session['user']))
            connection.commit()

            # Make sure address changes on page. - Laiba
            cur.execute("SELECT * FROM users WHERE UID = ?", (session['user'],)) # finds all standard data on the user
            data = cur.fetchone()
            
            connection.commit()
            connection.close()
            return render_template('account.html', userData = data, userType = session['user_type'], typeSpecific = typeSpecific, passUpdate = False, error = False, addressUpdate = True, ohUpdate = False, type = userType, rating = rating)
        elif ("Update Office Hours" in request.form):
            day = 0
            for d in ['M', 'T', 'W', 'R', 'F']:
                if (request.form.get(d)):
                    day = d
            
            start = request.form['start']
            end = request.form['end']
            
            cur.execute("SELECT TSID FROM time_slot WHERE start_time = ? AND end_time = ? AND day = ?", (start, end, day)) # searches if the time slot exists
            timeID = cur.fetchone()
            if (timeID == None): # corrected from timeID == 0
                cur.execute("SELECT MAX(TSID) FROM time_slot")
                timeI = cur.fetchone()
                timeID = timeI['MAX(TSID)']
                timeID += 1 # adds one to make sure no id's are repeated
                cur.execute("INSERT INTO time_slot (TSID, start_time, end_time, day) VALUES (?, ?, ?, ?)", (timeID, start, end, day)) # creates a new time slot if necessary
                connection.commit()
            if session['user_type'] == 'gradSec':
                cur.execute("UPDATE grad_secretary SET OH_time = ? WHERE GID = ?", (timeID, session['user']))
            else: 
                cur.execute("UPDATE instructor SET OH_time = ? WHERE IID = ?", (timeID, session['user']))
            
            # Make sure address changes on page. - Laiba
            cur.execute("SELECT * FROM users WHERE UID = ?", (session['user'],)) # finds all standard data on the user
            data = cur.fetchone()
            cur.execute("SELECT * FROM grad_secretary JOIN time_slot ON grad_secretary.OH_time = time_slot.TSID WHERE GID = ?", (session['user'],))
            typeSpecific = cur.fetchone()

            connection.commit()
            connection.close()
            return render_template('account.html', userData = data, userType = session['user_type'], typeSpecific = typeSpecific, passUpdate = False, error = False, addressUpdate = False, ohUpdate = True, type = userType, rating = rating)

    connection.commit()
    connection.close()
    return render_template('account.html', userData = data, userType = session['user_type'], typeSpecific = typeSpecific, passUpdate = False, error = False, addressUpdate = False, ohUpdate = False, type = userType, rating = rating)

@app.route('/courseCatalogue', methods = ["GET", "POST"])
def courseCatalogue(): # Editted together
    # if user cam here from course registration without pressing "return to account" button, pop all those variables to reset them. - Laiba
    if 'registration_can_search' in session: 
        session.pop('registration_can_search')
    if 'registration_search_general' in session:
        session.pop('registration_search_general')
    if 'registration_search_capacity' in session:
        session.pop('registration_search_capacity')
    if 'registration_search_enrollment' in session:
        session.pop('registration_search_enrollment')
    if 'registration_search_professors' in session:
        session.pop('registration_search_professors')
    if 'registration_search_CRN' in session:
        session.pop('registration_search_CRN')
    if 'registration_add_CRN_list' in session:
        session.pop('registration_add_CRN_list')
    if 'registration_add_class_data' in session:
        session.pop('registration_add_class_data')
    if 'registration_drop_CRN_list' in session:
        session.pop('registration_drop_CRN_list')
    if 'registration_drop_class_data' in session:
        session.pop('registration_drop_class_data')

    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    # get courses, credits, section info
    cur.execute("SELECT course.dept, course.cnum, course.title, course.credit_hours, course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) JOIN sec_time ON course_section.CRN = sec_time.CRN JOIN time_slot ON sec_time.TSID = time_slot.TSID JOIN sec_room ON course_section.CRN = sec_room.CRN WHERE course_section.semester = ? AND course_section.year = ? ORDER BY course_section.dept, course_section.cnum", ("Fall", "2025"))
    allClasses = cur.fetchall()

    # get professors
    cur.execute("SELECT course_section.dept, course_section.cnum, course_section.CRN, users.first_name, users.last_name, users.UID FROM course_section JOIN teaches ON course_section.CRN = teaches.CRN JOIN users ON teaches.UID = users.UID WHERE course_section.semester = ? AND course_section.year = ? AND users.user_type = ? ORDER BY course_section.dept, course_section.cnum", ("Fall", "2025", "instructor"))
    allProfessors = cur.fetchall()
    
    # get the average rating for each professor. 
    cur.execute("SELECT UID, AVG(rating) AS Rating FROM ratings GROUP BY UID")
    rateRow = cur.fetchall()
    # rating = 0
    rateDict = {}
    if (rateRow != None and len(rateRow) != 0):
        for rate in rateRow: # gives rating to professors who have ratings. Those without ratings do not appear in the list. 
            rateDict[rate['UID']] = round(rate['Rating'], 2) # use UID to give rating (UID maps to rating)
    

    # get prereqs
    cur.execute("SELECT prerequisites.cdept, prerequisites.cnum, prerequisites.pdept, prerequisites.pnum FROM prerequisites ORDER BY prerequisites.cdept, prerequisites.cnum")
    allPrereqs = cur.fetchall()

    connection.commit()
    connection.close()
    
    return render_template('courseCatalogue.html', classList = allClasses, professorList = allProfessors, prereqList = allPrereqs, profRatings = rateDict)

@app.route('/transcriptSearch', methods = ["GET", "POST"])
def transcriptSearch(): 
    if ('user' not in session): # redirects if necessary
        return redirect('/')
    elif (session['user_type'] == 'student'):
        return redirect('/transcript')
    elif (session['user_type'] == 'instructor'): # less conusing (and more effiecient) than checking not admin and not gradSec. 
        return redirect('/account')
    
    # if user cam here from course registration without pressing "return to account" button, pop all those variables to reset them. - Laiba
    if 'registration_can_search' in session: 
        session.pop('registration_can_search')
    if 'registration_search_general' in session:
        session.pop('registration_search_general')
    if 'registration_search_capacity' in session:
        session.pop('registration_search_capacity')
    if 'registration_search_enrollment' in session:
        session.pop('registration_search_enrollment')
    if 'registration_search_professors' in session:
        session.pop('registration_search_professors')
    if 'registration_search_CRN' in session:
        session.pop('registration_search_CRN')
    if 'registration_add_CRN_list' in session:
        session.pop('registration_add_CRN_list')
    if 'registration_add_class_data' in session:
        session.pop('registration_add_class_data')
    if 'registration_drop_CRN_list' in session:
        session.pop('registration_drop_CRN_list')
    if 'registration_drop_class_data' in session:
        session.pop('registration_drop_class_data')
    
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    
    if (request.method == "POST"):
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        sID = request.form.get('id')
        dept = request.form.get('dept')
        program = request.form.get('program')
        year = request.form.get('gradYear')
        
        cur.execute("SELECT * FROM users JOIN grad_student ON users.UID = grad_student.SID WHERE (UPPER(first_name) LIKE ? AND UPPER(last_name) LIKE ?) OR UID = ? OR UPPER(department) LIKE ? OR UPPER(degree_program) LIKE ? OR grad_year = ?", (fname, lname, sID, dept, program, year))
        students = cur.fetchall()

        if (students == None or len(students) == 0):
            connection.commit()
            connection.close()
            return render_template('transcriptSearch.html', error = True, result = False, students = None)
        elif (len(students) == 1):
            connection.commit()
            connection.close()
            return redirect(f"/transcriptSearchResult/{students[0]['UID']}")
        else: 
            connection.commit()
            connection.close()
            return render_template('transcriptSearch.html', error = False, result = True, students = students)
        
    connection.commit()
    connection.close()
    return render_template('transcriptSearch.html', error = False, result = False, students = None)
            
@app.route('/transcriptSearchResult/<string:UID>')        
def transcriptSearchResult(UID): # for admin and grad secs to view searched transcripts
    if ('user' not in session):
        return redirect('/')
    elif (session['user_type'] == 'instructor'):
        return redirect('/account') # doesn't allow instructors to view transcripts
    elif (session['user_type'] == 'student'):
        return redirect('/transcript')
    
    # if user cam here from course registration without pressing "return to account" button, pop all those variables to reset them. - Laiba
    if 'registration_can_search' in session: 
        session.pop('registration_can_search')
    if 'registration_search_general' in session:
        session.pop('registration_search_general')
    if 'registration_search_capacity' in session:
        session.pop('registration_search_capacity')
    if 'registration_search_enrollment' in session:
        session.pop('registration_search_enrollment')
    if 'registration_search_professors' in session:
        session.pop('registration_search_professors')
    if 'registration_search_CRN' in session:
        session.pop('registration_search_CRN')
    if 'registration_add_CRN_list' in session:
        session.pop('registration_add_CRN_list')
    if 'registration_add_class_data' in session:
        session.pop('registration_add_class_data')
    if 'registration_drop_CRN_list' in session:
        session.pop('registration_drop_CRN_list')
    if 'registration_drop_class_data' in session:
        session.pop('registration_drop_class_data')
    
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    
    # gathers class information
    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, course_section.dept, course_section.cnum, course_section.semester, course_section.year, course.title, course.credit_hours, profs.first_name, profs.last_name FROM takes JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches ON course_section.CRN = teaches.CRN JOIN users AS profs ON teaches.UID = profs.UID WHERE takes.SID = ? AND profs.user_type = 'instructor'", (UID,))
    classes = cur.fetchall()

    if classes == None: # user does not exist. 
        connection.commit()
        connection.close()
        return render_template('transcriptSearch.html', error = True, result = False, students = None)
    
    current = []
    past = []
    complete = 0
    inprogress = 0
    gradeCalc = 0
    
    for course in classes: 
        if (course['grade'] == 'IP'):
            current.append(course)
            inprogress += course['credit_hours']
        else:
            past.append(course)
            complete += course['credit_hours']
            gradeWeight = 0
            if (course['grade'] == 'A'):
                gradeWeight = 4
            elif (course['grade'] == 'A-'):
                gradeWeight = 3.7
            elif (course['grade'] == 'B+'):
                gradeWeight = 3.3
            elif (course['grade'] == 'B'):
                gradeWeight = 3
            elif (course['grade'] == 'B-'):
                gradeWeight = 2.7
            elif (course['grade'] == 'C+'):
                gradeWeight = 2.3
            elif (course['grade'] == 'C'):
                gradeWeight = 2
            else:
                gradeWeight = 0
            gradeCalc += (course['credit_hours'] * gradeWeight) 
            
    # gathers user information
    cur.execute("SELECT * FROM users WHERE UID = ?", (UID,))
    userData = cur.fetchone()
    
    # gathers student information
    cur.execute("SELECT * FROM grad_student WHERE SID = ?", (UID,))
    studentData = cur.fetchone()
    
    # finalizing gpa calculation
    gpa = 0
    if (len(past) > 0):
        gpa = gradeCalc / (complete)
        gpa = round(gpa, 2)
            
    connection.commit()
    connection.close()
    return render_template('transcriptSearchResult.html', current = current, past = past, gpa = gpa, completeCredits = complete, inprogressCredits = inprogress, userData = userData, studentData = studentData)    
    
@app.route('/transcript', methods = ["GET", "POST"])
def transcript(): # for students to view their own transcripts
    if ('user' not in session):
        return redirect('/')
    elif (session['user_type'] == 'instructor'):
        return redirect('/account') # doesn't allow instructors or grad secs to view full transcripts
    elif (session['user_type'] == 'admin' or session['user_type'] == 'gradSec'):
        return redirect('/transcriptSearch') # redirect to search page
    
    # if user cam here from course registration without pressing "return to account" button, pop all those variables to reset them. - Laiba
    if 'registration_can_search' in session: 
        session.pop('registration_can_search')
    if 'registration_search_general' in session:
        session.pop('registration_search_general')
    if 'registration_search_capacity' in session:
        session.pop('registration_search_capacity')
    if 'registration_search_enrollment' in session:
        session.pop('registration_search_enrollment')
    if 'registration_search_professors' in session:
        session.pop('registration_search_professors')
    if 'registration_search_CRN' in session:
        session.pop('registration_search_CRN')
    if 'registration_add_CRN_list' in session:
        session.pop('registration_add_CRN_list')
    if 'registration_add_class_data' in session:
        session.pop('registration_add_class_data')
    if 'registration_drop_CRN_list' in session:
        session.pop('registration_drop_CRN_list')
    if 'registration_drop_class_data' in session:
        session.pop('registration_drop_class_data')
    
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    
    submit = False
    submitError = False
    if (request.method == "POST"):
        faculty = request.form.get('prof') 
        """ # removing rating
        # allows for the form to not send anything back
        # since it's not guaranteed for prof to be filled out, request.form would have an error if trying to rate a sec
        if (faculty == None or len(faculty) == 0):
            faculty = request.form['gradSec']
        """
        rate = request.form['rating']
        
        # extra check to make sure that the rating is allowed
        cur.execute("SELECT rating FROM ratings WHERE UID = ? AND SID = ?", (faculty, session['user']))
        existingRating = cur.fetchall()
        if (existingRating == None or len(existingRating) == 0):
            cur.execute("INSERT INTO ratings (UID, SID, rating) VALUES (?, ?, ?)", (faculty, session['user'], rate))
            connection.commit()
            submit = True
    
    # gathers class information
    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, course_section.dept, course_section.cnum, course_section.CRN, course_section.semester, course_section.year, course.title, course.credit_hours, profs.UID AS profID, profs.first_name AS profFirst, profs.last_name AS profLast FROM takes JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches AS instructors ON course_section.CRN = instructors.CRN JOIN users AS profs ON (instructors.UID = profs.UID AND profs.user_type = 'instructor') WHERE takes.SID = ?", (session['user'],))
    classes = cur.fetchall()
    
    current = []
    past = []
    profRatings = []
    complete = 0
    inprogress = 0
    gradeCalc = 0 
    
    for course in classes:
        # determines what faculty a student can rate
        if (course['profID'] not in profRatings):
            cur.execute("SELECT * FROM ratings WHERE SID = ? AND UID = ?", (session['user'], course['profID']))
            ratingResults = cur.fetchall()
            if (ratingResults == None or len(ratingResults) == 0):
                profRatings.append((course['profID'], course['profFirst'], course['profLast']))
        """ # removing sec rating
        if (len(course['secID']) > 0 and course['secID'] not in secRatings):
            cur.execute("SELECT rating FROM ratings WHERE SID = ? AND UID = ?", (session['user'], course['secID']))
            ratingResults = cur.fetchall()
            if (ratingResults == None or len(ratingResults) == 0):
                secRatings.append((course['secID'], course['secFirst'], course['secLast']))
        """
        
        if (course['grade'] == 'IP'):
            current.append(course)
            inprogress += course['credit_hours']
        else:
            past.append(course)
            complete += course['credit_hours']
            gradeWeight = 0
            if (course['grade'] == 'A'):
                gradeWeight = 4
            elif (course['grade'] == 'A-'):
                gradeWeight = 3.7
            elif (course['grade'] == 'B+'):
                gradeWeight = 3.3
            elif (course['grade'] == 'B'):
                gradeWeight = 3
            elif (course['grade'] == 'B-'):
                gradeWeight = 2.7
            elif (course['grade'] == 'C+'):
                gradeWeight = 2.3
            elif (course['grade'] == 'C'):
                gradeWeight = 2
            else:
                gradeWeight = 0
            gradeCalc += (course['credit_hours'] * gradeWeight) 
            
    # gathers user information
    cur.execute("SELECT * FROM users WHERE UID = ?", (session['user'],))
    userData = cur.fetchone()
    
    # gathers student information
    cur.execute("SELECT * FROM grad_student WHERE SID = ?", (session['user'],))
    studentData = cur.fetchone()
    
    # finalizing gpa calculation
    gpa = 0
    if (len(past) > 0):
        gpa = gradeCalc / (complete)
        gpa = round(gpa, 2)
            
    connection.commit()
    connection.close()
    return render_template('transcript.html', current = current, past = past, gpa = gpa, completeCredits = complete, inprogressCredits = inprogress, userData = userData, studentData = studentData, rateSubmit = submit, profRatings = profRatings)    

@app.route('/courseRegistration', methods = ["GET", "POST"])
def courseRegistration(): #written by Kate

    # if the user is not logged in, redirect to login
    if ('user' not in session):
        return redirect('/')
    # if user is not a student, redirect to account
    if (session['user_type'] != 'student'):
        return redirect('/account')
    
    # set default search check to no search and initialize session variable
    canSearch = "No Search"
    if (session.get('registration_can_search') is None):
        session['registration_can_search'] = ""

    # error that happens when user tries to add the same class multiple times
    # associated with add button
    alreadyAddedError = "False"

    # error that happens when user has not met all the prereqs for a class they are trying to add
    # associated with add button
    prereqError = "False"

    # error that happens when the user tries to add a class that violates time constraint
    # associated with add button
    timeConstraintError = "False"

    # error that happens when user tries to drop the same class multiple times
    # associated with drop button
    alreadyDroppedError = "False"

    # error that happens when the user tries to drop a class that had not been added or they have not registered for
    # associated with drop button
    notAddedError = "False"

    # error that happens when user tries to submit changes and a class is already full
    # associated with submit changes button
    submitCapacityError = "False"

    # initialize DB query result variables
    DBSearchResult = []
    DBCapacityResult = []
    DBEnrollmentResult = []
    DBProfessorResult = []
    classToAddList = []
    classToDropList = []

    # initialize lists for use during add process
    if ('registration_add_CRN_list' not in session):
        session['registration_add_CRN_list'] = []
    if ('registration_add_class_data' not in session):
        session['registration_add_class_data'] = []

    # initialize session variables for use during drop process
    if ('registration_drop_CRN_list' not in session):
        session['registration_drop_CRN_list'] = []
    if ('registration_drop_class_data' not in session):
        session['registration_drop_class_data'] = []
    
    # open connection to DB
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()

    # get user's current class schedule
    cur.execute("SELECT course.dept, course.cnum, course.title, course.credit_hours, course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) JOIN sec_time ON course_section.CRN = sec_time.CRN JOIN time_slot ON sec_time.TSID = time_slot.TSID JOIN sec_room ON course_section.CRN = sec_room.CRN JOIN takes ON course_section.CRN = takes.CRN WHERE course_section.semester = ? AND course_section.year = ? AND takes.SID = ?", ("Fall", "2025", session['user']))
    DBCurrentSchedule = cur.fetchall()

    # assign session variable to pre-registration class schedule
    if ('registration_current_schedule' not in session):
        session['registration_current_schedule'] = []
        for registeredClass in DBCurrentSchedule:
            session['registration_current_schedule'].append([registeredClass['CRN'], registeredClass['dept'], registeredClass['cnum'], registeredClass['title'], registeredClass['sec_num'], registeredClass['credit_hours'], registeredClass['building'], registeredClass['room'], registeredClass['day'], registeredClass['start_time'], registeredClass['end_time']])
            session.modified = True
    # search button functionality
    if (request.method == "POST" and request.form.get('submitSearch')):
        # get search term
        inputtedCRN = request.form['CRN']

        # get general class data matching CRN, calculate current enrollment
        cur.execute("SELECT course.dept, course.cnum, course.title, course.credit_hours, course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) JOIN sec_room ON (course_section.CRN = sec_room.CRN) JOIN sec_time ON (course_section.CRN = sec_time.CRN) JOIN time_slot ON (sec_time.TSID = time_slot.TSID) WHERE course_section.semester = ? AND course_section.year = ? AND course_section.CRN = ?", ("Fall", "2025", inputtedCRN))
        DBSearchResult = cur.fetchall()

        # get room capacities
        cur.execute("SELECT classroom.capacity FROM classroom JOIN sec_room ON (classroom.building = sec_room.building AND classroom.room = sec_room.room) WHERE sec_room.CRN = ?", (inputtedCRN,))
        DBCapacityResult = cur.fetchall()

        # get enrollment
        cur.execute("SELECT COUNT(takes.SID) AS enrolled FROM takes WHERE takes.CRN = ?", (inputtedCRN,))
        DBEnrollmentResult = cur.fetchall()

        # get professors
        cur.execute("SELECT users.first_name, users.last_name FROM course_section JOIN teaches ON course_section.CRN = teaches.CRN JOIN users ON teaches.UID = users.UID WHERE course_section.semester = ? AND course_section.year = ? AND users.user_type = ? AND course_section.CRN = ?", ("Fall", "2025", "instructor", inputtedCRN))
        DBProfessorResult = cur.fetchall()

        # check for invalid CRN search input
        if (DBSearchResult == [] or DBCapacityResult == [] or DBEnrollmentResult == [] or DBProfessorResult == []):
            # set search check to false to display error message
            session['registration_can_search'] = "False"
            connection.commit()
            connection.close()
            # return to /courseRegistration with error
            return render_template('courseRegistration.html', userSchedule = DBCurrentSchedule, validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)
        
        # set search check to true, search result can now be displayed
        session['registration_can_search'] = "True"

        # save search results in session variables
        if ('registration_search_general' not in session):
            session['registration_search_general'] = []
        for searchResult in DBSearchResult:
                session['registration_search_general'] = [searchResult['CRN'], searchResult['dept'], searchResult['cnum'], searchResult['title'], searchResult['sec_num'], searchResult['credit_hours'], searchResult['building'], searchResult['room'], searchResult['day'], searchResult['start_time'], searchResult['end_time']]

        if ('registration_search_capacity' not in session):
            session['registration_search_capacity'] = []
        for classCapacityResult in DBCapacityResult:
            session['registration_search_capacity'] = [classCapacityResult['capacity']]

        if ('registration_search_enrollment' not in session):
            session['registration_search_enrollment'] = []
        for classEnrollmentResult in DBEnrollmentResult:
            session['registration_search_enrollment'] = [classEnrollmentResult['enrolled']]

        session['registration_search_professors'] = []
        for classProfessorResult in DBProfessorResult:
            session['registration_search_professors'].append([classProfessorResult['first_name'], classProfessorResult['last_name']])
            session.modified = True

        # save search CRN for potential add/drop, for use later
        if ('registration_search_CRN' not in session):
            session['registration_search_CRN'] = []
        for searchResult in DBSearchResult:
            session['registration_search_CRN'] = [(searchResult['CRN'])]

        # commit and close for valid search input
        connection.commit()
        connection.close()
        # return to /courseRegistration with valid search result
        return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)
    
    # add button functionality
    if (request.method == "POST" and request.form.get('addClass')):
        # get CRN that was searched and selected for add
        addCRN = session['registration_search_CRN'][0]
        
        # check if selected class had already been added
        for addedCRN in session['registration_add_CRN_list']:
            if (addCRN == addedCRN):
                alreadyAddedError = "True"
                # stop if the selected class has already been added
                return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)
        
        # check if selected class is already registered
        for registeredClass in session['registration_current_schedule']:
            if (addCRN == registeredClass[0]):
                alreadyAddedError = "True"
                # stop if the selected class has already been added
                return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)
        
        # check if the prereqs have been met for selected class
        # get past and current classes
        cur.execute("SELECT course_section.dept, course_section.cnum FROM course_section JOIN takes ON course_section.CRN = takes.CRN WHERE takes.SID = ? AND course_section.semester != ? AND course_section.year != ?", (session['user'], "Fall", "2025"))
        takenClasses = cur.fetchall()
        # get prereqs
        cur.execute("SELECT prerequisites.pdept, prerequisites.pnum FROM prerequisites JOIN course_section ON (prerequisites.cdept = course_section.dept AND prerequisites.cnum = course_section.cnum) WHERE course_section.CRN = ?", (session['registration_search_CRN'][0],))
        prereqs = cur.fetchall()
        # compare past classes against prereqs
        if (prereqs != []):
            prereqError = "True"
            for prereq in prereqs:
                prereqError = "True"
                for takenClass in takenClasses:
                    if (prereq == takenClass):
                        prereqError = "False"
                if prereqError == "True":
                    # if prereqs have not been met, return to /courseRegistration with error
                    return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)

        # check if selected class violates time constraint
        # get start and end times for selected class
        addDay = session['registration_search_general'][8]
        addStartTimeString = session['registration_search_general'][9]
        addEndTimeString = session['registration_search_general'][10]
        # set up string formatting for use in conversion of data type
        timeStringFormat = "%H:%M:%S"

        # convert String representations of times to Datetime representations of times
        # variables of type Datetime can be added, substracted, and compared, which we need to check for time conflicts
        # return value of comparison will be type timedelta
        addStartTimeDatetime = datetime.strptime(addStartTimeString, timeStringFormat)
        addEndTimeDatetime = datetime.strptime(addEndTimeString, timeStringFormat)
        # set up required time gap between classes as timedelta variable for use in comparisons
        timeConstraintTimedelta = timedelta(minutes=30)

        # check for time constraints with classes that have been registered
        for registeredClass in session['registration_current_schedule']:
            # check if classes happen on the same day
            registeredClassDay = registeredClass[8]
            if (addDay == registeredClassDay):
                # get time data for class in current schedule
                registeredClassStartTimeString = registeredClass[9]
                registeredClassEndTimeString = registeredClass[10]
                registeredClassStartTimeDatetime = datetime.strptime(registeredClassStartTimeString, timeStringFormat)
                registeredClassEndTimeDatetime = datetime.strptime(registeredClassEndTimeString, timeStringFormat)

                # find later class
                if (addStartTimeDatetime < registeredClassStartTimeDatetime):
                    timeDifferenceTimedelta = registeredClassStartTimeDatetime - addEndTimeDatetime
                    # check if time constraint is violated
                    if (timeDifferenceTimedelta < timeConstraintTimedelta):
                        timeConstraintError = "True"
                        # return to /courseRegistration with error
                        return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'],  timeConstraint = timeConstraintError)
                # find later class
                elif (addStartTimeDatetime > registeredClassStartTimeDatetime):
                    timeDifferenceTimedelta = addStartTimeDatetime - registeredClassEndTimeDatetime
                    # check if time constraint is violated
                    if (timeDifferenceTimedelta < timeConstraintTimedelta):
                        timeConstraintError = "True"
                        # return to /courseRegistration with error
                        return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'],  timeConstraint = timeConstraintError)
                # classes start at the same time, violates constraint
                else:
                    timeConstraintError = "True"
                    # return to /courseRegistration with error
                    return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], timeConstraint = timeConstraintError)

        # check for time constaints with classes that have been added
        for alreadyAddedClass in session['registration_add_class_data']:
            # check if classes happen on the same day
            alreadyAddedClassDay = alreadyAddedClass[8]
            if (addDay == alreadyAddedClassDay):
                # get time data for class in pending add list
                alreadyAddedClassStartTimeString = alreadyAddedClass[9]
                alreadyAddedClassEndTimeString = alreadyAddedClass[10]
                alreadyAddedClassStartTimeDatetime = datetime.strptime(alreadyAddedClassStartTimeString, timeStringFormat)
                alreadyAddedClassEndTimeDatetime = datetime.strptime(alreadyAddedClassEndTimeString, timeStringFormat)

                # find later class
                if (addStartTimeDatetime < alreadyAddedClassStartTimeDatetime):
                    timeDifferenceTimedelta = alreadyAddedClassStartTimeDatetime - addEndTimeDatetime
                    # check if time constraint is violated
                    if (timeDifferenceTimedelta < timeConstraintTimedelta):
                        timeConstraintError = "True"
                        # return to /courseRegistration with error
                        return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'],  timeConstraint = timeConstraintError)
                # find later class
                elif (addStartTimeDatetime > alreadyAddedClassStartTimeDatetime):
                    timeDifferenceTimedelta = addStartTimeDatetime - alreadyAddedClassEndTimeDatetime
                    # check if time constraint is violated
                    if (timeDifferenceTimedelta < timeConstraintTimedelta):
                        timeConstraintError = "True"
                        # return to /courseRegistration with error
                        return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'],  timeConstraint = timeConstraintError)
                # classes start at the same time, violates constraint
                else:
                    timeConstraintError = "True"
                    # return to /courseRegistration with error
                    return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], timeConstraint = timeConstraintError)

        # proceed if the class is new, prereqs have been met, and no time constraint violation
        # add added class to list of CRNs
        session['registration_add_CRN_list'].append(addCRN)
        session.modified = True

        # get info for added class
        cur.execute("SELECT course.dept, course.cnum, course.title, course.credit_hours, course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) JOIN sec_time ON course_section.CRN = sec_time.CRN JOIN time_slot ON sec_time.TSID = time_slot.TSID JOIN sec_room ON course_section.CRN = sec_room.CRN WHERE course_section.CRN = ?", (addCRN,))
        classToAdd = cur.fetchall()

        # add class data to running list for this registration session
        for classToAddData in classToAdd:
            session['registration_add_class_data'].append([classToAddData['CRN'], classToAddData['dept'], classToAddData['cnum'], classToAddData['title'], classToAddData['sec_num'], classToAddData['credit_hours'], classToAddData['building'], classToAddData['room'], classToAddData['day'], classToAddData['start_time'], classToAddData['end_time']])
            session.modified = True

        connection.commit()
        connection.close()
        # return to /courseRegistration with updated data
        return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)

    # drop button functionality
    if (request.method == "POST" and request.form.get('dropClass')):
        # get CRN that was searched and selected for drop
        dropCRN = session['registration_search_CRN'][0]
        
        # check if selected class had already been dropped
        for droppedCRN in session['registration_drop_CRN_list']:
            if (dropCRN == droppedCRN):
                alreadyDroppedError = "True"
                # stop if the selected class has already been dropped, return to /courseRegistration with error
                return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError, alreadyDropped = alreadyDroppedError)
        
        # check if selected class is in current schedule
        notAddedError = "True"
        for registeredClass in session['registration_current_schedule']:
            if (dropCRN == registeredClass[0]):
                notAddedError = "False"
        if (notAddedError == "True"):
            # if class to be dropped is not found in current schedule, check if selected class is pending add
            # if the class has been selected for add, "drop" deletes it from add list
            for addedCRN in session['registration_add_CRN_list']:
                if (dropCRN == addedCRN):
                    notAddedError = "False"
                    # if class has been marked for add, remove class from CRN list
                    session['registration_add_CRN_list'].remove(dropCRN)

                    # if class has been marked for add, remove class from data list
                    cur.execute("SELECT course.dept, course.cnum, course.title, course.credit_hours, course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) JOIN sec_time ON course_section.CRN = sec_time.CRN JOIN time_slot ON sec_time.TSID = time_slot.TSID JOIN sec_room ON course_section.CRN = sec_room.CRN WHERE course_section.CRN = ?", (dropCRN,))
                    classToRemove = cur.fetchall()
                    for classToRemoveData in classToRemove:
                        session['registration_add_class_data'].remove([classToRemoveData['CRN'], classToRemoveData['dept'], classToRemoveData['cnum'], classToRemoveData['title'], classToRemoveData['sec_num'], classToRemoveData['credit_hours'], classToRemoveData['building'], classToRemoveData['room'], classToRemoveData['day'], classToRemoveData['start_time'], classToRemoveData['end_time']])
                        session.modified = True
                    
                    connection.commit()
                    connection.close()
                    # return to /courseRegistration with updated add list
                    return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError, alreadyDropped = alreadyDroppedError)

            # stop if the selected class is not in current schedule and return to /courseRegistration with error
            return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError, alreadyDropped = alreadyDroppedError)
        
        # proceed if the class is not already dropped, is currently registered, and is not pending add
        # add dropped class to list of CRNs
        session['registration_drop_CRN_list'].append(dropCRN)
        session.modified = True

        # get data for dropped class
        cur.execute("SELECT course.dept, course.cnum, course.title, course.credit_hours, course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) JOIN sec_time ON course_section.CRN = sec_time.CRN JOIN time_slot ON sec_time.TSID = time_slot.TSID JOIN sec_room ON course_section.CRN = sec_room.CRN WHERE course_section.CRN = ?", (dropCRN,))
        classToDrop = cur.fetchall()

        # add class data to drop list
        for classToDropData in classToDrop:
            session['registration_drop_class_data'].append([classToDropData['CRN'], classToDropData['dept'], classToDropData['cnum'], classToDropData['title'], classToDropData['sec_num'], classToDropData['credit_hours'], classToDropData['building'], classToDropData['room'], classToDropData['day'], classToDropData['start_time'], classToDropData['end_time']])
            session.modified = True

        connection.commit()
        connection.close()
        # return to /courseRegistration with updated data
        return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)
    
    # submit button functionality
    if (request.method == "POST" and request.form.get('submitChanges')):

        # update DB with added classes
        for addedCRN in session['registration_add_CRN_list']:
            # get capacity
            cur.execute("SELECT classroom.capacity FROM sec_room JOIN classroom ON (sec_room.building = classroom.building AND sec_room.room = classroom.room) WHERE sec_room.CRN = ?", (addedCRN,))
            addCapacityDB = cur.fetchone()
            # get capacity as int for comparison with enrollment
            addCapacityInt = addCapacityDB['capacity']

            # get enrollment
            cur.execute("SELECT COUNT(takes.SID) AS enrolled FROM takes WHERE takes.CRN = ?", (addedCRN,))
            addEnrollmentDB = cur.fetchone()
            # get enrollment as int for comparison with capacity
            addEnrollmentInt = addEnrollmentDB['enrolled']

            # check capacity against enrollment
            if (addEnrollmentInt >= addCapacityInt):
                submitCapacityError = "True"
                # return to /courseRegistration with error
                return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError, submitCapacity = submitCapacityError, submitCapacityCRN = addedCRN)

            # if no capacity error, proceed with DB insertion for the user
            cur.execute("INSERT INTO takes (SID, CRN, grade) VALUES (?, ?, ?)", (session['user'], addedCRN, "IP"))
            connection.commit()

            # update current schedule session variable
            cur.execute("SELECT course.dept, course.cnum, course.title, course.credit_hours, course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) JOIN sec_time ON course_section.CRN = sec_time.CRN JOIN time_slot ON sec_time.TSID = time_slot.TSID JOIN sec_room ON course_section.CRN = sec_room.CRN WHERE course_section.CRN = ?", (addedCRN,))
            addData = cur.fetchall()
            for classToAddData in addData:
                session['registration_current_schedule'].append([classToAddData['CRN'], classToAddData['dept'], classToAddData['cnum'], classToAddData['title'], classToAddData['sec_num'], classToAddData['credit_hours'], classToAddData['building'], classToAddData['room'], classToAddData['day'], classToAddData['start_time'], classToAddData['end_time']])
                session.modified = True

        # update DB with dropped classes
        for droppedCRN in session['registration_drop_CRN_list']:
            cur.execute("DELETE FROM takes WHERE SID = ? AND CRN = ?", (session['user'], droppedCRN))
            connection.commit()

            # update current schedule session variable
            cur.execute("SELECT course.dept, course.cnum, course.title, course.credit_hours, course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) JOIN sec_time ON course_section.CRN = sec_time.CRN JOIN time_slot ON sec_time.TSID = time_slot.TSID JOIN sec_room ON course_section.CRN = sec_room.CRN WHERE course_section.CRN = ?", (droppedCRN,))
            dropData = cur.fetchall()
            for classToDropData in dropData:
                session['registration_current_schedule'].remove([classToDropData['CRN'], classToDropData['dept'], classToDropData['cnum'], classToDropData['title'], classToDropData['sec_num'], classToDropData['credit_hours'], classToDropData['building'], classToDropData['room'], classToDropData['day'], classToDropData['start_time'], classToDropData['end_time']])
                session.modified = True

        # wipe add and drop session variables
        session['registration_add_CRN_list'] = []
        session['registration_add_class_data'] = []
        session['registration_drop_CRN_list'] = []
        session['registration_drop_class_data'] = []

        connection.commit()
        connection.close()
        # return to /courseRegistration with newly registered courses, updates class capacities, updated current schedule
        return render_template('courseRegistration.html', searchResults = session['registration_search_general'], professorResults = session['registration_search_professors'], capacityResults = session['registration_search_capacity'], enrollmentResults = session['registration_search_enrollment'], userSchedule = session['registration_current_schedule'], validSearch = session['registration_can_search'], addClasses = session['registration_add_class_data'], dropClasses = session['registration_drop_class_data'], alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)

    # return to account button functionality
    if (request.method == "POST" and request.form.get('returnToAccount')):
        # reset session variables when registration page is left
        # use this button for repeated testing
        session['registration_can_search'] = ""
        session['registration_search_general'] = []
        session['registration_search_capacity'] = []
        session['registration_search_enrollment'] = []
        session['registration_search_professors'] = []
        session['registration_search_CRN'] = []
        session['registration_add_CRN_list'] = []
        session['registration_add_class_data'] = []
        session['registration_drop_CRN_list'] = []
        session['registration_drop_class_data'] = []

        # return to account page
        return redirect('/account')

    # no buttons pressed, default layout for registration page
    return render_template('courseRegistration.html', searchResults = DBSearchResult, professorResults = DBProfessorResult, capacityResults = DBCapacityResult, enrollmentResults = DBEnrollmentResult, userSchedule = session['registration_current_schedule'], validSearch = canSearch, addClasses = classToAddList, dropClasses = classToDropList, alreadyAdded = alreadyAddedError, prereqNotMet = prereqError, notAdded = notAddedError)

@app.route('/gradeInput', methods = ["GET", "POST"])
def gradeInput():
    if ('user' not in session):
        return redirect('/')
    
    if (session['user_type'] == 'student' or session['user_type'] == 'admin'):
        return redirect('/account')
    
    # if user cam here from course registration without pressing "return to account" button, pop all those variables to reset them. - Laiba
    if 'registration_can_search' in session: 
        session.pop('registration_can_search')
    if 'registration_search_general' in session:
        session.pop('registration_search_general')
    if 'registration_search_capacity' in session:
        session.pop('registration_search_capacity')
    if 'registration_search_enrollment' in session:
        session.pop('registration_search_enrollment')
    if 'registration_search_professors' in session:
        session.pop('registration_search_professors')
    if 'registration_search_CRN' in session:
        session.pop('registration_search_CRN')
    if 'registration_add_CRN_list' in session:
        session.pop('registration_add_CRN_list')
    if 'registration_add_class_data' in session:
        session.pop('registration_add_class_data')
    if 'registration_drop_CRN_list' in session:
        session.pop('registration_drop_CRN_list')
    if 'registration_drop_class_data' in session:
        session.pop('registration_drop_class_data')
    
    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    
    courses = []
    if (session['user_type'] == "instructor"): # select only students with grade IP
        cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches ON course_section.CRN = teaches.CRN WHERE teaches.UID = ?", (session['user'],))
        courses = cur.fetchall()
    else:
        cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum)")
        courses = cur.fetchall()
        
    results = None
    if (request.method == "POST"):
        formType = request.form.get("form_type") 
        
        if ("SubmitSearch" in request.form):
            searchName = request.form.get("name") # using get since only one or the other is required
            searchCourse = request.form.get("course")
            searchCRN = request.form.get("crn")
            
            if (searchName != None and len(searchName) > 0 and searchName.find(" ") == -1): # checks if only one name was given (ex. just a last name)
                if (session['user_type'] == "instructor"):
                    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches ON course_section.CRN = teaches.CRN WHERE teaches.UID = ? AND (UPPER(student.first_name) LIKE ? OR UPPER(student.last_name) LIKE ?) ORDER BY student.last_name, student.first_name", (session['user'], str(searchName), str(searchName)))
                    results = cur.fetchall()
                else:
                    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) WHERE (UPPER(student.first_name) LIKE ? OR UPPER(student.last_name) LIKE ?) ORDER BY student.last_name, student.first_name", (str(searchName), str(searchName)))
                    results = cur.fetchall()
            elif (searchName != None and len(searchName) > 0 and searchName.find(" ") > -1): # checks for if multiple names are given
                split = searchName.split(" ")
                if (len(split) != 2):
                    return render_template('gradeInput.html', courses = courses, submitted = False, nameSearchError = True, searchResults = results, userType = session['user_type'])
                first = split[0]
                last = split[1]
                if (session['user_type'] == "instructor"):
                    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches ON course_section.CRN = teaches.CRN WHERE teaches.UID = ? AND UPPER(student.first_name) LIKE ? AND UPPER(student.last_name) LIKE ? ORDER BY student.last_name, student.first_name", (session['user'], first, last))
                    results = cur.fetchall()
                else:
                    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) WHERE (UPPER(student.first_name) LIKE ? AND UPPER(student.last_name) LIKE ?) ORDER BY student.last_name, student.first_name", (first, last))
                    results = cur.fetchall()
            elif (searchCourse != None and len(searchCourse) > 0):
                if (session['user_type'] == "instructor"):
                    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches ON course_section.CRN = teaches.CRN WHERE teaches.UID = ? AND course_section.cnum = ? ORDER BY student.last_name, student.first_name", (session['user'], int(searchCourse)))
                    results = cur.fetchall()
                else:
                    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches ON course_section.CRN = teaches.CRN WHERE course_section.cnum = ? ORDER BY student.last_name, student.first_name", (int(searchCourse),))
                    results = cur.fetchall()
            elif (searchCRN != None and len(searchCRN) > 0):
                if (session['user_type'] == "instructor"):
                    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches ON course_section.CRN = teaches.CRN WHERE teaches.UID = ? AND course_section.CRN = ? ORDER BY student.last_name, student.first_name", (session['user'], int(searchCRN)))
                    results = cur.fetchall()
                else:
                    cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) WHERE course_section.CRN = ?", (int(searchCRN),))
                    results = cur.fetchall()
                    
            if (results == None or len(results) == 0):
                connection.commit()
                connection.close()
                return render_template('gradeInput.html', courses = courses, submitted = False, nameSearchError = False, searchResults = results, searchError = True, userType = session['user_type'])
            connection.commit()
            connection.close()
            return render_template('gradeInput.html', courses = courses, submitted = False, nameSearchError = False, searchResults = results, searchError = False, userType = session['user_type'])
        
        if ("SubmitGrades" in request.form):
            gradeByStudent = request.form.to_dict()
            
            for grade in gradeByStudent:
                sid = 0
                crn = 0
                if (gradeByStudent[grade] != "default"):
                    if (grade.startswith("grades[") and grade.endswith("]")):
                        sid = grade[7:15]
                        crn = grade[17:-1]
                    cur.execute("UPDATE takes SET grade = ? WHERE SID = ? AND CRN = ?", (gradeByStudent[grade], sid, crn))
                    connection.commit()
            connection.commit()

            courses = [] 
            if (session['user_type'] == "instructor"): # recollects students with updated grades
                cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) JOIN teaches ON course_section.CRN = teaches.CRN WHERE teaches.UID = ?", (session['user'],))
                courses = cur.fetchall()
            else:
                cur.execute("SELECT takes.SID, takes.CRN, takes.grade, student.first_name, student.last_name, course_section.dept, course_section.cnum, course.title FROM takes JOIN users AS student ON takes.SID = student.UID JOIN course_section ON takes.CRN = course_section.CRN JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum)")
                courses = cur.fetchall()
            
            connection.commit()
            connection.close()         
            return render_template('gradeInput.html', courses = courses, submitted = True, nameSearchError = False, searchResults = results, searchError = False, userType = session['user_type'])
        
    connection.commit()
    connection.close()
    return render_template('gradeInput.html', courses = courses, submitted = False, nameSearchError = False, searchResults = results, searchError = False, userType = session['user_type'])

@app.route('/studentSignUp', methods = ["GET", "POST"])
def studentSignUp():
    if 'user' in session: 
        redirect('/account')

    connection = sqlite3.connect("myDatabase.db")
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()

    if (request.method == "POST"):
        fname = request.form['fname']
        lname = request.form['lname']
        address = request.form['address']
        userType = "student"
        password = request.form['password']
        dept = request.form.get('Department')
        program = request.form.get('program')

        gwid = ""
        
        # randomization of GWID (using increment method will not work bc we have user wih 99999999 and adding 1 will cause overflow, 
        # and even if we ignore that and set to 0, we would still have to increment at least 41 times due to there being at least 41 incremental UID's. 
        # So, this method is more efficient. )
        characters = string.digits # simplified gwid randomization
        gwid = ''.join(random.choices(characters, k = 8))
        
        cur.execute("SELECT COUNT(UID) FROM users WHERE UID = ?", (gwid,))
        row = cur.fetchone()
        if (row == None): # if null returned
            connection.commit()
            connection.close()
            return render_template('studentSignUp.html', error = True, submitted = False, GWID = None)

        # if (and while) the same gwid as an existing one keeps being returned, regenerate the GWID so that a unique one can be generated. 
        while (int(row['COUNT(UID)']) != 0): 
            characters = string.digits # simplified password randomization
            gwid = ''.join(random.choices(characters, k = 8))
            
            cur.execute("SELECT COUNT(UID) FROM users WHERE UID = ?", (gwid,))
            row = cur.fetchall()
            if (row == None): # if null returned. 
                connection.commit()
                connection.close()
                return render_template('studentSignUp.html', error = True, submitted = False, GWID = None)
        
        try: 
            cur.execute("INSERT INTO users (UID, password, first_name, last_name, address, user_type, department) VALUES (?, ?, ?, ?, ?, ?, ?)", (gwid, password, fname, lname, address, userType, dept))
        except:
            connection.commit()
            connection.close()
            return render_template('studentSignUp.html', error = True, submitted = False, GWID = None)
        
        if (program == 'Doctoral' or program == 'PhD'):
            try:
                cur.execute("INSERT INTO grad_student (SID, degree_program, grad_year) VALUES (?, ?, ?)", (gwid, program, (datetime.now().year + 6)))
            except:
                return render_template('studentSignUp.html', submitted = False, error = True, GWID = None)
        elif (program == "Masters"):
            try: 
                cur.execute("INSERT INTO grad_student (SID, degree_program, grad_year) VALUES (?, ?, ?)", (gwid, program, (datetime.now().year + 2)))
            except:
                return render_template('studentSignUp.html', submitted = False, error = True, GWID = None)
        
        connection.commit()
        connection.close()
        return render_template('studentSignUp.html', submitted = True, error = False, GWID = gwid) # reloads page with submission confirmation
    

    connection.commit()
    connection.close()
    return render_template('studentSignUp.html', error = False, submitted = False, GWID = None)


app.run(host='0.0.0.0', port=8080)