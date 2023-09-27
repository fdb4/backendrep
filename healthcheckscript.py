
from flask import Flask, render_template, request, Response
from flaskext.mysql import MySQL
import cryptography
import pdfkit
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
      query = "call sakila.film_in_stock((select film_id from sakila.film where title=\"" + request.form['filmN'] + "\")," + request.form['storeID'] + ",@count)"
      cursor.execute(query)
      data = cursor.fetchall()
      return render_template("movies.html",inStock=data)
    elif request.form['SOR']=="1":
      query="insert into sakila.rental(rental_date, inventory_id, customer_id, staff_id) values(NOW(), "+request.form['invID']+", "+request.form['custID']+", 1);"
      cursor.execute(query)
      print(query)
      conn.commit()
      return render_template("movies.html")
    elif request.form['SOR']=="2":

      query="select film.title,film.description,film.release_year,film.length,film.rating,film.special_features , category.name as \"category\", actor.first_name,actor.last_name from sakila.film inner join sakila.film_category on film.film_id=film_category.film_id inner join sakila.category on category.category_id=film_category.category_id inner join sakila.film_actor on film.film_id=film_actor.film_id inner join sakila.actor on film_actor.actor_id=actor.actor_id"
      if request.form['Title']!='':
        query = query + "where film.title=\""+request.form['Title']+"\""
        if request.form['Category']!='':
          query = query + " AND category.name=\"" + request.form['Category'] + "\""
          if request.form['ActorFN']!='':
            query = query + " AND actor.first_name=\"" + request.form['ActorFN'] + "\""
            if request.form['ActorLN']!='':
              query = query + " AND actor.last_name=\"" + request.form['ActorLN'] + "\""
          elif request.form['ActorLN']!='':
            query = query + " AND actor.last_name=\"" + request.form['ActorLN'] + "\""
        elif request.form['ActorFN'] != '':
          query = query + " AND actor.first_name=\"" + request.form['ActorFN'] + "\""
          if request.form['ActorLN'] != '':
            query = query + " AND actor.last_name=\"" + request.form['ActorLN'] + "\""
        elif request.form['ActorLN'] != '':
          query = query + " AND actor.last_name=\"" + request.form['ActorLN'] + "\""
      elif request.form['Category'] != '':
        query = query + "where category.name=\"" + request.form['Category'] + "\""
        if request.form['ActorFN'] != '':
          query = query + " AND actor.first_name=\"" + request.form['ActorFN'] + "\""
          if request.form['ActorLN'] != '':
            query = query + " AND actor.last_name=\"" + request.form['ActorLN'] + "\""
        elif request.form['ActorLN'] != '':
          query = query + " AND actor.last_name=\"" + request.form['ActorLN'] + "\""
      elif request.form['ActorFN'] != '':
          query = query + "where actor.first_name=\"" + request.form['ActorFN'] + "\""
          if request.form['ActorLN'] != '':
            query = query + " AND actor.last_name=\"" + request.form['ActorLN'] + "\""
      elif request.form['ActorLN'] != '':
        query = query + "where actor.last_name=\"" + request.form['ActorLN'] + "\""
      cursor.execute(query)
      data = cursor.fetchall()
      print(query)
      print(data)
      return render_template("movies.html",data=data)
  return render_template("movies.html")

@app.route('/customers/',methods=['GET','POST'])
def customers():
  query="select * from sakila.customer"
  if request.method=="POST":
    if request.form['CRUD']=='1':
      query = "insert into sakila.city (city,country_id) values(\"" + request.form['city'] + "\", (select country_id from sakila.country where country=\"" + request.form['country'] + "\"));"
      cursor.execute(query)
      query = "insert into sakila.address (address, address2, district, city_id, postal_code, phone, location) values(\"" +request.form['address'] + "\", \"" + request.form['address2'] + "\", \"" + request.form['district'] + "\" ,(select city_id from sakila.city order by city_id DESC limit 1), \"" + request.form['postal'] + "\", \"" + request.form['phone'] + "\", ST_GeomFromText('POLYGON((0 5, 2 5, 2 7, 0 7, 0 5))'));"
      cursor.execute(query)
      query = "insert into sakila.customer (store_id, first_name, last_name, email, address_id, active) values(" + request.form['storeID'] + ", \"" + request.form['custFN'] + "\", \"" + request.form['custLN'] + "\" ,\"" + request.form['email'] + "\",(select address_id from sakila.address order by address_id DESC limit 1) , 1);"
      print(query)
      cursor.execute(query)
      conn.commit()
      query = "select * from sakila.customer"
    if request.form['CRUD']=='2':
      query = "update sakila.customer Set store_id=\"" + request.form['storeID2'] + "\", first_name=\"" + request.form['custFN2'] + "\",last_name=\"" + request.form['custLN2'] + "\",email=\"" + request.form['email2'] + "\" where customer.customer_id=" + request.form['custID2'] + ";"
      cursor.execute(query)
      query = "update sakila.address Set address=\"" + request.form['address2'] + "\" , address2=\"" + request.form['address22'] + "\", district=\"" + request.form['district2'] + "\",postal_code=\"" + request.form['postal2'] + "\",phone=\"" + request.form['phone2'] + "\" where address_id=(select * from (select address.address_id from sakila.customer inner join sakila.address on customer.address_id=address.address_id inner join sakila.city on address.city_id=city.city_id where customer.customer_id=" + request.form['custID2'] + ")as c);"
      cursor.execute(query)
      query = "update sakila.city Set city=\"" + request.form['city2'] + "\" , country_id=(select country_id from sakila.country where country=\"" + request.form['country2'] + "\") where city.city_id=(select * from(select city.city_id from sakila.customer inner join sakila.address on customer.address_id=address.address_id inner join sakila.city on address.city_id=city.city_id where customer.customer_id=" + request.form['custID2'] + ")as c);"
      cursor.execute(query)
      conn.commit()
      query = "select * from sakila.customer"
    if request.form['CRUD']=='3':
      query = "delete from sakila.customer where customer_id=" + request.form['custID3'] + ";"
      cursor.execute(query)
      query = "delete from sakila.address where address_id=" + request.form['addressID3'] + ";"
      cursor.execute(query)
      query = "delete from sakila.city where city_id=" + request.form['cityID3'] + ";"
      cursor.execute(query)
      conn.commit()
      return render_template('customers.html')
    if request.form['CRUD']=='0':
      if request.form['custID']!='':
        query = query + " where customer.customer_id=" + request.form['custID']
        if request.form['custFN']!='':
          query=query+" AND customer.first_name=\""+request.form['custFN']+"\""
          if request.form['custLN'] != '':
            query = query + " AND customer.last_name=\"" + request.form['custLN'] + "\""
        if request.form['custLN']!='':
          query = query + " AND customer.last_name=\"" + request.form['custLN'] + "\""
      elif request.form['custFN']!='':
        query=query+" where customer.first_name=\""+request.form['custFN']+"\""
        if request.form['custLN']!='':
          query = query + " AND customer.last_name=\"" + request.form['custLN'] + "\""
      elif request.form['custLN']!='':
        query=query+" where customer.last_name=\""+request.form['custLN']+"\""
  print(query)
  cursor.execute(query)
  data=cursor.fetchall()
  print(data)
  query = "select country from sakila.country;"
  cursor.execute(query)
  country = cursor.fetchall()
  return render_template('customers.html', data=data,country=country)

@app.route('/custDetails/',methods=['GET','POST'])
def custD():
  query = "select customer.customer_id, address.address_id, city.city_id, customer.first_name, customer.last_name, address.address, address.address2,address.phone, address.district,city.city, film.title, rental.rental_date, rental.return_date from  sakila.rental  inner join sakila.customer on rental.customer_id=customer.customer_id inner join sakila.inventory on rental.inventory_id=inventory.inventory_id inner join sakila.film on inventory.film_id=film.film_id inner join sakila.address on customer.address_id=address.address_id inner join sakila.city on address.city_id=city.city_id inner join sakila.country on city.country_id=country.country_id"
  if request.method=="POST":
    if request.form['custID']!='':
      query = query + " where customer.customer_id=" + request.form['custID']
      if request.form['custFN']!='':
        query=query+" AND customer.first_name=\""+request.form['custFN']+"\""
        if request.form['custLN'] != '':
          query = query + " AND customer.last_name=\"" + request.form['custLN'] + "\""
      if request.form['custLN']!='':
        query = query + " AND customer.last_name=\"" + request.form['custLN'] + "\""
    elif request.form['custFN']!='':
      query=query+" where customer.first_name=\""+request.form['custFN']+"\""
      if request.form['custLN']!='':
        query = query + " AND customer.last_name=\"" + request.form['custLN'] + "\""
    elif request.form['custLN']!='':
      query=query+" where customer.last_name=\""+request.form['custLN']+"\""
  cursor.execute(query)
  data = cursor.fetchall()
  return render_template('customersD.html', data=data)
@app.route('/reports/')
def reports():
  query="select  customer.first_name,customer.last_name,film.title, inventory.inventory_id, rental.rental_date, rental.return_date from sakila.inventory  inner join sakila.rental on inventory.inventory_id=rental.inventory_id inner join sakila.film on inventory.film_id=film.film_id inner join sakila.customer on rental.customer_id=customer.customer_id where return_date is not null;"
  cursor.execute(query)
  data = cursor.fetchall()
  temp=render_template('pdf.html',data=data)
  report=pdfkit.from_string(temp, configuration=config)
  return Response(report,mimetype="application/pdf")



if __name__ == '__main__':
  app.run(debug=True)
