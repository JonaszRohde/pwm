#!/usr/bin/env python
from time import sleep
from pathlib import Path
from glob import glob
from multiprocessing import Process

aktywne = (
    (   # cpu
        {65: 0.30, 70: 0.50, 75: 0.70, 80: 0.90},
        "/sys/class/hwmon/hwmon*/temp11_input",
        "/sys/devices/platform/nct6775.2592/hwmon/hwmon*/pwm2"
    ),
    (   # rx 550
        {65: 0.30, 70: 0.50, 75: 0.70, 80: 0.90},
        "/sys/class/drm/card0/device/hwmon/hwmon*/temp1_input", 
        "/sys/devices/platform/nct6775.2592/hwmon/hwmon*/pwm1",
    )
)

def pwm(progi, sciezka_temp, sciezka_pwm, histereza=10, interwal=10):
    progi_dolne = [
        temperatura - histereza
        for temperatura in progi
    ]
    progi_gorne = [
        temperatura + histereza
        for temperatura in progi
    ]
    wartosci_obrotow = [
        str(round(255 * ulamek))
        for ulamek in progi.values()
    ]
    sciezka_temp, sciezka_pwm, sciezka_pwm_enable = [
        Path(*glob(sciezka))
        for sciezka in [sciezka_temp, sciezka_pwm, sciezka_pwm + "_enable"]
    ]
    poziom = 0
    ostatni_poziom = len(progi) - 1

    try:
        sciezka_pwm_enable.write_text("1")
        sciezka_pwm.write_text(wartosci_obrotow[poziom])

        while True:
            sleep(interwal)

            temperatura = int(sciezka_temp.read_text()) // 1000
            if temperatura < progi_dolne[poziom] and poziom > 0:
                poziom -= 1
            elif temperatura > progi_gorne[poziom] and poziom < ostatni_poziom:
                poziom += 1
            else:
                continue
            sciezka_pwm.write_text(wartosci_obrotow[poziom])
    finally:
        sciezka_pwm_enable.write_text("5")

if __name__ == "__main__":
    for i in aktywne:
        Process(target=pwm, args=i).start()
