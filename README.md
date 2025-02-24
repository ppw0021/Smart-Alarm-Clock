# Smart Alarm Clock

## Overview
The Smart Alarm Clock is a Raspberry Pi-based alarm system designed to help users wake up more efficiently by detecting phone presence, monitoring bed occupancy, and providing personalized wake-up times. The system integrates an LCD display, ultrasonic sensors, a snooze button, and a sound module.
![image](https://github.com/user-attachments/assets/542d9082-c46b-4f26-a538-def80394839c)

## Features
- **Alarm Scheduling**: Sets wake-up time based on user input and external recommendations.
- **Snooze Functionality**: Allows the user to snooze the alarm with a button press.
- **Phone Detection**: Detects whether the phone is placed nearby as part of the wake-up process.
- **Bed Exit Detection**: Uses an ultrasonic sensor to determine when the user leaves the bed.
- **LCD Display**: Shows current time, alarm status, and reminders.
- **Sound Module**: Plays an alarm sound when the wake-up time is reached.
- **Remote API Integration**: Connects to a remote server to retrieve and update alarm settings.

## Hardware Requirements
- Raspberry Pi (with GPIO support)
- LCD Display (compatible with `rpi_lcd` library)
- Ultrasonic Distance Sensor (HC-SR04 or similar)
- Push Button (for snooze functionality)
- Sound Module (such as a buzzer or speaker)
- Obstacle Sensor (for phone presence detection)

## Chassis
The chassis is 3d printed from PLA plastic. It was designed in shapr3d.
![render](https://github.com/user-attachments/assets/00db2917-d7e3-4f7e-ad39-72b9e9242046)


## Software Requirements
- Python 3.x
- Required Python libraries:
  - `RPi.GPIO`
  - `time`
  - `requests`
  - `pygame`
  - `rpi_lcd`
  - `signal`

## Installation
1. Clone the repository or copy the script to your Raspberry Pi.
2. Install the required Python dependencies:
   ```bash
   pip install requests pygame rpi-lcd
   ```
3. Connect the required hardware components to the Raspberry Pi GPIO pins.
4. Run the script:
   ```bash
   python main.py
   ```

## Usage
- Press the snooze button to set the sleep time or snooze the alarm.
- The system will automatically detect if the user leaves the bed.
- The alarm sound will stop when the user gets out of bed.
- The LCD screen provides real-time status updates, including sleep and wake-up times.
- The device connects to an external API to fetch optimal sleep schedules.

## API Endpoints
- `/setalarm` (Set the alarm)
- `/stopalarm` (Snooze the alarm)
- `/cancelalarm` (Cancel the alarm)
