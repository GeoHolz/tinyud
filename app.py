import sqlite3
import time
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    conn = sqlite3.connect('tinyud.db')
    conn.row_factory = sqlite3.Row
    return conn
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM tinyud WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post
def get_settings():
    conn = get_db_connection()
    post = conn.execute('SELECT config FROM tinyud_config WHERE name ="GotifyURL" ').fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post[0] 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s) # datetime.datetime.fromtimestamp(s)

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM tinyud').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        ipaddr = request.form['ipaddr']
        nbcheck = request.form['nbcheck']


        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO tinyud (nom ,addr ,state ,attempt_fail ,lasttime_down , check_attempt ) VALUES (?,?,"Up",0,0,?)',(title, ipaddr,nbcheck))
            conn.commit()
            conn.close()
            flash('"{}" was successfully added!'.format(title))
            return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/settings', methods=('GET', 'POST'))
def settings():
    settings=get_settings()
    
    if request.method == 'POST':
        Gotify = request.form['Gotify']
        if not Gotify:
            flash('Gotify URL is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO tinyud_config (name ,config) VALUES ("GotifyURL",?)',(Gotify,))
            conn.commit()
            conn.close()
            flash('"{}" was successfully added!'.format(Gotify))
            return redirect(url_for('index'))
    
    return render_template('settings.html', settings=settings)


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['nom']
        ipaddr = request.form['addr']
        nbcheck = request.form['check_attempt']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE tinyud SET nom = ?, addr = ?, check_attempt = ? WHERE id = ?',(title, ipaddr, nbcheck,id))
            conn.commit()
            conn.close()
            flash('"{}" was successfully edited!'.format(title))
            return redirect(url_for('index'))
    
    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM tinyud WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['nom']))
    return redirect(url_for('index'))