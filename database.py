import psycopg2
#connect to database

conn = psycopg2.connect(host="localhost",dbname="myduka_system",user="postgres",password="mubby",port=5432)
cur = conn.cursor()
# def get_products():
   
#     cur.execute("SELECT * FROM products")
#     prods= cur.fetchall()
#     for prod in prods:
#         print(prod)
   

# get_products()    

# TO GET SALES
# def get_sales():
    
#     cur.execute("SELECT * FROM  sales")
#     sales=cur.fetchall()
#     for sale in sales:
#         print(sale)

# get_sales() 

def get_data(table_name):
    select =f"select * from {table_name}"
  
    cur.execute(select)
    data=cur.fetchall()
    return data

# get_data('sales')
# get_data('products')

#insert data
def insert_products(values):
    products="insert into products(name,buying_price,\
         selling_price,stock_quantity)values(%s,%s,%s,%s);"
    cur.execute(products,values)
    conn.commit()



def register_users(values):
      users="insert into users (full_name,email,password)\
        values(%s,%s,%s)" 
      cur.execute(users,values)
      conn.commit() 

def check_email(email):
      query='select exists(select email from users where email= %s )'
      cur.execute(query,(email,))
      exist=cur.fetchone()[0]
      return exist
def check_logins(email,password):
      query="select * from users where email=%s and password=%s;"
      cur.execute(query,(email,password,))
      check=cur.fetchone()[0]
      return check

# product_value=("potato",600,1000,10) 
# insert_products(product_value)
# get_data('sales')
# get_data('products') 

#connect sales
# def  insert_sales(values):
#          sales= "insert into sales(pid,\
#             quantity,created)values(%s,%s,now())"
#          cur.execute(sales,values)
#          conn.commit()
# sale_value=(2,500)
# insert_sales(sale_value)
# get_data('sales')  
def insert_sales(values):
    insert="INSERT INTO sales( pid, quantity, created_date)values(%s,%s,now());"
    cur.execute(insert,values)
    conn.commit()

# function to display every sale
def sales_product():
      display='select pr.name,sum(pr.selling_price*sl.quantity)\
          as res from products as pr join sales as sl on pr.id=sl.pid group by pr.name;'
      cur.execute(display)
      data=cur.fetchall()
      print (data)
      return data

# displaye sales by name of e prducts
def product_name(b):
      pr_name='select p.name from products as p where id=%s;'
      cur.execute(pr_name,(b,))
      d=cur.fetchone()
      return d


# display profit product
def profit_product():
      display ='select p.name,sum(((selling_price-buying_price)*quantity))\
          as profit from products as p join sales as s on s.pid=p.id group by p.name;' 
      cur.execute(display)
      data=cur.fetchall()
      return data  

def sales_day():
      display='select date(created_date) as day ,sum (selling_price *quantity)as slp\
          from products as p join sales as s on s.pid=p.id group by day order by day'
      cur.execute(display)
      data=cur.fetchall()
      return data


def profit_day():
     display= 'select date(created_date) as day ,sum(((selling_price-buying_price)*quantity)) as profit \
        from products as p join sales as s on s.pid=p.id group by day order by day;'
     cur.execute(display)
     data=cur.fetchall()
     return data


#getting sales per day
def sales_per_day():
      display_total_sales='select date (created_date) as day ,sum((selling_price )*quantity) as sale from products as p \
            join sales as s on s.pid=p.id where date (created_date)=current_date group by day;'
      cur.execute(display_total_sales)
      data=cur.fetchall()
      return data
#getting total sales  of all time
def  total_sales():
      display_total_sales="Select sum(selling_price*quantity) as Total_Sales From products as p \
      join sales as s on s.pid=pid;"
      cur.execute(display_total_sales)
      data=cur.fetchall()
      return data
#display profit of today
def  todays_profit():
    display_todays_profit="select to_char(CURRENT_DATE,'YYYY/MM/DD') as Date_only,round(sum((selling_price-buying_price)*quantity),2)as profit from sales as s\
      join products as p on s.pid=p.id group by date_only order by date_only limit 1;"
    cur.execute(display_todays_profit)
    data=cur.fetchall()
    return data
# display total profit  of all time
def total_profit():
     display_total_profit = "select round (sum(((selling_price-buying_price)*quantity)),2) as Total_Profits from products as p join sales as s on s.pid=p.id;"
     cur.execute(display_total_profit)
     data=cur.fetchall()
     return data
#this  query calculates the remaining stockfor each product
def get_remaining_stock_per_product():
     query="SELECT p.name,stock_quantity-COALESCE(SUM(s.quantity),0)as remaining_stock FROM products as p LEFT JOIN sales as s on p.id=s.pid GROUP BY p.id,p.name,stock_quantity ORDER BY remaining_stock DESC;"
     cur.execute(query)
     result=cur.fetchall()
     return result

# this function is used to update the quantity in the inventory table when a sale is