import pymysql.err
from flask import Flask, render_template, request, Response, flash
from flaskext.mysql import MySQL
import cryptography
import pdfkit
from flask_paginate import Pagination, get_page_parameter
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
config = pdfkit.configuration(wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
@app.errorhandler(404)
def error_page(error):
  return render_template('home.html')

@app.route('/', methods=['GET','POST'])
@app.route('/homepage/', methods=['GET','POST'])
def mainpg():
  cursor.execute("select film.title,count(inventory.film_id)  from sakila.rental inner join sakila.inventory on rental.inventory_id=inventory.inventory_id inner join sakila.film on inventory.film_id=film.film_id group by inventory.film_id order by count(inventory.film_id) DESC limit 5;")
  top5movies = cursor.fetchall()
  print(top5movies)
  cursor.execute("select  actor.first_name, actor.last_name,count(*) as \"Films in\" from sakila.film_actor inner join sakila.actor on film_actor.actor_id=actor.actor_id group by film_actor.actor_id order by count(*) DESC limit 5;")
  top5Actors = cursor.fetchall()
  print(top5Actors)
  if request.method =="POST":
    if request.form['AoM']=='1':
      query="select film.title,count(inventory.film_id), actor.first_name, actor.last_name from sakila.rental inner join sakila.inventory on rental.inventory_id=inventory.inventory_id  inner join sakila.film on inventory.film_id=film.film_id inner join sakila.film_actor on film.film_id=film_actor.film_id inner join sakila.actor on film_actor.actor_id=actor.actor_id where actor.first_name=\""+request.form['ActorFN']+"\" and actor.last_name=\"" + request.form['ActorLN']+"\" group by inventory.film_id, film_actor.actor_id order by count(inventory.film_id) DESC limit 5;"
      cursor.execute(query)
      actorInfo=cursor.fetchall()
      print(actorInfo)
      return render_template('home.html', top5movies=top5movies, top5Actors=top5Actors,actorInfo=actorInfo)
    elif request.form['AoM']=='0':
      query = "select film.title,film.description,film.release_year,film.length,film.rating,film.special_features , category.name as \"category\", actor.first_name,actor.last_name from sakila.film inner join sakila.film_category on film.film_id=film_category.film_id inner join sakila.category on category.category_id=film_category.category_id inner join sakila.film_actor on film.film_id=film_actor.film_id inner join sakila.actor on film_actor.actor_id=actor.actor_id  where film.title=\""+request.form['Title']+"\""
      cursor.execute(query)

      movieInfo =cursor.fetchall()

      print(movieInfo)
      return render_template('home.html', top5movies=top5movies, top5Actors=top5Actors, movieInfo=movieInfo)
  return render_template('home.html',top5movies=top5movies,top5Actors=top5Actors)

@app.route('/movies/', methods=['GET','POST'])
def movies():
  if request.method == "POST":
    if request.form['SOR'] == "0":
      query = "call sakila.film_in_stock((select film_id from sakila.film where title=%s), %s ,@count)"
      cursor.execute(query,(request.form['filmN'],request.form['storeID']))
      data = cursor.fetchall()
      return render_template("movies.html",inStock=data)
    elif request.form['SOR']=="1":
      query="insert into sakila.rental(rental_date, inventory_id, customer_id, staff_id) values(NOW(), %s, %s, 1);"
      cursor.execute(query,(request.form['invID'],request.form['custID']))
      print(query)
      conn.commit()
      return render_template("movies.html")



    elif request.form['SOR']=="2":
      query="select film.title,film.description,film.release_year,film.length,film.rating,film.special_features , category.name as \"category\", actor.first_name,actor.last_name from sakila.film inner join sakila.film_category on film.film_id=film_category.film_id inner join sakila.category on category.category_id=film_category.category_id inner join sakila.film_actor on film.film_id=film_actor.film_id inner join sakila.actor on film_actor.actor_id=actor.actor_id"

      #if request.form['Title']!='' and request.form['Category']!='' and request.form['ActorFN']!='' and request.form['ActorLN']!='':
      #  query = query + " where film.title=%s AND category.name=%s AND actor.first_name=%s AND actor.last_name=%s"
      if request.form['ActorLN']!=''and request.form['ActorFN']=='' and request.form['Category']=='' and request.form['Title']=='':#0001
        query = query + " where actor.last_name=%s"
        cursor.execute(query, (request.form['ActorLN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['ActorFN']!='' and request.form['ActorLN']=='' and request.form['Category']=='' and request.form['Title']=='':#0010
        query = query + " where actor.first_name=%s"
        cursor.execute(query, (request.form['ActorFN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['ActorFN']!='' and request.form['ActorLN']!='' and request.form['Category']=='' and request.form['Title']=='': #0011
        query = query + " where actor.first_name=%s AND actor.last_name=%s"
        cursor.execute(query, (request.form['ActorFN'],request.form['ActorLN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Category']!='' and request.form['Title']=='' and request.form['ActorLN']==''and request.form['ActorFN']=='':#0100
        query = query + " where category.name=%s"
        cursor.execute(query, (request.form['Category']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Category']!='' and request.form['ActorLN']!=''and request.form['ActorFN']==''and request.form['Title']=='':#0101
        query = query + " where category.name=%s AND actor.last_name=%s"
        cursor.execute(query, (request.form['Category'],request.form['ActorLN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Category']!='' and request.form['ActorFN']!=''and request.form['Title']==''and request.form['ActorLN']=='':#0110
        query = query + " where category.name=%s AND actor.first_name=%s"
        cursor.execute(query, (request.form['Category'],request.form['ActorFN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Category']!='' and request.form['ActorFN']!='' and request.form['ActorLN']!='' and request.form['Title']=='':#0111
        query = query + " where category.name=%s AND actor.first_name=%s  AND actor.last_name=%s"
        cursor.execute(query, (request.form['Category'],request.form['ActorFN'],request.form['ActorLN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Title']!='' and request.form['ActorLN']==''and request.form['ActorFN']=='' and request.form['Category']=='':#1000
        query = query + " where film.title=%s "
        cursor.execute(query, (request.form['Title']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Title']!='' and request.form['ActorLN']!=''and request.form['ActorFN']=='' and request.form['Category']=='':#1001
        query = query + " where film.title=%s AND actor.last_name=%s"
        cursor.execute(query, (request.form['Title'],request.form['ActorLN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Title']!='' and request.form['ActorFN']!=''and request.form['ActorLN']=='' and request.form['Category']=='':#1010
        query = query + " where film.title=%s AND actor.first_name=%s"
        cursor.execute(query, (request.form['Title'],request.form['ActorFN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Title']!='' and request.form['ActorFN']!='' and request.form['ActorLN']!='' and request.form['Category']=='':#1011
        query = query + " where film.title=%s AND actor.first_name=%s AND actor.last_name=%s"
        cursor.execute(query, (request.form['Title'],request.form['ActorFN'],request.form['ActorLN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Title']!='' and request.form['Category']!=''and request.form['ActorLN']==''and request.form['ActorFN']=='':#1100
        query = query + " where film.title=%s AND category.name=%s"
        cursor.execute(query, (request.form['Title'],request.form['Category']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Title']!='' and request.form['Category']!='' and request.form['ActorLN']!=''and request.form['ActorFN']=='':#1101
        query = query + " where film.title=%s AND category.name=%s AND actor.last_name=%s"
        cursor.execute(query, (request.form['Title'],request.form['Category'],request.form['ActorLN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Title']!='' and request.form['Category']!='' and request.form['ActorFN']!=''and request.form['ActorLN']=='':#1110
        query = query + " where film.title=%s AND category.name=%s AND actor.first_name=%s"
        cursor.execute(query, (request.form['Title'],request.form['Category'],request.form['ActorFN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      elif request.form['Title']!='' and request.form['Category']!='' and request.form['ActorFN']!='' and request.form['ActorLN']!='':#1111
        query = query + " where film.title=%s AND category.name=%s AND actor.first_name=%s AND actor.last_name=%s"
        cursor.execute(query, (request.form['Title'],request.form['Category'],request.form['ActorFN'],request.form['ActorLN']))
        data = cursor.fetchall()
        return render_template('movies.html', data=data)
      cursor.execute(query)
      data = cursor.fetchall()
      return render_template("movies.html", data=data)


  return render_template("movies.html")

@app.route('/customers/',methods=['GET','POST'])
def customers():
  query = "select country from sakila.country;"
  cursor.execute(query)
  country = cursor.fetchall()
  query="select * from sakila.customer"
  if request.method=="POST":
    if request.form['CRUD']=='1':
      query = "insert into sakila.city (city,country_id) values(%s, (select country_id from sakila.country where country=%s));"
      cursor.execute(query,(request.form['city'],request.form['country']))
      query = "insert into sakila.address (address, address2, district, city_id, postal_code, phone, location) values(%s, %s, %s ,(select city_id from sakila.city order by city_id DESC limit 1), %s, %s, ST_GeomFromText('POLYGON((0 5, 2 5, 2 7, 0 7, 0 5))'));"
      cursor.execute(query,(request.form['address'],request.form['address2'],request.form['district'],request.form['postal'],request.form['phone']))
      query = "insert into sakila.customer (store_id, first_name, last_name, email, address_id, active) values(%s, %s, %s , %s,(select address_id from sakila.address order by address_id DESC limit 1) , 1);"
      print(query)
      cursor.execute(query,(request.form['storeID'], request.form['custFN'],request.form['custLN'],request.form['email']))
      conn.commit()
      query = "select * from sakila.customer"
    if request.form['CRUD']=='2':
      query = "update sakila.customer Set store_id=%s, first_name=%s,last_name=%s,email=%s where customer.customer_id=%s;"
      cursor.execute(query,(request.form['storeID2'],request.form['custFN2'],request.form['custLN2'],request.form['email2'],request.form['custID2']))
      query = "update sakila.address Set address=%s , address2=%s, district=%s,postal_code=%s,phone=%s where address_id=(select * from (select address.address_id from sakila.customer inner join sakila.address on customer.address_id=address.address_id inner join sakila.city on address.city_id=city.city_id where customer.customer_id=%s)as c);"
      cursor.execute(query, (request.form['address2'],request.form['address22'],request.form['district2'],request.form['postal2'],request.form['phone2'],request.form['custID2']))
      query = "update sakila.city Set city=%s , country_id=(select country_id from sakila.country where country=%s) where city.city_id=(select * from(select city.city_id from sakila.customer inner join sakila.address on customer.address_id=address.address_id inner join sakila.city on address.city_id=city.city_id where customer.customer_id=%s)as c);"
      cursor.execute(query,(request.form['city2'],request.form['country2'],request.form['custID2'] ))
      conn.commit()
      query = "select * from sakila.customer"
    if request.form['CRUD']=='3':
     # try:
      cursor.execute("set foreign_key_checks=0;")
      query = "delete from sakila.customer where customer_id=%s and address_id=%s;"
      cursor.execute(query,(request.form['custID3'],request.form['addressID3']))
      print("success1")
      query = "delete from sakila.address where address_id=%s and city_id=%s;"
      cursor.execute(query,(request.form['addressID3'],request.form['cityID3']))
      query = "delete from sakila.city where city_id=%s;"
      cursor.execute(query,(request.form['cityID3']))
      cursor.execute("set foreign_key_checks=1;")
      conn.commit()
      #except pymysql.err.IntegrityError:
      #  er='Customer is renting movie Wait for them to return it'
      return render_template('customers.html',country=country)
    if request.form['CRUD']=='4':
      try:
        er=''
        query = "update sakila.rental Set return_date=now() where rental_id=%s and customer_id=%s"
        cursor.execute(query,(request.form['rentalID'],request.form['custID4']))
        conn.commit()
      except pymysql.err.IntegrityError:
        er='Error'
      return render_template('customers.html',country=country, er=er)
    if request.form['CRUD']=='0':
      if request.form['custID']!='' and request.form['custFN'] != '' and request.form['custLN'] != '':
        query = query + " where customer.customer_id=%s AND customer.first_name=%s AND customer.last_name=%s"
        cursor.execute(query, (request.form['custID'], request.form['custFN'],request.form['custLN']))
        data = cursor.fetchall()
        return render_template('customers.html', data=data, country=country)
      elif request.form['custID']!='' and request.form['custFN'] != '' and request.form['custLN'] == '':
        query = query + " where customer.customer_id=%s AND customer.first_name=%s"
        cursor.execute(query, (request.form['custID'],request.form['custFN'],))
        data = cursor.fetchall()
        return render_template('customers.html', data=data, country=country)
      elif request.form['custID']!='' and request.form['custLN'] != '' and request.form['custFN'] == '':
        query = query + " where customer.customer_id=%s AND customer.last_name=%s"
        cursor.execute(query, (request.form['custID'],request.form['custLN'],))
        data = cursor.fetchall()
        return render_template('customers.html', data=data, country=country)
      elif request.form['custID'] != '' and request.form['custLN'] == '' and request.form['custFN'] == '':
        query = query + " where customer.customer_id=%s"
        cursor.execute(query, (request.form['custID'],))
        data = cursor.fetchall()
        return render_template('customers.html', data=data, country=country)
      elif request.form['custFN'] != '' and request.form['custID'] == '' and request.form['custLN'] == '':
        query = query + " where customer.first_name=%s"
        cursor.execute(query, (request.form['custFN'],))
        data = cursor.fetchall()
        return render_template('customers.html', data=data, country=country)
      elif request.form['custLN'] != '' and request.form['custID'] == '' and request.form['custFN'] == '':
        query = query + " where customer.last_name=%s"
        cursor.execute(query, (request.form['custLN'],))
        data = cursor.fetchall()
        return render_template('customers.html', data=data, country=country)
      elif request.form['custFN'] != '' and request.form['custLN'] != '' and request.form['custID'] == '':
        query = query + " where customer.first_name=%s AND customer.last_name=%s"
        cursor.execute(query, (request.form['custFN'], request.form['custLN'],))
        data = cursor.fetchall()
        return render_template('customers.html', data=data, country=country)
  print(query)
  cursor.execute(query)
  data=cursor.fetchall()
  print(data)
  return render_template('customers.html', data=data,country=country)

@app.route('/custDetails/',methods=['GET','POST'])
def custD():
  query = "select customer.customer_id, address.address_id, city.city_id, customer.first_name, customer.last_name, address.address, address.address2,address.phone, address.district,city.city, film.title, rental.rental_date, rental.return_date from  sakila.rental  inner join sakila.customer on rental.customer_id=customer.customer_id inner join sakila.inventory on rental.inventory_id=inventory.inventory_id inner join sakila.film on inventory.film_id=film.film_id inner join sakila.address on customer.address_id=address.address_id inner join sakila.city on address.city_id=city.city_id inner join sakila.country on city.country_id=country.country_id"
  page =request.args.get(get_page_parameter(), type=int,default=1)
  limit=20
  offset=page*limit-limit
  if request.method=="POST":
    if request.form['custID']!='' and request.form['custFN']!='' and request.form['custLN'] != '':#111
      query = query + " where customer.customer_id=%s AND customer.first_name=%s AND customer.last_name=%s"
      cursor.execute(query, (request.form['custID'],request.form['custFN'],request.form['custLN']))
      data = cursor.fetchall()
      total = len(data)
      pagination = Pagination()
      return render_template('customersD.html', data=data, pagination=pagination)
    elif request.form['custID'] != '' and request.form['custFN'] != '' and request.form['custLN'] == '':#110
      query = query + " where customer.customer_id=%s AND customer.first_name=%s"
      cursor.execute(query, (request.form['custID'], request.form['custFN']))
      data = cursor.fetchall()
      total = len(data)
      pagination = Pagination()
      return render_template('customersD.html', data=data, pagination=pagination)
    elif request.form['custID'] != '' and request.form['custFN'] == '' and request.form['custLN'] == '':#100
      query = query + " where customer.customer_id=%s"
      cursor.execute(query, (request.form['custID']))
      data = cursor.fetchall()
      total = len(data)
      pagination = Pagination()
      return render_template('customersD.html', data=data, pagination=pagination)
    elif request.form['custID'] == '' and request.form['custFN'] != '' and request.form['custLN'] != '':#011
      query = query + " where customer.first_name=%s AND customer.last_name=%s"
      cursor.execute(query, (request.form['custFN'], request.form['custLN']))
      data = cursor.fetchall()
      total = len(data)
      pagination = Pagination()
      return render_template('customersD.html', data=data, pagination=pagination)
    elif request.form['custID'] == '' and request.form['custFN'] == '' and request.form['custLN'] != '':  # 001
      query = query + " where customer.last_name=%s"
      cursor.execute(query, (request.form['custLN']))
      data = cursor.fetchall()
      total = len(data)
      pagination = Pagination()
      return render_template('customersD.html', data=data, pagination=pagination)
    elif request.form['custID'] == '' and request.form['custFN'] != '' and request.form['custLN'] == '':  # 010
      query = query + " where customer.first_name=%s"
      cursor.execute(query, (request.form['custFN']))
      data = cursor.fetchall()
      total = len(data)
      pagination = Pagination()
      return render_template('customersD.html', data=data, pagination=pagination)
    elif request.form['custID'] != '' and request.form['custFN'] == '' and request.form['custLN'] != '':  # 101
      query = query + " where customer.customer_id=%s AND customer.last_name=%s"
      cursor.execute(query,(request.form['custID'],request.form['custLN']))
      data = cursor.fetchall()
      total = len(data)
      pagination = Pagination()
      return render_template('customersD.html', data=data, pagination=pagination)
  cursor.execute(query)
  data = cursor.fetchall()
  total=len(data)
  cursor.execute(query+" LIMIT %s OFFSET %s", (limit,offset))
  data= cursor.fetchall()
  pagination=Pagination(page=page,per_page=limit,total=total,record_name='detailed')
  return render_template('customersD.html', data=data,pagination=pagination)
@app.route('/reports/')
def reports():
  query="select  customer.first_name,customer.last_name,film.title, inventory.inventory_id, rental.rental_date, rental.return_date from sakila.inventory  inner join sakila.rental on inventory.inventory_id=rental.inventory_id inner join sakila.film on inventory.film_id=film.film_id inner join sakila.customer on rental.customer_id=customer.customer_id where return_date is not null;"
  cursor.execute(query)
  data = cursor.fetchall()
  temp=render_template('pdf.html',data=data)
  report=pdfkit.from_string(temp, configuration=config)
  return Response(report,mimetype="application/pdf")


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

if __name__ == '__main__':
  app.run(debug=True)
