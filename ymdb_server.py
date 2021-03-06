import secrets

import re
import sqlite3

from flask import Flask, render_template, abort, session, redirect, url_for, request

from accounts import accounts_api
from browse import browse_api
from entry import entry_api
from globals import db_connection, from_unix_time
from search import search_api

app = Flask(__name__)
app.register_blueprint(browse_api)
app.register_blueprint(entry_api)
app.register_blueprint(search_api)
app.register_blueprint(accounts_api)


@app.route('/')
def index():
    return render_template('index.html')


""" use this to disable caching (useful for debugging)
@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response
"""


@app.route('/<mid>')
def view_movie(mid):
    """
    View a movie's details.
    :param mid: movie id to lookup
    :return: rendered template with movie name, director, poster, reviews, etc.
    """
    # first check that mid is an int
    try:
        mid = int(mid)
    except ValueError:
        abort(400)

    # check if the movie is in the database
    curs = db_connection.cursor()
    curs.execute('SELECT MID, director_UID, title, release_date FROM MOVIE WHERE MID = ?', (mid,))
    movie_row = curs.fetchone()
    # if not found, then don't render
    if movie_row is None:
        # TODO: render a 404
        abort(404)
        return
    # otherwise, get other info, starting with poster
    curs.execute('SELECT img FROM POSTER WHERE MID = ?', (mid,))
    poster_row = curs.fetchone()
    if poster_row is None:
        poster_name = None
    else:
        poster_name = poster_row[0]

    # now get director
    if movie_row[1] is None:
        director_name = 'n/a'
    else:
        curs.execute('SELECT given_name FROM DIRECTOR WHERE UID = ?', (movie_row[1],))
        director_name = curs.fetchone()[0]

    # now set title
    title = movie_row[2]

    # set release date
    if movie_row[3] is None:
        released = 'n/a'
    else:
        released = from_unix_time(movie_row[3])

    # get actors
    curs.execute('SELECT UID, character_role FROM ACTED_IN WHERE MID = ?', (mid,))
    character_rows = curs.fetchall()
    actors = []
    characters = []
    for row in character_rows:
        curs.execute('SELECT name FROM ACTOR WHERE UID = ?', (row[0],))
        actors.append(curs.fetchone()[0])
        characters.append(row[1])

    # get reviews
    curs.execute('SELECT UID, text, rating, created_date FROM REVIEW WHERE MID = ? ORDER BY created_date DESC ', (mid,))
    review_rows = curs.fetchall()
    usernames = []
    reviews = []
    ratings = []
    dates = []
    for row in review_rows:
        curs.execute('SELECT u_name FROM USER WHERE UID = ?', (row[0],))
        usernames.append(curs.fetchone()[0])
        reviews.append(row[1])
        ratings.append(row[2])
        dates.append(row[3])

    movie_info = {
        'mid': mid,
        'title': title,
        'director': director_name,
        'released': released,
    }

    character_info = [
        {'actor': actors[i], 'character': characters[i]}
        for i in range(0, len(actors))
    ]

    review_info = [
        {'username': usernames[i], 'text': reviews[i], 'rating': ratings[i], 'date': dates[i]}
        for i in range(0, len(reviews))
    ]

    # render the template with this data
    return render_template('movie.html',
                           poster=poster_name,
                           movie_info=movie_info,
                           character_info=character_info,
                           review_info=review_info
                           )


@app.route('/<mid>/review', methods=['POST'])
def make_review(mid):
    # first check that mid is an int
    try:
        mid = int(mid)
    except ValueError:
        abort(400)
        return

    if session['uid'] is None:
        return redirect(url_for('accounts_api.forbidden', account_type='user', resource='/movie/review'))

    # check if the movie is in the database
    curs = db_connection.cursor()
    curs.execute('SELECT MID, director_UID, title, release_date FROM MOVIE WHERE MID = ?', (mid,))
    movie_row = curs.fetchone()
    # if not found, then don't render
    if movie_row is None:
        # TODO: render a 404
        abort(404)
        return

    try:
        text = request.form['text']
        rating = int(request.form['rating'])
    except KeyError:
        abort(400)
        return

    if not re.match(r'[0-9a-zA-Z_.,"\'()!@$*=\-+&:]*', text):
        # test for text matching only alphanumeric and punctuation
        message = 'text must be alphanumeric with punctuation (no carats, braces, or octothorpes)'
        return render_template('movie.html', message=message), 400
    if rating < 0 or rating > 5:
        # make sure rating is [0:5]
        message = 'rating must be from zero to five'
        return render_template('movie.html', message=message), 400

    try:
        uid = session['uid']
        # try to insert the new review entry
        # pass now as created date for this review
        curs.execute("INSERT INTO REVIEW VALUES (?, ?, ?, ?, strftime('%s', 'now'))",
                     (mid, uid, text, rating))
        # commit changes
        db_connection.commit()
        return redirect(url_for('view_movie', mid=mid))
    except sqlite3.Error as err:
        # handle sql errors (probably mid, uid already existing)
        db_connection.rollback()
        # show error message on bad value
        message = 'error inserting tuple (' + str(err) + ')'
        return render_template('movie.html', message=message), 400


db_connection.execute('PRAGMA foreign_keys = ON')
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if __name__ == '__main__':
    # enable foreign key on all database connections
    db_connection.execute('PRAGMA foreign_keys = ON')

    # configure secret key for signing session cookies
    app.secret_key = secrets.token_hex(16)

    # configure max length (for limiting uploads)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # run the app (flask)
    app.run(host='0.0.0.0')
