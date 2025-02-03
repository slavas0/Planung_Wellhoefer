import sqlite3
from datetime import datetime
from screeninfo import get_monitors
import kundenanleg
import produkte
import hilfe
from ttkbootstrap import Style, Window, Frame, Label, Entry, Button, Treeview, Scrollbar
from ttkbootstrap.constants import *

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
            input_entry.delete(0, 'end')  # Eingabefeld leeren
            print(f"Nutzer '{user_input}' wurde erfolgreich gelöscht.")
        else:
            print(f"Kein Nutzer mit dem Namen '{user_input}' gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

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
    root1.withdraw()  # Verstecke das aktuelle Fenster
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

def on_user_select(event):
    selected_item = user_tree.selection()
    if selected_item:
        user_name = user_tree.item(selected_item, "values")[0]
        input_entry.delete(0, 'end')  # Eingabefeld leeren
        input_entry.insert(0, user_name)  # Name einfügen

def show_customer_list():
    global customer_list_frame, product_list_frame
    if customer_list_frame is not None:
        customer_list_frame.destroy()
        customer_list_frame = None
        return
    if product_list_frame is not None:
        product_list_frame.destroy()
        product_list_frame = None
    customer_list_frame = Frame(main_frame, padding=10)
    customer_list_frame.grid(row=0, column=2, padx=20, pady=10, sticky="n")
    customer_label = Label(customer_list_frame, text="Kundenliste", font=("Helvetica", 18, "bold"))
    customer_label.pack(pady=10)
    customer_tree = Treeview(customer_list_frame, columns=("name", "telefonnummer", "plz", "stadt", "adresse", "hausnummer", "email", "bemerkung"), show="headings")
    customer_tree.heading("name", text="Name")
    customer_tree.heading("telefonnummer", text="Telefonnummer")
    customer_tree.heading("plz", text="PLZ")
    customer_tree.heading("stadt", text="Stadt")
    customer_tree.heading("adresse", text="Adresse")
    customer_tree.heading("hausnummer", text="Hausnummer")
    customer_tree.heading("email", text="E-Mail")
    customer_tree.heading("bemerkung", text="Bemerkung")
    customer_tree.column("#0", width=40)
    customer_tree.column("name", width=120)
    customer_tree.column("telefonnummer", width=100)
    customer_tree.column("plz", width=60)
    customer_tree.pack(fill="both", expand=True)
    hilfe.load_customer_list(customer_tree)

    create_customer_button = Button(customer_list_frame, text="Kundenliste bearbeiten", bootstyle=SUCCESS, command=lambda: kundenanleg.create_gui())
    create_customer_button.pack(pady=10)
    refresh_customer_button = Button(customer_list_frame, text="Refresh", bootstyle=INFO, command=lambda: double_show_customer_list())
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
    product_list_frame = Frame(main_frame, padding=10)
    product_list_frame.grid(row=0, column=2, padx=20, pady=10, sticky="n")
    product_label = Label(product_list_frame, text="Produktliste", font=("Helvetica", 18, "bold"))
    product_label.pack(pady=10)
    product_tree = Treeview(product_list_frame, columns=("artikelnummer", "name", "preis", "bemerkung"), show="headings")
    product_tree.heading("artikelnummer", text="Artikelnummer")
    product_tree.heading("name", text="Name")
    product_tree.heading("preis", text="Preis")
    product_tree.heading("bemerkung", text="Bemerkung")
    product_tree.column("#0", width=40)
    product_tree.column("artikelnummer", width=100)
    product_tree.column("name", width=150)
    product_tree.column("preis", width=60)
    product_tree.pack(fill="both", expand=True)
    hilfe.load_product_list(product_tree)

    create_product_button = Button(product_list_frame, text="Produktliste bearbeiten", bootstyle=SUCCESS, command=lambda: produkte.create_gui())
    create_product_button.pack(pady=10)
    refresh_product_button = Button(product_list_frame, text="Refresh", bootstyle=INFO, command=lambda: double_show_product_list())
    refresh_product_button.pack(pady=10)

input_entry = main_frame = user_tree = root1 = conn = cursor = None

def starten():
    global input_entry, main_frame, user_tree, root1, cursor, conn
    # Verbinde zur SQLite-Datenbank
    conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
    cursor = conn.cursor()
    # Hauptfenster erstellen
    root1 = Window(themename="sandstone")
    root1.title("Geflügelhof Wellhöfer")
    monitor = get_monitors()[0]
    root1.state("zoomed")
    title_frame = Frame(root1, padding=10)
    title_frame.pack(fill="both")
    title_label = Label(title_frame, text="Geflügelhof Wellhöfer Planungssystem", font=("Helvetica", 28, "bold"))
    title_label.pack(pady=10)

    main_frame = Frame(root1, padding=20)
    main_frame.pack(fill="both", expand=True)

    left_frame = Frame(main_frame, padding=10)
    left_frame.grid(row=0, column=0, padx=20, pady=10, sticky="n")

    user_list_frame = Frame(left_frame, padding=10)
    user_list_frame.pack(pady=10)

    user_list_label = Label(user_list_frame, text="Benutzerliste", font=("Helvetica", 14, "bold"))
    user_list_label.pack(pady=15)

    user_tree = Treeview(user_list_frame, columns=("name",), show="headings", height=10)
    user_tree.heading("name", text="Zum auswählen antippen")
    user_tree.column("name", width=190, anchor="center")
    user_tree.pack(fill="both", expand=True)

    user_scrollbar = Scrollbar(user_list_frame, orient="vertical", command=user_tree.yview)
    user_tree.bind("<<TreeviewSelect>>", on_user_select)
    hilfe.load_user_list(user_tree)

    input_entry = Entry(left_frame, font=("Helvetica", 14), width=16)
    input_entry.pack(pady=10)
    login_label = Label(left_frame, text="Anmelden", font=("Helvetica", 16, "bold"))
    login_label.pack(pady=10)

    upper_button_frame = Frame(left_frame)
    upper_button_frame.pack(pady=10)

    start_button = Button(upper_button_frame, text="Start", bootstyle=SUCCESS, command=start_function)
    start_button.pack(side="left", padx=10)

    delete_button = Button(upper_button_frame, text="Löschen", bootstyle=DANGER, command=delete_nutzer)
    delete_button.pack(side="left", padx=10)

    customer_button = Button(left_frame, text="Kundenliste anzeigen", bootstyle=PRIMARY, command=show_customer_list)
    customer_button.pack(pady=10, padx=10, fill="both")

    product_button = Button(left_frame, text="Produktliste anzeigen", bootstyle=PRIMARY, command=show_product_list)
    product_button.pack(pady=10, padx=10, fill="both")

    root1.mainloop()
    conn.close()

if __name__ == "__main__":
    starten()