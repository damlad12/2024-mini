from machine import Pin
import time
import random
import json
import network
import urequests


N: int = 10
sample_ms = 10.0
on_ms = 500

ssid = input("Enter your Wi-Fi SSID: ")
wifi_password = input("Enter your Wi-Fi password: ")
#firebase_api_key = "AIzaSyAlfonCarFCUA3u0AZTw5CEJuAPxciEM9U"
#email = input("Enter your Firebase email: ")
#firebase_password = input("Enter your Firebase password: ")
database = "https://miniproject-team31-default-rtdb.firebaseio.com/scores.json"


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, wifi_password)

if wlan.isconnected():
    print("Connected to Wi-Fi")


def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)


def blinker(N: int, led: Pin) -> None:
    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)


def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file."""
    with open(json_filename, "w") as f:
        json.dump(data, f)


def scorer(t: list[int | None]) -> None:
    """Calculates scores and uploads results to Firebase Storage."""
    # collate results
    misses = t.count(None)
    print(f"You missed the light {misses} / {len(t)} times")

    t_good = [x for x in t if x is not None]

    print(t_good)

    data = {}
    if t_good:
        data['max_response'] = max(t_good)
        data['min_response'] = min(t_good)
        data['avg_response'] = sum(t_good)/len(t_good)
   
    data['score'] = len(t_good)/len(t)

    now: tuple[int] = time.localtime()
    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"score-{now_str}.json"

    print("write", filename)
    write_json(filename, data)
    headers = {'Content-Type': 'application/json'}
    with open(filename, 'r') as file:
        json_data = file.read()
    # Upload to Firebase Storage
    response = urequests.post(database, data=json_data, headers=headers)
    print(f"Response code: {response.status_code}")
    print(f"Response content: {response.text}")
    response.close()
       
if __name__ == "__main__":
    # using "if __name__" allows us to reuse functions in other script files
    led = Pin("LED", Pin.OUT)
    button = Pin(16, Pin.IN, Pin.PULL_UP)

    t: list[int | None] = []

    blinker(3, led)

    for i in range(N):
        time.sleep(random_time_interval(0.5, 5.0))

        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)

        led.low()

    blinker(5, led)

    scorer(t)