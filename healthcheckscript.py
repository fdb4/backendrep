
from flask import Flask, render_template
from healthcheck import HealthCheck
app = Flask(__name__)
health= HealthCheck()

def wokringcheck():
  return True, "Hello world"
health.add_check( wokringcheck )

@app.route('/')
def mainpg():
  return render_template('frontendpage.html')

@app.route('/healthcheck/')
def healthcheck():
  return health.run_check(wokringcheck)

if __name__ == '__main__':
  app.run(debug=True)
