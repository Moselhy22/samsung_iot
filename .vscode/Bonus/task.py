import RPi.GPIO as GPIO
import Adafruit_DHT
import time
import datetime
import csv
import matplotlib.pyplot as plt

# GPIO setup
GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# DHT setup
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Log file
log_file = "sensor_log.csv"

def read_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2

    return distance

def read_temperature():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return temperature
    else:
        return None

def log_data(distance, temperature):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, distance, temperature])

def plot_data():
    timestamps = []
    distances = []
    temperatures = []

    with open(log_file, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            timestamps.append(row[0])
            distances.append(float(row[1]))
            temperatures.append(float(row[2]))

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, distances, label='Distance (cm)')
    plt.plot(timestamps, temperatures, label='Temperature (C)')
    plt.xlabel('Time')
    plt.ylabel('Readings')
    plt.title('Sensor Readings Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    with open(log_file, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Distance (cm)", "Temperature (C)"])

    try:
        while True:
            distance = read_distance()
            temperature = read_temperature()

            if temperature is not None:
                log_data(distance, temperature)
                print(f"Distance: {distance:.2f} cm, Temperature: {temperature:.2f} C")
            else:
                print("Failed to retrieve data from temperature sensor")

            time.sleep(2)  # Adjust the delay as needed

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        plot_data()
        GPIO.cleanup()
