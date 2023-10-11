import sqlite3
database = sqlite3.connect('/app/db/tinyud.db')
database.execute('CREATE TABLE IF NOT EXISTS tinyud (	id INTEGER PRIMARY KEY ,	nom VARCHAR(100),	addr VARCHAR(100),	state VARCHAR(10),	attempt_fail INT(5),	lasttime_down FLOAT(100),check_attempt INT(5));')
database.execute('CREATE TABLE IF NOT EXISTS tinyud_config (id INTEGER PRIMARY KEY ,	name VARCHAR(100),	config VARCHAR(100))')
database.execute('INSERT INTO tinyud_config (name ,config) VALUES ("GotifyURL","https://Gotify.URL/message?token=TOKEN")')
database.commit()
database.close()