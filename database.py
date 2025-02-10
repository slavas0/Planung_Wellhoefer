
import pandas as pd
import sqlite3
conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
cursor = conn.cursor()


def tabelle_ausgeben(tab):
    if tab == "alle":
        query = "SELECT name FROM sqlite_master WHERE type='table';"
    else:
        query = f"SELECT * FROM {tab}"
    df = pd.read_sql_query(query, conn)
    #print(f"Tabelle {tab}")
    #print(df)
    df.to_csv(f"datenbank/{tab}.csv")
def tabellen_ausgeben():
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    df = pd.read_sql_query(query, conn)
    for name in df['name']:
        if name != "sqlite_sequence":
            tabelle_ausgeben(name)

def eintrag_updaten(id,stall,KW,jahr,name,telefonnummer,braune,weise,verfahren,preis,bemerkung):
    query = """
        UPDATE eintrag
        SET
            stall = ?,
            KW = ?,
            jahr = ?,
            name = ?,
            telefonnummer = ?,
            braune = ?,
            weise = ?,
            verfahren = ?,
            preis = ?,
            bemerkung = ?
        WHERE
            id = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (stall, KW, jahr, name, telefonnummer, braune, weise, verfahren, preis, bemerkung, id))
def datenbank_erstellen():
    query = """CREATE TABLE letztereintrag (
        id SERIAL PRIMARY KEY,
        kw INTEGER NOT NULL,
        jahr INTEGER, 
        nutzer VARCHAR(30)        
        );"""
    cursor = conn.cursor()
    cursor.execute(query)
    query = """CREATE TABLE nutzer (
            id SERIAL PRIMARY KEY,
            name VARCHAR(30)        
            );"""
    cursor = conn.cursor()
    cursor.execute(query)
def findeid(name):
    query = f"SELECT * FROM letztereintrag WHERE nutzer = {name} ORDER BY id DESC LIMIT 10;"
    df = pd.read_sql_query(query, conn)
    print(df['name'])
def create_inventar_table():
    """Erstellt die Tabelle 'inventar' in der Datenbank.

    Die Tabelle enthält Spalten für:
    * kw: Kalenderwoche
    * stall: Stall
    * jahr: Jahr
    * weiss: Menge Weiß
    * braun: Menge Braun
    * lila: Menge Lila
    """

    conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/mydatabase.db')
    cursor = conn.cursor()

    # SQL-Anweisung zum Erstellen der Tabelle
    sql = "DELETE FROM letztereintrag WHERE stall = Stall-2"
    cursor.execute(sql)

    conn.commit()

# Rufe die Funktion auf, um die Tabelle zu erstellen
#create_inventar_table()



#cursor.execute('DROP TABLE IF EXISTS letztereintrag;')

conn.commit()

#sql = "CREATE TABLE produkte (    Artikelnummer TEXT PRIMARY KEY,    Name TEXT NOT NULL,    Preis REAL NOT NULL,    Bemerkung TEXT);"
#sql = "DROP TABLE produkte"
#sql = "DELETE FROM letztereintrag WHERE id NOT IN (SELECT MAX(id) FROM letztereintrag GROUP BY nutzer, stall, kw, jahr);"
#cursor.execute(sql)

# Alle Tabellen in der Datenbank
#tabellen = cursor.fetchall()
# Durch jede Tabelle iterieren und deren Spalten und Datentypen abfragen
#for tabelle in tabellen:
#    tabelle_name = tabelle[0]
#    print(f"Tabelle: {tabelle_name}")
#
#    # Abfrage, um die Spalten und Datentypen der aktuellen Tabelle zu erhalten
#    cursor.execute(f"PRAGMA table_info({tabelle_name});")
#    spalten = cursor.fetchall()
#
#
    # Ausgabe der Spaltennamen und Datentypen
 #   for spalte in spalten:
  #      spalten_name = spalte[1]
   #     datentyp = spalte[2]
    #    print(f"  Spalte: {spalten_name}, Datentyp: {datentyp}")

    #print()  # Leerzeile für bessere Lesbarkeit



conn.commit()
#findeid("peter")
#datenbank_erstellen()
#eintrag_updaten(0, "Stall 2", "7", "2024", "Günter Jauch", "+491794392737", "5", "7", "per Backflip", "6,50€", "Dies ist ein Testeintrag")

#zeige Tabellen
#'kunden', 'eintrag' oder 'alle'
#tabelle_ausgeben("alle")
#tabelle_ausgeben("kunden")
#tabelle_ausgeben("eintrag")

tabellen_ausgeben()



#speichern und Verbindung schließen
conn.commit()
conn.close()