import sqlite3
conn = sqlite3.connect(r'C:\Users\Temo 2\Desktop\курсовая финальный билд (почти)\course prj(flask)\shop.db')
cur = conn.cursor()
cur.execute("DELETE  FROM Item WHERE iditem > 0;")
conn.commit()