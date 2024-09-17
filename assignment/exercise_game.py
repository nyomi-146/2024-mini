"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import json
import network
import urequests

url = "https://kyla-nyomi-mini2024-default-rtdb.firebaseio.com/"

N: int = 10
sample_ms = 10.0
on_ms = 500

def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)


def blinker(N: int, led: Pin) -> None:
    # %% let user know game started / is over

    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)


def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file.

    Parameters
    ----------

    json_filename: str
        The name of the file to write to. This will overwrite any existing file.

    data: dict
        Dictionary data to write to the file.
    """

    with open(json_filename, "w") as f:
        json.dump(data, f)
   
    json_object = json.dumps(data)

    response = urequests.put(url + json_filename, headers = {}, data = json_object)
    print(response.text)


def scorer(t: list[int | None]) -> None:
    # %% collate results
    misses = t.count(None)
    print(f"You missed the light {misses} / {len(t)} times")

    print(t)
   
    t_good = [x for x in t if x is not None]

    print(t_good)

    # add key, value to this dict to store the minimum, maximum, average response time
    # and score (non-misses / total flashes) i.e. the score a floating point number
    # is in range [0..1]
    data = {
        "minimum": min(t_good),
        "maximum": max(t_good),
        "average": sum(t_good)/len(t_good),
        "score": len(t_good)/len(t)
    }

    # %% make dynamic filename and write JSON
   
    print(data)

    now: tuple[int] = time.localtime()

    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"score-{now_str}.json"

    print("write", filename)

    write_json(filename, data)

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    ssid = 'redacted'
    password = 'redacted'
    wlan.connect(ssid, password)


if __name__ == "__main__":
    # using "if __name__" allows us to reuse functions in other script files

    connect()
    #define LED
    led = Pin("LED", Pin.OUT)
   
    #define button pin, change to 15
    button = Pin(15, Pin.IN, Pin.PULL_UP)


    #initialize a list t that can contain integers or None values
    t: list[int | None] = []

    #indicate game has started
    blinker(3, led)


   
    for i in range(N):
       
        #sleep for a random time interval
        time.sleep(random_time_interval(0.5, 5.0))

        #turn LED on
        led.high()
        print("LED on")
       
        #set the reference tic
        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            #if button is pressed, get response time and turn LED off
            if button.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        #add the response time to the list, if LED was not pressed, add NONE
        t.append(t0)
       
        #set LED low
        led.low()

    #indicate game has ended
    blinker(5, led)

    scorer(t)

