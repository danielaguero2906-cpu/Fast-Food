import  pyodbc

try:
    connection =  pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-JKQOT32P\\SQLEXPRESS;"
        "DATABASE=FastFoodDB;"     
        "Trusted_Connection=yes;"
    )

    print("Conexión exitosa a SQL Server")

    cursor = connection.cursor()
    cursor.close()
    connection.close()

except Exception as e:
    print("Error al conectar:", e)
