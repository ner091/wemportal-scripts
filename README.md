# WEM Portal Scripts

Fork of dm82m and modified to be used within HomeAssistant and selenium grid.

Scripts for Weishaupt WEM Portal using Python and Selenium Grid (and Chromium Headless in a docker).

## 3-step Installation

### On your HomeAssistant instance

You need to install the selenium chorme docker image (if you're not using another grid) and also the Python selenium package. Commands may be different on your system, just use them as an idea.

```bash
docker pull kynetiv/selenium-standalone-chromium-pi

docker run -d -p 4444:4444 --restart unless-stopped --name chrome kynetiv/selenium-standalone-chromium-pi

pip3 install selenium
```

### Script

Within the script **config.py** search for **USERNAME** and **PASSWORD** and replace it with your data.

Put the changed file **config.py** & **ExportFachmannInfo.py** into your HomeAssistant config directory within the folder **scripts** (/config/scripts or change the absolute path within the command argument).

### Sensor definition

```
- platform: command_line
    name: heating
    json_attributes:
      - timestamp
      - current_outside_temperature_celsius
      - average_outside_temperature_celsius
      - longtime_outside_temperature_celsius
      - room_set_temperature_celsius
      - water_inlet_set_temperature_celsius
      - water_inlet_temperature_celsius
      - hot_water_temperature_celsius
      - performance
      - performance_request_ratio
      - dynamic_switch_temperature_difference_kelvin
      - lwt_temperature_celsius
      - water_outlet_temperature_celsius
      - pump_rotation_ratio
      - volume_flow_cubicmeter_per_hour
      - crossover_valve_setting
      - set_frequency_compressor_hertz
      - frequency_compressor_hertz
      - air_inlet_temperature_celsius
      - outside_heat_exchanger_inlet_temperature_celsius
      - outside_heat_exchanger_middle_temperature_celsius
      - pressure_gas_temperature_celsius
      - inside_heat_exchanger_temperature_celsius
      - refrigerant_inside_temperature_celsius
      - compressor_operating_hours
      - compressor_cycles
      - defrosting_cycles
      - heating1_state
      - heating2_state
      - heating1_operating_hours
      - heating2_operating_hours
      - heating1_cycles
      - heating2_cycles
      - total_energy_per_day
      - total_energy_per_month
      - total_energy_per_year
      - heating_energy_per_day
      - heating_energy_per_month
      - heating_energy_per_year
      - water_energy_per_day
      - water_energy_per_month
      - water_energy_per_year
      - cooling_energy_per_day
      - cooling_energy_per_month
      - cooling_energy_per_year
    value_template: >-
      {{ value_json.crossover_valve_setting }}
    command: "pip3 install selenium -q && python3 /config/scripts/ExportFachmannInfo.py"
    scan_interval: 300
    command_timeout: 120
  - platform: template
    sensors:
      heating_current_outside_temperature_celsius:
        friendly_name: "Heizung Aussentemperatur"
        value_template: "{{ states.sensor.heating.attributes.current_outside_temperature_celsius }}"
        unit_of_measurement: "°C"
        device_class: "temperature"
      heating_hot_water_temperature_celsius:
        friendly_name: "Heizung Warmwassertemperatur"
        value_template: "{{ states.sensor.heating.attributes.hot_water_temperature_celsius }}"
        unit_of_measurement: "°C"
        device_class: "temperature"
      heating_water_inlet_temperature_celsius:
        friendly_name: "Heizung Vorlauftemperatur"
        value_template: "{{ states.sensor.heating.attributes.water_inlet_temperature_celsius }}"
        unit_of_measurement: "°C"
        device_class: "temperature"
      heating_water_outlet_temperature_celsius:
        friendly_name: "Heizung Rücklauftemperatur"
        value_template: "{{ states.sensor.heating.attributes.water_outlet_temperature_celsius }}"
        unit_of_measurement: "°C"
        device_class: "temperature"
      heating_performance:
        friendly_name: "Heizung Leistung"
        value_template: "{{ states.sensor.heating.attributes.performance }}"
        unit_of_measurement: " kW"
        device_class: "power"
      heating_performance_request_ratio:
        friendly_name: "Heizung Leistungsanforderung"
        value_template: "{{ states.sensor.heating.attributes.performance_request_ratio }}"
        unit_of_measurement: " %"
        device_class: "power_factor"
      heating_pump_rotation_ratio:
        friendly_name: "Heizung Drehzahl Pumpe"
        value_template: "{{ states.sensor.heating.attributes.pump_rotation_ratio }}"
        unit_of_measurement: " %"
        device_class: "power_factor"
```
If you want, you can add every json attribute from the command line as a template sensor.
