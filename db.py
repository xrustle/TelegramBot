import sqlite3
import config

def createtable():
	conn = sqlite3.connect(config.dbfile)
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS USERS 
		(ID INTEGER PRIMARY KEY,
		FIRST_NAME TEXT,
		LAST_NAME TEXT,
		USERNAME TEXT,
		STEP INTEGER DEFAULT 0)''')
	conn.commit()
	conn.close()

def exist(id):
	conn = sqlite3.connect(config.dbfile)
	c = conn.cursor()
	for row in c.execute('SELECT * FROM USERS WHERE ID=?', (id,)):
		ret = True
		break
	else:
		ret = False
	conn.close()
	return ret

def step(id):
	conn = sqlite3.connect(config.dbfile)
	c = conn.cursor()
	ret = c.execute('SELECT * FROM USERS WHERE ID=?', (id,)).fetchone()[4]
	conn.close()
	return ret

def insert(chat, step):
	conn = sqlite3.connect(config.dbfile)
	c = conn.cursor()
	for row in c.execute('SELECT * FROM USERS WHERE ID=?', (chat.id,)):
		c.execute('UPDATE users SET FIRST_NAME = ?, LAST_NAME = ?, USERNAME = ?, STEP = ? WHERE id = ?;', (chat.first_name, chat.last_name, chat.username, step, chat.id))
		break
	else:
		c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', (chat.id, chat.first_name, chat.last_name, chat.username, step))
	conn.commit()
	conn.close()

def show():
	conn = sqlite3.connect(config.dbfile)
	c = conn.cursor()
	for row in c.execute('SELECT * FROM USERS'):
		print(row)
	conn.close()