import mysql.connector

try:
    con = mysql.connector.connect(
        host='localhost',
        database='animal_api_db',
        user='animal_api_user',
        password='secure_password123'
    )
    if con.is_connected():
        print("Verbindung erfolgreich!")
        con.close()
        print("Verbindung geschlossen.")
except mysql.connector.Error as e:
    print(f"Fehler aufgetreten: {e}")