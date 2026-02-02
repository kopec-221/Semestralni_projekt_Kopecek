# main.py
import time
import nastaveni as cfg
import grafika as gui
import vypocty as calc
import data as db


# KALKULACE A VYDAJE

def modul_nova_kalkulace():
    gui.zobrazit_logo()
    gui.blok_text("KROK 1: PRIJMY", "^")
    gui.cara("-")
    
    jmeno = gui.ziskej_text("Jmeno")
    hruba = gui.ziskej_cislo("Hruba mzda")
    podpis_txt = gui.ziskej_text("Podepsano prohlaseni (a/n)?")
    podpis = podpis_txt.lower().startswith('a')
    
    deti = 0
    if podpis:
        deti = int(gui.ziskej_cislo("Pocet deti"))
    
    print()
    gui.animace_nacitani("Probiha vypocet mzdy")
    
    # Vypocet pres modul vypocty.py
    cista, soc, zdr, dan = calc.vypocet_mzdy(hruba, podpis, deti)
    
    
    gui.zobrazit_logo()
    gui.blok_text(f"VYPOCET MZDY: {jmeno.upper()}", "^")
    gui.cara("=")
    gui.radek_tabulky("Hruba mzda", f"{hruba:,.0f} Kc".replace(",", " "))
    gui.radek_tabulky("Socialni a Zdrav.", f"-{soc+zdr:,.0f} Kc".replace(",", " "))
    gui.radek_tabulky("Dan", f"-{dan:,.0f} Kc".replace(",", " "))
    gui.cara("-")
    gui.radek_tabulky("CISTA MZDA", f"{cista:,.0f} Kc".replace(",", " "))
    gui.cara("=")
    
    input("\n   > Stiskni Enter pro pokracovani na vydaje...")
    
   
    vydaje_celkem = 0
    seznam_vydaju = {}
    
    while True:
        gui.zobrazit_logo()
        gui.blok_text("KROK 2: ZADAVANI VYDAJU", "^")
        gui.cara("-")
        
        if vydaje_celkem > 0:
            gui.blok_text(f"Zatim zadano: {vydaje_celkem:,.0f} Kc".replace(",", " "), ">")
            gui.cara(".")
            
        
        for klic, nazev in cfg.KATEGORIE.items():
            gui.vypis(f"[{klic}] {nazev}")
        
        gui.cara("-")
        gui.vypis("[X] KONEC a ulozit")
        
        volba = gui.ziskej_text("Vyber kategorii").upper()
        if volba == "X": 
            break
        
        if volba in cfg.KATEGORIE:
            nazev_kat = cfg.KATEGORIE[volba]
            castka = gui.ziskej_cislo(f"Castka pro '{nazev_kat}'")
            
            if castka > 0:
                seznam_vydaju[nazev_kat] = seznam_vydaju.get(nazev_kat, 0) + castka
                vydaje_celkem += castka
        else:
            print("     [!] Neplatna volba.")
            time.sleep(0.5)
            
    
    gui.zobrazit_logo()
    gui.blok_text(f"FINANCNI REPORT: {jmeno.upper()}", "^")
    gui.cara("=")
    gui.radek_tabulky("CISTA MZDA", f"{cista:,.0f} Kc".replace(",", " "))
    gui.cara("-")
    
    if vydaje_celkem > 0:
        gui.vykreslit_graf(seznam_vydaju)
        gui.radek_tabulky("Vydaje celkem", f"-{vydaje_celkem:,.0f} Kc".replace(",", " "))
        gui.cara("=")
    
    zustatek = cista - vydaje_celkem
    gui.radek_tabulky("ZUSTATEK", f"{zustatek:,.0f} Kc".replace(",", " "))
    gui.cara("=")
    
    # Ulozeni do DB
    db.ulozit_zaznam(jmeno, hruba, cista, vydaje_celkem, seznam_vydaju, zustatek)
    input("\n   > Zaznam ulozen. Enter pro navrat...")


# SPORICI CILE 

def modul_cile():
    while True:
        gui.zobrazit_logo()
        gui.blok_text("SPORICI CILE", "^")
        gui.cara("-")
        
       
        data_all = db.nacti_vsechna_data()
        cile = data_all.get("cile", [])
        
        
        if not cile:
            gui.blok_text("Zatim nemas zadne sporici cile.", "^")
        else:
            for i, c in enumerate(cile):
                
                print(f"   ID [{i+1}]", end="") 
                gui.vykreslit_progress_bar(c["nazev"], c["aktualne"], c["cil"])
                print() # Mezera mezi grafy
        
        gui.cara("-")
        gui.vypis("[1] Pridat novy cil")
        gui.vypis("[2] Vlozit penize do cile") 
        gui.vypis("[0] Zpet do menu")
        
        volba = gui.ziskej_text("Tva volba")
        
        if volba == "1":
           
            nazev = gui.ziskej_text("Nazev cile (napr. Auto)")
            cil = gui.ziskej_cislo("Cilova castka")
            aktualne = gui.ziskej_cislo("Kolik uz mas nasetreno")
            
            db.pridat_cil(nazev, cil, aktualne)
            input("\n   > Cil ulozen! Enter...")
            
        elif volba == "2":
            
            if not cile:
                input("\n   > Nemas zadne cile! Enter...")
                continue
                
            id_str = gui.ziskej_text("Napis ID cile (cislo)")
            
            if id_str.isdigit():
                idx = int(id_str) - 1 
                
                
                if 0 <= idx < len(cile):
                    vybrany_cil = cile[idx]
                    print(f"   Vybrano: {vybrany_cil['nazev']}")
                    castka = gui.ziskej_cislo("Kolik chces vlozit (Kc)")
                    
                    
                    if db.vlozit_do_cile(idx, castka):
                        print(f"\n   [OK] Uspesne vlozeno {castka:,.0f} Kc.".replace(",", " "))
                    else:
                        print("\n   [CHYBA] Nepodarilo se ulozit.")
                else:
                    print("\n   [!] Toto ID neexistuje.")
            else:
                print("\n   [!] Musis zadat cislo.")
            
            input("   > Enter pro pokracovani...")
            
        elif volba == "0":
            break


#FINANCNI ZDRAVI

def modul_financni_zdravi():
    gui.zobrazit_logo()
    gui.blok_text("ANALYZATOR FINANCNIHO ZDRAVI", "^")
    gui.cara("-")
    
    
    data_all = db.nacti_vsechna_data()
    zaznamy = data_all.get("zaznamy", [])
    
    if not zaznamy:
        gui.blok_text("Chybi data. Proved nejprve kalkulaci.", "^")
        input("\n   > Enter pro navrat...")
        return

    
    posledni = zaznamy[-1]
    
    cista = float(posledni.get('cista', 0))
    vydaje = float(posledni.get('vydaje_celkem', 0))
    detail = posledni.get('vydaje_detail', {})
    
    if cista == 0:
        print("   [CHYBA] Cista mzda je 0, nelze pocitat procenta.")
        input("   Enter...")
        return

    
    bydleni = detail.get("Bydleni", 0)
    proc_bydleni = (bydleni / cista) * 100
    proc_uspora = (((cista - vydaje) / cista)) * 100
    
    gui.blok_text(f"Analyza pro: {posledni.get('jmeno')}", "^")
    gui.cara("-")
    
    
    stav_uspory = "[ OK ]" if proc_uspora >= 20 else "[MALO]"
    if proc_uspora < 0: stav_uspory = "[DLUH]"
    gui.radek_tabulky(f"MIRA USPORY {stav_uspory}", f"{proc_uspora:.1f} %")
    
   
    stav_bydleni = "[ OK ]" if proc_bydleni <= 35 else "[MOC ]"
    gui.radek_tabulky(f"NAKLADY BYDLENI {stav_bydleni}", f"{proc_bydleni:.1f} %")
    
    gui.cara("=")
    gui.blok_text("DOPORUCENI:", "<")
    
    if proc_uspora < 0:
        gui.vypis("! POZOR: Jses v minusu. Omez zbytne vydaje.")
    elif proc_uspora < 20:
        gui.vypis("! Zkus zvysit usporu alespon na 20%.")
    else:
        gui.vypis("* Skvela prace! Sporis zodpovedne.")
        
    if proc_bydleni > 35:
        gui.vypis("! Bydleni ti bere prilis velkou cast prijmu.")
    
    input("\n   > Enter pro navrat...")


# HISTORIE

def modul_historie():
    data_all = db.nacti_vsechna_data()
    zaznamy = data_all.get("zaznamy", [])

    if not zaznamy:
        gui.zobrazit_logo()
        gui.blok_text("Zatim zadna ulozena data.", "^")
        input("\n   > Enter pro navrat...")
        return

    while True:
        gui.zobrazit_logo()
        gui.blok_text("HISTORIE ZAZNAMU", "^")
        gui.cara("-")
        
        # Hlavicka tabulky
        print(f"| {'ID':<3} {'JMENO':<10} {'DATUM':<16} {'CISTA':<12} {'ZUSTATEK'}")
        gui.cara("-")
        
        for i, z in enumerate(zaznamy):
            cista = float(z.get('cista', 0))
            vydaje = float(z.get('vydaje_celkem', 0))
            zustatek = z.get('zustatek', cista - vydaje)
            
            datum = z.get('datum', '')[5:] # Orezeme rok
            jmeno = z.get('jmeno', 'Neznamy')[:9]
            
            print(f"| {i+1:<3} {jmeno:<10} {datum:<16} {int(cista):<12} {int(zustatek)}")

        gui.cara("-")
        gui.vypis("Napis ID zaznamu pro detail a graf")
        volba = gui.ziskej_text("Nebo Enter pro navrat")
        
        if volba == "": 
            break
        
        if volba.isdigit():
            idx = int(volba) - 1
            if 0 <= idx < len(zaznamy):
                # Detail zaznamu
                vybrany = zaznamy[idx]
                gui.zobrazit_logo()
                gui.blok_text(f"DETAIL: {vybrany.get('jmeno')}", "^")
                
                detail = vybrany.get('vydaje_detail', {})
                if detail:
                    gui.vykreslit_graf(detail)
                else:
                    gui.blok_text("Tento zaznam nema zadne vydaje.", "^")
                    
                input("\n   > Enter zpet do seznamu...")
            else:
                print("   [!] Neplatne ID.")
                time.sleep(1)


# ROZCESTNIK

def main():
    while True:
        gui.zobrazit_logo()
        gui.blok_text("HLAVNI MENU", "^")
        gui.cara("-")
        gui.vypis("[1] Nova kalkulace mzdy")
        gui.vypis("[2] Historie vypoctu")
        gui.vypis("[3] Financni zdravi (Analyza)")
        gui.vypis("[4] Export do Excelu")
        gui.vypis("[5] SPORICI CILE")
        gui.cara("-")
        gui.vypis("[0] Ukoncit")
        
        volba = gui.ziskej_text("Tva volba")
        
        if volba == "1":
            modul_nova_kalkulace()
        elif volba == "2":
            modul_historie()
        elif volba == "3":
            modul_financni_zdravi()
        elif volba == "4":
            db.export_do_excelu()
        elif volba == "5":
            modul_cile()
        elif volba == "0":
            print("\n   Na shledanou! Uklizim...")
            time.sleep(0.5)
            break
        else:
            print("   [!] Neplatna volba, zkus to znovu.")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
