import sqlite3
from tkinter import Text, Canvas, messagebox, PhotoImage, Button
from ttkbootstrap import ttk, Window, SUCCESS, INFO, DANGER, SECONDARY
from screeninfo import get_monitors
from datetime import datetime, timedelta
import re

# Globale Variablen
username = "nutzer"
derstall = "Stall 2"
dieKW = 7
dasjahr = 2024
id_regist = []
lastitems = []
allestalle = []
nextstall = derstall
nexttime = [dieKW, dasjahr]
entry_count = 0
entries = []
eingang = []
state = False

# Verbinde zur SQLite-Datenbank
conn = sqlite3.connect('datenbank/diedatenbank.db')
cursor = conn.cursor()
def aktuelle_kw_jahr():
    # Aktuelles Datum
    heute = datetime.today()
    # Kalenderwoche und Jahr nach ISO-8601-Standard
    kw = heute.isocalendar()[1]
    jahr = heute.isocalendar()[0]
    return kw, jahr
# Funktionen für die Buttons
def start_function():
    user_input = input_entry.get().lower().strip()

    # Falls keine Eingabe erfolgt ist, auf einen Standardwert setzen
    if not user_input:
        user_input = "nutzer"

    print(f"Eingegebener Text: {user_input}")

    # Wenn ein Element im Treeview ausgewählt wurde, wird der Text hinzugefügt
    selected_item = user_tree.selection()
    if selected_item:
        # Falls ein Element ausgewählt ist, fügen wir den `user_input` in den Tree ein
        user_tree.insert(selected_item, 'end', text=user_input)
    else:
        # Falls kein Element ausgewählt wurde, fügen wir den Text als neues Element im Treeview hinzu
        user_tree.insert('', 'end', text=user_input)
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
    stall, kw, jahr = "Stall 1", 8, 2024
    global nexttime, dieKW, dasjahr
    dieKW, dasjahr = aktuelle_kw_jahr()
    nexttime = [dieKW, dasjahr]
    global username
    username = user_input
    start_frame.pack_forget()
    table_frame.pack(fill="both", expand=True)
    refresh_table_frame()
def show_customer_list():
    start_frame.pack_forget()
    customer_frame.pack(fill="both", expand=True)
def show_product_list():
    start_frame.pack_forget()
    product_frame.pack(fill="both", expand=True)
def back_to_start():
    table_frame.pack_forget()
    customer_frame.pack_forget()
    product_frame.pack_forget()
    start_frame.pack(fill="both", expand=True)
def close_program():
    conn.close()
    root1.destroy()
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
def on_user_select(event):
    selected_item = user_tree.selection()[0]
    user = user_tree.item(selected_item, "values")[0]
    input_entry.delete(0, "end")
    input_entry.insert(0, user)

def delete_nutzer():
    selected_item = user_tree.selection()
    if selected_item:
        user_tree.delete(selected_item)
    user_input = input_entry.get().lower().strip()
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
# Funktion zum Laden aller Produkte aus der Datenbank
def lade_produkte():
    cursor.execute("SELECT * FROM produkte")
    produkte = cursor.fetchall()
    return produkte

# Funktion zum Hinzufügen oder Bearbeiten eines Produkts
def produkt_speichern(tree):
    artikelnummer = artikelnummer_entry.get().strip()
    name = name_entry.get()
    preis = preis_entry.get()
    bemerkung = bemerkung_text.get("1.0", "end-1c")

    if not artikelnummer or not name or not preis:
        messagebox.showerror("Fehler", "Artikelnummer, Name und Preis sind Pflichtfelder.")
        return
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

    conn.commit()
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
            values=(produkt[1], produkt[2], produkt[3], produkt[4])
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
        cursor.execute("DELETE FROM produkte WHERE Artikelnummer = ?", (values[0],))
        conn.commit()

        # Treeview aktualisieren
        aktualisiere_tabelle(tree)
        messagebox.showinfo("Erfolg", f"Produkt {values[1]} wurde gelöscht!")
    except IndexError:
        messagebox.showerror("Fehler", "Bitte wähle ein Produkt aus, das gelöscht werden soll.")
# Funktion zum Aktualisieren der Kundenliste in der TreeView
def aktualisiere_ktabelle(tree, daten):
    tree.delete(*tree.get_children())
    for kunde in daten:
        tree.insert("", "end", values=(
            kunde["id"], kunde["Name"], kunde["PLZ"], kunde["Adresse"],
            kunde["Hausnummer"], kunde["Stadt"], kunde["Telefonnummer"],
            kunde["Email"], kunde["Bemerkung"]))

# Funktion zum Speichern oder Aktualisieren eines Kunden
def kunde_speichern(tree):
    daten = {
        "id": id_entry.get(),
        "Name": kname_entry.get(),
        "PLZ": plz_entry.get(),
        "Adresse": adresse_entry.get(),
        "Hausnummer": hausnummer_entry.get(),
        "Stadt": stadt_entry.get(),
        "Telefonnummer": telefon_entry.get(),
        "Email": email_entry.get(),
        "Bemerkung": kbemerkung_text.get("1.0", "end-1c")
    }

    if not daten["Name"] and not daten["Telefonnummer"]:
        messagebox.showerror("Fehler", "Name oder Telefonnummer sind Pflichtfelder.")
        return

    try:
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
        aktualisiere_ktabelle(tree, lade_kundendaten())
        messagebox.showinfo("Erfolg", f"Kunde {daten['Name']} wurde gespeichert!")
        clear_form()

    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Speichern der Daten: {e}")

# Funktion zum Auswählen eines Kunden aus der Tabelle
def kunde_bearbeiten(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Fehler", "Bitte wählen Sie einen Kunden aus der Liste aus.")
        return

    kunde = tree.item(selected_item)["values"]
    id_entry.delete(0, "end")
    id_entry.insert(0, kunde[0])  # ID in das unsichtbare Feld schreiben
    kname_entry.delete(0, "end")
    kname_entry.insert(0, kunde[1])
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
    kbemerkung_text.delete("1.0", "end")
    kbemerkung_text.insert("1.0", kunde[8])
# Funktion zum Löschen eines Kunden
def kunde_loeschen(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Fehler", "Bitte wählen Sie einen Kunden aus der Liste aus.")
        return

    kunde_id = tree.item(selected_item[0], "values")[0]
    try:
        cursor.execute("DELETE FROM kunden WHERE id = ?", (kunde_id,))
        conn.commit()
        aktualisiere_ktabelle(tree, lade_kundendaten())
        messagebox.showinfo("Erfolg", f"Kunde mit ID {kunde_id} wurde gelöscht.")
    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Löschen des Kunden: {e}")
# Funktion zum Abrufen der Kundendaten aus der Datenbank
def lade_kundendaten():
    try:
        cursor.execute("SELECT * FROM kunden")
        daten = [
            {
                "id": eintrag[0], "Name": eintrag[1], "PLZ": eintrag[2], "Adresse": eintrag[3],
                "Hausnummer": eintrag[4], "Stadt": eintrag[5], "Telefonnummer": eintrag[6],
                "Email": eintrag[7], "Bemerkung": eintrag[8]
            }
            for eintrag in cursor.fetchall()
        ]
        return daten
    except sqlite3.Error as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden der Daten: {e}")
        return []
def clear_form():
    artikelnummer_entry.delete(0, "end")
    name_entry.delete(0, "end")
    preis_entry.delete(0, "end")
    kbemerkung_text.delete("1.0", "end")
    plz_entry.delete(0, "end")
    adresse_entry.delete(0, "end")
    hausnummer_entry.delete(0, "end")
    stadt_entry.delete(0, "end")
    telefon_entry.delete(0, "end")
    email_entry.delete(0, "end")
    kname_entry.delete(0, "end")
    artikelnummer_entry.delete(0, "end")
    bemerkung_text.delete("1.0", "end")
def lastitemsdef():
    global lastitems
    sql = "SELECT DISTINCT stall, kw, jahr FROM eintrag WHERE archived = 0 ORDER BY jahr, kw;"
    cursor.execute(sql)
    lastitems = []
    for row in cursor.fetchall():
        monat = kalenderwoche_monat(row[2], row[1])
        neuer_eintrag = [str(row[0]), monat, row[2], row[1]]
        if  len(lastitems) < 12:
            lastitems.append(neuer_eintrag)
    lastitems.sort(key=lambda x: (x[2], x[3], x[0]))  # x[2] = Jahr, x[3] = KW, x[0] = Stall

    cursor.execute("SELECT DISTINCT stall FROM eintrag;")
    global allestalle
    for i in cursor.fetchall():
        allestalle.append(i[0])
def kalenderwoche_daten(jahr, kw):
    vierten_januar = datetime(jahr, 1, 4)
    start_der_ersten_kw = vierten_januar - timedelta(days=vierten_januar.weekday())
    start_der_kw = start_der_ersten_kw + timedelta(weeks=kw - 1)
    ende_der_kw = start_der_kw + timedelta(days=6)
    start_der_kw = ende_der_kw - timedelta(days=6)
    formatierter_start = start_der_kw.strftime("%d. %B %Y")
    formatierter_ende = ende_der_kw.strftime("%d. %B %Y")
    return formatierter_start, formatierter_ende
def kalenderwoche_monat(jahr, kw):
    vierten_januar = datetime(jahr, 1, 4)
    start_der_ersten_kw = vierten_januar - timedelta(days=vierten_januar.weekday())
    start_der_kw = start_der_ersten_kw + timedelta(weeks=kw - 1)
    return start_der_kw.month
def create_scrollable_area(root):
    canvas = Canvas(root)
    scrollable_frame = ttk.Frame(canvas)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack_forget()
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        if scrollable_frame.winfo_height() > canvas.winfo_height():
            scrollbar.pack(side="right", fill="y")
        else:
            scrollbar.pack_forget()
            canvas.yview_moveto(0)

    scrollable_frame.bind("<Configure>", update_scrollregion)
    return canvas, scrollable_frame

def daten_abfragen_und_fuellen(scrollable_frame, kw, jahr, stall):
    sql = "SELECT name, telefonnummer, braune, weise, verfahren, preis, bemerkung, id FROM eintrag WHERE kw = ? AND jahr = ? AND stall = ?"
    cursor.execute(sql, (kw, jahr, stall))
    daten = cursor.fetchall()
    if daten:
        for row in daten:
            print(row)
            eintrag_hinzufuegen(scrollable_frame, row[7])
            aktueller_eintrag = entries[-1]
            aktueller_eintrag["name"].insert(0, row[0])
            aktueller_eintrag["telefon"].insert(0, row[1])
            aktueller_eintrag["braun"].insert(0, row[2])
            aktueller_eintrag["weiss"].insert(0, row[3])
            aktueller_eintrag["verhalten"].insert(0, row[4])
            aktueller_eintrag["preis"].insert(0, row[5])
            aktueller_eintrag["bemerkung"].insert(0, row[6])
            aktueller_eintrag["id"].config(text=row[7])
            id_regist.append(row[7])

def enable_mouse_scroll(canvas):
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
    canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

def create_title(root):
    title_label = ttk.Label(root, text="Planungssystem", font=("Arial", 28, "bold"), background="#f5f5f5")
    title_label.pack(pady=10)

def create_headers(scrollable_frame):
    headers = ["Name", "Telefonnummer", "Stück Braun", "Stück Weiß", "Verhalten", "Preis", "Bemerkung"]
    for i, header in enumerate(headers):
        label = ttk.Label(scrollable_frame, text=header, font=("Arial", 12, "bold"), background="#f5f5f5")
        label.grid(row=2, column=i, padx=10, pady=10)

def check_check_entry(frame, id, numb, row, check):
    cursor.execute("SELECT checked FROM eintrag WHERE id = ?", (id,))
    result = cursor.fetchone()
    print(result[0])
    if result[0]:
        check_entry(frame, id, numb, row, 0)
def check_entry(frame, id, numb, row, check):
    exist = 0
    if id == 'none':
        exist = 0
    else:
        exist = 1
    # Überprüfen, ob bereits ein Hintergrund-Label existiert
    if hasattr(frame, f"hintergrund_label_{row}"):
        # Wenn das Label existiert, entfernen wir es
        if exist and check:
            cursor.execute("UPDATE eintrag SET checked = 0 WHERE id = ?", (id,))
            conn.commit()
        hintergrund_label = getattr(frame, f"hintergrund_label_{row}")
        hintergrund_label.destroy()
        delattr(frame, f"hintergrund_label_{row}")

        # Setze die Hintergrundfarbe der Widgets zurück
        for widget in frame.grid_slaves(row=row):
            if isinstance(widget, (ttk.Entry, ttk.Label, ttk.Button)):
                try:
                    widget.configure(background="")  # Setze den Standardhintergrund zurück
                except:
                    pass  # Ignoriere den Fehler, falls `background` nicht unterstützt wird
    else:
        # Wenn kein Label existiert, erstellen wir ein neues
        if exist and check:
            cursor.execute("UPDATE eintrag SET checked = 1 WHERE id = ?", (id,))
            conn.commit()
        hintergrund_label = ttk.Label(frame, background="#d0f0c0")
        hintergrund_label.grid(row=row, column=0, columnspan=10, sticky="nsew", pady=5)
        hintergrund_label.lower()  # Hinter die anderen Widgets verschieben
        # Speichern des Labels als Attribut des Frames
        setattr(frame, f"hintergrund_label_{row}", hintergrund_label)

        # Setze die Hintergrundfarbe der Widgets auf grün
        for widget in frame.grid_slaves(row=row):
            if isinstance(widget, (ttk.Entry, ttk.Label, ttk.Button)):
                try:
                    widget.configure(background="#d0f0c0")  # Grüner Hintergrund
                except:
                    pass  # Ignoriere den Fehler, falls `background` nicht unterstützt wird

def del_entry(frame, id, numb, row, check):
    hintergrund_label = ttk.Label(frame, background="#ffcccb")
    hintergrund_label.grid(row=row, column=0, columnspan=10, sticky="nsew", pady=5)
    hintergrund_label.lower()  # Hinter die anderen Widgets verschieben
    # Speichern des Labels als Attribut des Frames
    setattr(frame, f"hintergrund_dellabel_{row}", hintergrund_label)

    # Setze die Hintergrundfarbe der Widgets auf grün
    for widget in frame.grid_slaves(row=row):
        if isinstance(widget, (ttk.Entry, ttk.Label, ttk.Button)):
            try:
                widget.configure(background="#ffcccb")  # Grüner Hintergrund
            except:
                pass  # Ignoriere den Fehler, falls `background` nicht unterstützt wird


def eintrag_hinzufuegen(scrollable_frame, id):
    global entry_count
    row_offset = 3 + entry_count
    numb = len(id_regist)
    id_regist.append(0)
    entry_count += 1

    name_entry = ttk.Entry(scrollable_frame)
    name_entry.grid(row=row_offset, column=0, padx=5, pady=5)
    telefon_entry = ttk.Entry(scrollable_frame)
    telefon_entry.grid(row=row_offset, column=1, padx=5, pady=5)
    braun_entry = ttk.Entry(scrollable_frame)
    braun_entry.grid(row=row_offset, column=2, padx=5, pady=5)
    weiss_entry = ttk.Entry(scrollable_frame)
    weiss_entry.grid(row=row_offset, column=3, padx=5, pady=5)
    verhalten_entry = ttk.Entry(scrollable_frame)
    verhalten_entry.grid(row=row_offset, column=4, padx=5, pady=5)
    preis_entry = ttk.Entry(scrollable_frame)
    preis_entry.grid(row=row_offset, column=5, padx=5, pady=5)
    bemerkung_entry = ttk.Entry(scrollable_frame)
    bemerkung_entry.grid(row=row_offset, column=6, padx=5, pady=5)
    id_label = ttk.Label(scrollable_frame, text=id)
    id_label.grid(row=row_offset, column=7, padx=5, pady=5)
    id_label.grid_remove()
    number_label = ttk.Label(scrollable_frame, text=numb)
    number_label.grid(row=row_offset, column=7, padx=5, pady=5)
    number_label.grid_remove()
    delete_button = ttk.Button(scrollable_frame, text="Löschen", command=lambda: delete_entry(scrollable_frame, id, numb, row_offset), bootstyle="DANGER")
    delete_button.grid(row=row_offset, column=8, padx=5, pady=5)
    if not id == "none":
        # Häkchen-Icon laden
        check_icon = PhotoImage(file="checkmark.png")  # Pfad zum Häkchen-Icon
        check_button = ttk.Button(scrollable_frame, image=check_icon, command=lambda: check_entry(scrollable_frame, id, numb, row_offset, 1), bootstyle="SUCCESS")
        check_button.image = check_icon  # Referenz halten, um Garbage Collection zu verhindern
        check_button.grid(row=row_offset, column=9, padx=5, pady=5)
    if not id == "none":
        check_check_entry(scrollable_frame, id, numb, row_offset, 0)
    entries.append({
        "id": id_label,
        "number": number_label,
        "name": name_entry,
        "telefon": telefon_entry,
        "braun": braun_entry,
        "weiss": weiss_entry,
        "verhalten": verhalten_entry,
        "preis": preis_entry,
        "bemerkung": bemerkung_entry
    })

def eingang_indb_speichern(kw, stall, jahr):
    for entry in eingang:
        sql_update = "UPDATE inventar SET weiss = ?, braun = ?, anmerkung = ? WHERE kw = ? AND stall = ? AND jahr = ?"
        cursor.execute(sql_update, (entry["weiss"], entry["braun"], entry["lila"], kw, stall, jahr))
        rows_affected = cursor.rowcount
        if rows_affected == 0:
            sql_insert = "INSERT INTO inventar (kw, stall, jahr, weiss, braun, anmerkung) VALUES (?, ?, ?, ?, ?, ?)"
            values = (kw, stall, jahr, entry["weiss"], entry["braun"], entry["lila"])
            cursor.execute(sql_insert, values)
    conn.commit()

def speichern_daten(textfeld_braun, textfeld_weiss, textfeld3):
    weiss = int(textfeld_weiss.get())
    braun = int(textfeld_braun.get())
    lila = str(textfeld3.get())
    eingang.append({'weiss': weiss, 'braun': braun, 'lila': lila})
    eingang_indb_speichern(dieKW, derstall, dasjahr)
    try:
        for entry in entries:
            if entry["id"].winfo_exists():
                id = entry["id"].cget("text")
            else:
                print("Fehler: ID-Label existiert nicht mehr.")
            id = entry["id"].cget("text")
            name = entry["name"].get()
            telefon = entry["telefon"].get()
            braun = entry["braun"].get()
            weiss = entry["weiss"].get()
            verhalten = entry["verhalten"].get()
            preis = entry["preis"].get()
            bemerkung = entry["bemerkung"].get()
            #checked = entry["checked"].cget()
            if id != 'none':
                sql = f"UPDATE eintrag SET name = '{name}', stall = '{derstall}', kw = {int(dieKW)}, jahr = {int(dasjahr)}, telefonnummer = '{telefon}', braune = {braun}, weise = {weiss}, verfahren = '{verhalten}', preis = '{preis}', bemerkung = '{bemerkung}' WHERE id = {id};"
                cursor.execute("SELECT id FROM eintrag WHERE id = ?", (id,))
                isnone = cursor.fetchone()
                if isnone == 'None':
                    sql = "INSERT INTO eintrag (id, stall, kw, jahr, name, telefonnummer, braune, weise, verfahren, preis, bemerkung) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    cursor.execute(sql, (id, derstall, dieKW, dasjahr, name, telefon, braun, weiss, verhalten, preis, bemerkung))
                else:
                    cursor.execute(sql)
                conn.commit()
            else:
                if (name + telefon + str(braun) + str(weiss) + verhalten + preis + bemerkung) != "":
                    sql = "INSERT INTO eintrag (stall, kw, jahr, name, telefonnummer, braune, weise, verfahren, preis, bemerkung) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    cursor.execute(sql, (derstall, dieKW, dasjahr, name, telefon, braun, weiss, verhalten, preis, bemerkung))
                    sql_max_id = "SELECT MAX(id) FROM eintrag WHERE stall = ? AND kw = ? AND jahr = ?"
                    cursor.execute(sql_max_id, (derstall, dieKW, dasjahr))
                    max_id = cursor.fetchone()[0]
                    entry["id"].config(text=max_id)
                    id_regist[int(entry["number"].cget("text"))] = max_id
            print(f"Speichere: Name={name}, Telefon={telefon}, Braun={braun}, Weiß={weiss}, Verhalten={verhalten}, Preis={preis}, Bemerkung={bemerkung} in {derstall} am {dieKW} {dasjahr}")
        conn.commit()
        messagebox.showinfo("Speichern", "Die Daten wurden erfolgreich gespeichert!")
    except sqlite3.Error as e:
        messagebox.showerror("Datenbankfehler", str(e))
def delete_entry(scrollable_frame, entry_id, numb, row):
    if entry_id == 'none':
        entry_id = id_regist[numb]
        if entry_id == 0:
            remove_entry_from_gui(numb)
            return
    cursor.execute("SELECT id FROM eintrag WHERE id = ?", (entry_id,))
    result = cursor.fetchone()
    if result:
        del_entry(scrollable_frame, entry_id, numb, row, 0)
        cursor.execute("DELETE FROM eintrag WHERE id = ?", (entry_id,))
        conn.commit()
        messagebox.showinfo("Löschen", f"Eintrag mit ID {entry_id} wurde gelöscht.")
        remove_entry_from_gui(numb)
    else:
        messagebox.showwarning("Nicht gefunden", f"Eintrag mit ID {entry_id} existiert nicht.")
    #update_scrollregion(scrollable_frame)

def remove_entry_from_gui(numb):
    for entry in entries:
        if entry["number"].cget("text") == str(numb):
            for widget in entry.values():
                widget.grid_remove()
            break

def update_scrollregion(scrollable_frame):
    scrollable_frame.update_idletasks()
    scrollable_frame.winfo_toplevel().children['!canvas'].configure(scrollregion=scrollable_frame.bbox("all"))

def create_footer(root):
    global derstall, dieKW, dasjahr
    footer_frame = ttk.Frame(root)
    footer_frame.pack(side="bottom", fill="x", pady=10)
    gesamt_label = ttk.Label(footer_frame, text="Gesamte bestellte Tieranzahl", font=("Arial", 12, "bold"))
    gesamt_label.pack(side="left", padx=10)
    braun_summe_label = ttk.Label(footer_frame, font=("Arial", 12))
    braun_summe_label.pack(side="left", padx=10)
    weiss_summe_label = ttk.Label(footer_frame, font=("Arial", 12))
    weiss_summe_label.pack(side="left", padx=10)

    def berechne_summen():
        sql = "SELECT SUM(braune), SUM(weise) FROM eintrag WHERE stall = ? AND kw = ? AND jahr = ?"
        cursor.execute(sql, (derstall, dieKW, dasjahr))
        result = cursor.fetchone()
        if result:
            braun_summe, weiss_summe = result
            braun_summe_label.config(text=f"Braun: {braun_summe}")
            weiss_summe_label.config(text=f"Weiß: {weiss_summe}")
        else:
            braun_summe_label.config(text="Braun: 0")
            weiss_summe_label.config(text="Weiß: 0")

    berechne_summen()
    ubrig_label = ttk.Label(footer_frame, text="Übrige Tieranzahl", font=("Arial", 12, "bold"))
    ubrig_label.pack(side="left", padx=10)
    braun_ubrig_label = ttk.Label(footer_frame, font=("Arial", 12))
    braun_ubrig_label.pack(side="left", padx=10)
    weiss_ubrig_label = ttk.Label(footer_frame, font=("Arial", 12))
    weiss_ubrig_label.pack(side="left", padx=10)
    def berechne_ubrig():
        sql = "SELECT braun, weiss FROM inventar WHERE stall = ? AND kw = ? AND jahr = ?"
        cursor.execute(sql, (derstall, dieKW, dasjahr))
        result = cursor.fetchone()
        if result:
            braun_ubrig, weiss_ubrig = result
            try:
                braune_summe = int(re.sub(r"[^\d-]", "", braun_summe_label.cget("text")))
            except ValueError:
                braune_summe = 0
            try:
                weisse_summe = int(re.sub(r"[^\d-]", "", weiss_summe_label.cget("text")))
            except ValueError:
                weisse_summe = 0
            braun = braun_ubrig - braune_summe
            weiss = weiss_ubrig - weisse_summe
            braun_ubrig_label.config(text=f"Braun: {braun}")
            weiss_ubrig_label.config(text=f"Weiß: {weiss}")
            if braun > 0:
                braun_ubrig_label.config(background="#d0f0c0")
            else:
                braun_ubrig_label.config(background="#ffcccb")
            if weiss > 0:
                weiss_ubrig_label.config(background="#d0f0c0")
            else:
                weiss_ubrig_label.config(background="#ffcccb")
        else:
            braun_ubrig_label.config(text="Braun: 0", background="#ffcccb")
            weiss_ubrig_label.config(text="Weiß: 0", background="#ffcccb")

    berechne_ubrig()
def create_welcome_label(root):
    welcome_label = ttk.Label(root, text=f"Willkommen, {username}!", font=("Arial", 16))
    welcome_label.pack(pady=10)

def create_large_text(root):
    txt = derstall + " - KW " + str(dieKW) + " " + str(dasjahr)
    large_text_label = ttk.Label(root, text=txt, font=("Arial", 20, "bold"))
    large_text_label.pack(pady=10)
    txt2a, txt2b = kalenderwoche_daten(dasjahr, dieKW)
    txt2 = f"Woche vom {txt2a}\n bis {txt2b}"
    large_text2_label = ttk.Label(root, text=txt2, font=("Arial", 20, "bold"))
    large_text2_label.pack(pady=10)

def select_kw_jahr_stall(neukw, neustall, neujahr):
    global nextstall, nexttime
    nextstall = neustall
    nexttime = [neukw, neujahr]
    refresh_table_frame()
def setglobs():
    global derstall, dieKW, dasjahr, nextstall, nexttime
    derstall = nextstall
    dieKW = nexttime[0]
    dasjahr = nexttime[1]
def create_last_items_tabs(root):
    last_items_frame = ttk.Frame(root)
    last_items_frame.pack(side="bottom", fill="x", pady=10)
    monate = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    lastitemsdef()
    for idx, item in enumerate(lastitems):
        tab_text = f"{item[0]} - KW {item[3]}  {monate[item[1]-1]} {item[2]}"
        last_item_tab = ttk.Button(last_items_frame, text=tab_text, bootstyle=SECONDARY, command=lambda i=item: select_kw_jahr_stall(i[3], i[0], i[2]))
        last_item_tab.pack(side="left", padx=5, pady=5)
def eingang_db_abfragen():
    sql = "SELECT braun, weiss, anmerkung FROM inventar WHERE kw = ? AND stall = ? AND jahr = ?"
    cursor.execute(sql, (dieKW, derstall, dasjahr))
    result = cursor.fetchone()
    if result:
        braun, weiss, lila = result
        return braun, weiss, lila
    else:
        return 0, 0, 0
def refresh_table_frame():
    global table_frame, entries, entry_count
    setglobs()
    table_frame.destroy()  # Entfernt den alten Frame
    table_frame = ttk.Frame(root1, bootstyle="light")  # Erstellt einen neuen Frame
    table_frame.pack(fill="both", expand=True)  # Neu positionieren
    entries = []
    entry_count = 0
    build_ui2()  # Setzt das UI neu auf
def set_archived(value):
    global nextstall, nexttime
    sql = "UPDATE eintrag SET archived = ?  WHERE stall = ? AND kw = ? AND jahr = ?;"
    cursor.execute(sql, (value, nextstall, nexttime[0], nexttime[1]))
    conn.commit()
def defstate():
    global nextstall, nexttime, state

    # Überprüfen, ob es einen Eintrag gibt, der nicht archiviert ist (archived = 0)
    sql_check = "SELECT COUNT(*) FROM eintrag WHERE stall = ? AND kw = ? AND jahr = ? AND archived = 0;"
    cursor.execute(sql_check, (nextstall, nexttime[0], nexttime[1]))
    result = cursor.fetchone()
    print("count")
    print(result)
    # Wenn es mindestens einen nicht archivierten Eintrag gibt, setze state auf False, andernfalls auf True
    if result[0] > 0:
        state = False
    else:
        state = True
    return state


#! Hier fängt Frontend an!
# Hauptfenster erstellen
root1 = Window(themename="sandstone")
root1.title("Geflügelhof Wellhöfer")
monitor = get_monitors()[0]
root1.state("zoomed")
root1.configure(bg="#f5f5f5")

# Startseite
start_frame = ttk.Frame(root1, bootstyle="light")
start_frame.pack(fill="both", expand=True)

title_label = ttk.Label(start_frame, text="Geflügelhof Wellhöfer", font=("Helvetica", 28, "bold"), background="#f5f5f5")
title_label.pack(pady=10)

user_list_frame = ttk.Frame(start_frame, bootstyle="light", borderwidth=2, relief="sunken")
user_list_frame.pack(pady=10)

user_list_label = ttk.Label(user_list_frame, text="Benutzerliste", font=("Helvetica", 14, "bold"), background="#f5f5f5")
user_list_label.pack(pady=15)

user_tree = ttk.Treeview(user_list_frame, columns=("name",), show="headings", height=10, bootstyle="light")
user_tree.heading("name", text="Zum auswählen antippen")
user_tree.column("name", width=190, anchor="center")
user_tree.pack(fill="both", expand=True)

#user_scrollbar = ttk.Scrollbar(user_list_frame, orient="vertical", command=user_tree.yview)
#user_tree.configure(yscrollcommand=user_scrollbar.set)
#user_scrollbar.pack(side="right", fill="y")

user_tree.bind("<<TreeviewSelect>>", on_user_select)
load_user_list(user_tree)

input_entry = ttk.Entry(start_frame, font=("Helvetica", 14), width=16)
input_entry.pack(pady=10)

login_label = ttk.Label(start_frame, text="Anmelden", font=("Helvetica", 16, "bold"), background="#f5f5f5")
login_label.pack(pady=10)

upper_button_frame = ttk.Frame(start_frame, bootstyle="light")
upper_button_frame.pack(pady=10)

start_button = ttk.Button(upper_button_frame, text="Start", bootstyle="success", command=start_function)
start_button.pack(side="left", pady=10)

delete_button = ttk.Button(upper_button_frame, text="Löschen", bootstyle="danger", command=delete_nutzer)
delete_button.pack(side="left", padx=10)

customer_button = ttk.Button(start_frame, text="Kundenliste anzeigen", bootstyle="primary", command=show_customer_list)
customer_button.pack(pady=10)

product_button = ttk.Button(start_frame, text="Produktliste anzeigen", bootstyle="primary", command=show_product_list)
product_button.pack(pady=10)

close_button = ttk.Button(start_frame, text="Schließen", bootstyle="danger", command=close_program)
close_button.pack(pady=10)

# Tabelle Seite
table_frame = ttk.Frame(root1, bootstyle="light")
def build_ui2():
    def update_next_kw(change):
        kwtemp = nexttime[0] + change
        nexttime[0] = (kwtemp - 1) % 53 + 1
        if kwtemp < 1:
            nexttime[1] -= 1
        elif kwtemp > 53:
            nexttime[1] += 1
        next_kw_label.config(text=str(nexttime[0]))
    def next_stall(change):
        global nextstall
        try:
            current_index = allestalle.index(nextstall)
            new_index = (current_index + change) % len(allestalle)
            nextstall = allestalle[new_index]
        except ValueError:
            print(f"nextstall {allestalle} nicht in allestalle gefunden.")
        next_stall_entry.delete(0, "end")
        next_stall_entry.insert(0, str(nextstall))  # Neuen Wert setzen

    create_last_items_tabs(table_frame)
    create_footer(table_frame)
    canvas, scrollable_frame = create_scrollable_area(table_frame)
    enable_mouse_scroll(canvas)
    create_title(table_frame)
    create_welcome_label(table_frame)
    create_large_text(table_frame)
    braun, weiss, lila = eingang_db_abfragen()
    label = ttk.Label(scrollable_frame, text="Braune", font=("Arial", 12, "bold"))
    label.grid(row=0, column=0, padx=10, pady=10)
    textfeld_braun = ttk.Entry(scrollable_frame)
    textfeld_braun.grid(row=1, column=0, padx=5, pady=5)

    label = ttk.Label(scrollable_frame, text="Weiße", font=("Arial", 12, "bold"))
    label.grid(row=0, column=1, padx=10, pady=10)
    textfeld_weiss = ttk.Entry(scrollable_frame)
    textfeld_weiss.grid(row=1, column=1, padx=5, pady=5)

    label = ttk.Label(scrollable_frame, text="Anmerkung", font=("Arial", 12, "bold"))
    label.grid(row=0, column=2, padx=10, pady=10)
    textfeld3 = ttk.Entry(scrollable_frame, width=40)
    textfeld3.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

    textfeld_braun.insert(0, braun)
    textfeld_weiss.insert(0, weiss)
    textfeld3.insert(0, lila)
    create_headers(scrollable_frame)

    button_frame = ttk.Frame(table_frame, bootstyle="light")
    button_frame.pack(pady=10)
    hinzufuegen_button = ttk.Button(button_frame, text="Eintrag hinzufügen",
                                    command=lambda: eintrag_hinzufuegen(scrollable_frame, "none"),
                                    bootstyle=SUCCESS)
    hinzufuegen_button.pack(side="left", pady=20, padx=10)
    def toggle():
        global state
        state = not state
        btn.config(text="  ✔ archiviert  " if state else "  X archivieren  ")
        if state:
            set_archived(1)
        else:
            set_archived(0)
    global state
    state = defstate()
    if state:
        btn = Button(button_frame, text="  ✔ archiviert  ", command=toggle, height=2)
    else:
        btn = Button(button_frame, text="  X archivieren  ", command=toggle, height=2)
    btn.pack(side="right", pady=20, padx=10)
    def reload():
        global nextstall
        nextstall = next_stall_entry.get()
        refresh_table_frame()

    save_frame = ttk.Frame(table_frame, bootstyle="light")
    save_frame.pack(pady=5)
    speichern_button = ttk.Button(save_frame, text="Speichern",
                                  command=lambda: speichern_daten(textfeld_braun, textfeld_weiss, textfeld3),
                                  bootstyle="primary")
    speichern_button.pack(side="right", pady=10, padx=5)
    wechsel_button = ttk.Button(save_frame, text="Neu laden", command=lambda: reload())
    wechsel_button.pack(side="left", pady=10, padx=5)
    arrow_frame_1 = ttk.Frame(table_frame, bootstyle="light")
    arrow_frame_1.pack(pady=5)

    left_arrow_1 = ttk.Button(arrow_frame_1, text="<<", command=lambda: update_next_kw(-10), width=5)
    left_arrow_1.pack(side="left", padx=5)

    left_arrow_12 = ttk.Button(arrow_frame_1, text="<", command=lambda: update_next_kw(-1), width=5)
    left_arrow_12.pack(side="left", padx=5)

    next_kw_label = ttk.Label(arrow_frame_1, text=str(nexttime[0]))
    next_kw_label.pack(side="left", padx=5)

    right_arrow_1 = ttk.Button(arrow_frame_1, text=">", command=lambda: update_next_kw(1), width=5)
    right_arrow_1.pack(side="left", padx=5)
    right_arrow_12 = ttk.Button(arrow_frame_1, text=">>", command=lambda: update_next_kw(10), width=5)
    right_arrow_12.pack(side="left", padx=5)

    arrow_frame_2 = ttk.Frame(table_frame, bootstyle="light")
    arrow_frame_2.pack(pady=5)

    left_arrow_2 = ttk.Button(arrow_frame_2, text="<", command=lambda: next_stall(-1), width=5)
    left_arrow_2.pack(side="left", padx=5)

    next_stall_entry = ttk.Entry(arrow_frame_2)
    next_stall_entry.insert(0, str(nextstall))  # Standardwert setzen
    next_stall_entry.pack(side="left", padx=5)

    right_arrow_2 = ttk.Button(arrow_frame_2, text=">", command=lambda: next_stall(1), width=5)
    right_arrow_2.pack(side="left", padx=5)

    arrow_frame_2 = ttk.Frame(table_frame, bootstyle="light")
    arrow_frame_2.pack(pady=5)

    abmelden_button = ttk.Button(table_frame, text="Abmelden", command=lambda: back_to_start(), bootstyle=DANGER)
    abmelden_button.pack(pady=10)

    daten_abfragen_und_fuellen(scrollable_frame, dieKW, dasjahr, derstall)

# Kundenliste Seite
customer_frame = ttk.Frame(root1, bootstyle="light")

customer_list_label = ttk.Label(customer_frame, text="Kundenverwaltung", font=("Helvetica", 14, "bold"), background="#f5f5f5")
customer_list_label.pack(pady=15)

customer_tree = ttk.Treeview(customer_frame, columns=("name", "plz", "adresse", "hausnummer", "stadt", "telefon", "email", "bemerkung"), show="headings", bootstyle="light")
for col in customer_tree["columns"]:
    customer_tree.heading(col, text=col.capitalize())
    customer_tree.column(col, width=100)

list_frame = ttk.Frame(customer_frame, padding=10)
list_frame.pack(fill="both", expand=True)

columns = ("id", "Name", "PLZ", "Adresse", "Hausnummer", "Stadt", "Telefonnummer", "Email", "Bemerkung")
customer_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
for col in columns:
    customer_tree.heading(col, text=col)
    customer_tree.column(col, width=100)

customer_tree.pack(fill="both", expand=True)
aktualisiere_ktabelle(customer_tree, lade_kundendaten())


back_button_customer = ttk.Button(customer_frame, text="Zurück", bootstyle="warning", command=back_to_start)
back_button_customer.pack(pady=10)

form_frame = ttk.Frame(customer_frame, padding=10)
form_frame.pack(fill="x", pady=5)

id_entry = ttk.Entry(form_frame, width=15)
id_entry.grid(row=0, column=5)
id_entry.grid_remove()

labels = ["Name*", "PLZ", "Adresse", "Hausnummer", "Stadt", "Telefonnummer*", "Email", "Bemerkung"]
kentries = {}
for i, label in enumerate(labels[:7]):
    ttk.Label(form_frame, text=label + ":").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=5, pady=5)
    entry = ttk.Entry(form_frame, width=30)
    entry.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=5)
    kentries[label] = entry

bemerkung_label = ttk.Label(form_frame, text="Bemerkung:")
bemerkung_label.grid(row=4, column=0, sticky="nw", padx=5, pady=5)
kbemerkung_text = Text(form_frame, width=30, height=4)
kbemerkung_text.grid(row=4, column=1, padx=5, pady=5)

(kname_entry, plz_entry, adresse_entry, hausnummer_entry, stadt_entry, telefon_entry, email_entry) = (
    kentries["Name*"], kentries["PLZ"], kentries["Adresse"], kentries["Hausnummer"],
    kentries["Stadt"], kentries["Telefonnummer*"], kentries["Email"]
)

button_frame = ttk.Frame(customer_frame, padding=10)
button_frame.pack(fill="x", pady=5)

ttk.Button(button_frame, text="Speichern", command=lambda: kunde_speichern(customer_tree), bootstyle=SUCCESS).pack(side="left", padx=10)
ttk.Button(button_frame, text="Bearbeiten", command=lambda: kunde_bearbeiten(customer_tree), bootstyle=INFO).pack(side="left", padx=10)
ttk.Button(button_frame, text="Leeren", command=lambda: clear_form(), bootstyle=DANGER).pack(side="left", padx=10)
ttk.Button(button_frame, text="Löschen", command=lambda: kunde_loeschen(customer_tree), bootstyle=DANGER).pack(side="right", padx=10)



# Produktliste Seite
product_frame = ttk.Frame(root1, bootstyle="light")
product_list_label = ttk.Label(product_frame, text="Produktverwaltung", font=("Helvetica", 14, "bold"), background="#f5f5f5")
product_list_label.pack(pady=15)

columns = ("Artikelnummer", "Name", "Preis", "Bemerkung")
prodtree = ttk.Treeview(product_frame, columns=columns, show="headings", bootstyle="light")
for col in columns:
    prodtree.heading(col, text=col)
    prodtree.column(col, width=150)

prodtree.pack(fill="both", expand=True, pady=10)

prodtree_scrollbar = ttk.Scrollbar(product_frame, orient="vertical", command=prodtree.yview)
prodtree.configure(yscrollcommand=prodtree_scrollbar.set)
prodtree_scrollbar.pack(side="right", fill="y")

back_button_product = ttk.Button(product_frame, text="Zurück", bootstyle="warning", command=back_to_start)
back_button_product.pack(pady=10)

prod_form_frame = ttk.Frame(product_frame, padding=10)
prod_form_frame.pack(fill="x", pady=10)

artikelnummer_label = ttk.Label(prod_form_frame, text="Artikelnummer*:", font=("Arial", 12))
artikelnummer_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
artikelnummer_entry = ttk.Entry(prod_form_frame, width=30)
artikelnummer_entry.grid(row=0, column=1, pady=5)

name_label = ttk.Label(prod_form_frame, text="Name*:", font=("Arial", 12))
name_label.grid(row=1, column=0, sticky="w", pady=5, padx=5)
name_entry = ttk.Entry(prod_form_frame, width=30)
name_entry.grid(row=1, column=1, pady=5)

preis_label = ttk.Label(prod_form_frame, text="Preis*:", font=("Arial", 12))
preis_label.grid(row=2, column=0, sticky="w", pady=5, padx=5)
preis_entry = ttk.Entry(prod_form_frame, width=30)
preis_entry.grid(row=2, column=1, pady=5)

bemerkung_label = ttk.Label(prod_form_frame, text="Bemerkung:", font=("Arial", 12))
bemerkung_label.grid(row=3, column=0, sticky="nw", pady=5, padx=5)
bemerkung_text = Text(prod_form_frame, width=40, height=5)
bemerkung_text.grid(row=3, column=1, pady=5)

aktualisiere_tabelle(prodtree)

button_frame = ttk.Frame(product_frame, padding=10)
button_frame.pack(fill="x", pady=10)

add_button = ttk.Button(button_frame, text="Speichern", command=lambda: produkt_speichern(prodtree), bootstyle=SUCCESS)
add_button.pack(side="left", padx=10)

edit_button = ttk.Button(button_frame, text="Bearbeiten", command=lambda: produkt_bearbeiten(prodtree), bootstyle=INFO)
edit_button.pack(side="left", padx=10)

clear_button = ttk.Button(button_frame, text="Leeren", command=lambda: clear_form(), bootstyle=DANGER)
clear_button.pack(side="left", padx=10)

delete_button = ttk.Button(button_frame, text="Löschen", command=lambda: produkt_loeschen(prodtree), bootstyle=DANGER)
delete_button.pack(side="right", padx=10)


root1.mainloop()