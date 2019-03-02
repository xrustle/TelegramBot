import os
import psycopg2

class db():
	def __init__(self):
		self.conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
		#self.conn = psycopg2.connect(host="localhost",database="xrustle", user="postgres", password="postgres")
		self.conn.autocommit = True

	def __del__(self):
		self.conn.close()

	def createtable(self):
		self.c = self.conn.cursor()
		self.c.execute('''CREATE TABLE IF NOT EXISTS USERS 
			(ID INTEGER PRIMARY KEY,
			FIRST_NAME VARCHAR(255),
			LAST_NAME VARCHAR(255),
			USERNAME VARCHAR(255),
			STEP INTEGER DEFAULT 0);''')

	def exist(self, id):
		self.c = self.conn.cursor()
		self.c.execute('SELECT * FROM USERS WHERE ID=%s;', (id,))
		return self.c.fetchone() is not None

	def step(self, id):
		self.c = self.conn.cursor()
		self.c.execute('SELECT * FROM USERS WHERE ID=%s;', (id,))
		return self.c.fetchone()[4]

	def insert(self, chat, step):
		self.c = self.conn.cursor()
		self.c.execute('SELECT * FROM USERS WHERE ID=%s;', (chat.id,))
		if self.c.fetchone() is not None:
			self.c.execute('UPDATE USERS SET FIRST_NAME = %s, LAST_NAME = %s, USERNAME = %s, STEP = %s WHERE id = %s;', (chat.first_name, chat.last_name, chat.username, step, chat.id))
		else:
			self.c.execute('INSERT INTO USERS (ID, FIRST_NAME, LAST_NAME, USERNAME, STEP) VALUES (%s, %s, %s, %s, %s);', (chat.id, chat.first_name, chat.last_name, chat.username, step))

	def show(self):
		self.c = self.conn.cursor()
		self.c.execute('SELECT * FROM USERS;')
		for row in self.c.fetchall():
			print(row)