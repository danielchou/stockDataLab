import pyodbc

def fmtParentheses(v):
    return "" if(v=="") else f"({v})"

def fmtSquare(v):
    return "" if(v=="") else f"[{v}] "

def fmtNull(v):
    return " NULL" if(v=="Y") else " NOT NULL"


    #寫入到資料庫中.....
def ExecuteMSSQL(sql):
	server = 'UBT\SQLEXPRESS'
	database = 'DB_9AB840_Vague'
	username = 'DB_9AB840_Vague_admin'
	password = 'Apple005'
	driver= '{ODBC Driver 17 for SQL Server}'
	cnxn = pyodbc.connect(f'DRIVER={driver};PORT=1433;SERVER={server};PORT=1443;DATABASE={database};UID={username};PWD={password}')
	cursor = cnxn.cursor()

	cursor.execute(sql)
	cursor.commit()
	return cnxn

def connMSSQL(db):
	# server = 'UBT\SQLEXPRESS'
	server = "DESKTOP-T0P44I2"
	database = "newcti"
	username = 'sa'
	password = 'Passw0rd'
	driver= '{ODBC Driver 17 for SQL Server}'
	ss = 'DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password
	return ss