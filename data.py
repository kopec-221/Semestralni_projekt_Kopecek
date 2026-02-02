# data.py
import json
import os
import time
import re
import nastaveni as cfg
import grafika as gui

# Zkusime import xlsxwriter
try:
    import xlsxwriter
    MA_XLSX = True
except ImportError:
    MA_XLSX = False

#  POMOCNÉ FUNKCE

def bezpecny_nazev_souboru(jmeno):
    
    ciste = re.sub(r'[\\/*?:"<>|]', "", jmeno)
    return ciste.replace(" ", "_")

#  PRÁCE S JSON DATY 

def nacti_vsechna_data():
   
    struktura = {"zaznamy": [], "cile": []}
    
    if not os.path.exists(cfg.DATA_FILE):
        return struktura

    try:
        with open(cfg.DATA_FILE, "r", encoding="utf-8") as f:
            nacteno = json.load(f)
            
        # Migrace stareho formatu (pokud je to jen seznam zaznamu)
        if isinstance(nacteno, list):
            struktura["zaznamy"] = nacteno
        else:
            struktura = nacteno
            
    except Exception as e:
        print(f"CHYBA PRI CTENI DAT: {e}")
        # Vracime prazdnou strukturu, abychom nespadli
        
    return struktura

def ulozit_vsechna_data(struktura):
    
    try:
        with open(cfg.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(struktura, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"CHYBA PRI UKLADANI: {e}")

def ulozit_zaznam(jmeno, hruba, cista, vydaje_celkem, vydaje_seznam, zustatek):
    
    data = nacti_vsechna_data()
    
    novy = {
        "jmeno": jmeno,
        "datum": time.strftime("%Y-%m-%d %H:%M"),
        "hruba": hruba,
        "cista": cista,
        "vydaje_celkem": vydaje_celkem,
        "vydaje_detail": vydaje_seznam,
        "zustatek": zustatek
    }
    
    data["zaznamy"].append(novy)
    ulozit_vsechna_data(data)

def pridat_cil(nazev, cilova_castka, aktualne_nasetreno):
    
    data = nacti_vsechna_data()
    
    novy_cil = {
        "nazev": nazev,
        "cil": cilova_castka,
        "aktualne": aktualne_nasetreno,
        "datum_vytvoreni": time.strftime("%Y-%m-%d")
    }
    
    data["cile"].append(novy_cil)
    ulozit_vsechna_data(data)

#   EXCELU 

def _vytvorit_jeden_excel(zaznam, slozka, index):
    
    
    jmeno_safe = bezpecny_nazev_souboru(zaznam.get("jmeno", "Neznamy"))
    datum_safe = zaznam.get("datum", "")[:10]
    nazev_souboru = f"{slozka}/{jmeno_safe}_{datum_safe}_{index}.xlsx"
    
    print(f"   > Vytvarim: {nazev_souboru}")

   
    workbook = xlsxwriter.Workbook(nazev_souboru)
    ws_report = workbook.add_worksheet("Report")
    ws_data = workbook.add_worksheet("Data_Grafy") 

    #  Formaty
    style_nadpis = workbook.add_format({'bold': True, 'font_size': 16, 'color': 'white', 'bg_color': '#44546A', 'align': 'center', 'valign': 'vcenter'})
    style_bold = workbook.add_format({'bold': True})
    style_penize = workbook.add_format({'num_format': '#,##0 Kc'})
    
    zustatek = zaznam.get("cista", 0) - zaznam.get("vydaje_celkem", 0)
    barva_zustatku = 'green' if zustatek >= 0 else 'red'
    style_zustatek = workbook.add_format({'num_format': '#,##0 Kc', 'bold': True, 'font_color': barva_zustatku})

   
    ws_report.merge_range('B2:E3', zaznam.get("jmeno", "").upper(), style_nadpis)
    ws_report.write('B4', f"Datum vypoctu: {zaznam.get('datum', '')}")

    
    ws_report.write('B6', "Cista mzda:", style_bold)
    ws_report.write('C6', zaznam.get("cista", 0), style_penize)
    ws_report.write('B7', "Celkove vydaje:", style_bold)
    ws_report.write('C7', zaznam.get("vydaje_celkem", 0), style_penize)
    ws_report.write('B8', "Zustatek:", style_bold)
    ws_report.write('C8', zustatek, style_zustatek)

    
    detail = zaznam.get("vydaje_detail", {})
    if detail:
        ws_report.write('B11', "Rozpis vydaju:", style_bold)
        radek = 12
        for kat, castka in detail.items():
            ws_report.write(f'B{radek}', kat)
            ws_report.write(f'C{radek}', castka, style_penize)
            radek += 1

    
    ws_data.write_column('A1', ['Cista mzda', 'Vydaje'])
    ws_data.write_column('B1', [zaznam.get("cista", 0), zaznam.get("vydaje_celkem", 0)])
    
    kategorie = list(detail.keys()) if detail else ["Zadne"]
    hodnoty = list(detail.values()) if detail else [0]
    ws_data.write_column('D1', kategorie)
    ws_data.write_column('E1', hodnoty)

    #  Grafy
    
    graf_sloupec = workbook.add_chart({'type': 'column'})
    graf_sloupec.add_series({
        'name': 'Bilance',
        'categories': ['Data_Grafy', 0, 0, 1, 0],
        'values':     ['Data_Grafy', 0, 1, 1, 1],
        'points': [{'fill': {'color': '#4472C4'}}, {'fill': {'color': '#C00000'}}],
        'data_labels': {'value': True}
    })
    ws_report.insert_chart('E6', graf_sloupec)

    # Kolacovy 
    graf_kolac = workbook.add_chart({'type': 'pie'})
    graf_kolac.add_series({
        'name': 'Vydaje',
        'categories': ['Data_Grafy', 0, 3, len(kategorie)-1, 3],
        'values':     ['Data_Grafy', 0, 4, len(hodnoty)-1, 4],
        'data_labels': {'percentage': True}
    })
    graf_kolac.set_title({'name': 'Slozeni vydaju'})
    ws_report.insert_chart('E22', graf_kolac)

    workbook.close()

# Uprava cilu

def vlozit_do_cile(index_cile, castka):
    
    data = nacti_vsechna_data()
    cile = data.get("cile", [])
    
    
    if 0 <= index_cile < len(cile):
        
        stara_castka = cile[index_cile]["aktualne"]
        cile[index_cile]["aktualne"] = stara_castka + castka
        
        
        data["cile"] = cile 
        ulozit_vsechna_data(data)
        return True 
    else:
        return False 
    

# Excel export

def export_do_excelu():
    
    gui.zobrazit_logo()
    gui.blok_text("HROMADNY EXPORT (1 osoba = 1 soubor)", "^")
    gui.cara("-")
    
    
    if not MA_XLSX:
        gui.blok_text("CHYBA: Chybi knihovna xlsxwriter!", "<")
        input("\n   > Enter pro navrat...")
        return

    data_all = nacti_vsechna_data()
    zaznamy = data_all.get("zaznamy", [])

    if not zaznamy:
        gui.blok_text("Nejsou k dispozici zadna data.", "^")
        input("\n   > Enter pro navrat...")
        return

    
    slozka = "exporty"
    if not os.path.exists(slozka):
        os.makedirs(slozka)
        gui.blok_text(f"Vytvorena slozka '{slozka}'", "^")

    
    try:
        gui.blok_text(f"Zpracovavam {len(zaznamy)} zaznamu...", "^")
        gui.cara("-")

        for i, zaznam in enumerate(zaznamy):
            _vytvorit_jeden_excel(zaznam, slozka, i+1)

        print()
        gui.blok_text("HOTOVO!", "^")
        gui.blok_text(f"Soubory najdes ve slozce '{slozka}'", "^")
        gui.cara("=")
        
    except Exception as e:
        gui.blok_text(f"KRITICKA CHYBA PRI EXPORTU: {e}", "<")
        
    input("\n   > Enter pro navrat...")
