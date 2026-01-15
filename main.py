# main.py
import time
import os
import json

import nastaveni as cfg
import grafika as gui
import vypocty as calc
import data as db

def modul_nova_kalkulace():
    gui.zobrazit_logo()
    gui.blok_text("KROK 1: PRIJMY", "^")
    gui.cara("-")
    
    jmeno = gui.ziskej_text("Jmeno")
    hruba = gui.ziskej_cislo("Hruba mzda")
    podpis = gui.ziskej_text("Podepsano prohlaseni (a/n)?").lower().startswith('a')
    deti = 0
    if podpis: deti = int(gui.ziskej_cislo("Pocet deti"))
    
    print()
    gui.progress_bar("Probiha vypocet mzdy...")
    cista, soc, zdr, dan = calc.vypocet_mzdy(hruba, podpis, deti)
    
    gui.zobrazit_logo()
    gui.blok_text(f"VYPOCET MZDY: {jmeno.upper()}", "^")
    gui.cara("=")
    gui.radek_tabulky("Hruba mzda", f"{hruba:,.0f}".replace(",", " "))
    gui.radek_tabulky("Socialni a Zdrav.", f"-{soc+zdr:,.0f}".replace(",", " "))
    gui.radek_tabulky("Dan", f"-{dan:,.0f}".replace(",", " "))
    gui.cara("-")
    gui.radek_tabulky("CISTA MZDA", f"{cista:,.0f}".replace(",", " "))
    gui.cara("=")
    
    input("\n   > Stiskni Enter pro pokracovani na vydaje...")
    
    # Zadavani vydaju
    vydaje_celkem = 0
    seznam_vydaju = {}
    gui.zobrazit_logo()
    
    while True:
        gui.blok_text("KROK 2: ZADAVANI VYDAJU", "^")
        gui.cara("-")
        if vydaje_celkem > 0:
            gui.blok_text(f"Celkem zadano: {vydaje_celkem:,.0f} Kc".replace(",", " "), ">")
            gui.cara(".")
            
        for klic, nazev in cfg.KATEGORIE.items():
            gui.blok_text(f"  {klic}. {nazev}")
        gui.blok_text("  X. Konec a vykreslit graf")
        gui.cara("-")
        
        volba = input("   > Vyber kategorii (cislo): ").strip().upper()
        if volba == "X": break
        
        if volba in cfg.KATEGORIE:
            nazev_kat = cfg.KATEGORIE[volba]
            gui.blok_text(f"Kategorie: {nazev_kat.upper()}")
            castka = gui.ziskej_cislo(f"Castka pro '{nazev_kat}' (Kc)")
            
            if nazev_kat in seznam_vydaju: seznam_vydaju[nazev_kat] += castka
            else: seznam_vydaju[nazev_kat] = castka
            
            vydaje_celkem += castka
            gui.zobrazit_logo()
            print(f"     [OK] Pridano: {nazev_kat} ({castka} Kc)\n")
        else:
            print("     [!] Neplatna volba.")
            time.sleep(0.5)
            gui.zobrazit_logo()
            
    # Finalni report
    gui.zobrazit_logo()
    gui.blok_text(f"FINANCNI REPORT: {jmeno.upper()}", "^")
    gui.cara("=")
    gui.radek_tabulky("CISTA MZDA", f"{cista:,.0f}".replace(",", " "))
    gui.cara("-")
    if vydaje_celkem > 0:
        gui.vykreslit_graf(seznam_vydaju)
        gui.radek_tabulky("Vydaje celkem", f"-{vydaje_celkem:,.0f}".replace(",", " "))
        gui.cara("=")
    
    zustatek = cista - vydaje_celkem
    gui.radek_tabulky("ZUSTATEK", f"{zustatek:,.0f}".replace(",", " "))
    gui.cara("=")
    
    db.ulozit_zaznam(jmeno, hruba, cista, vydaje_celkem, seznam_vydaju, zustatek)
    input("\n   > Enter pro navrat...")

def modul_financni_zdravi():
    gui.zobrazit_logo()
    gui.blok_text("ANALYZATOR FINANCNIHO ZDRAVI", "^")
    gui.cara("-")
    if not os.path.exists(cfg.DATA_FILE):
        gui.blok_text("Chybi data. Proved nejprve kalkulaci.", "^")
        input("\n   > Enter pro navrat...")
        return
    try:
        with open(cfg.DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            posledni = data[-1]
    except:
        gui.blok_text("Chyba cteni dat.", "^")
        return
    
    cista = float(posledni.get('cista', 0))
    vydaje_celkem = float(posledni.get('vydaje_celkem', 0))
    detail_vydaju = posledni.get('vydaje_detail', {})
    
    if cista == 0:
        gui.blok_text("Chyba: Cista mzda je 0.", "^")
        input("\n   > Enter pro navrat...")
        return

    bydleni = detail_vydaju.get("Bydleni", 0)
    proc_vydaje = (vydaje_celkem / cista) * 100
    proc_bydleni = (bydleni / cista) * 100
    proc_uspora = ((cista - vydaje_celkem) / cista) * 100
    
    gui.blok_text(f"Analyza pro: {posledni.get('jmeno', 'Neznamy')}", "^")
    gui.cara("-")
    gui.radek_tabulky("Prijem (Cista mzda)", f"{cista:,.0f}".replace(",", " "))
    gui.radek_tabulky("Celkove vydaje", f"{vydaje_celkem:,.0f}".replace(",", " "))
    gui.cara("-")
    
    stav_uspory = "[ OK ]" if proc_uspora >= 20 else "[MALO]"
    if proc_uspora < 0: stav_uspory = "[DLUH]"
    gui.radek_tabulky(f"MIRA USPORY {stav_uspory}", f"{proc_uspora:.1f} %")
    
    stav_bydleni = "[ OK ]" if proc_bydleni <= 35 else "[MOC ]"
    gui.radek_tabulky(f"NAKLADY BYDLENI {stav_bydleni}", f"{proc_bydleni:.1f} %")
    gui.cara("=")
    gui.blok_text("HODNOCENI A DOPORUCENI:", "<")
    
    if proc_uspora < 0:
        gui.blok_text("! POZOR: Jses v minusu. Omez zbytne vydaje.", "<")
    elif proc_uspora < 10:
        gui.blok_text("! Uspora je nizka. Doporuceno aspon 10-20%.", "<")
    elif proc_uspora >= 20:
        gui.blok_text("* Skvela prace! Sporis vice nez 20%.", "<")
    if proc_bydleni > 40:
        gui.blok_text("! Bydleni ti bere prilis velkou cast prijmu.", "<")
    
    gui.cara("=")
    input("\n   > Enter pro navrat...")

def nacist_historii_interaktivne():
    if not os.path.exists(cfg.DATA_FILE):
        gui.blok_text("Zatim zadna ulozena data.", "^")
        input("\n   > Enter pro navrat...")
        return

    while True:
        gui.zobrazit_logo()
        gui.blok_text("HISTORIE ZAZNAMU", "^")
        gui.cara("-")
        
        try:
            with open(cfg.DATA_FILE, "r", encoding="utf-8") as f: 
                data = json.load(f)
        except:
            gui.blok_text("Chyba cteni dat.", "^")
            return

        print(f"| {'ID':<3} {'JMENO':<10} {'DATUM':<16} {'CISTA':<10} {'BILANCE'}")
        print("+" + "-"*(cfg.SIRKA_UI-2) + "+")
        
        for i, z in enumerate(data):
            cista = float(z.get('cista', z.get('cista_mzda', 0)))
            vydaje = float(z.get('vydaje_celkem', 0))
            zustatek = float(z.get('zustatek', cista - vydaje))
            
            datum_kratke = z.get('datum', '')[5:] 
            jmeno = z.get('jmeno', 'Neznamy')[:9]
            print(f"| {i+1:<3} {jmeno:<10} {datum_kratke:<16} {int(cista):<10} {int(zustatek)}")

        gui.cara("-")
        print("   Napis cislo zaznamu pro zobrazeni GRAFU")
        volba = input("   > Nebo stiskni Enter pro navrat: ").strip()
        
        if volba == "": break
        
        if volba.isdigit():
            idx = int(volba) - 1
            if 0 <= idx < len(data):
                vybrany = data[idx]
                gui.zobrazit_logo()
                gui.blok_text(f"DETAIL: {vybrany.get('jmeno')}", "^")
                vydaje_detail = vybrany.get('vydaje_detail', {})
                if vydaje_detail:
                    gui.vykreslit_graf(vydaje_detail)
                else:
                    gui.blok_text("Tento zaznam nema detailni vydaje.", "^")
                input("\n   > Enter pro zpet do seznamu...")
            else:
                print("   [!] Neplatne ID zaznamu.")
                time.sleep(1)

def main():
    while True:
        gui.zobrazit_logo()
        gui.blok_text("HLAVNI MENU", "^")
        gui.cara("-")
        gui.blok_text("1. Nova kalkulace")
        gui.blok_text("2. Historie")
        gui.blok_text("3. Financni zdravi") 
        gui.blok_text("4. Export do Excelu")          
        gui.blok_text("5. Ukoncit")
        gui.cara("-")
        volba = input("   > Tva volba: ")
        
        if volba == "1": modul_nova_kalkulace()
        elif volba == "2": nacist_historii_interaktivne() 
        elif volba == "3": modul_financni_zdravi()
        elif volba == "4": db.export_do_excelu()
        elif volba == "5":
            print("\n   Ukoncuji...")
            break

if __name__ == "__main__":
    main()

