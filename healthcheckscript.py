
from flask import Flask, render_template
from healthcheck import HealthCheck

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/projectserver/frontendproj')
def mainpg():
  return render_template('frontendpage.html')

@app.route('/projectserver/frontendproj/route')
def my_link():


  return 'Click.'

if __name__ == '__main__':
  app.run(debug=True)
