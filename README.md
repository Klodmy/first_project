# HAPPY DIARY
#### Video Demo: https://youtu.be/sZO-lVp_G-s
#### Description:

This is description for HAPPY DIARY, the final project for CS50 course. 

Project is completed using HTML5, CSS, Flask, Python, Sqlite3, Java Script. As addition, hashlib, plotly and pandas were used for certain purposes. 

#### General goal
Happy Diary is a diary that also offers to track how different aspects of life affect user's happiness, how user feels about certain activities on day-to-day basis. 

#### Learned while completing

- Setting up Flask on virtual environment
- Read documentation (very helpful)
- Creating wrap for loging required
- Learned about good hash for passwords
- Connecting database to the app
- Setting cookies
- A lot about html and css
- Got familiar with plotly.express on very basic level
- Got familiar with pandas on very basic level

#### Elements overview:

###### Main page
As a template for main page layout.html is used. It consists of short description of the project and buttons that lead to login or registration pages. HTML contains links to CSS, Jinja2 blocks which are used by 'login' and 'registration' tamplates as layout.

###### Sign-Up
This page has a form that asks user for username, password and password confirmation. If username is not occupied and password matches with confirmation, user consider registred and is redirected to '/diary' with started session.

###### Login   
On login page there is a form that asks user for login and password, and if combination provided matches the one in database, user consider logged in and is redirected to '/diary' with started session. 

###### Diary
HTML of diary page is used by other pages (Data, Settings) as a Jinja2 template. On diary page there is a header that contains user greeting on the left side and 4 ancors on the right. Anchors are My Diary - refreshes the page, Data - leads to graph with activities, Settings - page were user can add and delete activities, Logout - ends session, redirects user to the homepage. 

There are 2 components of diary: form for adding a note and history. 

**Form** consists of input for a title, textarea for a note, and, if user added any trackers in 'Settings', select menu for each tracker. User is asced to estimate each tracker on scale from 1 to 10. 

**History** is a history of notes that user added. It is done as buttons with hidden content that pops or hides on click. It gives user the following information: date, mark for each tracker, title and a note. 

###### Data
There is only one element on data page - it is a interactive graph that shows user a line for each activity added and tracked. Graph was done with pandas (for DaraFrame creation and manipulation) and plotly.express (for representing data as a graph) libreries.

In this case I was intended to use matplotlib, however it works bad with macOS, so I shifted my attention to plotly.

###### Settings
Settings page serves to add and delete trackers. There is a form with field that allows user to add one unique tracker. Case here does not matter, Tracker = tracker = tRacKer. If there are no activities, user is offered to add one with flash-messege provided by Flask. Otherwise, user sees a list of activities and 'delete' button near each. Deleted activity can be restored by re-adding in settings.

###### Error
Just a page that tells user that something went wrong.

###### Static
There are only 2 files in Static folder - background picture for main page and styles.css for styling the app. 

###### app.py
Contains all the back-end of the app. Maybe it was worth it to create another file for functions, but for now it left as it is. 

###### happy.db
Is a sqlite3 database for the app. Below is the schema of the database.

- users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, date DATETIME NOT NULL)
- sqlite_sequence(name,seq)
- activities (user_id INTEGER NOT NULL, activity TEXT NOT NULL)
notes (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, note TEXT NOT NULL, date DATETIME NOT NULL, title TEXT NOT NULL, datetime DATETIME NOT NULL)
- trackers (user_id INTEGER NOT NULL, post_id INTEGER, activity TEXT, mark INTEGER, date DATETIME, FOREIGN KEY(post_id) REFERENCES notes(id))

