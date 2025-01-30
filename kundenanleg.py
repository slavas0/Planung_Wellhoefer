import ttkbootstrap as ttkboots
from ttkbootstrap.constants import *
from tkinter import Text, messagebox
import sqlite3
import os

# Funktion zum Neustart des Skripts
def reset():
    os.execlp("python", "python", "kundenanleg.py")

# Funktion zum Aktualisieren der Kundenliste in der TreeView
def aktualisiere_tabelle(tree, daten):
    tree.delete(*tree.get_children())
    for kunde in daten:
        tree.insert("", "end", values=(
            kunde["id"], kunde["Name"], kunde["PLZ"], kunde["Adresse"],
            kunde["Hausnummer"], kunde["Stadt"], kunde["Telefonnummer"],
            kunde["Email"], kunde["Bemerkung"]))

# Funktion zum Abrufen der Kundendaten aus der Datenbank
def lade_kundendaten():
    try:
        conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kunden")
        daten = [
            {
                "id": eintrag[0], "Name": eintrag[1], "PLZ": eintrag[2], "Adresse": eintrag[3],
                "Hausnummer": eintrag[4], "Stadt": eintrag[5], "Telefonnummer": eintrag[6],
                "Email": eintrag[7], "Bemerkung": eintrag[8]
            }
            for eintrag in cursor.fetchall()
        ]
        conn.close()
        return daten
    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden der Daten: {e}")
        return []

# Funktion zum Speichern oder Aktualisieren eines Kunden
def kunde_speichern(tree):
    daten = {
        "id": id_entry.get(),
        "Name": name_entry.get(),
        "PLZ": plz_entry.get(),
        "Adresse": adresse_entry.get(),
        "Hausnummer": hausnummer_entry.get(),
        "Stadt": stadt_entry.get(),
        "Telefonnummer": telefon_entry.get(),
        "Email": email_entry.get(),
        "Bemerkung": bemerkung_text.get("1.0", "end-1c")
    }

    if not daten["Name"] and not daten["Telefonnummer"]:
        messagebox.showerror("Fehler", "Name oder Telefonnummer sind Pflichtfelder.")
        return

    try:
        conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
        cursor = conn.cursor()

        if daten["id"]:  # Update vorhandenen Kunden
            cursor.execute(
                """
                UPDATE kunden SET Name=?, PLZ=?, Adresse=?, Hausnummer=?, Stadt=?,
                Telefonnummer=?, Email=?, Bemerkung=? WHERE id=?
                """,
                (daten["Name"], daten["PLZ"], daten["Adresse"], daten["Hausnummer"],
                 daten["Stadt"], daten["Telefonnummer"], daten["Email"], daten["Bemerkung"], daten["id"])
            )
        else:  # Neuen Kunden hinzufügen
            cursor.execute(
                """
                INSERT INTO kunden (Name, PLZ, Adresse, Hausnummer, Stadt, Telefonnummer, Email, Bemerkung)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (daten["Name"], daten["PLZ"], daten["Adresse"], daten["Hausnummer"], daten["Stadt"],
                 daten["Telefonnummer"], daten["Email"], daten["Bemerkung"])
            )

        conn.commit()
        conn.close()
        aktualisiere_tabelle(tree, lade_kundendaten())
        messagebox.showinfo("Erfolg", f"Kunde {daten['Name']} wurde gespeichert!")
        reset_inputs()

    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Speichern der Daten: {e}")

# Funktion zum Löschen eines Kunden
def kunde_loeschen(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Fehler", "Bitte wählen Sie einen Kunden aus der Liste aus.")
        return

    kunde_id = tree.item(selected_item[0], "values")[0]
    try:
        conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kunden WHERE id = ?", (kunde_id,))
        conn.commit()
        conn.close()
        aktualisiere_tabelle(tree, lade_kundendaten())
        messagebox.showinfo("Erfolg", f"Kunde mit ID {kunde_id} wurde gelöscht.")

    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Löschen des Kunden: {e}")

# Funktion zum Zurücksetzen der Eingabefelder
def reset_inputs():
    for entry in [id_entry, name_entry, plz_entry, adresse_entry, hausnummer_entry, stadt_entry, telefon_entry, email_entry]:
        entry.delete(0, "end")
    bemerkung_text.delete("1.0", "end")

# Funktion zum Auswählen eines Kunden aus der Tabelle
def kunde_bearbeiten(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Fehler", "Bitte wählen Sie einen Kunden aus der Liste aus.")
        return

    kunde = tree.item(selected_item)["values"]
    id_entry.delete(0, "end")
    id_entry.insert(0, kunde[0])  # ID in das unsichtbare Feld schreiben
    name_entry.delete(0, "end")
    name_entry.insert(0, kunde[1])
    plz_entry.delete(0, "end")
    plz_entry.insert(0, kunde[2])
    adresse_entry.delete(0, "end")
    adresse_entry.insert(0, kunde[3])
    hausnummer_entry.delete(0, "end")
    hausnummer_entry.insert(0, kunde[4])
    stadt_entry.delete(0, "end")
    stadt_entry.insert(0, kunde[5])
    telefon_entry.delete(0, "end")
    telefon_entry.insert(0, kunde[6])
    email_entry.delete(0, "end")
    email_entry.insert(0, kunde[7])
    bemerkung_text.delete("1.0", "end")
    bemerkung_text.insert("1.0", kunde[8])

# GUI erstellen
def create_gui():
    root = ttkboots.Window(themename="sandstone")
    root.title("Kundenverwaltung")
    root.state("zoomed")

    global id_entry, name_entry, plz_entry, adresse_entry, hausnummer_entry, stadt_entry, telefon_entry, email_entry, bemerkung_text

    # Formularelemente
    form_frame = ttkboots.Frame(root, padding=10)
    form_frame.pack(fill="x", pady=5)

    id_entry = ttkboots.Entry(form_frame, width=15)
    id_entry.grid(row=0, column=5)
    id_entry.grid_remove()

    labels = ["Name*", "PLZ", "Adresse", "Hausnummer", "Stadt", "Telefonnummer*", "Email", "Bemerkung"]
    entries = {}

    for i, label in enumerate(labels[:7]):
        ttkboots.Label(form_frame, text=label + ":").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=5, pady=5)
        entry = ttkboots.Entry(form_frame, width=30)
        entry.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=5)
        entries[label] = entry

    bemerkung_label = ttkboots.Label(form_frame, text="Bemerkung:")
    bemerkung_label.grid(row=4, column=0, sticky="nw", padx=5, pady=5)
    bemerkung_text = Text(form_frame, width=30, height=4)
    bemerkung_text.grid(row=4, column=1, padx=5, pady=5)

    (name_entry, plz_entry, adresse_entry, hausnummer_entry, stadt_entry, telefon_entry, email_entry) = (
        entries["Name*"], entries["PLZ"], entries["Adresse"], entries["Hausnummer"],
        entries["Stadt"], entries["Telefonnummer*"], entries["Email"]
    )

    # Buttons
    button_frame = ttkboots.Frame(root, padding=10)
    button_frame.pack(fill="x", pady=5)

    ttkboots.Button(button_frame, text="Speichern", command=lambda: kunde_speichern(customer_tree), bootstyle=SUCCESS).pack(side="left", padx=10)
    ttkboots.Button(button_frame, text="Bearbeiten", command=lambda: kunde_bearbeiten(customer_tree), bootstyle=INFO).pack(side="left", padx=10)
    ttkboots.Button(button_frame, text="Schließen", command=lambda: root.destroy(), bootstyle=SECONDARY).pack(side="right", padx=10)
    ttkboots.Button(button_frame, text="Löschen", command=lambda: kunde_loeschen(customer_tree), bootstyle=DANGER).pack(side="right", padx=10)

    # Kundenliste
    list_frame = ttkboots.Frame(root, padding=10)
    list_frame.pack(fill="both", expand=True)

    columns = ("id", "Name", "PLZ", "Adresse", "Hausnummer", "Stadt", "Telefonnummer", "Email", "Bemerkung")
    customer_tree = ttkboots.Treeview(list_frame, columns=columns, show="headings")
    for col in columns:
        customer_tree.heading(col, text=col)
        customer_tree.column(col, width=100)

    customer_tree.pack(fill="both", expand=True)
    aktualisiere_tabelle(customer_tree, lade_kundendaten())

    root.mainloop()

#create_gui()
