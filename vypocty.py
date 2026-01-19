# vypocty.py
import math
import nastaveni as cfg

def zaokrouhlit_nahoru(cislo):
    """Pomocna funkce pro zaokrouhleni na cele koruny nahoru."""
    return math.ceil(cislo)

def vypocet_mzdy(hruba, podepsano, deti):
    
    soc = zaokrouhlit_nahoru(hruba * cfg.SOC_POJISTENI_SAZBA)
    zdr = zaokrouhlit_nahoru(hruba * cfg.ZDR_POJISTENI_SAZBA)
    
    
    zaklad_dane = math.ceil(hruba / 100) * 100
    
    
    zaloha_dan = zaklad_dane * cfg.DAN_Z_PRIJMU_SAZBA
    
    
    sleva = 0
    if podepsano:
        sleva += cfg.SLEVA_POPLATNIK
        if deti >= 1: sleva += cfg.ZVYHODNENI_DITE_1
        if deti >= 2: sleva += cfg.ZVYHODNENI_DITE_2
        if deti >= 3: sleva += cfg.ZVYHODNENI_DITE_3 * (deti - 2)
        
    # Dan po sleve
    dan_realna = max(0, zaloha_dan - sleva)
    dan_realna = zaokrouhlit_nahoru(dan_realna)

    # 5. Cista mzda
    cista = hruba - soc - zdr - dan_realna
    
    return int(cista), int(soc), int(zdr), int(dan_realna)
