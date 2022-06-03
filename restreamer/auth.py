import functools
import json
import os

from flask import (Blueprint, current_app, flash, g, redirect, render_template,
                   request, session, url_for)

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=('GET', 'POST'))
def login(): 
    if request.method == 'POST': 
        error = None
        username = request.form['username']
        passwd = request.form['password']
        with open(os.path.join(current_app.instance_path, "userInfo.json")) as f: 
            user_info = json.load(f)
        if (username != user_info['username']) or (passwd != user_info['password']): 
            error = 'Invalid token'
        
        if error is None: 
            session.clear()
            session['username'] = user_info['username']
            if g.stream_server: 
                session['stream_server'] = g.stream_server
            
            return redirect(url_for('restreamer.index'))
        
        flash(error)

    return render_template('login.html')


@bp.before_app_request
def load_logged_in_user(): 
    username = session.get('username')
    with open(os.path.join(current_app.instance_path, "userInfo.json")) as f: 
        user_info = json.load(f)
    if username == user_info['username']: 
        g.user = username
    else: 
        g.user = None
    g.stream_server = session.get('stream_server')


@bp.route('/logout')
def logout(): 
    session.clear()
    if g.stream_server: 
        session['stream_server'] = g.stream_server
    return redirect(url_for('index'))


def login_required(view): 
    @functools.wraps(view)
    def wrapped_view(**kwargs): 
        if g.user is None: 
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view
    