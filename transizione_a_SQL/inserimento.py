import json
import sqlite3


dict_gare = json.load(open('../script/dizionario_gare.json'))
conn = sqlite3.connect('bozza.db')
cursor = conn.cursor()

res = cursor.execute("SELECT * FROM eventi")
print(res.fetchall())

exit()

# Insert data into table
insert_query = """
INSERT INTO "eventi" (id, nome, tipo, classifica, vento, codice)
VALUES (?, ?, ?, ?, ?, ?)
"""

for evento in dict_gare.keys():
    cursor.execute(insert_query, (
        evento,
        evento,
        dict_gare[evento]['tipo'],
        dict_gare[evento]['classifica'],
        dict_gare[evento]['vento'],
        dict_gare[evento]['codice']
        ))


res = cursor.execute("SELECT * FROM eventi")
print(res.fetchall())


# Commit the transaction
conn.commit()

# Close the connection
conn.close()


'''
'''

