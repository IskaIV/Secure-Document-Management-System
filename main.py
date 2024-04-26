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


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        con = sqlite3.connect('database.db')
        try:
            WorkID = request.form['WorkID']
            Password = request.form['Password']

            hashed_password = hashlib.sha256(
                Password.encode()).hexdigest()  # Correct hashing method

            cur = con.cursor()

            # Fetch the user with the provided WorkID
            cur.execute("SELECT * FROM Users WHERE WORKID = ? AND Password = ?",
                        (WorkID, hashed_password))
            rows = cur.fetchall()
            if len(rows) == 0:
                return render_template("NoMatchingUser.html")

            token = generate_token(WorkID)
            user[0] = rows[0][0]

            # Check Users table for the role of the user and assign it to the role
            role = cur.execute(
                "SELECT Role FROM Users WHERE WORKID = ?", (WorkID)).fetchone()[4]

            # Redirect to the appropriate page based on the role
            if role == 'Admin':
                return redirect('/AdminMainPage')
            elif role == 'Manager':
                return redirect('/ManagerMainPage')
            else:
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
            return redirect("/")
        finally:
            con.close()


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    return render_template('SignUp.html')


@app.route('/signupvalid', methods=['POST', 'GET'])
def signupvalid():
    if request.method == 'POST':
        con = sqlite3.connect('database.db')
        try:
            firstName = request.form['First']
            lastName = request.form['Last']
            WorkID = request.form['WorkID']
            password = request.form['Password']
            confirm_pass = request.form['ConfirmPassword']
            # Check if the user is Admin, Manager, or User
            if WorkID[0] == 'A':
                role = 'Admin'
            elif WorkID[0] == 'M':
                role = 'Manager'
            else:
                role = 'User'
            user[0] = WorkID

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            with con:
                cur = con.cursor()

                # Check if WORKID is valid
                if not cur.execute("SELECT * FROM ValidWorkID WHERE WORKID = ?", (WorkID,)).fetchall():
                    return render_template('InvalidWorkID.html')

                # Check if WorkID is already in the database
                if cur.execute("SELECT * FROM Users WHERE WORKID = ?", (WorkID,)).fetchone():
                    return render_template('InvalidWorkID.html')

                # If password and confirm password are the same, insert the user into the database
                if password == confirm_pass:
                    cur.execute("INSERT INTO Users (WORKID, Password, First, Last) VALUES (?,?,?,?)", (
                        WorkID, hashed_password, firstName, lastName))
                    cur.execute(
                        "UPDATE Users SET Role = ? WHERE WORKID = ?", (role, WorkID))

                # Redirect regardless of the insertion status
                return redirect("/")

        except Exception as e:
            logging.error(f"Error: {e}")
            con.rollback()
            return render_template('Error.html')
        finally:
            con.close()


@app.route('/UserMainPage', methods=['POST', 'GET'])
def main():
    session_token = request.cookies.get('AuthToken')

    if not check_token(session_token, user[0]):
        return render_template('TokenError.html')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users")
    users = cur.fetchall()
    cur.execute("SELECT * FROM Files ORDER BY FileId DESC")
    files = cur.fetchall()

    return render_template('UserMainPage.html', Users=users, Files=files)


@app.route('/addfile', methods=['POST', 'GET'])
def addfile():
    session_token = request.cookies.get('AuthToken')

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
    app.run(debug=True)
