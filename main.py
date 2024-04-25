import sqlite3
from flask import Flask, render_template, request, redirect, make_response
import hashlib
import logging
from setup import start_db
from check import generate_token, check_token
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
user = ['']


@app.route('/')
def front_page():
    return render_template('Login.html')


@app.route('/login', methods=['POST'])
def login():
    con = sqlite3.connect('database.db')
    try:
        WorkID = request.form['WorkID']
        Password = request.form['Password']

        hashed_password = hashlib.sha256(Password.encode()).hexdigest()
        cur = con.cursor()
        cur.execute("SELECT * FROM Users WHERE WorkID = ? AND Password = ?",
                    (WorkID, hashed_password))
        rows = cur.fetchall()
        if len(rows) == 0:
            return render_template("NoMatchingUser.html")

        token = generate_token(WorkID)
        user[0] = rows[0][0]

        response = make_response(redirect('/main'))
        response.set_cookie('AuthToken', token)

        return response
    except sqlite3.Error as e:
        logging.error(f"Database Error: {e}")
        return render_template("Error.html")
    except Exception as e:
        logging.error(f"Exception Error: {e}")
        return render_template("Error.html")
    except:
        return render_template("/")
    finally:
        con.close()


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    return render_template('SignUp.html')


@app.route('/signupvalid', methods=['POST', 'GET'])
def signupvalid():
    if request.method == "POST":
        con = sqlite3.connect('database.db')
        try:
            WorkID = request.form['WorkID']
            firstName = request.form['First']
            lastName = request.form['Last']
            password = request.form['Password']
            confirm_pass = request.form['ConfirmPassword']
            user[0] = WorkID

            hashed_password = hashlib.sha1(password.encode()).hexdigest()

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()

                # Check WORKID is valid
                cur.execute(
                    "SELECT * FROM ValidWorkID WHERE WORKID = ?", (WorkID,))

                # If if WorkID is already in the database, return an error
                cur.execute("SELECT * FROM User WHERE WORKID = ?", (WorkID,))

                # If password and confirm password are the same, insert the user into the database
                if (password == confirm_pass):
                    cur.execute("INSERT INTO User (WORKID, First, Last, Password) VALUES (?,?,?,?)", (
                        WorkID, firstName, lastName, hashed_password))
                return redirect("/")

        except:
            con.rollback()
            return render_template('Error.html')
        finally:
            con.close()


@app.route('/main', methods=['POST', 'GET'])
def main():
    session_token = request.cookies.get('auth_token')

    if not check_token(session_token, user[0]):
        return render_template('TokenError.html')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Files ORDER BY Id DESC")
    posts = cur.fetchall()

    return render_template('MainPage.html', posts=posts)


@app.route('/uploadfile', methods=['POST', 'GET'])
def uploadfile():
    session_token = request.cookies.get('auth_token')

    if not check_token(session_token, user[0]):
        return render_template('TokenError.html')

    return render_template('UploadFile.html')


@app.route('/addfile', methods=['POST', 'GET'])
def addfile():
    session_token = request.cookies.get('auth_token')

    if not check_token(session_token, user[0]):
        return render_template('TokenError.html')

    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        file = request.files['file']
        filename = file.filename
        filedata = file.read()
        cur.execute(
            "INSERT INTO Files (FileName, FileData) VALUES (?, ?)", (filename, filedata))
        conn.commit()
        conn.close()
        return redirect('/main')


if __name__ == "__main__":
    start_db()
    app.run()
