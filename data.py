# data.py
import json
import os
import time
import re
import nastaveni as cfg
import grafika as gui


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

def bezpecny_nazev_souboru(jmeno):
    """Odstrani ze jmena znaky, ktere nesmi byt v nazvu souboru."""
    
    ciste = re.sub(r'[\\/*?:"<>|]', "", jmeno)
    return ciste.replace(" ", "_")

def export_do_excelu():
    """Vytvori SAMOSTATNY Excel soubor pro kazdy zaznam."""
    gui.zobrazit_logo()
    gui.blok_text("HROMADNY EXPORT (1 osoba = 1 soubor)", "^")
    gui.cara("-")
    
    if not MA_XLSX:
        gui.blok_text("CHYBA: Chybi knihovna xlsxwriter!", "<")
        input("\n   > Enter pro navrat...")
        return

    if not os.path.exists(cfg.DATA_FILE):
        gui.blok_text("Nejsou k dispozici zadna data.", "^")
        input("\n   > Enter pro navrat...")
        return

    
    slozka = "exporty"
    if not os.path.exists(slozka):
        os.makedirs(slozka)
        gui.blok_text(f"Vytvorena slozka '{slozka}'", "^")

    try:
        with open(cfg.DATA_FILE, "r", encoding="utf-8") as f: 
            data = json.load(f)
        
        gui.blok_text(f"Zpracovavam {len(data)} souboru...", "^")
        gui.cara("-")

       
        for i, z in enumerate(data):
            
           
            jmeno_safe = bezpecny_nazev_souboru(z.get("jmeno", "Neznamy"))
            datum_safe = z.get("datum", "")[:10] 
            nazev_souboru = f"{slozka}/{jmeno_safe}_{datum_safe}_{i+1}.xlsx"
            
            print(f"   > Vytvarim: {nazev_souboru}")
            
           
            workbook = xlsxwriter.Workbook(nazev_souboru)
            
          
            ws_report = workbook.add_worksheet("Report")
            ws_data = workbook.add_worksheet("Data_Grafy") 
            
            # Formaty
            bold = workbook.add_format({'bold': True})
            title_fmt = workbook.add_format({'bold': True, 'font_size': 16, 'color': '#FFFFFF', 'bg_color': '#44546A', 'align': 'center', 'valign': 'vcenter'})
            money_fmt = workbook.add_format({'num_format': '#,##0 Kc'})
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
            
           
            cista = z.get("cista", 0)
            vydaje = z.get("vydaje_celkem", 0)
            detail = z.get("vydaje_detail", {})
            
          
            ws_report.merge_range('B2:E3', z.get("jmeno", "").upper(), title_fmt)
            ws_report.write('B4', f"Datum vypoctu: {z.get('datum', '')}")
            
          
            ws_report.write('B6', "Cista mzda:", bold)
            ws_report.write('C6', cista, money_fmt)
            
            ws_report.write('B7', "Celkove vydaje:", bold)
            ws_report.write('C7', vydaje, money_fmt)
            
            ws_report.write('B8', "Zustatek:", bold)
            zustatek = cista - vydaje
            format_zustatek = workbook.add_format({'num_format': '#,##0 Kc', 'bold': True, 'font_color': 'green' if zustatek > 0 else 'red'})
            ws_report.write('C8', zustatek, format_zustatek)

            # 3. Tabulka detailu vydaju (pokud jsou)
            if detail:
                ws_report.write('B11', "Rozpis vydaju:", bold)
                r = 12
                for kat, castka in detail.items():
                    ws_report.write(f'B{r}', kat)
                    ws_report.write(f'C{r}', castka, money_fmt)
                    r += 1

          
            
            # Priprava dat na skryty list
            ws_data.write_column('A1', ['Cista mzda', 'Vydaje'])
            ws_data.write_column('B1', [cista, vydaje])
            
            cats = list(detail.keys()) if detail else ["Zadne"]
            vals = list(detail.values()) if detail else [0]
            
            ws_data.write_column('D1', cats)
            ws_data.write_column('E1', vals)
            
            # A) Sloupcovy graf (Bilance)
            chart_col = workbook.add_chart({'type': 'column'})
            chart_col.add_series({
                'name': 'Bilance',
                'categories': ['Data_Grafy', 0, 0, 1, 0],
                'values':     ['Data_Grafy', 0, 1, 1, 1],
                'points': [{'fill': {'color': '#4472C4'}}, {'fill': {'color': '#C00000'}}],
                'data_labels': {'value': True}
            })
            chart_col.set_title({'name': 'Bilance'})
            chart_col.set_legend({'none': True})
            
           
            chart_pie = workbook.add_chart({'type': 'pie'})
            chart_pie.add_series({
                'name': 'Vydaje',
                'categories': ['Data_Grafy', 0, 3, len(cats)-1, 3],
                'values':     ['Data_Grafy', 0, 4, len(vals)-1, 4],
                'data_labels': {'percentage': True}
            })
            chart_pie.set_title({'name': 'Slozeni vydaju'})

            ws_report.insert_chart('E6', chart_col)
            ws_report.insert_chart('E22', chart_pie)

            workbook.close()
            

        print()
        gui.blok_text("HOTOVO!", "^")
        gui.blok_text(f"Soubory najdes ve slozce '{slozka}'", "^")
        gui.cara("=")
        
    except Exception as e:
        gui.blok_text(f"CHYBA: {e}", "<")
        
    input("\n   > Enter pro navrat...")
