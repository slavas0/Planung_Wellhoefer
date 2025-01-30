import sqlite3

# Verbindung zur SQLite-Datenbank herstellen (die Datei wird erstellt, wenn sie noch nicht existiert)
conn = sqlite3.connect('diedatenbank.db')  # Ersetze den Dateinamen nach Bedarf
cursor = conn.cursor()

# Tabelle: nutzer erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS nutzer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL,
    datum DATETIME NOT NULL
);
''')

# Tabelle: eintrag erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS eintrag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stall TEXT NOT NULL,
    kw INTEGER NOT NULL,
    jahr INTEGER NOT NULL,
    name TEXT NOT NULL,
    telefonnummer TEXT NOT NULL,
    braune INTEGER NOT NULL,
    weise INTEGER NOT NULL,
    verfahren TEXT NOT NULL,
    preis TEXT NOT NULL,
    bemerkung TEXT
);
''')

# Tabelle: letztereintrag erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS letztereintrag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kw INTEGER NOT NULL,
    jahr INTEGER NOT NULL,
    nutzer TEXT NOT NULL,
    stall TEXT NOT NULL
);
''')

# Tabelle: inventar erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kw INTEGER NOT NULL,
    stall TEXT NOT NULL,
    jahr INTEGER NOT NULL,
    weiss INTEGER NOT NULL,
    braun INTEGER NOT NULL,
    lila INTEGER NOT NULL
);
''')

# Tabelle: produkte erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS produkte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artikelnummer TEXT NOT NULL,
    name TEXT NOT NULL,
    preis INTEGER NOT NULL,
    bemerkung TEXT
);
''')
# Tabelle: kunden erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS kunden (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    plz INTEGER NOT NULL,
    adresse TEXT NOT NULL,
    hausnummer TEXT NOT NULL,
    stadt TEXT NOT NULL,
    telefonnummer TEXT NOT NULL,
    email TEXT NOT NULL,
    bemerkung TEXT
);
''')
# Änderungen speichern
conn.commit()

# Verbindung schließen
conn.close()

print("Datenbank und Tabellen wurden erfolgreich erstellt.")
