import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="appuser",
        password="shamila@123",
        database="mood_recommendation"
    )