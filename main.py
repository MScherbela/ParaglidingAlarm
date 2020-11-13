from machine import Pin
import utime
import network
import urequests

leds = dict(red=Pin(4, Pin.OUT),
            yellow= Pin(0, Pin.OUT),
            green=Pin(2, Pin.OUT))
buzzer = Pin(16, Pin.OUT)
buzzer.off()
for l in leds.values():
    l.off()

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

def buzz(n=3, repeat=1):
    for r in range(repeat):
        for i in range(n):
            buzzer.on()
            utime.sleep_ms(30)
            buzzer.off()
            utime.sleep_ms(500)
        utime.sleep(5)


for l in leds:
    leds[l].on()
connectToWIFI()
leds['red'].off()

while True:
    status = getParaglidingStatus()
    for l in leds.values():
        l.off()
    leds[status].on()
    print(status)
    if status == 'green':
        buzz(n=4, repeat=10)
    for minute in range(5):
        utime.sleep(60)

