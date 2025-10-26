from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from urllib.parse import quote_plus

db = SQLAlchemy()

def init_app(app: Flask):
    USER = "sa2"
    PASS = "123456"
    HOST = r"ALEV\MSSQLSERVER01"   # usa "ALEV\\MSSQLSERVER01" si falla
    DB   = "MassielQA"
    DRIVER = "ODBC Driver 17 for SQL Server"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mssql+pyodbc://{USER}:{PASS}@{HOST}/{DB}"
        f"?driver={quote_plus(DRIVER)}&TrustServerCertificate=yes"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True  # ver queries SQL

    db.init_app(app)
    return app
