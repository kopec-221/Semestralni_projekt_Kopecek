# data.py
import json
import os
import time
import nastaveni as cfg
import grafika as gui

# Zkusime import xlsxwriter
try:
    import xlsxwriter
    MA_XLSX = True
except ImportError:
    MA_XLSX = False

def ulozit_zaznam(jmeno, hruba, cista, vydaje_celkem, vydaje_seznam, zustatek):
    """Ulozi novy zaznam do JSON souboru."""
    data = []
    if os.path.exists(cfg.DATA_FILE):
        try:
            with open(cfg.DATA_FILE, "r", encoding="utf-8") as f: 
                data = json.load(f)
        except: pass
    
    novy = {
        "jmeno": jmeno,
        "datum": time.strftime("%Y-%m-%d %H:%M"),
        "hruba": hruba,
        "cista": cista,
        "vydaje_celkem": vydaje_celkem,
        "vydaje_detail": vydaje_seznam,
        "zustatek": zustatek
    }
    data.append(novy)
    
    with open(cfg.DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def export_do_excelu():
    """Exportuje vsechna data do Excelu s galerii grafu."""
    gui.zobrazit_logo()
    gui.blok_text("EXPORT DO EXCELU (.xlsx)", "^")
    gui.cara("-")
    
    if not MA_XLSX:
        gui.blok_text("CHYBA: Chybi knihovna xlsxwriter!", "<")
        gui.blok_text("Nainstaluj ji prikazem:", "<")
        gui.blok_text("py -m pip install xlsxwriter", "^")
        input("\n   > Enter pro navrat...")
        return

    if not os.path.exists(cfg.DATA_FILE):
        gui.blok_text("Nejsou k dispozici zadna data.", "^")
        input("\n   > Enter pro navrat...")
        return

    nazev_souboru = "financni_report.xlsx"
    
    try:
        with open(cfg.DATA_FILE, "r", encoding="utf-8") as f: 
            data = json.load(f)
            
        workbook = xlsxwriter.Workbook(nazev_souboru)
        
        # --- VYTVORENI LISTU ---
        # 1. Prehledova tabulka
        ws_prehled = workbook.add_worksheet("Prehled")
        # 2. Zde budou grafy pod sebou
        ws_galerie = workbook.add_worksheet("Galerie_Grafu")
        # 3. Pomocny list pro data grafu (aby neprekazela)
        ws_data = workbook.add_worksheet("Data_Grafy")
        
        # --- FORMATY ---
        bold = workbook.add_format({'bold': True})
        # Format meny bez hacku a carek
        money_fmt = workbook.add_format({'num_format': '#,##0 Kc'})
        date_fmt = workbook.add_format({'align': 'center'})
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        
        # Hlavicka tabulky
        hlavicky = ["Jmeno", "Datum", "Hruba mzda", "Cista mzda", "Vydaje Celkem", "Zustatek"]
        ws_prehled.write_row('A1', hlavicky, header_fmt)
        ws_prehled.set_column('A:F', 15)
        
        # Promenne pro pozicovani
        row_prehled = 1
        row_data_grafy = 0  
        row_galerie = 1     
        
        gui.blok_text(f"Generuji grafy pro {len(data)} zaznamu...", "^")
        
        # --- HLAVNI SMYCKA PRES VSECHNY ZAZNAMY ---
        for i, z in enumerate(data):
            # 1. Zapis do tabulky Prehled
            cista = z.get("cista", z.get("cista_mzda", 0))
            vydaje = z.get("vydaje_celkem", 0)
            zustatek = z.get("zustatek", cista - vydaje)
            
            ws_prehled.write(row_prehled, 0, z.get("jmeno", ""))
            ws_prehled.write(row_prehled, 1, z.get("datum", ""), date_fmt)
            ws_prehled.write(row_prehled, 2, z.get("hruba", 0), money_fmt)
            ws_prehled.write(row_prehled, 3, cista, money_fmt)
            ws_prehled.write(row_prehled, 4, vydaje, money_fmt)
            ws_prehled.write(row_prehled, 5, zustatek, money_fmt)
            row_prehled += 1
            
            # 2. Generovani grafu (pokud ma zaznam vydaje)
            detail = z.get('vydaje_detail', {})
            if detail:
                # A) Zapis dat pro graf do skryteho listu
                start_row = row_data_grafy
                ws_data.write(start_row, 0, f"ID_{i}") 
                
                curr_r = start_row
                for kat, castka in detail.items():
                    ws_data.write(curr_r, 1, kat)       # Kategorie
                    ws_data.write(curr_r, 2, castka)    # Castka
                    curr_r += 1
                
                end_row = curr_r - 1
                row_data_grafy = curr_r + 1 
                
                # B) Vytvoreni grafu
                chart = workbook.add_chart({'type': 'pie'})
                chart.add_series({
                    'name':       'Vydaje',
                    'categories': ['Data_Grafy', start_row, 1, end_row, 1],
                    'values':     ['Data_Grafy', start_row, 2, end_row, 2],
                    'data_labels': {'value': True, 'percentage': True},
                })
                
                # Titulek grafu
                datum = z.get('datum', '')
                jmeno = z.get('jmeno', '')
                chart.set_title({'name': f"{datum} - {jmeno} (Celkem: {vydaje})"})
                chart.set_style(10)
                
                # C) Vlozeni grafu do listu Galerie
                bunka = f"B{row_galerie}"
                ws_galerie.insert_chart(bunka, chart)
                
                # Posun pro dalsi graf (aby byly pod sebou)
                row_galerie += 16

        workbook.close()
        
        print()
        gui.blok_text("USPESNE EXPORTOVANO!", "^")
        gui.blok_text(f"Soubor: {nazev_souboru}", "^")
        gui.blok_text("Zkontroluj list 'Galerie_Grafu'", "^")
        gui.cara("=")
        
    except Exception as e:
        gui.blok_text(f"CHYBA EXPORTU: {e}", "<")
        
    input("\n   > Enter pro navrat...")