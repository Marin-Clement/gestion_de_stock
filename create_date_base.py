import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Minecraft01@",
  database="boutique"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE produit (id INT AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(255), description TEXT, prix INT, quantite INT, id_categorie INT)")

mycursor.execute("CREATE TABLE categorie (id INT AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(255))")


