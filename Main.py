import sqlite3
from datetime import datetime
from screeninfo import get_monitors
import kundenanleg
import produkte
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import Main2

# Globale Variablen, um Tabellen zu verfolgen
customer_list_frame = None
product_list_frame = None
conn = sqlite3.connect('datenbank/diedatenbank.db')  # Ersetze 'deine_datenbank.db' durch den Pfad deiner Datenbank
cursor = conn.cursor()

def aktuelle_kw_jahr():
    # Aktuelles Datum
    heute = datetime.today()
    # Kalenderwoche und Jahr nach ISO-8601-Standard
    kw = heute.isocalendar()[1]
    jahr = heute.isocalendar()[0]
    return kw, jahr

def delete_nutzer():
    user_input = input_entry.get().lower().strip()
    if not user_input:
        print("Bitte einen gültigen Namen eingeben.")
        return

    try:
        cursor.execute("DELETE FROM nutzer WHERE name = ?", (user_input,))
        conn.commit()

        if cursor.rowcount > 0:
            input_entry.delete(0, ttk.END)  # Eingabefeld leeren
            print(f"Nutzer '{user_input}' wurde erfolgreich gelöscht.")
        else:
            print(f"Kein Nutzer mit dem Namen '{user_input}' gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

# Funktion, die beim Klicken auf "Start" ausgeführt wird
def start_function():
    global root1
    user_input = input_entry.get().lower().strip()
    if not user_input:
        user_input = "nutzer"
    print(f"Eingegebener Text: {user_input}")

    # Prüfen, ob der Nutzer bereits in der Datenbank existiert
    cursor.execute("SELECT * FROM nutzer WHERE name = ?", (user_input,))
    result = cursor.fetchone()

    # Aktuelles Datum und Uhrzeit
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if result:
        # Nutzer existiert, Datum kann hier optional aktualisiert werden
        cursor.execute("UPDATE nutzer SET datum = ? WHERE name = ?", (current_date, user_input))
        conn.commit()
        print(f"Nutzer {user_input} existiert bereits: {result}")
    else:
        # Nutzer existiert nicht, neuen Eintrag erstellen
        cursor.execute("INSERT INTO nutzer (name, datum) VALUES (?, ?)", (user_input, current_date))
        conn.commit()
        print(f"Neuer Nutzer {user_input} hinzugefügt mit Datum {current_date}")

    # Wechsle zur Main2-Seite
    root1.withdraw()  # Schließe das aktuelle Fenster
    stall, kw, jahr = "Stall 1", 8, 2024
    kw, jahr = aktuelle_kw_jahr()
    print(kw, jahr)
    sql = "SELECT stall, kw, jahr FROM letztereintrag WHERE nutzer = ? ORDER BY id DESC LIMIT 1"
    cursor.execute(sql, (user_input,))
    result = cursor.fetchone()
    if result:
        # Wenn ein Eintrag gefunden wurde, ersetze die Variablen
        stall, kw, jahr = result
        print(f"Eintrag gefunden: Stall: {stall}, KW: {kw}, Jahr: {jahr}")
    else:
        # Wenn kein Eintrag gefunden wurde, bleiben die Variablen unverändert
        print("Kein Eintrag für den angegebenen Nutzer gefunden.")
    # Schließen der Verbindung
    conn.close()
    Main2.starten(stall, kw, jahr, user_input)
    stall = stall.replace(" ", "-")
    #os.system(f"python Main2.py {user_input} {stall} {kw} {jahr}")

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

# Funktion, die ausgeführt wird, wenn ein Benutzer in der Liste angeklickt wird
def on_user_select(event):
    selected_item = user_tree.selection()
    if selected_item:
        user_name = user_tree.item(selected_item, "values")[0]
        input_entry.delete(0, ttk.END)  # Eingabefeld leeren
        input_entry.insert(0, user_name)  # Name einfügen

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
        conn = sqlite3.connect('datenbank/diedatenbank.db')
        cursor = conn.cursor()

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

        conn = sqlite3.connect('datenbank/diedatenbank.db')
        cursor = conn.cursor()

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
        conn.close()
    except Exception as e:
        print(f"Fehler beim Laden der Produktliste: {e}")

# Funktionen für die Anzeige von Kunden- und Produktlisten
def show_customer_list():
    global main_frame
    global customer_list_frame, product_list_frame
    if customer_list_frame is not None:
        customer_list_frame.destroy()
        customer_list_frame = None
        return
    if product_list_frame is not None:
        product_list_frame.destroy()
        product_list_frame = None
    customer_list_frame = ttk.Frame(main_frame, bootstyle="light")
    customer_list_frame.grid(row=0, column=2, padx=20, pady=10, sticky="n")
    customer_label = ttk.Label(customer_list_frame, text="Kundenliste", font=("Helvetica", 18, "bold"))
    customer_label.pack(pady=10)
    customer_tree = ttk.Treeview(customer_list_frame, columns=("name", "telefonnummer", "plz", "stadt", "adresse", "hausnummer", "email", "bemerkung"), show="headings", bootstyle="light")
    customer_tree.heading("name", text="Name")
    customer_tree.heading("telefonnummer", text="Telefonnummer")
    customer_tree.heading("plz", text="PLZ")
    customer_tree.heading("stadt", text="Stadt")
    customer_tree.heading("adresse", text="Adresse")
    customer_tree.heading("hausnummer", text="Hausnummer")
    customer_tree.heading("email", text="E-Mail")
    customer_tree.heading("bemerkung", text="Bemerkung")
    customer_tree.column("#0", width=40)  # Breite der ersten Spalte anpassen
    customer_tree.column("name", width=120)  # Breite der zweiten Spalte anpassen
    customer_tree.column("telefonnummer", width=100)  # Breite der dritten Spalte anpassen
    customer_tree.column("plz", width=60)  # Breite der vierten Spalte anpassen
    customer_tree.pack(fill="both", expand=True)
    load_customer_list(customer_tree)

    # Button zum Erstellen eines neuen Kunden hinzufügen
    create_customer_button = ttk.Button(customer_list_frame, text="Kundenliste bearbeiten", bootstyle="success", command=lambda: kundenanleg.create_gui())
    create_customer_button.pack(pady=10)
    refresh_customer_button = ttk.Button(customer_list_frame, text="Refresh", bootstyle="success", command=lambda: double_show_customer_list())
    refresh_customer_button.pack(pady=10)

def double_show_customer_list():
    show_customer_list()
    show_customer_list()

def double_show_product_list():
    show_product_list()
    show_product_list()

def show_product_list():
    global product_list_frame, customer_list_frame
    if product_list_frame is not None:
        product_list_frame.destroy()
        product_list_frame = None
        return
    if customer_list_frame is not None:
        customer_list_frame.destroy()
        customer_list_frame = None
    product_list_frame = ttk.Frame(main_frame, bootstyle="light")
    product_list_frame.grid(row=0, column=2, padx=20, pady=10, sticky="n")
    product_label = ttk.Label(product_list_frame, text="Produktliste", font=("Helvetica", 18, "bold"))
    product_label.pack(pady=10)
    product_tree = ttk.Treeview(product_list_frame, columns=("artikelnummer", "name", "preis", "bemerkung"), show="headings", bootstyle="light")
    product_tree.heading("artikelnummer", text="Artikelnummer")
    product_tree.heading("name", text="Name")
    product_tree.heading("preis", text="Preis")
    product_tree.heading("bemerkung", text="Bemerkung")
    product_tree.column("#0", width=40)  # Breite der ersten Spalte anpassen
    product_tree.column("artikelnummer", width=100)  # Breite der zweiten Spalte anpassen
    product_tree.column("name", width=150)  # Breite der dritten Spalte anpassen
    product_tree.column("preis", width=60)  # Breite der vierten Spalte anpassen
    product_tree.pack(fill="both", expand=True)
    load_product_list(product_tree)

    # Button zum Erstellen eines neuen Produkts hinzufügen
    create_product_button = ttk.Button(product_list_frame, text="Produktliste bearbeiten", bootstyle="success", command=lambda: produkte.create_gui())
    create_product_button.pack(pady=10)

    refresh_product_button = ttk.Button(product_list_frame, text="Refresh", bootstyle="SUCCESS", command=lambda: double_show_product_list())
    refresh_product_button.pack(pady=10)

input_entry = main_frame = user_tree = root1 = conn = cursor = None
def close_program():
    print("Programm wird geschlossen...")  # Zusätzliche Aktionen
    root1.destroy()  # Hauptfenster schließen
def starten():
    global input_entry, main_frame, user_tree, root1, cursor, conn
    # Verbinde zur SQLite-Datenbank
    conn = sqlite3.connect('datenbank/diedatenbank.db')
    cursor = conn.cursor()
    # Hauptfenster erstellen
    root1 = ttk.Window(themename="sandstone")
    root1.title("Geflügelhof Wellhöfer")
    monitor = get_monitors()[0]
    root1.state("zoomed")
    root1.configure(bg="#f5f5f5")

    title_frame = ttk.Frame(root1, bootstyle="light")
    title_frame.pack(fill="both")
    title_label = ttk.Label(title_frame, text="Geflügelhof Wellhöfer", font=("Helvetica", 28, "bold"), background="#f5f5f5")
    title_label.pack(pady=10)

    main_frame = ttk.Frame(root1, bootstyle="light", borderwidth=2, relief="sunken")
    main_frame.pack(padx=20, pady=20)

    left_frame = ttk.Frame(main_frame, bootstyle="light", borderwidth=2, relief="sunken")
    left_frame.grid(row=0, column=0, padx=20, pady=10, sticky="n")

    user_list_frame = ttk.Frame(left_frame, bootstyle="light")
    user_list_frame.pack(pady=10)

    user_list_label = ttk.Label(user_list_frame, text="Benutzerliste", font=("Helvetica", 14, "bold"), background="#f5f5f5")
    user_list_label.pack(pady=15)

    user_tree = ttk.Treeview(user_list_frame, columns=("name",), show="headings", height=10, bootstyle="light")
    user_tree.heading("name", text="Zum auswählen antippen")
    user_tree.column("name", width=190, anchor="center")
    user_tree.pack(fill="both", expand=True)

    user_scrollbar = ttk.Scrollbar(user_list_frame, orient="vertical", command=user_tree.yview)
    user_tree.bind("<<TreeviewSelect>>", on_user_select)
    load_user_list(user_tree)

    input_entry = ttk.Entry(left_frame, font=("Helvetica", 14), width=16)
    input_entry.pack(pady=10)
    # Label "Anmelden" hinzufügen
    login_label = ttk.Label(left_frame, text="Anmelden", font=("Helvetica", 16, "bold"), background="#f5f5f5")
    login_label.pack(pady=10)


    # Benutzerdefinierten Style erstellen
    style = ttk.Style()
    style.configure("Custom.TFrame", background="#f5f5f5")  # Hintergrundfarbe definieren

    # Frame für die oberen Buttons (Start und Löschen)
    upper_button_frame = ttk.Frame(left_frame, style="Custom.TFrame")  # Style anwenden
    upper_button_frame.pack(pady=10)

    # Start Button
    start_button = ttk.Button(upper_button_frame, text="Start", bootstyle="success", command=start_function)
    start_button.pack(side="left", padx=10)

    # Delete Button
    delete_button = ttk.Button(upper_button_frame, text="Löschen", bootstyle="danger", command=delete_nutzer)
    delete_button.pack(side="left", padx=10)

    # Untere Buttons (Kundenliste und Produktliste)
    customer_button = ttk.Button(left_frame, text="Kundenliste anzeigen", bootstyle="primary", command=show_customer_list)
    customer_button.pack(pady=10, padx=10, fill="both")

    product_button = ttk.Button(left_frame, text="Produktliste anzeigen", bootstyle="primary", command=show_product_list)
    product_button.pack(pady=10, padx=10, fill="both")



    close_button = ttk.Button(left_frame, text="Schließen", bootstyle="danger",command=close_program)
    close_button.pack(pady=10, padx=10, fill="both")

    root1.mainloop()
    conn.close()

if __name__ == "__main__":
    starten()