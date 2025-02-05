from tkinter import StringVar  # Fügen Sie dies hinzu
from ttkbootstrap import Window, Frame, Label, Entry, Button, Scrollbar, Style
from ttkbootstrap.constants import *
from tkinter import Canvas, messagebox
from datetime import datetime, timedelta
import sys
import sqlite3
import re

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
    conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
    cursor = conn.cursor()
    sql_insert = "INSERT INTO letztereintrag (nutzer, stall, kw, jahr) VALUES (?, ?, ?, ?)"
    cursor.execute(sql_insert, (username, derstall, dieKW, dasjahr))
    sql = "DELETE FROM letztereintrag WHERE id NOT IN (SELECT MAX(id) FROM letztereintrag GROUP BY nutzer, stall, kw, jahr);"
    cursor.execute(sql)
    conn.commit()
    sql = "SELECT stall, kw, jahr FROM letztereintrag WHERE nutzer = ? ORDER BY id"
    cursor.execute(sql, (username,))
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

def create_main_window():
    window = Window(themename="sandstone")
    window.title("Planungssystem")
    window.geometry("1800x750")
    return window

def create_scrollable_area(root):
    canvas = Canvas(root)
    scrollable_frame = Frame(canvas)
    scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
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
    conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
    cursor = conn.cursor()
    sql = "SELECT name, telefonnummer, braune, weise, verfahren, preis, bemerkung, id FROM eintrag WHERE kw = ? AND jahr = ? AND stall = ?"
    cursor.execute(sql, (kw, jahr, stall))
    daten = cursor.fetchall()
    if daten:
        for row in daten:
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
    conn.close()

def enable_mouse_scroll(canvas):
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
    canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

def create_title(root):
    title_label = Label(root, text="Planungssystem", font=("Arial", 28, "bold"))
    title_label.pack(pady=10)

def create_headers(scrollable_frame):
    headers = ["Name", "Telefonnummer", "Stück Braun", "Stück Weiß", "Verhalten", "Preis", "Bemerkung"]
    for i, header in enumerate(headers):
        label = Label(scrollable_frame, text=header, font=("Arial", 12, "bold"))
        label.grid(row=2, column=i, padx=10, pady=10)

entry_count = 0
entries = []
eingang = []

def eintrag_hinzufuegen(scrollable_frame, id):
    global entry_count
    row_offset = 3 + entry_count
    numb = len(id_regist)
    id_regist.append(0)
    name_entry = Entry(scrollable_frame)
    name_entry.grid(row=row_offset, column=0, padx=5, pady=5)
    telefon_entry = Entry(scrollable_frame)
    telefon_entry.grid(row=row_offset, column=1, padx=5, pady=5)
    braun_entry = Entry(scrollable_frame)
    braun_entry.grid(row=row_offset, column=2, padx=5, pady=5)
    weiss_entry = Entry(scrollable_frame)
    weiss_entry.grid(row=row_offset, column=3, padx=5, pady=5)
    verhalten_entry = Entry(scrollable_frame)
    verhalten_entry.grid(row=row_offset, column=4, padx=5, pady=5)
    preis_entry = Entry(scrollable_frame)
    preis_entry.grid(row=row_offset, column=5, padx=5, pady=5)
    bemerkung_entry = Entry(scrollable_frame)
    bemerkung_entry.grid(row=row_offset, column=6, padx=5, pady=5)
    id_label = Label(scrollable_frame, text=id)
    id_label.grid(row=row_offset, column=7, padx=5, pady=5)
    id_label.grid_remove()
    number_label = Label(scrollable_frame, text=numb)
    number_label.grid(row=row_offset, column=7, padx=5, pady=5)
    number_label.grid_remove()
    delete_button = Button(scrollable_frame, text="Löschen", command=lambda: delete_entry(scrollable_frame, id, numb), bootstyle=DANGER)
    delete_button.grid(row=row_offset, column=8, padx=5, pady=5)
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
    conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
    cursor = conn.cursor()
    for entry in eingang:
        sql_update = """
        UPDATE inventar
        SET weiss = ?, braun = ?, lila = ?
        WHERE kw = ? AND stall = ? AND jahr = ?
        """
        cursor.execute(sql_update, (entry["weiss"], entry["braun"], entry["lila"], kw, stall, jahr))
        rows_affected = cursor.rowcount
        if rows_affected == 0:
            sql_insert = """
            INSERT INTO inventar (kw, stall, jahr, weiss, braun, lila)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            values = (kw, stall, jahr, entry["weiss"], entry["braun"], entry["lila"])
            cursor.execute(sql_insert, values)
    conn.commit()
    conn.close()

def speichern_daten(textfeld_braun, textfeld_weiss, textfeld3):
    weiss = int(textfeld_weiss.get())
    braun = int(textfeld_braun.get())
    lila = int(textfeld3.get())
    eingang.append({'weiss': weiss, 'braun': braun, 'lila': lila})
    eingang_indb_speichern(dieKW, derstall, dasjahr)
    try:
        conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
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
                sql = f"UPDATE eintrag SET name = '{name}', stall = '{derstall}', kw = {int(dieKW)}, jahr = {int(dasjahr)}, telefonnummer = '{telefon}', braune = {braun}, weise = {weiss}, verfahren = '{verhalten}', preis = '{preis}', bemerkung = '{bemerkung}' WHERE id = {id};"
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
                    sql = """
                           INSERT INTO eintrag (stall, kw, jahr, name, telefonnummer, braune, weise, verfahren, preis, bemerkung)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """
                    cursor.execute(sql,(derstall, dieKW, dasjahr, name, telefon, braun, weiss, verhalten, preis, bemerkung))
                    sql_max_id = "SELECT MAX(id) FROM eintrag WHERE stall = ? AND kw = ? AND jahr = ?"
                    cursor.execute(sql_max_id, (derstall, dieKW, dasjahr))
                    max_id = cursor.fetchone()[0]
                    print(max_id)
                    entry["id"].config(text=max_id)
                    id_regist[int(entry["number"].cget("text"))] = max_id
            print(f"Speichere: Name={name}, Telefon={telefon}, Braun={braun}, Weiß={weiss}, Verhalten={verhalten}, Preis={preis}, Bemerkung={bemerkung} in {derstall} am {dieKW} {dasjahr}")
        conn.commit()
        messagebox.showinfo("Speichern", "Die Daten wurden erfolgreich gespeichert!")
    except sqlite3.Error as e:
        messagebox.showerror("Datenbankfehler", str(e))
    finally:
        if conn:
            conn.close()

def create_add_button(root, scrollable_frame):
    button_frame = Frame(root)
    button_frame.pack(pady=10)
    hinzufuegen_button = Button(button_frame, text="Eintrag hinzufügen", command=lambda: eintrag_hinzufuegen(scrollable_frame, NONE), bootstyle=SUCCESS)
    hinzufuegen_button.pack(side="left", padx=10)

def create_save_button(root, textfeld_braun, textfeld_weiss, textfeld3):
    speichern_button = Button(root, text="Speichern", command=lambda: speichern_daten(textfeld_braun, textfeld_weiss, textfeld3), bootstyle=PRIMARY)
    speichern_button.pack(pady=10)

def delete_entry(scrollable_frame, entry_id, numb):
    if entry_id == 'none':
        entry_id = id_regist[numb]
        if entry_id == 0:
            remove_entry_from_gui(numb)
            return
    conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM eintrag WHERE id = ?", (entry_id,))
    result = cursor.fetchone()
    if result:
        cursor.execute("DELETE FROM eintrag WHERE id = ?", (entry_id,))
        conn.commit()
        messagebox.showinfo("Löschen", f"Eintrag mit ID {entry_id} wurde gelöscht.")
        remove_entry_from_gui(numb)
    else:
        messagebox.showwarning("Nicht gefunden", f"Eintrag mit ID {entry_id} existiert nicht.")
    conn.close()
    update_scrollregion(scrollable_frame)

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

    footer_frame = Frame(root)
    footer_frame.pack(side="bottom", fill="x", pady=10)

    gesamt_label = Label(footer_frame, text="Gesamte bestellte Tieranzahl", font=("Arial", 12, "bold"))
    gesamt_label.pack(side="left", padx=10)

    braun_summe_label = Label(footer_frame, font=("Arial", 12))
    braun_summe_label.pack(side="left", padx=10)

    weiss_summe_label = Label(footer_frame, font=("Arial", 12))
    weiss_summe_label.pack(side="left", padx=10)

    def berechne_summen():
        conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
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

    ubrig_label = Label(footer_frame, text="Übrige Tieranzahl", font=("Arial", 12, "bold"))
    ubrig_label.pack(side="left", padx=10)

    braun_ubrig_label = Label(footer_frame, font=("Arial", 12))
    braun_ubrig_label.pack(side="left", padx=10)

    weiss_ubrig_label = Label(footer_frame, font=("Arial", 12))
    weiss_ubrig_label.pack(side="left", padx=10)

    def berechne_ubrig():
        conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
        cursor = conn.cursor()

        # Ändern Sie 'inventar' in 'eintrag', wenn dies die korrekte Tabelle ist
        sql = "SELECT braun, weiss FROM inventar WHERE stall = ? AND kw = ? AND jahr = ?"
        cursor.execute(sql, (derstall, dieKW, dasjahr))
        result = cursor.fetchone()
        conn.close()

        if result:
            braun_ubrig, weiss_ubrig = result
            braune_summe = int(re.sub(r"[^\d-]", "", braun_summe_label.cget("text")))
            weisse_summe = int(re.sub(r"[^\d-]", "", weiss_summe_label.cget("text")))
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
# Funktion zum Begrüßen des Benutzers
def create_welcome_label(root):
    welcome_label = Label(root, text=f"Willkommen, {username}!", font=("Arial", 16))
    welcome_label.pack(pady=10)

# Text "Stall 2 KW 7 2024" hinzufügen
def create_large_text(root):
    txt = derstall + " - KW " + str(dieKW) + " " + str(dasjahr)
    large_text_label = Label(root, text=txt, font=("Arial", 20, "bold"))
    large_text_label.pack(pady=10)
    txt2a, txt2b = kalenderwoche_daten(dasjahr, dieKW)
    txt2 = f"Woche vom {txt2a}\n bis {txt2b}"
    large_text2_label = Label(root, text=txt2, font=("Arial", 20, "bold"))
    large_text2_label.pack(pady=10)

def select_kw_jahr_stall(neukw, neustall, neujahr):
    root.withdraw()  # Schließe das aktuelle Fenster
    starten(neustall, neukw, neujahr, username)

def select_kw_jahr_stall_fake(neukw, neustall, neujahr):
    global root, derstall, dieKW, dasjahr
    root.withdraw()
    neustall = neustall.replace(" ", "-")
    derstall = neustall
    dieKW = neukw
    dasjahr = neujahr
    main()

def erster_montag_kw(monat, jahr):
    erster_tag = datetime(jahr, monat, 1)
    erster_montag = erster_tag + timedelta(days=(7 - erster_tag.weekday()) % 7)
    kalenderwoche = erster_montag.isocalendar()[1]
    erster_montag2 = erster_montag.strftime("%d. %B %Y")
    return kalenderwoche

def month_to_kw(month, jahr, stall):
    kw = erster_montag_kw(month, jahr)
    select_kw_jahr_stall(kw, stall, jahr)

def create_last_items_tabs(root):
    last_items_frame = Frame(root)
    last_items_frame.pack(side="bottom", fill="x", pady=10)
    monate = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    lastitemsdef()
    for idx, item in enumerate(lastitems):
        tab_text = f"{item[0]} - {monate[item[1]-1]} {item[2]}"
        last_item_tab = Button(last_items_frame, text=tab_text, bootstyle=SECONDARY, command=lambda i=item: month_to_kw(i[1], i[2], i[0]))
        last_item_tab.pack(side="left", padx=5, pady=5)

def eingang_db_abfragen():
    conn = sqlite3.connect('../../PycharmProjects/Planung_Wellhoefer/datenbank/diedatenbank.db')
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
    global root, nextstall

    # Wenn root bereits existiert, verstecke es
    if 'root' in globals() and root:
        root.withdraw()

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
        next_stall_label.config(text=str(nextstall))

    root = create_main_window()
    create_last_items_tabs(root)
    create_footer(root)
    canvas, scrollable_frame = create_scrollable_area(root)
    enable_mouse_scroll(canvas)
    create_title(root)
    create_welcome_label(root)
    create_large_text(root)

    braun, weiss, lila = eingang_db_abfragen()
    label = Label(scrollable_frame, text="Braune", font=("Arial", 12, "bold"))
    label.grid(row=0, column=0, padx=10, pady=10)
    textfeld_braun = Entry(scrollable_frame)
    textfeld_braun.grid(row=1, column=0, padx=5, pady=5)

    label = Label(scrollable_frame, text="Weiße", font=("Arial", 12, "bold"))
    label.grid(row=0, column=1, padx=10, pady=10)
    textfeld_weiss = Entry(scrollable_frame)
    textfeld_weiss.grid(row=1, column=1, padx=5, pady=5)

    label = Label(scrollable_frame, text="Anmerkung", font=("Arial", 12, "bold"))
    label.grid(row=0, column=2, padx=10, pady=10)
    textfeld3 = Entry(scrollable_frame)
    textfeld3.grid(row=1, column=2, padx=5, pady=5)

    textfeld_braun.insert(0, braun)
    textfeld_weiss.insert(0, weiss)
    textfeld3.insert(0, lila)
    create_headers(scrollable_frame)
    create_add_button(root, scrollable_frame)
    create_save_button(root, textfeld_braun, textfeld_weiss, textfeld3)

    wechsel_button = Button(root, text="Refresh", command=lambda: select_kw_jahr_stall(nexttime[0], nextstall, nexttime[1]))
    wechsel_button.pack(pady=10)

    def abmelden():
        root.destroy()
        import Main
        Main.starten()

    abmelden_button = Button(root, text="Abmelden", command=abmelden, bootstyle=DANGER)
    abmelden_button.pack(pady=10)

    arrow_frame_1 = Frame(root)
    arrow_frame_1.pack(pady=5)

    left_arrow_1 = Button(arrow_frame_1, text="<<", command=lambda: update_next_kw(-10), width=5)
    left_arrow_1.pack(side="left", padx=5)

    left_arrow_12 = Button(arrow_frame_1, text="<", command=lambda: update_next_kw(-1), width=5)
    left_arrow_12.pack(side="left", padx=5)

    next_kw_label = Label(arrow_frame_1, text=str(nexttime[0]))
    next_kw_label.pack(side="left", padx=5)

    right_arrow_1 = Button(arrow_frame_1, text=">", command=lambda: update_next_kw(1), width=5)
    right_arrow_1.pack(side="left", padx=5)

    right_arrow_12 = Button(arrow_frame_1, text=">>", command=lambda: update_next_kw(10), width=5)
    right_arrow_12.pack(side="left", padx=5)

    arrow_frame_2 = Frame(root)
    arrow_frame_2.pack(pady=5)

    left_arrow_2 = Button(arrow_frame_2, text="<", command=lambda: next_stall(-1), width=5)
    left_arrow_2.pack(side="left", padx=5)

    next_stall_label = Label(arrow_frame_2, text=str(nextstall))
    next_stall_label.pack(side="left", padx=5)

    right_arrow_2 = Button(arrow_frame_2, text=">", command=lambda: next_stall(1), width=5)
    right_arrow_2.pack(side="left", padx=5)

    next_stall_var = StringVar(value=str(nextstall))
    next_stall_entry = Entry(arrow_frame_2, textvariable=next_stall_var, justify="center", width=10)
    next_stall_entry.pack(side="left", padx=5)

    def update_stall(event=None):
        global nextstall
        try:
            new_stall = str(next_stall_var.get())
            nextstall = new_stall
            next_stall_label.config(text=str(nextstall))
        except ValueError:
            next_stall_var.set(str(nextstall))

    next_stall_entry.bind("<Return>", update_stall)

    daten_abfragen_und_fuellen(scrollable_frame, dieKW, dasjahr, derstall)
    root.mainloop()

def starten(stall, kw, jahr, name):
    global derstall, nextstall, dieKW, dasjahr, nexttime, username
    username = name
    derstall = nextstall = stall
    dieKW = kw
    dasjahr = jahr
    nexttime = [kw, jahr]
    #mit main einblenden ersetzen
    main()
    print(f"Willkommen, {username}. Stall: {derstall}, KW: {dieKW}, Jahr: {dasjahr}")

def einfachso():
    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Willkommen, {username}!")
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
