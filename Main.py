import tkinter
import sqlite3
from tkinter import ttk
from datetime import datetime
#import os
from screeninfo import get_monitors
#import kundenanleg
#import produkte
import hilfe

# Globale Variablen, um Tabellen zu verfolgen
customer_list_frame = None
product_list_frame = None

def delete_nutzer():
    user_input = input_entry.get().lower().strip()
    if not user_input:
        print("Bitte einen gültigen Namen eingeben.")
        return

    try:
        cursor.execute("DELETE FROM nutzer WHERE name = ?", (user_input,))
        conn.commit()

        if cursor.rowcount > 0:
            input_entry.delete(0, tkinter.END)  # Eingabefeld leeren
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
    root1.destroy()  # Schließe das aktuelle Fenster
    stall, kw, jahr = "Stall 1", 8, 2024
    kw, jahr = hilfe.aktuelle_kw_jahr()
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
    import Main2
    Main2.starten(stall, kw, jahr, user_input)
    stall = stall.replace(" ", "-")
    #os.system(f"python Main2.py {user_input} {stall} {kw} {jahr}")

# Funktion, die ausgeführt wird, wenn ein Benutzer in der Liste angeklickt wird
def on_user_select(event):
    selected_item = user_tree.selection()
    if selected_item:
        user_name = user_tree.item(selected_item, "values")[0]
        input_entry.delete(0, tkinter.END)  # Eingabefeld leeren
        input_entry.insert(0, user_name)  # Name einfügen

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
    customer_list_frame = tkinter.Frame(main_frame, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
    customer_list_frame.grid(row=0, column=2, padx=20, pady=10, sticky="n")
    customer_label = tkinter.Label(customer_list_frame, text="Kundenliste", font=("Helvetica", 18, "bold"), bg="#ffffff", fg="#333333")
    customer_label.pack(pady=10)
    customer_tree = ttk.Treeview(customer_list_frame, columns=("name", "telefonnummer", "plz", "stadt", "adresse", "hausnummer", "email", "bemerkung"), show="headings")
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
    hilfe.load_customer_list(customer_tree)

    # Button zum Erstellen eines neuen Kunden hinzufügen
    create_customer_button = ttk.Button(customer_list_frame, text="Kundenliste bearbeiten", style="Accent.TButton", command=lambda: kundenanleg.create_gui())
    create_customer_button.pack(pady=10)    # Button zum Erstellen eines neuen Kunden hinzufügen
    refresh_customer_button = ttk.Button(customer_list_frame, text="Refresh", style="Accent.TButton", command=lambda: double_show_customer_list())
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
    product_list_frame = tkinter.Frame(main_frame, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
    product_list_frame.grid(row=0, column=2, padx=20, pady=10, sticky="n")
    product_label = tkinter.Label(product_list_frame, text="Produktliste", font=("Helvetica", 18, "bold"), bg="#ffffff", fg="#333333")
    product_label.pack(pady=10)
    product_tree = ttk.Treeview(product_list_frame, columns=("artikelnummer", "name", "preis", "bemerkung"), show="headings")
    product_tree.heading("artikelnummer", text="Artikelnummer")
    product_tree.heading("name", text="Name")
    product_tree.heading("preis", text="Preis")
    product_tree.heading("bemerkung", text="Bemerkung")
    product_tree.column("#0", width=40)  # Breite der ersten Spalte anpassen
    product_tree.column("artikelnummer", width=100)  # Breite der zweiten Spalte anpassen
    product_tree.column("name", width=150)  # Breite der dritten Spalte anpassen
    product_tree.column("preis", width=60)  # Breite der vierten Spalte anpassen
    product_tree.pack(fill="both", expand=True)
    hilfe.load_product_list(product_tree)

    # Button zum Erstellen eines neuen Produkts hinzufügen
    create_product_button = ttk.Button(product_list_frame, text="Produktliste bearbeiten", style="Accent.TButton", command=lambda: produkte.create_gui())
    create_product_button.pack(pady=10)
    # Button zum Erstellen eines neuen Produkts hinzufügen
    refresh_product_button = ttk.Button(product_list_frame, text="Refresh", style="Accent.TButton", command=lambda: double_show_product_list())
    refresh_product_button.pack(pady=10)
input_entry = main_frame = user_tree = root1 = conn = cursor = None
def starten():
    global input_entry, main_frame, user_tree, root1, cursor, conn
    # Verbinde zur SQLite-Datenbank
    conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
    cursor = conn.cursor()
    # Hauptfenster erstellen
    root1 = tkinter.Tk()
    root1.title("Geflügelhof Wellhöfer")
    monitor = get_monitors()[0]
    root1.state("zoomed")
    root1.configure(bg="#f5f5f5")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Helvetica", 14))
    style.configure("Accent.TButton", font=("Helvetica", 14, "bold"), background="#3bd128", foreground="#ffffff")
    title_frame = tkinter.Frame(root1, bg="#ffffff", bd=2, relief="solid")
    title_frame.pack(fill="both")
    title_label = tkinter.Label(title_frame, text="Geflügelhof Wellhöfer", font=("Helvetica", 28, "bold"), bg="#ffffff", fg="#333333")
    title_label.pack(pady=10)

    main_frame = tkinter.Frame(root1, bg="#f4f4f4")
    main_frame.pack(padx=20, pady=20)

    left_frame = tkinter.Frame(main_frame, bg="#ffffff", bd=2, relief="solid")
    left_frame.grid(row=0, column=0, padx=20, pady=10, sticky="n")

    user_list_frame = tkinter.Frame(left_frame, bg="#ffffff", bd=2, relief="solid")
    user_list_frame.pack(pady=10)

    user_list_label = tkinter.Label(user_list_frame, text="Benutzerliste", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#333333")
    user_list_label.pack(pady=15)

    user_tree = ttk.Treeview(user_list_frame, columns=("name",), show="headings", height=10)
    user_tree.heading("name", text="Zum auswählen antippen")
    user_tree.column("name", width=190, anchor="center")
    user_tree.pack(fill="both", expand=True)

    user_scrollbar = ttk.Scrollbar(user_list_frame, orient="vertical", command=user_tree.yview)
    user_tree.bind("<<TreeviewSelect>>", on_user_select)
    hilfe.load_user_list(user_tree)

    input_entry = tkinter.Entry(left_frame, font=("Helvetica", 14), width=16, bd=2, relief="solid")
    input_entry.pack(pady=10)
    # Label "Anmelden" hinzufügen
    login_label = tkinter.Label(left_frame, text="Anmelden", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333333")
    login_label.pack(pady=10)

    # Frame für die oberen Buttons (Start und Löschen)
    upper_button_frame = tkinter.Frame(left_frame)
    upper_button_frame.pack(pady=10)

    # Start Button
    start_button = ttk.Button(upper_button_frame, text="Start", style="Accent.TButton", command=start_function)
    start_button.pack(side="left", padx=10)

    # Delete Button
    delete_button = tkinter.Button(upper_button_frame, text="Löschen", font=("Helvetica", 16, "bold"), bg="red", fg="white", command=delete_nutzer)
    delete_button.pack(side="left", padx=10)

    # Untere Buttons (Kundenliste und Produktliste)
    customer_button = ttk.Button(left_frame, text="Kundenliste anzeigen", style="TButton", command=show_customer_list)
    customer_button.pack(pady=10, padx=10, fill="both")

    product_button = ttk.Button(left_frame, text="Produktliste anzeigen", style="TButton", command=show_product_list)
    product_button.pack(pady=10, padx=10, fill="both")

    root1.mainloop()
    conn.close()

if __name__ == "__main__":
    starten()