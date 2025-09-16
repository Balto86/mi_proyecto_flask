import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

class DBManager:
    def __init__(self):
        self.conn = None

    def get_connection(self):
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DB"),
                port=int(os.getenv("MYSQL_PORT"))
            )
            return self.conn
        except mysql.connector.Error as err:
            print(f"Error de conexión a MySQL: {err}")
            return None

    def close_connection(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Conexión a MySQL cerrada.")