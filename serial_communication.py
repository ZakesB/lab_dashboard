import serial
import time
import threading

# Define the serial port and baud rate for Arduino communication
SERIAL_PORT = '/dev/tty.usbmodem141301' #'/dev/ttyS0'  # Update with the correct port
BAUD_RATE = 19200

# Variables to store the latest sensor data
latest_sensor_data = {"temperature": 0, "humidity": 0}

# Lock for thread safety
data_lock = threading.Lock()


def start_serial_communication():
    with serial.Serial(SERIAL_PORT, BAUD_RATE) as ser:
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                # Parse the received data (adjust as needed)
                temperature, humidity = map(float, line.split(','))
                with data_lock:
                    latest_sensor_data["temperature"] = temperature
                    latest_sensor_data["humidity"] = humidity
                    print(f"Latest data {latest_sensor_data}")
            except (ValueError, UnicodeDecodeError):
                pass
            time.sleep(1)


def get_latest_sensor_data():
    with data_lock:
        return latest_sensor_data


if __name__ == '__main__':
    start_serial_communication()
