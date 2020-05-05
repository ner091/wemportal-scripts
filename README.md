# WEM Portal Scripts

Fork of neiser and modified to be used within HomeAssistant.

Scripts for Weishaupt WEM Portal using Python and Selenium (and Chromium Headless).

## 3-step Installation

### On your HomeAssistant instance

You need to install the chromium-driver and also the Python selenium package. Commands may be different on your system, just use them as an idea.

```bash
apt-get install chromium-driver

sudo -u homeassistant -H -s

pip3 install selenium
```

### Script

Within the script **ExportFachmannInfo.py** search for **YOUR\_USERNAME** and **YOUR\_PASSWORD** and replace it with your data.

Put the changed file **ExportFachmannInfo.py** into your HomeAssistant home directory (.homeassistant) within the folder **scripts**.

### Sensor definition

```sensor:
  - platform: command_line
    name: heating
    json_attributes:
      - "aussentemperatur_aktuell"
      - "warmwassertemperatur_aktuell"
    value_template: '{{ value_json.timestamp }}'
    command: 'python3 /home/homeassistant/.homeassistant/scripts/ExportFachmannInfos.py'
    scan_interval: 600
    command_timeout: 180
  - platform: template
    sensors:
      heating_aussentemperatur_aktuell:
        friendly_name: "Heizung - Außentemperatur Aktuell"
        value_template: "{{ states.sensor.heating.attributes.aussentemperatur_aktuell }}"
        unit_of_measurement: '°C'
        device_class: 'temperature'
  - platform: template
    sensors:
      heating_warmwassertemperatur_aktuell:
        friendly_name: "Heizung Warmwassertemperatur Aktuell"
        value_template: "{{ states.sensor.heating.attributes.warmwassertemperatur_aktuell }}"
        unit_of_measurement: '°C'
        device_class: 'temperature'
```
