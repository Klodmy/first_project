from flask import Flask, flash, redirect, render_template, request, session, current_app, g, make_response, url_for
from functools import wraps
import sqlite3
import datetime
from hashlib import blake2b

app = Flask(__name__)

# set secret key
app.secret_key = b'didama/949621!'

# connect db to the app
def db_conn():
    conn = None
    try:
        conn = sqlite3.connect('happy.db')
    except sqlite3.error as e:
        print(e)
    return conn

def get_data_from_db(activity, user_id):
    # connection to db
    conn = sqlite3.connect('happy.db')
    cur = conn.cursor()

    # get mark, date and activity from activity that = parameter taken by the function
    cur.execute("SELECT mark, date, activity FROM trackers WHERE activity = ? and user_id = ?", [activity, user_id])
    data = cur.fetchall()

    # creating pandas dataframe with 2 cols
    df = pd.DataFrame(data, columns=['mark', 'date', 'activity'])
    conn.close()
    return df

# hash
def password_hash(password):
    e_pass = password.encode(encoding='UTF-8', errors='ignore')
    h = blake2b(key=b'happydiarysecretkey', digest_size=16)
    h.update(e_pass)
    final = h.hexdigest()
    return final


# def login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# error page
@app.route('/error', methods=['GET'])
def error():
    if request.method == 'GET':
        return render_template('error.html')


# cookies
@app.route("/", methods=['GET', 'POST'])
def main_page():
    # cookies
    username = request.cookies.get('username')
    resp = make_response(render_template('error.html'))
    resp.set_cookie('username', 'the username')
    
    return render_template('layout.html')

# login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # forget any session
        session.clear()

        # variables for gethered information
        name = request.form.get('username')
        pw = password_hash(request.form.get('password'))

        # check db for name
        conn = db_conn()
        cur = conn.cursor()
        
        # ask db for usernames
        names = cur.execute('SELECT username FROM users')
        conn.commit()
        
        # flag for login
        log_allow = False


        # check for password and if it matches log the user in
        psw = cur.execute('SELECT hash FROM users WHERE username = ?', [name])
        psw = cur.fetchone()

        if not psw:
            return redirect('/error'), 400

        if psw[0] == pw:
            log_allow = True
        
        # login
        if log_allow == True:
            session['username'] = name
            return redirect ('/diary') 
        
            
        return render_template('login.html', psw=psw, pw=pw)

    else:
        return render_template('login.html')


@app.route("/sign-up", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        # ask for existing usernames
        conn = db_conn()
        cur = conn.cursor()

        all_users = cur.execute('SELECT username FROM users')
        conn.commit()

        # check if name is already taken
        for u in all_users:
            if request.form.get('username') == u[0]:
                return redirect('/error'), 400
        
        # check if password match to confirmation
        if request.form.get('password') != request.form.get('confirmation'):
            return redirect('/error'), 400

        # get current date and time
        reg_date = datetime.datetime.now()
        
        # insert user data into db
        cur.execute('INSERT INTO users (username, hash, date) VALUES (?, ?, ?)', (request.form.get('username'), password_hash(request.form.get('password')), reg_date))
        conn.commit()

        # set session to current user and redirects to main page
        session['username'] = request.form.get('username')

        return render_template('diary.html')

    else:
        return render_template('register.html')

# main page
@app.route("/diary", methods=['GET', 'POST'])
@login_required
def diary():
    if request.method == 'POST':
        # cursor for db
        conn = db_conn()
        cur = conn.cursor()

        # title
        title = request.form.get('note-title')

        # get new note
        post = request.form.get('new-note')

        # get current date and time
        post_date = datetime.datetime.now()
        formated_date = post_date.strftime('%-d %B %Y\n%H:%M %p')
        formated_for_activity = post_date.strftime('%-d %b %Y')

        # get user id
        u_id = cur.execute('SELECT id FROM users WHERE username = (?)', [session['username']])
        u_id = cur.fetchone()

         # get all user's activities
        trackers = cur.execute('SELECT activity FROM activities WHERE user_id = ?', [u_id[0]])
        trackers = cur.fetchall()

        # get post id
        last_id = cur.execute('SELECT id FROM notes ORDER BY id DESC LIMIT 1')
        last_id = cur.fetchone()    
        post_id = int(last_id[0]) + 1

        # check user input for every user activity and insert it to trackers
        for track in trackers:
            mark = request.form.get(track[0])
            cur.execute('INSERT INTO trackers (user_id, post_id, activity, mark, date) VALUES (?, ?, ?, ?, ?)', [u_id[0], post_id, track[0], mark, formated_for_activity])
            conn.commit()

        # insert note to the db
        cur.execute('INSERT INTO notes (user_id, note, date, title, datetime) VALUES (?, ?, ?, ?, ?)', [u_id[0], post, formated_date, title, post_date])

        # commit all db operations
        conn.commit()
        
        return redirect('/diary'), 302

    else:
        # check if user in session
        if session['username']:

            # cursor for db
            conn = db_conn()
            cur = conn.cursor()

            # get user id
            u_id = cur.execute('SELECT id FROM users WHERE username = ?', [session['username']])
            u_id = cur.fetchone()

            # get all user's activities
            trackers = cur.execute('SELECT activity FROM activities WHERE user_id = ?', [u_id[0]])
            trackers = cur.fetchall()

            # get post id
            last_id = cur.execute('SELECT id FROM notes WHERE user_id = ?', [u_id[0]])
            post_id = cur.fetchall()


            # get marked trackers
            marked = cur.execute('SELECT * FROM trackers WHERE user_id = ?', [u_id[0]])
            marked = cur.fetchall()

            # get all posts
            history = cur.execute('SELECT * FROM notes WHERE user_id = ? ORDER BY datetime(datetime) DESC', [u_id[0]])
            history = cur.fetchall()

            # commit
            conn.commit()

            return render_template('diary.html', history=history, trackers=trackers, marked=marked)
        else:
            redirect ('/error')
            

# settings
@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == "POST":
        
        # get activity
        activity = request.form.get('activity')

        # cursor for db
        conn = db_conn()
        cur = conn.cursor()


        # get user id
        u_id = cur.execute('SELECT id FROM users WHERE username = ?', [session['username']])
        u_id = cur.fetchone()

        # get all user's activities
        uniq_activities = cur.execute('SELECT activity FROM activities WHERE user_id = ?', [u_id[0]])
        uniq_activities = cur.fetchall()

        # get number of activities
        num_activities = cur.execute('SELECT COUNT(*) FROM activities WHERE user_id = ?', [u_id[0]])
        num_activities = cur.fetchone()

        if num_activities[0] > 4:
            flash('You have reached maximum amount of trackers.')
            return redirect('/settings'), 302

        # block duplicates
        for a in uniq_activities:
            act = a[0]
            if activity.lower().strip() == act.lower().strip():
                flash('This activity is already on the list, please select another one.')
                return redirect('/settings'), 302

        # add new activity
        cur.execute('INSERT INTO activities (user_id, activity) VALUES (?, ?)', [u_id[0], activity])
        conn.commit()

        return redirect('/settings'), 302
    
    else:
        # check if user in session
        if session['username']:
            # cursor for db
            conn = db_conn()
            cur = conn.cursor()

            # get user id
            u_id = cur.execute('SELECT id FROM users WHERE username = ?', [session['username']])
            u_id = cur.fetchone()

            # get all activities
            activities = cur.execute('SELECT activity FROM activities WHERE user_id = ?', [u_id[0]])
            activities = cur.fetchall()

            return render_template('settings.html', activities=activities)
        else:
            redirect ('/error')

# delete activity
@app.route("/delete_activity", methods=['POST'])
@login_required
def delete_activity():
    if request.method == 'POST':

        # cursor for db
        conn = db_conn()
        cur = conn.cursor()

        # get user id
        u_id = cur.execute('SELECT id FROM users WHERE username = ?', [session['username']])
        u_id = cur.fetchone()
    
        to_delete = request.form.get('this_activity')

        cur.execute('DELETE FROM activities WHERE activity = ? and user_id = ?', [to_delete, u_id[0]])
        conn.commit()

        return redirect('/settings')


# logout
@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'GET':
        session.clear()
        return redirect('/')

