# grafika.py
import os
import time
import nastaveni as cfg


try:
    import plotext as plt
    MA_PLOTEXT = True
except ImportError:
    MA_PLOTEXT = False

#  OVLADANI KONZOLE A SYSTEM

def vycistit_konzoli():
    
    os.system('cls' if os.name == 'nt' else 'clear')
    # Pojistka pro nektere terminaly
    print("\033[H\033[2J", end="")

def zobrazit_logo():
    
    vycistit_konzoli() 
    cara("=")
    zahlavi("FINANCNI MANAZER") 
    zahlavi("Matyas Kopecek")
    cara("=")
    print()

def animace_nacitani(popis="Zpracovavam"):
    
    print(f"| {popis}...")
    print("| [", end="", flush=True)
    for _ in range(cfg.SIRKA_UI - 6):
        time.sleep(0.01) 
        print("#", end="", flush=True)
    print("] |")
    time.sleep(0.2)

#  FORMATOVANI TEXTU 

def cara(znak="-"):
    
    
    print(f"+{znak * (cfg.SIRKA_UI - 2)}+")

def zahlavi(text):
    
   
    text_stred = text.center(cfg.SIRKA_UI - 4)
    print(f"|  {text_stred}  |")

def blok_text(text, zarovnani="<"):
    
    format_str = f"| {{:{zarovnani}{cfg.SIRKA_UI - 4}}} |"
    print(format_str.format(text))

def radek_tabulky(popis, hodnota):
    
    
    delka_popisu = cfg.SIRKA_UI - 20 
    print(f"| {popis:.<{delka_popisu}} {hodnota:>15} |")

def vypis(text):
    
    print(f"   {text}")

# VIZUALIZACE A GRAFY

def vykreslit_progress_bar(nazev, aktualne, cil):
    
    
    if cil > 0:
        procenta = (aktualne / cil) * 100
    else:
        procenta = 0
        
    
    sirka_listy = 30
    pocet_plnych = int((procenta / 100) * sirka_listy)
    
    
    if pocet_plnych > sirka_listy: pocet_plnych = sirka_listy
    if pocet_plnych < 0: pocet_plnych = 0
        
    pocet_prazdnych = sirka_listy - pocet_plnych
    lista = "#" * pocet_plnych + "." * pocet_prazdnych
    
    
    print(f"\n   {nazev.upper()}")
    print(f"   [{lista}] {int(procenta)} %")
    
    print(f"   {aktualne:,.0f} Kc / {cil:,.0f} Kc".replace(",", " "))


def _graf_plotext(vydaje_dict):
    
    kategorie = list(vydaje_dict.keys())
    hodnoty = list(vydaje_dict.values())
    
    plt.clear_figure()
    plt.simple_bar(kategorie, hodnoty, width=cfg.SIRKA_UI, title="Rozlozeni vydaju")
    plt.theme("pro")
    print()
    blok_text("GRAFICKY PREHLED (Plotext)", "^")
    cara("-")
    plt.show()
    cara("-")

def _graf_ascii(vydaje_dict):
    
    blok_text("GRAFICKY PREHLED (ASCII)", "^")
    cara("-")
    
    try:
        max_hodnota = max(vydaje_dict.values())
    except ValueError:
        max_hodnota = 0
        
    max_sirka_sloupce = 25 
    serazene = sorted(vydaje_dict.items(), key=lambda x: x[1], reverse=True)
    
    for nazev, castka in serazene:
        if max_hodnota > 0:
            pomer = castka / max_hodnota
            delka = int(pomer * max_sirka_sloupce)
        else:
            delka = 0
            
        graf = cfg.ZNAK_GRAFU * delka
        # Format: Nazev (12 znaku) | Graf (26 znaku) | Castka
        radek = f"{nazev[:12]:<12} {graf:<26} {int(castka)}"
        blok_text(radek, "<")
        
    cara("-")

def vykreslit_graf(vydaje_dict):
    
    if not vydaje_dict: 
        blok_text("Zadne vydaje k zobrazeni.", "^")
        return
    
    if MA_PLOTEXT:
        _graf_plotext(vydaje_dict)
    else:
        _graf_ascii(vydaje_dict)



# VSTUPY OD UZIVATELE

def ziskej_cislo(popis):
    
    while True:
        try:
            raw = input(f"   > {popis}: ")
            
            val = float(raw.replace(",", "."))
            if val < 0: 
                print(f"     [CHYBA] Prosim zadej kladne cislo.")
                continue
            return val
        except ValueError:
            print(f"     [CHYBA] '{raw}' neni platne cislo.")

def ziskej_text(popis):
    
    return input(f"   > {popis}: ").strip()
