from datetime import datetime
import sqlite3

conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')  # Ersetze 'deine_datenbank.db' durch den Pfad deiner Datenbank
cursor = conn.cursor()
def aktuelle_kw_jahr():
    # Aktuelles Datum
    heute = datetime.today()
    # Kalenderwoche und Jahr nach ISO-8601-Standard
    kw = heute.isocalendar()[1]
    jahr = heute.isocalendar()[0]
    return kw, jahr
# Funktion zum Laden der Benutzerliste aus der Datenbank
def load_user_list(tree):
    try:
        # Benutzer aus der Datenbank abrufen
        cursor.execute("SELECT name FROM nutzer ORDER BY name ASC")
        users = cursor.fetchall()

        # Vorhandene Einträge in der Treeview entfernen
        for item in tree.get_children():
            tree.delete(item)

        # Neue Einträge hinzufügen
        for user in users:
            tree.insert("", "end", values=(user[0],))
    except sqlite3.Error as e:
        print(f"Fehler beim Laden der Benutzerliste: {e}")
def load_customer_list(tree):
    try:
        # Vorhandene Einträge in der Treeview entfernen
        for item in tree.get_children():
            tree.delete(item)

        # 100 Beispielkunden dynamisch generieren
        example_customers = [
            {
                "name": f"Kunde {i}",
                "telefonnummer": f"012345678{i:02d}",
                "plz": f"{10000 + i}",
                "stadt": f"Stadt {i}",
                "adresse": f"Straße {i}",
                "hausnummer": f"{i}",
                "email": f"kunde{i}@beispiel.de",
                "bemerkung": f"Bemerkung {i}"
            }
            for i in range(1)
        ]
        # Alle Einträge aus der Tabelle 'kunden' abfragen
        cursor.execute("SELECT * FROM kunden")
        alle_kunden = cursor.fetchall()
        keinekunden = True
        # Einträge in einer Schleife ausgeben
        for eintrag in alle_kunden:
            keinekunden = False
            tree.insert(
                "",
                "end",
                values=(eintrag[1], eintrag[6], eintrag[2], eintrag[5], eintrag[3], eintrag[4], eintrag[7], eintrag[8]))
        # Beispielkunden in die Treeview einfügen
        if keinekunden:
            for customer in example_customers:
                tree.insert(
                    "",
                    "end",
                    values=(
                        customer["name"],
                        customer["telefonnummer"],
                        customer["plz"],
                        customer["stadt"],
                        customer["adresse"],
                        customer["hausnummer"],
                        customer["email"],
                        customer["bemerkung"]
                    )
                )
    except Exception as e:
        print(f"Fehler beim Laden der Kundenliste: {e}")

# Funktion zum Laden der Produktliste aus der Datenbank
def load_product_list(tree):
    try:
        # Vorhandene Einträge in der Treeview entfernen
        for item in tree.get_children():
            tree.delete(item)
        # Alle Einträge aus der Tabelle 'produkte' abfragen
        cursor.execute("SELECT * FROM produkte")
        alle_produkte = cursor.fetchall()

        # Wenn keine Produkte vorhanden sind, Beispielprodukte anzeigen
        if not alle_produkte:
            example_products = [
                {
                    "artikelnummer": f"P{str(i).zfill(3)}",
                    "name": f"Produkt {i}",
                    "preis": f"{9.99 + i:.2f}€",
                    "bemerkung": f"Bemerkung {i}"
                }
                for i in range(1)
            ]
            for product in example_products:
                tree.insert(
                    "",
                    "end",
                    values=(
                        product["artikelnummer"],
                        product["name"],
                        product["preis"],
                        product["bemerkung"]
                    )
                )
        else:
            # Einträge in einer Schleife ausgeben
            for eintrag in alle_produkte:
                tree.insert(
                    "",
                    "end",
                    values=(eintrag[0], eintrag[1], f"{eintrag[2]:.2f}€", eintrag[3])
                )
    except Exception as e:
        print(f"Fehler beim Laden der Produktliste: {e}")

