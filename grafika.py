# grafika.py
import os
import time
import nastaveni as cfg

# Zkusime importovat plotext, pokud je nainstalovan
try:
    import plotext as plt
    MA_PLOTEXT = True
except ImportError:
    MA_PLOTEXT = False

def vycistit_konzoli():
    # Univerzalni mazani pro Windows i VS Code terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[H\033[2J", end="")

def cara(znak="-"):
    print(f"+{znak * (cfg.SIRKA_UI - 2)}+")

def zahlavi(text):
    text_stred = text.center(cfg.SIRKA_UI - 4)
    print(f"|  {text_stred}  |")

def blok_text(text, zarovnani="<"):
    format_str = f"| {{:{zarovnani}{cfg.SIRKA_UI - 4}}} |"
    print(format_str.format(text))

def radek_tabulky(popis, hodnota):
    delka_popisu = cfg.SIRKA_UI - 4 - 15 - 1 
    print(f"| {popis:.<{delka_popisu}} {hodnota:>15} |")

def progress_bar(popis):
    print(f"| {popis}")
    print("| [", end="", flush=True)
    for _ in range(cfg.SIRKA_UI - 6):
        time.sleep(0.01) 
        print("#", end="", flush=True)
    print("] |")
    time.sleep(0.3)

def zobrazit_logo():
    vycistit_konzoli() 
    cara("=")
    zahlavi("FINANCNI MANAZER v9.0") # Verze 9 (Modularni)
    zahlavi("Modularni System")
    cara("=")
    print()

def vykreslit_graf(vydaje_dict):
    if not vydaje_dict: 
        blok_text("Zadne vydaje k zobrazeni.", "^")
        return
    
    if MA_PLOTEXT:
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
    else:
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
            radek = f"{nazev[:12]:<12} {graf:<26} {int(castka)}"
            blok_text(radek, "<")
        cara("-")
        
def ziskej_cislo(popis):
    while True:
        try:
            raw = input(f"   > {popis}: ")
            val = float(raw.replace(",", "."))
            if val < 0: raise ValueError
            return val
        except ValueError:
            print(f"     [CHYBA] Zadej platne kladne cislo.")

def ziskej_text(popis):
    return input(f"   > {popis}: ").strip()
