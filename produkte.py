import sqlite3
import ttkbootstrap as ttkboots
from ttkbootstrap.constants import *
from tkinter import Text, messagebox

# Funktion zur Herstellung der Verbindung zur SQLite-Datenbank
def get_db_connection():
    connection = sqlite3.connect("../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db")
    connection.row_factory = sqlite3.Row  # Erlaubt Zugriff auf Spalten per Namen
    return connection

# Funktion zum Laden aller Produkte aus der Datenbank
def lade_produkte():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM produkte")
    produkte = cursor.fetchall()
    connection.close()
    return produkte

# Funktion zum Hinzufügen oder Bearbeiten eines Produkts
def produkt_speichern(tree):
    artikelnummer = artikelnummer_entry.get()
    name = name_entry.get()
    preis = preis_entry.get()
    bemerkung = bemerkung_text.get("1.0", "end-1c")

    if not artikelnummer or not name or not preis:
        messagebox.showerror("Fehler", "Artikelnummer, Name und Preis sind Pflichtfelder.")
        return

    try:
        preis = float(preis)
    except ValueError:
        messagebox.showerror("Fehler", "Preis muss eine gültige Zahl sein.")
        return

    connection = get_db_connection()
    cursor = connection.cursor()

    # Prüfen, ob das Produkt bereits existiert
    cursor.execute("SELECT * FROM produkte WHERE Artikelnummer = ?", (artikelnummer,))
    produkt = cursor.fetchone()

    if produkt:
        # Bestehendes Produkt bearbeiten
        cursor.execute("UPDATE produkte SET Name = ?, Preis = ?, Bemerkung = ? WHERE Artikelnummer = ?",
                       (name, preis, bemerkung, artikelnummer))
        messagebox.showinfo("Erfolg", f"Produkt {artikelnummer} wurde aktualisiert!")
    else:
        # Neues Produkt hinzufügen
        cursor.execute("INSERT INTO produkte (Artikelnummer, Name, Preis, Bemerkung) VALUES (?, ?, ?, ?)",
                       (artikelnummer, name, preis, bemerkung))
        messagebox.showinfo("Erfolg", f"Produkt {name} wurde hinzugefügt!")

    connection.commit()
    connection.close()
    aktualisiere_tabelle(tree)

# Funktion zum Aktualisieren der Produktliste in der Treeview
def aktualisiere_tabelle(tree):
    # Vorhandene Einträge in der Treeview entfernen
    for item in tree.get_children():
        tree.delete(item)

    produkte = lade_produkte()  # Laden der Daten aus der Datenbank

    # Neue Daten hinzufügen
    for produkt in produkte:
        tree.insert(
            "",
            "end",
            values=(produkt["Artikelnummer"], produkt["Name"], produkt["Preis"], produkt["Bemerkung"])
        )

# Funktion zum Laden der Daten eines Produkts in die Eingabefelder
def produkt_bearbeiten(tree):
    try:
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, "values")

        artikelnummer_entry.delete(0, "end")
        artikelnummer_entry.insert(0, values[0])

        name_entry.delete(0, "end")
        name_entry.insert(0, values[1])

        preis_entry.delete(0, "end")
        preis_entry.insert(0, values[2])

        bemerkung_text.delete("1.0", "end")
        bemerkung_text.insert("1.0", values[3])
    except IndexError:
        messagebox.showerror("Fehler", "Bitte wähle ein Produkt aus, das bearbeitet werden soll.")

# Funktion zum Löschen eines Produkts
def produkt_loeschen(tree):
    try:
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, "values")

        # Produkt aus der Datenbank entfernen
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM produkte WHERE Artikelnummer = ?", (values[0],))
        connection.commit()
        connection.close()

        # Treeview aktualisieren
        aktualisiere_tabelle(tree)
        messagebox.showinfo("Erfolg", f"Produkt {values[1]} wurde gelöscht!")
    except IndexError:
        messagebox.showerror("Fehler", "Bitte wähle ein Produkt aus, das gelöscht werden soll.")

# GUI erstellen
def create_gui():
    global artikelnummer_entry, name_entry, preis_entry, bemerkung_text

    root = ttkboots.Window(themename="sandstone")
    root.title("Produktverwaltung")
    root.state("zoomed")

    # Titel
    title_label = ttkboots.Label(root, text="Produktverwaltung", font=("Arial", 20, "bold"))
    title_label.pack(pady=10)

    # Formularfelder
    form_frame = ttkboots.Frame(root, padding=10)
    form_frame.pack(fill="x", pady=10)

    # Artikelnummer
    artikelnummer_label = ttkboots.Label(form_frame, text="Artikelnummer*:", font=("Arial", 12))
    artikelnummer_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
    artikelnummer_entry = ttkboots.Entry(form_frame, width=30)
    artikelnummer_entry.grid(row=0, column=1, pady=5)

    # Name
    name_label = ttkboots.Label(form_frame, text="Name*:", font=("Arial", 12))
    name_label.grid(row=1, column=0, sticky="w", pady=5, padx=5)
    name_entry = ttkboots.Entry(form_frame, width=30)
    name_entry.grid(row=1, column=1, pady=5)

    # Preis
    preis_label = ttkboots.Label(form_frame, text="Preis*:", font=("Arial", 12))
    preis_label.grid(row=2, column=0, sticky="w", pady=5, padx=5)
    preis_entry = ttkboots.Entry(form_frame, width=30)
    preis_entry.grid(row=2, column=1, pady=5)

    # Bemerkung
    bemerkung_label = ttkboots.Label(form_frame, text="Bemerkung:", font=("Arial", 12))
    bemerkung_label.grid(row=3, column=0, sticky="nw", pady=5, padx=5)
    bemerkung_text = Text(form_frame, width=40, height=5)
    bemerkung_text.grid(row=3, column=1, pady=5)

    # Buttons
    button_frame = ttkboots.Frame(root, padding=10)
    button_frame.pack(fill="x", pady=10)

    add_button = ttkboots.Button(button_frame, text="Speichern", command=lambda: produkt_speichern(tree), bootstyle=SUCCESS)
    add_button.pack(side="left", padx=10)

    edit_button = ttkboots.Button(button_frame, text="Bearbeiten", command=lambda: produkt_bearbeiten(tree), bootstyle=INFO)
    edit_button.pack(side="left", padx=10)

    close_button = ttkboots.Button(button_frame, text="Schließen", command=root.destroy, bootstyle=SECONDARY)
    close_button.pack(side="right", padx=10)

    delete_button = ttkboots.Button(button_frame, text="Löschen", command=lambda: produkt_loeschen(tree), bootstyle=DANGER)
    delete_button.pack(side="right", padx=10)


    # Treeview für Produktliste
    tree_frame = ttkboots.Frame(root, padding=10)
    tree_frame.pack(fill="both", expand=True)

    columns = ("Artikelnummer", "Name", "Preis", "Bemerkung")
    tree = ttkboots.Treeview(tree_frame, columns=columns, show="headings", bootstyle="light")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True, pady=10)


    # Laden der Produktdaten und Anzeigen in der Treeview
    aktualisiere_tabelle(tree)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
