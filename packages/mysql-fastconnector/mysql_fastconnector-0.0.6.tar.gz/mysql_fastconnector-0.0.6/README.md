### mysql_fastconnector

"mysql_fastconnector" is a module or library designed to simplify MySQL database interactions and CRUD operations.

if you're considering using "mysql_fastconnector" in your projects, it's essential to refer to its resources to get a more detailed understanding of its capabilities, how to integrate it into your applications, and any specific benefits it offers compared to other MySQL connectors or libraries. Additionally, checking for updates and community feedback can help you gauge its reliability and suitability for your needs.


## Required Mysql client and connector

```
pip install mysqlclient
pip install mysql-connector-python
pip install pymysql

```

## Mysql Database connection example

```python
from  mysql_fastconnector import  Model ,table,query

obj=Model.connect({'host': "127.0.0.1",'user': "username",'password': "password",'db': "dbname"})

```

## Mysql Query Example

```python

res=query("select * from users").fetchAll()
for v in res: 
   print(res)

```

## Object based Query Example

```python

res=table("players").all()
res=table("players").one()
res=table("players").fromTable('pk').where('pk=37').all()
res=table("players").fromTable('pk').where('pk=37').limit(0,50).all()
res=table("players").fromTable('players.pk').leftJoin('player_images','player_id=players.pk').where('players.pk=37').limit(0,50).all()
res=table("players").fromTable('players.pk').rightJoin('player_images','player_id=players.pk').where('players.pk=37').limit(0,50).all()
for v in res:   
    print(res)

## Print Query Example

users=table("users")
users.printQuery=True
res=users.fromTable('users.pk').leftJoin('images','user_id=users.pk').where('users.pk=27').limit(50,0).all()

for v in res:   
    print(res)

## Sub Query Example

users=table("users")
users.printQuery=True
users.subQuery("(select count(*) from users ) as m,")
res=users.fromTable('users.pk').leftJoin('images','user_id=users.pk').where('users.pk=27').limit(50,0).all()

for v in res:   
    print(res)

```

## Insert Example

```python

id=obj.table("players").insert({'first_name':'r222222222','last_name':'r33333333','id':'555','email':'aa@gmail.com','mobile':'987654321'}).getId()
print(id)

ids=obj.table("players").insertMany([{'first_name':'r222222222','last_name':'r33333333','id':'555','email':'aa@gmail.com','mobile':'987654321'},{'first_name':'r222222223333333333','last_name':'r33333333','id':'555','email':'aa@gmail.com','mobile':'987654321'}])
print(ids)

```

## update Example

```python

id=obj.table("players").update({'first_name':'0000000000000000000','last_name':'r33333333','id':'555','email':'aa@gmail.com','mobile':'987654321'},"pk=66")


```

## delete Example

```python

table("players").delete("pk=66")

```

## Any help , contact me
```
email : ilayaraja.python@gmail.com

```

