# Semestralni_projekt_Kopecek

Název projektu: Rozpočtová kalkulačka
-- Původní vize --
Aplikace bude sloužit k organizaci financí. Do aplikace budou zadány veškeré příjmy a výdaje. Aplikace si údaje uloží a zapomocí vzorce k ideálnímu rozložení příjmů a výdajů doporučí jaké změny v rozpočtu provést. Budu moci exportovat data do excelu a zobrazovat grafy.
Klíčové cíle/funkce: Uložení výdajů a příjmů Grafické znázornění Doporučení pro optimálnější nakládání s penězi, propojení s excelem

## Popis projektu
Vytvořil jsem konzolovou finanční kalkulačku. Aplikace se spoští přímov konzoli. Použil jsem jednoduchý ascii desing. Princip zadávání 


## Klíčové funkce

* **Výpočet čisté mzdy (Legislativa 2025)**
    * Automatický výpočet z hrubé mzdy.
    * Implementace aktuálních sazeb sociálního (7,1 %) a zdravotního (4,5 %) pojištění.
    * Přesné zaokrouhlování základu daně a aplikace slev na poplatníka či děti.

* **Sledování a kategorizace výdajů**
    * Možnost řazení výdajů do kategorií (Bydlení, Jídlo, Doprava, Zábava, Pojištění, Ostatní).
    * Okamžitý výpočet zůstatku a bilance.
    * Zobrazení přehledných grafů

* **Vizualizace dat**
    * **Konzole (TUI):** Implementace ASCII grafů a knihovny `plotext` pro rychlý přehled přímo v terminálu.
    * **Excel:** Generování profesionálních reportů obsahujících sloupcové grafy (bilance) a koláčové grafy (struktura výdajů).

* **Pokročilý systém exportu**
    * Generování samostatného `.xlsx` souboru pro každý záznam.
    * Automatická organizace souborů do adresáře `exporty/`.
    * Dynamické vytváření listů a grafů uvnitř sešitu.
    * Přehledný soubor v úložišti počítače

### Analýza finančního zdraví
Modul pro vyhodnocení osobního rozpočtu poskytuje okamžitou zpětnou vazbu na základě zadaných dat. Analytické jádro pracuje s následujícími principy:
* **Metodika 50/30/20:** Algoritmus porovnává strukturu výdajů s obecně uznávaným finančním pravidlem, které dělí příjmy na nutné výdaje, osobní spotřebu a úspory.
* **Klíčové metriky (KPI):** Aplikace automaticky vypočítává a vyhodnocuje dva hlavní ukazatele:
    * *Míra úspor:* Poměr mezi disponibilním zůstatkem a čistou mzdou (cílová hodnota ≥ 20 %).
    * *Náklady na bydlení:* Procentuální podíl výdajů na bydlení vůči celkovému příjmu, kde systém hlídá překročení bezpečné hranice (typicky 30–35 %).
* **Interpretace výsledků:** Na základě vypočtených hodnot systém generuje slovní hodnocení a kontextová varování (např. při záporné bilanci, nedostatečné tvorbě rezerv nebo nadměrném zatížení fixními náklady), což uživateli pomáhá identifikovat rizikové oblasti rozpočtu.

---

## Struktura projektu

Projekt využívá modulární architekturu rozdělenou do 5 samostatných skriptů:

| Soubor | Popis |
| :--- | :--- |
| **`main.py`** | **Hlavní spouštěcí soubor.** Řídí životní cyklus aplikace, menu a volání modulů. |
| `vypocty.py` | Matematické jádro aplikace. Obsahuje funkce pro výpočet mezd, daní a odvodů. |
| `data.py` | Vrstva pro práci s daty. Zajišťuje ukládání do JSON a export reportů pomocí `xlsxwriter`. |
| `grafika.py` | Uživatelské rozhraní (UI/TUI). Obsahuje funkce pro formátování výstupu a vykreslování grafů. |
| `nastaveni.py` | Konfigurační soubor. Obsahuje globální konstanty, daňové sazby a definice kategorií. |

### Systém ukládání a konfigurace
Aplikace klade důraz na oddělení dat od logiky programu:
* **Perzistence dat:** Veškerá historie výpočtů a zadaných výdajů je ukládána do strukturovaného souboru `financni_data.json`. Tento formát zajišťuje snadnou přenositelnost a čitelnost dat.
* **Centralizovaná konfigurace:** Veškeré proměnné, které se mohou v čase měnit (daňové sazby, limity, názvy kategorií), jsou izolovány v modulu `nastaveni.py`. To umožňuje aktualizaci parametrů aplikace bez nutnosti zásahu do výkonného kódu.

### Generování Excel reportů
Exportní modul zajišťuje tvorbu nativních `.xlsx` souborů bez nutnosti instalace programu MS Excel na cílovém zařízení. Proces generování je plně automatizován pomocí knihovny `xlsxwriter`:
* **Struktura souboru:** Každý vygenerovaný sešit obsahuje prezentační list "Report" s formátovanými tabulkami a grafy, a pomocný list "Data_Grafy", který slouží jako zdroj dat pro vizualizace a je před uživatelem skryt pro zachování čistoty reportu.
* **Dynamické grafy:** Aplikace programově vytváří interaktivní grafy (sloupcový graf bilance a koláčový graf struktury výdajů). Tyto grafy nejsou statické obrázky, ale plnohodnotné objekty Excelu, které reagují na změnu dat.
* **Organizace souborů:** Exportní rutina automaticky spravuje adresářovou strukturu (`exporty/`) a zajišťuje unikátnost názvů souborů kombinací sanitizovaného jména uživatele, data výpočtu a unikátního identifikátoru záznamu.

 ## Možnosti nasazení a přenositelnost

Aplikace je navržena jako multi-platformní a nabízí několik scénářů spuštění v závislosti na potřebách uživatele a dostupném hardwaru.

### Spuštění aplikace (GitHub Codespaces)
Projekt je plně kompatibilní s vývojovým prostředím GitHub Codespaces. Toto řešení umožňuje spustit aplikaci přímo ve webovém prohlížeči bez nutnosti lokální instalace Pythonu nebo závislostí.
* **Dostupnost:** Aplikaci lze spustit z libovolného zařízení s přístupem k internetu (Desktop, Laptop, Tablet).
* **Postup:** V repozitáři projektu na GitHubu zvolte možnost *Code* > *Codespaces* > *Create codespace on main*. Po inicializaci virtuálního kontejneru stačí v integrovaném terminálu spustit příkaz `python main.py`.


---
