import pyodbc

conn_string = (
    r'DRIVER={SQL Server};'
    r'SERVER=JOAOHERMENEGILD;'
    r'DATABASE=FazendaUrbanaLotus;'

)

conn = pyodbc.connect(conn_string)
cursor = conn.cursor()

