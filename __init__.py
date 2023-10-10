from flask import Flask, render_template, request, Response
from flaskext.mysql import MySQL
import cryptography
import pdfkit

def createApp():
  app = Flask(__name__)
  mysql = MySQL()
  app.config['MYSQL_DATABASE_USER'] = 'fdb4'
  app.config['MYSQL_DATABASE_PASSWORD'] = '43121234'
  app.config['MYSQL_DATABASE_DB'] = 'sakila'
  app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
  app.config['MYSQL_DATABASE_PORT'] = 1070
  mysql.init_app(app)
  conn = mysql.connect()
  cursor = conn.cursor()
  return app
