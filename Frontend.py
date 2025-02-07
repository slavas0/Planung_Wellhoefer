import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Canvas

# Hauptfenster erstellen mit einem modernen Theme
def create_main_window():
    window = ttk.Window(themename="sandstone")
    window.title("Wellhöfer Hühnerplanung")
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

def eintrag_hinzufuegen(scrollable_frame, id):
    global entry_count
    row_offset = 3 + entry_count

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
    id_label.grid(row=row_offset, column=7, padx=5, pady=5)
    id_label.grid_remove()  # Das Label sofort verstecken

    # Button zum Löschen des Eintrags
    delete_button = ttk.Button(scrollable_frame, text="Löschen", bootstyle=DANGER)
    delete_button.grid(row=row_offset, column=8, padx=5, pady=5)

    # Button zum Checken des Eintrags
    check_button = ttk.Button(scrollable_frame, text="Check", bootstyle=SUCCESS)
    check_button.grid(row=row_offset, column=9, padx=5, pady=5)

    # Speichern der Entry-Felder für späteres Speichern in der Datenbank
    entries.append({
        "id": id_label,
        "name": name_entry,
        "telefon": telefon_entry,
        "braun": braun_entry,
        "weiss": weiss_entry,
        "verhalten": verhalten_entry,
        "preis": preis_entry,
        "bemerkung": bemerkung_entry
    })

    entry_count += 1

# Button zum Hinzufügen eines neuen Eintrags
def create_add_button(root, scrollable_frame):
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)

    hinzufuegen_button = ttk.Button(button_frame, text="Eintrag hinzufügen", bootstyle=SUCCESS)
    hinzufuegen_button.pack(side="left", padx=10)

# Button zum Speichern der Einträge
def create_save_button(root):
    speichern_button = ttk.Button(root, text="Speichern", bootstyle=PRIMARY)
    speichern_button.pack(pady=10)

# Footer erstellen
def create_footer(root):
    footer_frame = ttk.Frame(root)
    footer_frame.pack(side="bottom", fill="x", pady=10)

    gesamt_label = ttk.Label(footer_frame, text="Gesamte bestellte Tieranzahl", font=("Arial", 12, "bold"))
    gesamt_label.pack(side="left", padx=10)

    braun_summe_label = ttk.Label(footer_frame, font=("Arial", 12))
    braun_summe_label.pack(side="left", padx=10)

    weiss_summe_label = ttk.Label(footer_frame, font=("Arial", 12))
    weiss_summe_label.pack(side="left", padx=10)

    ubrig_label = ttk.Label(footer_frame, text="Übrige Tieranzahl", font=("Arial", 12, "bold"))
    ubrig_label.pack(side="left", padx=10)

    braun_ubrig_label = ttk.Label(footer_frame, font=("Arial", 12))
    braun_ubrig_label.pack(side="left", padx=10)

    weiss_ubrig_label = ttk.Label(footer_frame, font=("Arial", 12))
    weiss_ubrig_label.pack(side="left", padx=10)

# Funktion zum Begrüßen des Benutzers
def create_welcome_label(root):
    welcome_label = ttk.Label(root, text=f"Willkommen, Nutzer!", font=("Arial", 16))
    welcome_label.pack(pady=10)

# Text "Stall 2 KW 7 2024" hinzufügen
def create_large_text(root):
    txt = "Stall 2 - KW 7 2024"
    large_text_label = ttk.Label(root, text=txt, font=("Arial", 20, "bold"))
    large_text_label.pack(pady=10)

    txt2 = "Woche vom 12. Februar 2024 bis 18. Februar 2024"
    large_text2_label = ttk.Label(root, text=txt2, font=("Arial", 20, "bold"))
    large_text2_label.pack(pady=10)

# Hauptfunktion, die das GUI erstellt und startet
def main():
    # Fenster erstellen
    root = create_main_window()

    # Füge die Tabs ganz unten im Fenster hinzu
    create_footer(root)

    # Scrollbereich einrichten
    canvas, scrollable_frame = create_scrollable_area(root)

    # Titel und Überschrift
    create_title(root)
    create_welcome_label(root)
    create_large_text(root)

    # Neue Textfelder hinzufügen (z.B. in der zweiten Zeile)
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

    create_headers(scrollable_frame)

    # Hinzufügen-Button, Speichern-Button und Fußzeile
    create_add_button(root, scrollable_frame)
    create_save_button(root)

    # Mainloop starten
    root.mainloop()

if __name__ == "__main__":
    main()