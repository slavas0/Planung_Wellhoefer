#from Main2 import MainApp
from tkinter import Canvas, Scrollbar, messagebox
from datetime import datetime, timedelta
import sys
import sqlite3  # Importiere SQLite (oder passe dies für dein DBMS an)
#import os
import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import Main

username = "nutzer"
derstall = "Stall 2"
dieKW = 7
dasjahr = 2024
id_regist = []
lastitems = []
allestalle = []
nextstall = derstall
nexttime = [dieKW, dasjahr]

def lastitemsdef():
    global lastitems
    conn = sqlite3.connect('datenbank/diedatenbank.db')  # Ersetze 'deine_datenbank.db' durch den Pfad deiner Datenbank
    cursor = conn.cursor()
    # SQL-Abfrage, um einen neuen Eintrag hinzuzufügen
    sql_insert = "INSERT INTO letztereintrag (nutzer, stall, kw, jahr) VALUES (?, ?, ?, ?)"
    cursor.execute(sql_insert, (username, derstall, dieKW, dasjahr))
    sql = "DELETE FROM letztereintrag WHERE id NOT IN (SELECT MAX(id) FROM letztereintrag GROUP BY nutzer, stall, kw, jahr);"
    cursor.execute(sql)
    # Änderungen speichern
    conn.commit()
    # SQL-Abfrage, um 10 Einträge nach absteigender ID zu bekommen
    sql = "SELECT stall, kw, jahr FROM letztereintrag WHERE nutzer = ? ORDER BY id"
    cursor.execute(sql, (username,))

    # Daten abrufen und lastitems füllen
    for row in cursor.fetchall():
        monat = kalenderwoche_monat(row[2], row[1])
        neuer_eintrag = [str(row[0]), monat, row[2]]
        if neuer_eintrag not in lastitems and len(lastitems) < 10:
            lastitems.append(neuer_eintrag)
    lastitems.sort(key=lambda x: (x[1], x[2]))
    cursor.execute("SELECT DISTINCT stall FROM letztereintrag;")
    global allestalle
    for i in cursor.fetchall():
        allestalle.append(i[0])
    conn.close()
    print(lastitems)

def kalenderwoche_daten(jahr, kw):
    # Der 4. Januar eines Jahres fällt immer in die erste Kalenderwoche nach ISO-8601
    vierten_januar = datetime(jahr, 1, 4)
    # Bestimme den Montag dieser Woche
    start_der_ersten_kw = vierten_januar - timedelta(days=vierten_januar.weekday())
    # Berechne den Montag der gewünschten KW
    start_der_kw = start_der_ersten_kw + timedelta(weeks=kw - 1)
    # Das Ende der KW ist 6 Tage nach dem Montag
    ende_der_kw = start_der_kw + timedelta(days=6)
    start_der_kw = ende_der_kw - timedelta(days=6)
    formatierter_start = start_der_kw.strftime("%d. %B %Y")  # z. B. 2. Dezember 2024
    formatierter_ende = ende_der_kw.strftime("%d. %B %Y")
    return formatierter_start, formatierter_ende
#evtl unnötig
def gleicher_monat_kw(jahr1, kw1, jahr2, kw2):
    def montag_von_kw(jahr, kw):
        # Der 4. Januar eines Jahres fällt immer in die erste Kalenderwoche nach ISO-8601
        vierten_januar = datetime(jahr, 1, 4)
        # Bestimme den Montag dieser Woche
        start_der_ersten_kw = vierten_januar - timedelta(days=vierten_januar.weekday())
        # Berechne den Montag der gewünschten KW
        start_der_kw = start_der_ersten_kw + timedelta(weeks=kw - 1)
        return start_der_kw  # Montag der Kalenderwoche

    # Bestimme die Montage für beide Kalenderwochen
    montag1 = montag_von_kw(jahr1, kw1)
    montag2 = montag_von_kw(jahr2, kw2)

    # Vergleiche die Monate der Montage
    return montag1.month == montag2.month
def kalenderwoche_monat(jahr, kw):
    # Der 4. Januar eines Jahres fällt immer in die erste Kalenderwoche nach ISO-8601
    vierten_januar = datetime(jahr, 1, 4)
    # Bestimme den Montag dieser Woche
    start_der_ersten_kw = vierten_januar - timedelta(days=vierten_januar.weekday())
    # Berechne den Montag der gewünschten Kalenderwoche
    start_der_kw = start_der_ersten_kw + timedelta(weeks=kw - 1)
    # Gib den Monat als Zahl zurück (1 = Januar, 12 = Dezember)
    return start_der_kw.month
# Hauptfenster erstellen mit einem modernen Theme
def create_main_window():
    window = ttk.Window(themename="sandstone")
    window.title("Wellhöfer Hühnerplanung")
    #window.geometry("1500x750")  # Fenstergröße
    window.geometry("1800x750")  # Fenstergröße
    return window

# Scrollbar und Canvas erstellen
def create_scrollable_area(root):
    canvas = Canvas(root)
    scrollable_frame = ttk.Frame(canvas)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Scrollbar zuerst versteckt, erst sichtbar machen, wenn nötig
    scrollbar.pack_forget()
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Dynamische Anpassung der Scrollregion nur bei Bedarf
    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Zeige Scrollbar nur, wenn der Inhalt größer als der sichtbare Bereich ist
        if scrollable_frame.winfo_height() > canvas.winfo_height():
            scrollbar.pack(side="right", fill="y")
        else:
            scrollbar.pack_forget()
            # Setze die yview auf 0, um sicherzustellen, dass kein Scrollen möglich ist
            canvas.yview_moveto(0)

    scrollable_frame.bind("<Configure>", update_scrollregion)

    return canvas, scrollable_frame



# Funktion zur Abfrage der Datenbank und zum Füllen der Textfelder
def daten_abfragen_und_fuellen(scrollable_frame, kw, jahr, stall):
    # Verbindung zur Datenbank herstellen (Passe den Pfad zur Datenbank an)
    conn = sqlite3.connect('datenbank/diedatenbank.db')  # Ersetze 'deine_datenbank.db' durch den Pfad deiner Datenbank
    cursor = conn.cursor()
    # SQL-Abfrage
    sql = "SELECT name, telefonnummer, braune, weise, verfahren, preis, bemerkung, id FROM eintrag WHERE kw = ? AND jahr = ? AND stall = ?"
    cursor.execute(sql, (kw, jahr, stall))
    daten = cursor.fetchall()

    # Überprüfen, ob Daten vorhanden sind
    if daten:
        for row in daten:
            eintrag_hinzufuegen(scrollable_frame, row[7])  # Erstellt ein neues Entry-Set
            aktueller_eintrag = entries[-1]  # Greife auf den zuletzt erstellten Eintrag zu

            # Fülle die entsprechenden Textfelder
            aktueller_eintrag["name"].insert(0, row[0])
            aktueller_eintrag["telefon"].insert(0, row[1])
            aktueller_eintrag["braun"].insert(0, row[2])
            aktueller_eintrag["weiss"].insert(0, row[3])
            aktueller_eintrag["verhalten"].insert(0, row[4])
            aktueller_eintrag["preis"].insert(0, row[5])
            aktueller_eintrag["bemerkung"].insert(0, row[6])
            aktueller_eintrag["id"].config(text=row[7])
            id_regist.append(row[7])
    #else:
     #   messagebox.showinfo("Keine Daten", "Es wurden keine Daten für die angegebene KW, Jahr und Stall gefunden.")

    conn.close()

# Funktion für das Mausrad-Scrollen
def enable_mouse_scroll(canvas):
    # Mausrad-Scrollen aktivieren (für Windows und Linux)
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    # Für macOS (da das Scrollen auf macOS anders gehandhabt wird)
    canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

# Überschrift und Titel erstellen
def create_title(root):
    title_label = ttk.Label(root, text="Planungssystem", font=("Arial", 28, "bold"))
    title_label.pack(pady=10)

# Funktion zum Erstellen der Spaltenüberschriften
def create_headers(scrollable_frame):
    headers = ["Name", "Telefonnummer", "Stück Braun", "Stück Weiß", "Verhalten", "Preis", "Bemerkung"]
    for i, header in enumerate(headers):
        label = ttk.Label(scrollable_frame, text=header, font=("Arial", 12, "bold"))
        label.grid(row=2, column=i, padx=10, pady=10)

# Dynamische Eintragsfunktion
entry_count = 0
entries = []  # Liste, um alle erstellten Einträge zu speichern
eingang = []

def eintrag_hinzufuegen(scrollable_frame, id):
    global entry_count
    row_offset = 3 + entry_count
    numb = len(id_regist)
    id_regist.append(0)
    # Dynamisch erstellte Bestellungsfelder
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

    # Label für die ID, um sie unsichtbar zu machen
    id_label = ttk.Label(scrollable_frame, text=id)
    id_label.grid(row=row_offset, column=7, padx=5, pady=5)  # Eine Spalte für die ID einfügen
    id_label.grid_remove()  # Das Label sofort verstecken
    # Label für die ID, um sie unsichtbar zu machen
    number_label = ttk.Label(scrollable_frame, text=numb)
    number_label.grid(row=row_offset, column=7, padx=5, pady=5)  # Eine Spalte für die ID einfügen
    number_label.grid_remove()  # Das Label sofort verstecken

    # Button zum Löschen des Eintrags
    delete_button = ttk.Button(scrollable_frame, text="Löschen",command=lambda: delete_entry(scrollable_frame, id, numb), bootstyle=DANGER)
    delete_button.grid(row=row_offset, column=8, padx=5, pady=5)  # Spalte 8

    check_button = ttk.Button(scrollable_frame, text="Check", command=lambda: check_entry(scrollable_frame, id, numb),bootstyle=SUCCESS)
    check_button.grid(row=row_offset, column=9, padx=5, pady=5)  # Spalte 9

    #id_entry.insert(0, id)
    # Speichern der Entry-Felder für späteres Speichern in der Datenbank
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

    entry_count += 1
def eingang_indb_speichern(kw, stall, jahr):
    """Speichert die aktuellen Eingaben in der Datenbanktabelle 'inventar'.
    Überschreibt vorhandene Einträge für die gleiche KW, Stall und Jahr.

    Args:
        kw: Die Kalenderwoche.
        stall: Der Stall.
        jahr: Das Jahr.
    """

    conn = sqlite3.connect('datenbank/diedatenbank.db')
    cursor = conn.cursor()

    for entry in eingang:
        # Zuerst versuchen, den Eintrag zu aktualisieren
        sql_update = """
        UPDATE inventar
        SET weiss = ?, braun = ?, lila = ?
        WHERE kw = ? AND stall = ? AND jahr = ?
        """
        cursor.execute(sql_update, (entry["weiss"], entry["braun"], entry["lila"], kw, stall, jahr))
        # Anzahl der betroffenen Zeilen überprüfen
        rows_affected = cursor.rowcount

        # Wenn keine Zeilen aktualisiert wurden (Eintrag existiert nicht), dann einen neuen anlegen
        if rows_affected == 0:
            sql_insert = """
            INSERT INTO inventar (kw, stall, jahr, weiss, braun, lila)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            values = (kw, stall, jahr, entry["weiss"], entry["braun"], entry["lila"])
            cursor.execute(sql_insert, values)

    conn.commit()
    conn.close()
# Funktion zum Speichern der Daten (Platzhalter für die spätere Datenbank)
def speichern_daten(textfeld_braun, textfeld_weiss, textfeld3):
    # Holen der Daten aus den Textfeldern
    weiss = int(textfeld_weiss.get())
    braun = int(textfeld_braun.get())
    lila = int(textfeld3.get())

    # Hinzufügen eines neuen Eintrags zu eingang
    eingang.append({'weiss': weiss, 'braun': braun, 'lila': lila})
    eingang_indb_speichern(dieKW, derstall, dasjahr)
    try:
        # Verbindung zur Datenbank herstellen (Passe den Pfad zur Datenbank an)
        conn = sqlite3.connect('datenbank/diedatenbank.db')
        cursor = conn.cursor()
        for entry in entries:
            id = entry["id"].cget("text")
            name = entry["name"].get()
            telefon = entry["telefon"].get()
            braun = entry["braun"].get()
            weiss = entry["weiss"].get()
            verhalten = entry["verhalten"].get()
            preis = entry["preis"].get()
            bemerkung = entry["bemerkung"].get()
            if id != 'none':
                # SQL-Abfrage zum Aktualisieren eines bestehenden Eintrags in der Tabelle 'eintrag'
                sql = """
                       UPDATE eintrag
                       SET stall = ?, kw = ?, jahr = ?, name = ?, telefonnummer = ?, braune = ?, weise = ?, verfahren = ?, preis = ?, bemerkung = ?
                       WHERE id = ?
                       """
                if braun == "": braun = 0
                if weiss == "": weiss = 0
                sql = f"UPDATE eintrag SET name = '{name}', stall = '{derstall}', kw = {int(dieKW)}, jahr = {int(dasjahr)}, telefonnummer = '{telefon}', braune = {braun}, weise = {weiss}, verfahren = '{verhalten}', preis = '{preis}', bemerkung = '{bemerkung}' WHERE id = {id};"
                # Ausführen der SQL-Abfrage für Update
                #cursor.execute(sql, (derstall, dieKW, dasjahr, name, telefon, braun, weiss, verhalten, preis, bemerkung, int(id)))  # id in int umwandeln
                cursor.execute("SELECT id FROM eintrag WHERE id = ?", (id,))
                isnone = cursor.fetchone()
                if isnone == 'None':
                    sql = "INSERT INTO eintrag (id, stall, kw, jahr, name, telefonnummer, braune, weise, verfahren, preis, bemerkung) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    cursor.execute(sql,(id, derstall, dieKW, dasjahr, name, telefon, braun, weiss, verhalten, preis, bemerkung))
                else:
                    cursor.execute(sql)
                conn.commit()
            else:
                if (name + telefon + str(braun) + str(weiss) + verhalten + preis + bemerkung) != "":
                    # SQL-Abfrage zum Einfügen eines neuen Eintrags in die Tabelle 'eintrag'
                    sql = """
                           INSERT INTO eintrag (stall, kw, jahr, name, telefonnummer, braune, weise, verfahren, preis, bemerkung)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """
                    # Ausführen der SQL-Abfrage für Insert
                    cursor.execute(sql,(derstall, dieKW, dasjahr, name, telefon, braun, weiss, verhalten, preis, bemerkung))
                    # SQL-Abfrage zum Abrufen der maximalen ID mit Platzhaltern
                    sql_max_id = "SELECT MAX(id) FROM eintrag WHERE stall = ? AND kw = ? AND jahr = ?"
                    # Ausführen der Abfrage und Übergabe der Parameter
                    cursor.execute(sql_max_id, (derstall, dieKW, dasjahr))
                    # Abrufen des Ergebnisses
                    max_id = cursor.fetchone()[0]
                    print(max_id)
                    entry["id"].config(text=max_id)
                    id_regist[int(entry["number"].cget("text"))] = max_id
            # Hier können die Daten in eine Datenbank gespeichert werden
            print(f"Speichere: Name={name}, Telefon={telefon}, Braun={braun}, Weiß={weiss}, Verhalten={verhalten}, Preis={preis}, Bemerkung={bemerkung} in {derstall} am {dieKW} {dasjahr}")
        conn.commit()
        # Temporäre Meldung zur Bestätigung des Speichervorgangs
        messagebox.showinfo("Speichern", "Die Daten wurden erfolgreich gespeichert!")
    except sqlite3.Error as e:
        messagebox.showerror("Datenbankfehler", str(e))
    finally:
        if conn:
            conn.close()
# Button zum Hinzufügen eines neuen Eintrags
def create_add_button(root, scrollable_frame):
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)

    hinzufuegen_button = ttk.Button(button_frame, text="Eintrag hinzufügen", command=lambda: eintrag_hinzufuegen(scrollable_frame, NONE), bootstyle=SUCCESS)
    hinzufuegen_button.pack(side="left", padx=10)

# Button zum Speichern der Einträge
def create_save_button(root, textfeld_braun, textfeld_weiss, textfeld3):
    speichern_button = ttk.Button(root, text="Speichern",command=lambda: speichern_daten(textfeld_braun, textfeld_weiss, textfeld3),bootstyle=PRIMARY)
    speichern_button.pack(pady=10)

def delete_entry(scrollable_frame, entry_id, numb):
    if entry_id == 'none':
        entry_id = id_regist[numb]  # Hole die ID aus der Liste basierend auf der Eintragsnummer
        if entry_id == 0:
            # Linie löschen, ohne in der DB zu löschen
            remove_entry_from_gui(numb)  # Entferne das Widget aus der GUI
            return

    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect('datenbank/diedatenbank.db')
    cursor = conn.cursor()

    # Überprüfen, ob der Eintrag mit der angegebenen ID existiert
    cursor.execute("SELECT id FROM eintrag WHERE id = ?", (entry_id,))
    result = cursor.fetchone()

    if result:
        # Datenbankeintrag löschen
        cursor.execute("DELETE FROM eintrag WHERE id = ?", (entry_id,))
        conn.commit()
        messagebox.showinfo("Löschen", f"Eintrag mit ID {entry_id} wurde gelöscht.")

        # Lösche den entsprechenden Eintrag aus dem GUI
        remove_entry_from_gui(numb)

    else:
        messagebox.showwarning("Nicht gefunden", f"Eintrag mit ID {entry_id} existiert nicht.")

    # Verbindung schließen
    conn.close()

    # Scrollregion nach dem Löschen aktualisieren
    update_scrollregion(scrollable_frame)

# Funktion, um den Eintrag basierend auf der Eintragsnummer zu entfernen
def remove_entry_from_gui(numb):
    for entry in entries:
        if entry["number"].cget("text") == str(numb):
            for widget in entry.values():
                widget.grid_remove()  # Entferne das Widget nur aus der Ansicht (nicht zerstören)
            break

# Scrollregion dynamisch aktualisieren
def update_scrollregion(scrollable_frame):
    scrollable_frame.update_idletasks()  # GUI aktualisieren
    scrollable_frame.winfo_toplevel().children['!canvas'].configure(
        scrollregion=scrollable_frame.bbox("all")
    )
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
        conn = sqlite3.connect('datenbank/diedatenbank.db')
        cursor = conn.cursor()

        # Ändern Sie 'inventar' in 'eintrag', wenn dies die korrekte Tabelle ist
        sql = "SELECT SUM(braune), SUM(weise) FROM eintrag WHERE stall = ? AND kw = ? AND jahr = ?"
        cursor.execute(sql, (derstall, dieKW, dasjahr))
        result = cursor.fetchone()
        conn.close()

        if result:
            braun_summe, weiss_summe = result
            braun_summe_label.config(text=f"Braun: {braun_summe}")
            weiss_summe_label.config(text=f"Weiß: {weiss_summe}")
        else:
            braun_summe_label.config(text="Braun: 0")
            weiss_summe_label.config(text="Weiß: 0")

    # Initialisierung der Summen-Labels
    berechne_summen()

    ubrig_label = ttk.Label(footer_frame, text="Übrige Tieranzahl", font=("Arial", 12, "bold"))
    ubrig_label.pack(side="left", padx=10)

    braun_ubrig_label = ttk.Label(footer_frame, font=("Arial", 12))
    braun_ubrig_label.pack(side="left", padx=10)

    weiss_ubrig_label = ttk.Label(footer_frame, font=("Arial", 12))
    weiss_ubrig_label.pack(side="left", padx=10)

    def berechne_ubrig():
        conn = sqlite3.connect('datenbank/diedatenbank.db')
        cursor = conn.cursor()

        # Ändern Sie 'inventar' in 'eintrag', wenn dies die korrekte Tabelle ist
        sql = "SELECT braun, weiss FROM inventar WHERE stall = ? AND kw = ? AND jahr = ?"
        cursor.execute(sql, (derstall, dieKW, dasjahr))
        result = cursor.fetchone()
        conn.close()

        if result:
            braun_ubrig, weiss_ubrig = result
            try:
                braune_summe = int(re.sub(r"[^\d-]", "", braun_summe_label.cget("text")))
            except ValueError:
                braune_summe = 0  # Setzen Sie einen Standardwert, falls die Umwandlung fehlschlägt

            try:
                weisse_summe = int(re.sub(r"[^\d-]", "", weiss_summe_label.cget("text")))
            except ValueError:
                weisse_summe = 0  # Setzen Sie einen Standardwert, falls die Umwandlung fehlschlägt

            braun = braun_ubrig - braune_summe
            weiss = weiss_ubrig - weisse_summe
            braun_ubrig_label.config(text=f"Braun: {braun}")
            weiss_ubrig_label.config(text=f"Weiß: {weiss}")
        else:
            braun_ubrig_label.config(text="Braun: 0")
            weiss_ubrig_label.config(text="Weiß: 0")

    # Initialisierung der Summen-Labels
    berechne_ubrig()
# Funktion zum Begrüßen des Benutzers
def create_welcome_label(root):
    welcome_label = ttk.Label(root, text=f"Willkommen, {username}!", font=("Arial", 16))
    welcome_label.pack(pady=10)
# Text "Stall 2 KW 7 2024" hinzufügen
def create_large_text(root):
    txt = derstall + " - KW " + str(dieKW) + " " + str(dasjahr)
    large_text_label = ttk.Label(root, text=txt, font=("Arial", 20, "bold"))
    large_text_label.pack(pady=10)
    txt2a, txt2b = kalenderwoche_daten(dasjahr, dieKW)
    txt2 = f"Woche vom {txt2a}\n bis {txt2b}"
    large_text2_label = ttk.Label(root, text=txt2, font=("Arial", 20, "bold"))
    large_text2_label.pack(pady=10)
def select_kw_jahr_stall(neukw, neustall, neujahr):
    root.destroy()  # Schließe das aktuelle
    starten(neustall, neukw, neujahr, username)
    #neustall = neustall.replace(" ", "-")
    #os.system(f"python Main2.py {username} {neustall} {neukw} {neujahr}")

def select_kw_jahr_stall_fake(neukw, neustall, neujahr):
    global root  # Damit wir die aktuelle Instanz von `root` referenzieren können

    # Schließe das aktuelle Fenster
    root.destroy()

    # Passe den Stallnamen an
    neustall = neustall.replace(" ", "-")
    global derstall, dieKW, dasjahr
    derstall = neustall
    dieKW = neukw
    dasjahr = neujahr
    # Starte die Klasse oder lade die neue Ansicht
    main()
def erster_montag_kw(monat, jahr):
    # Starte am ersten Tag des Monats
    erster_tag = datetime(jahr, monat, 1)
    # Berechne den ersten Montag: gehe bis zum nächsten Montag, falls nötig
    erster_montag = erster_tag + timedelta(days=(7 - erster_tag.weekday()) % 7)
    # Gib die Kalenderwoche zurück
    kalenderwoche = erster_montag.isocalendar()[1]  # isocalendar()[1] = Kalenderwoche
    erster_montag2 = erster_montag.strftime("%d. %B %Y")
    return kalenderwoche
def month_to_kw(month, jahr, stall):
    kw = erster_montag_kw(month, jahr)
    select_kw_jahr_stall(kw, stall, jahr)
def create_last_items_tabs(root):
    last_items_frame = ttk.Frame(root)
    last_items_frame.pack(side="bottom", fill="x", pady=10)
    monate = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    lastitemsdef()
    # Gehe durch jeden Eintrag in lastitems und erstelle einen Tab/Button dafür
    for idx, item in enumerate(lastitems):
        tab_text = f"{item[0]} - {monate[item[1]-1]} {item[2]}"
        last_item_tab = ttk.Button(last_items_frame, text=tab_text, bootstyle=SECONDARY)
        # Erstelle den Button und weise eine Funktion zu, die select_kw_jahr_stall aufruft
        last_item_tab = ttk.Button(last_items_frame,
                                   text=tab_text,
                                   bootstyle=SECONDARY,
                                   command=lambda i=item: month_to_kw(i[1], i[2], i[0]))

        last_item_tab.pack(side="left", padx=5, pady=5)
def eingang_db_abfragen():
    """Fragt die Datenbank nach den Mengen für Braun, Weiß und Lila,
    basierend auf den globalen Variablen dieKW, derstall und dasjahr.

    Returns:
        Ein Tupel (braun, weiss, lila) mit den entsprechenden Mengen oder None, wenn kein Eintrag gefunden wurde.
    """

    conn = sqlite3.connect('datenbank/diedatenbank.db')
    cursor = conn.cursor()

    sql = "SELECT braun, weiss, lila FROM inventar WHERE kw = ? AND stall = ? AND jahr = ?"
    cursor.execute(sql, (dieKW, derstall, dasjahr))
    result = cursor.fetchone()

    conn.close()

    if result:
        braun, weiss, lila = result
        return braun, weiss, lila
    else:
        return 0, 0, 0
# Hauptfunktion, die das GUI erstellt und startet
def main():
    # Fenster erstellen
    global root  # Stelle sicher, dass diese Variable global ist
    global nextstall  # Stelle sicher, dass diese Variable global ist
    # Funktion, um nextKW zu aktualisieren

    def update_next_kw(change):
        kwtemp = nexttime[0] + change
        nexttime[0] = (kwtemp - 1) % 53 + 1  # kw wird im Bereich von 1 bis 53 gehalten
        if kwtemp < 1:
            nexttime[1] -= 1
        elif kwtemp > 53:
            nexttime[1] += 1
        print(nexttime)
        # Hier könnte zusätzlich eine Funktion zum Aktualisieren des Labels für nextKW aufgerufen werden
        next_kw_label.config(text=str(nexttime[0]))  # Aktualisiere das Label
    # Funktion für nextstall
    def next_stall(change):
        global nextstall
        # Suche den aktuellen Index von nextstall in allestalle
        try:
            current_index = allestalle.index(nextstall)  # Finde den Index von nextstall
            # Berechne den neuen Index
            new_index = (current_index + change) % len(allestalle)  # Verwende Modulo für Kreisverhalten
            nextstall = allestalle[new_index]  # Setze nextstall auf den neuen Wert

        except ValueError:
            print(f"nextstall {allestalle} nicht in allestalle gefunden.")
        next_stall_label.config(text=str(nextstall))  # Aktualisiere das Label

    root = create_main_window()

    # Füge die Tabs ganz unten im Fenster hinzu
    create_last_items_tabs(root)
    create_footer(root)
    # Scrollbereich einrichten
    canvas, scrollable_frame = create_scrollable_area(root)

    # Mausrad-Scrollen aktivieren
    enable_mouse_scroll(canvas)

    # Titel und Überschrift
    create_title(root)
    create_welcome_label(root)  # Hier den Willkommenslabel hinzufügen
    create_large_text(root)
    # Neue Textfelder hinzufügen (z.B. in der zweiten Zeile)
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
    textfeld3 = ttk.Entry(scrollable_frame)
    textfeld3.grid(row=1, column=2, padx=5, pady=5)

    textfeld_braun.insert(0, braun)
    textfeld_weiss.insert(0, weiss)
    textfeld3.insert(0, lila)
    create_headers(scrollable_frame)
    # Hinzufügen-Button, Speichern-Button und Fußzeile
    create_add_button(root, scrollable_frame)
    create_save_button(root, textfeld_braun, textfeld_weiss, textfeld3)

    # Refresh-Button
    wechsel_button = ttk.Button(root, text="Refresh",
                                command=lambda: select_kw_jahr_stall(nexttime[0], nextstall, nexttime[1]))
    wechsel_button.pack(pady=10)
    def abmelden():
        root.destroy()  # Schließe das aktuelle Fenster
        #update_gui()
        Main.starten()
        #os.system(f"python Main.py")
    # Refresh-Button
    abmelden_button = ttk.Button(root, text="Abmelden",
                                command=lambda: abmelden(), bootstyle=DANGER)
    abmelden_button.pack(pady=10)
    # Buttons mit großen Pfeilen nach links und rechts für nextKW
    arrow_frame_1 = ttk.Frame(root)
    arrow_frame_1.pack(pady=5)

    left_arrow_1 = ttk.Button(arrow_frame_1, text="<<",
                              command=lambda: update_next_kw(-10), width=5)
    left_arrow_1.pack(side="left", padx=5)

    left_arrow_12 = ttk.Button(arrow_frame_1, text="<",
                              command=lambda: update_next_kw(-1), width=5)
    left_arrow_12.pack(side="left", padx=5)

    # Label für nextKW
    next_kw_label = ttk.Label(arrow_frame_1, text=str(nexttime[0]))
    next_kw_label.pack(side="left", padx=5)

    right_arrow_1 = ttk.Button(arrow_frame_1, text=">",
                               command=lambda: update_next_kw(1), width=5)
    right_arrow_1.pack(side="left", padx=5)
    right_arrow_12 = ttk.Button(arrow_frame_1, text=">>",
                               command=lambda: update_next_kw(10), width=5)
    right_arrow_12.pack(side="left", padx=5)

    # Zweite Zeile mit Buttons für nextstall
    arrow_frame_2 = ttk.Frame(root)
    arrow_frame_2.pack(pady=5)

    left_arrow_2 = ttk.Button(arrow_frame_2, text="<",
                              command=lambda: next_stall(-1), width=5)
    left_arrow_2.pack(side="left", padx=5)

    # Label für nextstall
    next_stall_label = ttk.Label(arrow_frame_2, text=str(nextstall))
    next_stall_label.pack(side="left", padx=5)

    right_arrow_2 = ttk.Button(arrow_frame_2, text=">",
                               command=lambda: next_stall(1), width=5)
    right_arrow_2.pack(side="left", padx=5)

    # Zweite Zeile mit Buttons für nextstall
    arrow_frame_2 = ttk.Frame(root)
    arrow_frame_2.pack(pady=5)

    # Eingabefeld für nextstall
    next_stall_var = ttk.StringVar(value=str(nextstall))  # Variabel, um Wert zu binden
    next_stall_entry = ttk.Entry(arrow_frame_2, textvariable=next_stall_var, justify="center", width=10)
    next_stall_entry.pack(side="left", padx=5)

    # Event, um Eingabe zu bestätigen
    def update_stall(event=None):
        global nextstall
        try:
            new_stall = str(next_stall_var.get())
            nextstall = new_stall
            next_stall_label.config(text=str(nextstall))  # Aktualisiere das Label
            #set_stall(new_stall)  # Funktion zum Setzen des neuen Stalls
        except ValueError:
            next_stall_var.set(str(nextstall))  # Bei ungültiger Eingabe zurücksetzen

    next_stall_entry.bind("<Return>", update_stall)  # Bestätigen mit Enter


    # Fülle den Scrollbereich mit Daten
    daten_abfragen_und_fuellen(scrollable_frame, dieKW, dasjahr, derstall)
    # Mainloop starten
    root.mainloop()
def starten(stall, kw, jahr, name):
    global derstall, nextstall, dieKW, dasjahr, nexttime, username
    username = name
    derstall = nextstall = stall
    dieKW = kw
    dasjahr = jahr
    nexttime = [kw, jahr]
    main()
    print(f"Willkommen, {username}. Stall: {derstall}, KW: {dieKW}, Jahr: {dasjahr}")


def einfachso():
#if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]  # Das erste Argument (nach dem Skriptnamen)
        print(f"Willkommen, {username}!")  # Beispielausgabe
        if len(sys.argv) > 3:
            derstall = sys.argv[2]
            dieKW = int(sys.argv[3])
            dasjahr = int(sys.argv[4])
            derstall = derstall.replace("-", " ")
            print(f"Stall: {derstall}, KW: {dieKW}, Jahr: {dasjahr}")
            nextstall = derstall
            nexttime = [dieKW, dasjahr]

    else:
        print("Kein Benutzername übergeben.")
    main()
