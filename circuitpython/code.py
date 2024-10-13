import time
import board
import digitalio

from adafruit_hx711.hx711 import HX711
from adafruit_hx711.analog_in import AnalogIn

data = digitalio.DigitalInOut(board.GP28_A2)
data.direction = digitalio.Direction.INPUT
clock = digitalio.DigitalInOut(board.GP29)
clock.direction = digitalio.Direction.OUTPUT

hx711 = HX711(data, clock)
channel_a = AnalogIn(hx711, HX711.CHAN_A_GAIN_128)

tare_value = 33920  # This is the midpoint for a 24-bit ADC (2^23)
known_weight_g = 19.316
known_weight_reading = 73400  # This is an example value, you need to measure this
MAX_RAW_VALUE = 8388607
scale_factor = (known_weight_reading-tare_value)/known_weight_g

data_points = []
current_output = 0
dirty_points = []

def moving_average_filter(new_value, window_size=5):
    global data_points
    global dirty_points
    if new_value == 0 or new_value == MAX_RAW_VALUE:
       #print("ADC issue detected.")
       return 0
    
    converted_new_value = get_weight_g(new_value)
    valuediff = (abs(current_output-converted_new_value)/abs((current_output+converted_new_value)/2))*100
    #print(f"% Diff: {valuediff}")
    if valuediff > 199:
        if len(dirty_points) < 2:
            #print(f"DIRTY READING. DISCARDING.")
            dirty_points.append(new_value)
            return 0            
        else:
            #print(f"too. much. dirt.")
            dirty_points = []
            data_points = []
     
    data_points.append(new_value)    
    if len(data_points) > window_size:
        data_points = data_points[-window_size:]
  
    return sum(data_points) / len(data_points)




def get_weight_g(reading):
    net_value = reading - tare_value
    weight = net_value / scale_factor 
    #print(f"Raw: {reading}, Net: {net_value}, Weight: {weight}g")
    return weight

while True:
    get_new_value = moving_average_filter(channel_a.value)
    if get_new_value != 0:
        current_output = get_weight_g(get_new_value)
    #print(data_points)
    print(f"Reading: {round(current_output,3)}g")
    #time.sleep(0.01)