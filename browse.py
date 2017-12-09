from flask import Blueprint, render_template
from flask_paginate import Pagination, get_page_args

from db_connection import db_connection

browse_api = Blueprint('browse_api', __name__)


@browse_api.route("/browse")
def browse_index():
    return render_template('browse/index.html')


@browse_api.route("/browse/user")
def browse_user():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("SELECT * FROM USER")

    rows = cur.fetchall()

    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    cur.close()
    return render_template('browse/browse_user.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/admin")
def browse_admin():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("SELECT * FROM ADMIN")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    cur.close()
    return render_template('browse/browse_admin.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/director")
def browse_director():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("SELECT * FROM DIRECTOR")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    cur.close()
    return render_template('browse/browse_director.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/actor")
def browse_actor():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("SELECT * FROM ACTOR")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_actor.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/movie")
def browse_movie():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("SELECT * FROM MOVIE")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_movie.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/review")
def browse_review():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("SELECT * FROM REVIEW")

    rows = cur.fetchall();
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_review.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/acted_in")
def browse_acted_in():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("SELECT * FROM ACTED_IN")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/browse_acted_in.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )


@browse_api.route("/browse/poster")
def browse_poster():
    cur = db_connection.cursor()
    page, per_page, offset = get_page_args()
    cur.execute("SELECT * FROM POSTER")

    rows = cur.fetchall()
    rows_limited = rows[offset:(per_page + offset)]
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(rows), record_name='rows')

    return render_template('browse/poster.html',
                           rows=rows_limited,
                           pagination=pagination,
                           )
