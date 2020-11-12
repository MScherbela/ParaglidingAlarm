from machine import Pin
import utime
import network
import urequests

def parseParaglidingStatus(html):
    tokens = html.split('<div class="ampel ')
    for t in tokens[1:]:
        if 'Höhenflüge Hohe Wand' in t:
            if 'ampel_gruen' in t:
                return 'green'
            elif 'ampel_gelb' in t:
                return 'yellow'
            else:
                return 'red'
    return 'error'

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

leds = dict(red=Pin(4, Pin.OUT),
            yellow= Pin(0, Pin.OUT),
            green=Pin(2, Pin.OUT))
for l in leds.values():
    l.off()

connectToWIFI()

while True:
    status = getParaglidingStatus()
    for l in leds.values():
        l.off()
    leds[status].on()
    print(status)
    utime.sleep(60)

