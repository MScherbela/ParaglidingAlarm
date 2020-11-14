from machine import Pin, DAC, Timer
import machine
import utime
import network
import urequests
import math

LEDS = dict(red=Pin(4, Pin.OUT, value=0),
            yellow=Pin(0, Pin.OUT, value=0),
            green=Pin(2, Pin.OUT, value=0))
BUZZER = Pin(16, Pin.OUT)
BUZZER.off()

wake_on_yellow = True


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


# def dac_timer_callback(timer):
#     global dac, dac_buffer, dac_buffer_pos
#     value = dac_buffer[dac_buffer_pos]
#     dac.write(value)
#     dac_buffer_pos += 1
#     if dac_buffer_pos == len(dac_buffer):
#         dac_buffer_pos = 0

for l in LEDS.values():
    l.on()
connectToWIFI()

# dac = DAC(Pin(25, Pin.OUT))
# dac_buffer = [0] * 4096
# dac_buffer_pos = 0
# for i in range(len(dac_buffer)):
#     dac_buffer[i] = int((0.5+0.5*math.sin(50*i*math.pi*2/len(dac_buffer))) * 255)
# dac_timer = Timer(1)
# dac_timer.init(mode=Timer.PERIODIC, freq=4096, callback=dac_timer_callback) # every millisecond

LEDS['red'].off()

while True:
    status = getParaglidingStatus()
    displayStatusOnLEDs(status)
    print(status)
    if (status == ParagliderStatus.GREEN) or ((status == ParagliderStatus.YELLOW) and wake_on_yellow):
        buzz(n=3, repeat=5)

    # Sleep for 60 seconds; On wakeup, the script fill start fully from the beginning, with RAM being fully reset:
    # The while loop therefore actually runs only once!
    machine.deepsleep(60000)
