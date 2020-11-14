from machine import Pin
import machine
import utime
import network
import urequests

LEDS = dict(red=Pin(4, Pin.OUT, value=0),
            yellow=Pin(0, Pin.OUT, value=0),
            green=Pin(2, Pin.OUT, value=0))
BUZZER = Pin(16, Pin.OUT)
BUZZER.off()

wake_on_yellow = True
machine.freq(80000000)


class ParagliderStatus:
    RED = 0
    YELLOW = 1
    GREEN = 2
    ERROR = 3

def parseParaglidingStatus(html):
    tokens = html.split('<div class="ampel ')
    for t in tokens[1:]:
        if 'Höhenflüge Hohe Wand' in t:
            if 'ampel_gruen' in t:
                return ParagliderStatus.GREEN
            elif 'ampel_gelb' in t:
                return ParagliderStatus.YELLOW
            else:
                return ParagliderStatus.RED
    return ParagliderStatus.ERROR

def getParaglidingStatus():
    url = 'http://www.fly-hohewand.at/home/aktuelle-info-ueber-schulbetrieb'
    r = urequests.get(url)
    html = r.text
    r.close()
    return parseParaglidingStatus(html)

def connectToWIFI():
    print("Connecting to WIFI...")
    routercon = network.WLAN(network.STA_IF)
    routercon.active(True)
    routercon.connect("UPC3928459", "sebpK3tRhx8m")
    while not routercon.isconnected():
        utime.sleep_ms(100)


def buzz(n=3, repeat=1):
    for r in range(repeat):
        for i in range(n):
            BUZZER.on()
            utime.sleep_ms(100)
            BUZZER.off()
            utime.sleep_ms(500)
        utime.sleep(2)


def displayStatusOnLEDs(status):
    for l in LEDS.values():
        l.off()
    if status == ParagliderStatus.GREEN:
        LEDS['green'].on()
    elif status == ParagliderStatus.YELLOW:
        LEDS['yellow'].on()
    elif status == ParagliderStatus.RED:
        LEDS['red'].on()
    else:
        LEDS['red'].on()
        LEDS['yellow'].on()

for l in LEDS.values():
    l.on()
connectToWIFI()

LEDS['red'].off()

while True:
    status = getParaglidingStatus()
    displayStatusOnLEDs(status)
    print(status)
    if (status == ParagliderStatus.GREEN) or ((status == ParagliderStatus.YELLOW) and wake_on_yellow):
        buzz(n=3, repeat=5)
    utime.sleep(5*60)

    # Sleep for 60 seconds; On wakeup, the script fill start fully from the beginning, with RAM being fully reset:
    # The while loop therefore actually runs only once!
    # Note: This also disables the GPIOs!
    # machine.deepsleep(60000)
