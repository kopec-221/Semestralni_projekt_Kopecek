# vypocty.py
import nastaveni as cfg

def vypocet_mzdy(hruba, podepsano, deti):
    soc = hruba * cfg.SOC_POJISTENI_SAZBA
    zdr = hruba * cfg.ZDR_POJISTENI_SAZBA
    dan_zaklad = hruba * cfg.DAN_Z_PRIJMU_SAZBA
    
    sleva = 0
    if podepsano:
        sleva += cfg.SLEVA_POPLATNIK
        if deti >= 1: sleva += cfg.ZVYHODNENI_DITE_1
        if deti >= 2: sleva += cfg.ZVYHODNENI_DITE_2
        if deti >= 3: sleva += cfg.ZVYHODNENI_DITE_3 * (deti - 2)
        
    dan_realna = max(0, dan_zaklad - sleva)
    cista = hruba - soc - zdr - dan_realna
    
    return int(cista), int(soc), int(zdr), int(dan_realna)
