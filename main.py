import sqlite3
from flask import Flask, render_template, request, redirect, make_response, url_for, flash, send_file
from werkzeug.utils import secure_filename
import hashlib
import logging
from setup import start_db
from check import generate_token, check_token
import io

UPLOAD_FOLDER = '/home/poisoniv/Code/COP4521/Project1/files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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

            # Redirect to the appropriate page based on the role
            response = make_response(redirect("/AdminMainPage"))
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


@app.route('/AdminMainPage', methods=['POST', 'GET'])
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

    return render_template('AdminMainPage.html', Users=users, Files=files)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploadfile', methods=['POST', 'GET'])
def uploadfile():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Read the file content
            file_data = file.read()
            # Insert file data into the database
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Files (FileName, FileData, WorkID) VALUES (?, ?, ?)", (filename, file_data, user[0]))
            conn.commit()
            conn.close()
            return redirect(url_for('uploadfile'))
    return render_template('UploadFile.html')


@app.route('/download/<int:file_id>')
def downloadfile(file_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT FileName, FileData FROM Files WHERE FileId=?", (file_id,))
    file_record = cursor.fetchone()
    conn.close()

    if file_record:
        filename, file_data = file_record
        return send_file(io.BytesIO(file_data), attachment_filename=filename, as_attachment=True)
    else:
        return "File not found"


@app.route('/EditWorkID', methods=['POST', 'GET'])
def EditWorkID():
    return render_template('EditWorkID.html')


if __name__ == "__main__":
    start_db()
    app.run(debug=True)
