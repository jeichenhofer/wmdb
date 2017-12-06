import sqlite3
import os

import re

from validate_email import validate_email
from flask import Blueprint, render_template, abort, request


entry_api = Blueprint('entry_api', __name__)


db_connection = sqlite3.connect(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ym.db'
    )
)


def check_user():
    return True


@entry_api.route("/entry")
def entry_index():
    if not check_user():
        abort(403)
    return render_template('entry/index.html')


@entry_api.route("/entry/user", methods=['POST', 'GET'])
def user_entry():
    message = None
    if request.method == 'GET':
        return render_template('entry/user.html', message=message)
    elif request.method == 'POST':
        try:
            u_name = request.form['u_name']
            email = request.form['email']
        except KeyError:
            message = 'bad form data'
            return render_template('entry/user.html', message=message)
        if (not re.match(r'[a-z0-9]+', u_name)) or len(u_name) > 40:
            message = "u_name must be alphanumeric and at most 40 characters"
            return render_template('entry/user.html', message=message)
        if not validate_email(email):
            message = "invalid email format"
            return render_template('entry/user.html', message=message)
        try:
            cur = db_connection.cursor()
            cur.execute("INSERT INTO USER VALUES (NULL, ?, ?, strftime('%s', 'now'))", (u_name, email))
            uid = cur.lastrowid
            db_connection.commit()
            inserted_row = cur.execute("SELECT * FROM USER WHERE UID=?", (uid,))
            message = 'inserted new user successfully: ' + str(inserted_row.fetchone())
            return render_template('entry/user.html', message=message)
        except sqlite3.Error as err:
            print(err)
            db_connection.rollback()
            message = 'error inserting tuple (' + str(err) + ')'
            return render_template('entry/user.html', message=message)

    else:
        abort(405)
