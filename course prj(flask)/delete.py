import sqlite3
conn = sqlite3.connect(r'C:\Users\Limon\Desktop\course prj(flask)\shop.db')
cur = conn.cursor()
cur.execute("SELECT * FROM item;")
conn.commit()