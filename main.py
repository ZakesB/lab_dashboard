from flask import Flask, render_template, request, jsonify, redirect, url_for
import random
import subprocess
import socket
import json
from threading import Thread
import serial_communication

app = Flask(__name__, static_url_path='/static')
# Initialize the serial communication thread
serial_thread = Thread(target=serial_communication.start_serial_communication)
serial_thread.daemon = True
serial_thread.start()

# Maximum number of data points to retain
MAX_DATA_POINTS = 100

# Sample sensor data (replace with actual data)
sensor_data = {
    'temperature': [],
    'humidity': [],
}

# Dictionary for sensor units
sensor_units = {
    'temperature': '°C',
    'humidity': '%',
}

# Sample list of connected devices
online_devices = [
    {
        'name': 'Raspberry Pi 1',
        'ip_address': '192.168.1.101',
        'online': False,  # Indicate if the device is online
    },
    # Add more devices as needed
]


@app.route('/', methods=['GET', 'POST'])
def index():
    selected_sensor = request.args.get('sensor', 'temperature')
    sensor_data_formatted = get_sensor_data(selected_sensor)
    print(f"Sensor formatted: {sensor_data_formatted}")
    return render_template('index.html', selected_sensor=selected_sensor, sensor_data=json.dumps(sensor_data_formatted),
                           sensor_units=json.dumps(sensor_units))


@app.route('/get_data', methods=['GET'])
def get_data():
    selected_sensor = request.args.get('sensor', 'temperature')
    data = get_sensor_data(selected_sensor)
    return jsonify(data)


def get_sensor_data(selected_sensor):
    print(f"Selected sensor: {selected_sensor}")
    # Generate random data for demonstration
    #if selected_sensor in sensor_data:
    #    #new_data_point = random.uniform(1, 5)
    #    #sensor_data[selected_sensor].append(new_data_point)
    new_data_point = serial_communication.get_latest_sensor_data()
    print(f"Arduino data >>>>>> {new_data_point[selected_sensor]}")
    if selected_sensor in new_data_point:
        sensor_data[selected_sensor].append(new_data_point[selected_sensor])
    print(f"Sensor Data>>>>: {sensor_data}")

    # Limit the number of data points
    if len(sensor_data[selected_sensor]) > MAX_DATA_POINTS:
        sensor_data[selected_sensor].pop(0)

    # Format data for Chart.js
    sensor_data_formatted = [{'x': i, 'y': val} for i, val in enumerate(sensor_data[selected_sensor])]
    return sensor_data_formatted


@app.route('/devices')
def connected_devices():
    return render_template('devices.html', devices=online_devices)


@app.route('/try_connect/<int:device_index>')
def try_connect(device_index):
    # Add code to attempt a connection to the device
    # You can use the device_index to identify the selected device

    # For example, you can display a message indicating the connection attempt
    message = f"Attempting to connect to {online_devices[device_index]['name']} at {online_devices[device_index]['ip_address']}."

    return render_template('try_connect.html', message=message)


@app.route('/add_device', methods=['POST'])
def add_device():
    device_name = request.form.get('device-name')
    ip_address = request.form.get('ip-address')

    # Validate the IP address
    try:
        socket.inet_aton(ip_address)
    except socket.error:
        return "Invalid IP Address. Please provide a valid IP address."

    # Perform a ping to check if the device is reachable
    try:
        # Use a ping command (you may need to adjust the command for your platform)
        result = subprocess.run(['ping', '-c', '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return f"Device at IP address {ip_address} is not reachable."
    except Exception as e:
        return f"An error occurred: {str(e)}"

    # Add the device to the list of connected devices
    connected_devices.append({
        'name': device_name,
        'ip_address': ip_address,
        'online': True  # Mark it as online
    })

    # Redirect back to the connected devices page
    return redirect(url_for('devices'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
