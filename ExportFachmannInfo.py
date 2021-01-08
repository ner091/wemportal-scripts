import config
import os
import time
import json
from threading import Lock
from timeit import default_timer as timer

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

debug = False
seleniumGridUrl = "http://localhost:4444/wd/hub"

MAP_METRICS = {
    'Zeitstempel': {'name': 'timestamp', 'type': 'info'},
    'Außentemperatur': {'name': 'current_outside_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'AT Mittelwert': {'name': 'average_outside_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'AT Langzeitwert': {'name': 'longtime_outside_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Raumsolltemperatur': {'name': 'room_set_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Vorlaufsolltemperatur': {'name': 'water_inlet_set_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Vorlauftemperatur': {'name': 'water_inlet_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Warmwassertemperatur': {'name': 'hot_water_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Ist Leistung': {'name': 'performance', 'type': 'gauge', 'strip': len(' KW')},
    'Leistungsanforderung': {'name': 'performance_request_ratio', 'type': 'gauge', 'strip': len(' %')},
    'Schaltdifferenz dynamisch': {'name': 'dynamic_switch_temperature_difference_kelvin', 'type': 'gauge', 'strip': len(' K')},
    'LWT': {'name': 'lwt_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Rücklauftemperatur': {'name': 'water_outlet_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Drehzahl Pumpe': {'name': 'pump_rotation_ratio', 'type': 'gauge', 'strip': len(' %')},
    'Volumenstrom': {'name': 'volume_flow_cubicmeter_per_hour', 'type': 'gauge', 'strip': len('m3/h')},
    'Stellung Umschaltventil': {'name': 'crossover_valve_setting', 'type': 'info'},
    'Soll Frequenz Verdichter': {'name': 'set_frequency_compressor_hertz', 'type': 'gauge', 'strip': len(' Hz')},
    'Ist Frequenz Verdichter': {'name': 'frequency_compressor_hertz', 'type': 'gauge', 'strip': len(' Hz')},
    'Luftansaugtemperatur': {'name': 'air_inlet_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Wärmetauscher AG Eintritt': {'name': 'outside_heat_exchanger_inlet_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Wärmetauscher AG Mitte': {'name': 'outside_heat_exchanger_middle_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Druckgas': {'name': 'pressure_gas_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Wärmetauscher Innen': {'name': 'inside_heat_exchanger_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Kältemittel Innen': {'name': 'refrigerant_inside_temperature_celsius', 'type': 'gauge', 'strip': len(' °C')},
    'Betriebsstd. Verdichter': {'name': 'compressor_operating_hours', 'type': 'gauge', 'strip': len(' h')},
    'Schaltspiele Verdichter': {'name': 'compressor_cycles', 'type': 'counter'},
    'Schaltspiele Abtauen': {'name': 'defrosting_cycles', 'type': 'counter'},
    'Status E-Heizung 1': {'name': 'heating1_state', 'type': 'gauge'},
    'Status E-Heizung 2': {'name': 'heating2_state', 'type': 'gauge'},
    'Betriebsstunden E1': {'name': 'heating1_operating_hours', 'type': 'gauge', 'strip': len(' h')},
    'Betriebsstunden E2': {'name': 'heating2_operating_hours', 'type': 'gauge', 'strip': len(' h')},
    'Schaltspiele E1': {'name': 'heating1_cycles', 'type': 'counter'},
    'Schaltspiele E2': {'name': 'heating2_cycles', 'type': 'counter'},
    'Gesamt Energie Tage': {'name': 'total_energy_per_day', 'type': 'gauge', 'strip': len(' KWh')},
    'Gesamt Energie Monate': {'name': 'total_energy_per_month', 'type': 'gauge', 'strip': len(' KWh')},
    'Gesamt Energie Jahre': {'name': 'total_energy_per_year', 'type': 'gauge', 'strip': len(' KWh')},
    'Heizen Energie Tage': {'name': 'heating_energy_per_day', 'type': 'gauge', 'strip': len(' KWh')},
    'Heizen Energie Monat': {'name': 'heating_energy_per_month', 'type': 'gauge', 'strip': len(' KWh')},
    'Heizen Energie Jahre': {'name': 'heating_energy_per_year', 'type': 'gauge', 'strip': len(' KWh')},
    'WW Energie Tag': {'name': 'water_energy_per_day', 'type': 'gauge', 'strip': len(' KWh')},
    'WW Energie Monat': {'name': 'water_energy_per_month', 'type': 'gauge', 'strip': len(' KWh')},
    'WW Energie Jahr': {'name': 'water_energy_per_year', 'type': 'gauge', 'strip': len(' KWh')},
    'Kühlen Energie Tage': {'name': 'cooling_energy_per_day', 'type': 'gauge', 'strip': len(' KWh')},
    'Kühlen Energie Monate': {'name': 'cooling_energy_per_month', 'type': 'gauge', 'strip': len(' KWh')},
    'Kühlen Energie Jahre': {'name': 'cooling_energy_per_year', 'type': 'gauge', 'strip': len(' KWh')},
}

def refresh_page(driver):
    if (debug):
        print("Refreshing page...")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "ctl00_DeviceContextControl1_RefreshDeviceDataButton"))
    ).click()
    wait_until_page_loaded(driver)


def login_and_load_fachmann_page(driver):
    wemportal_user = config.WEMPORTAL_CONFIG['username']
    wemportal_password = config.WEMPORTAL_CONFIG['password']
    fachmann_password = "11"

    driver.get("https://www.wemportal.com/Web/")
    if (debug):
        print("Logging in...")
    driver.find_element(By.ID, "ctl00_content_tbxUserName").click()
    driver.find_element(By.ID, "ctl00_content_tbxUserName").send_keys(wemportal_user)
    driver.find_element(By.ID, "ctl00_content_tbxPassword").send_keys(wemportal_password)
    driver.find_element(By.ID, "ctl00_content_btnLogin").click()
    if (debug):
        print("Go to Fachmann info page...")
    driver.find_element(By.CSS_SELECTOR, "#ctl00_RMTopMenu > ul > li.rmItem.rmFirst > a > span").click()
    driver.find_element(By.CSS_SELECTOR, "#ctl00_SubMenuControl1_subMenu > ul > li:nth-child(4) > a > span").click()
    driver.switch_to.frame(0)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ctl00_DialogContent_tbxSecurityCode"))
    ).click()
    driver.find_element(By.ID, "ctl00_DialogContent_tbxSecurityCode").send_keys(fachmann_password)
    driver.find_element(By.ID, "ctl00_DialogContent_BtnSave").click()
    driver.switch_to.default_content()


def wait_until_page_loaded(driver):
    timeout = time.time() + 60*2   # 2 minutes from now
    while True:
        refresh_button_span = driver.find_element(By.ID, "ctl00_DeviceContextControl1_RefreshDeviceDataButton")
        if (debug):
            print("Waiting for page loaded...".format(refresh_button_span.id), end="")
        start = timer()
        try:
            WebDriverWait(driver, 8, poll_frequency=0.2).until(
                EC.staleness_of(refresh_button_span)
            )
            if (debug):
                print("took {}".format(timer() - start))
        except TimeoutException:
            if (debug):
                print("timed out")
            break
        if (time.time() > timeout):
            if (debug):
                print("Data got not loaded within 2 minutes, stopping it!")
            break
    if (debug):
        print("Page loaded")


def parse_page(driver):
    timestamp = driver.find_element(By.ID, "ctl00_DeviceContextControl1_lblDeviceLastDataUpdateInfo").text
    result = {"Zeitstempel": timestamp}
    if (debug):
        print("Parsing page with timestamp {}".format(timestamp))

    map_id_to_name = {}

    for element in driver.find_elements(By.CLASS_NAME, "simpleDataName"):
        stripped_id = element.get_attribute("id")[:-8]
        value = element.text
        map_id_to_name[stripped_id] = value

    for element in driver.find_elements(By.CLASS_NAME, "simpleDataValue"):
        stripped_id = element.get_attribute("id")[:-9]
        value = element.text.replace(",", ".")
        result[map_id_to_name[stripped_id]] = value
    if (debug):
        print("Found {} data points".format(len(result)))

    return result


def parse_value(value, strip=None):
    if value == "Aus" or value == "--":
        return 0
    elif strip is not None:
        return float(value[:-int(strip)])
    else:
        return float(value)

def collect_metrics_from_page(driver):
    result = parse_page(driver)

    data = {}

    for key, value in result.items():
        metric = MAP_METRICS.get(key)
        if metric is not None:
            name = metric["name"]
            t = metric.get("type", "gauge")
            if t == "gauge":
                value = parse_value(value, metric.get("strip"))
                data[name] = value
            if t == "counter":
                value = parse_value(value, metric.get("strip"))
                data[name] = value
            if t == "info":
                data[name] = value
        else:
            if (debug):
                print("No Metric for key '{}': {}".format(key, value))

    return json.dumps(data)

class CustomCollector(object):
    def __init__(self):
        self.lock = Lock()
        self.driver = None
        self.refreshed = False
        self.collections_done = 0
        self.start_driver()

    def collect(self):
        self.lock.acquire()
        try:
            return self.collect_metrics()
        finally:
            self.lock.release()

    def collect_metrics(self, retries_left=3):
        try:
            self.ensure_driver_restarted()
            self.ensure_refreshed()
            metrics = collect_metrics_from_page(self.driver)
            if (debug):
                print("Exporting {} metrics".format(len(metrics)))
            self.collections_done = self.collections_done + 1
            return metrics
        except WebDriverException as e:
            if (debug):
                print("Encountered web driver exception:")
                print(e)
            if retries_left == 0:
                if (debug):
                    print("No retries left, bailing out")
                raise e
            if (debug):
                print("Restarting driver... (retries_left={})".format(retries_left))
            self.restart_driver()
            return self.collect_metrics(retries_left - 1)
        finally:
            self.refreshed = False

    def ensure_driver_restarted(self):
        if self.collections_done <= 200:
            return
        try:
            if (debug):
                print("Restarting driver as {} collections done".format(self.collections_done))
            self.restart_driver()
        finally:
            self.collections_done = 0

    def ensure_refreshed(self):
        if not self.refreshed:
            refresh_page(self.driver)
            self.refreshed = True

    def restart_driver(self):
        self.driver.quit()
        self.start_driver()

    def start_driver(self):
        self.driver = webdriver.Remote(
           command_executor=seleniumGridUrl,
           desired_capabilities={
                    "browserName": "chrome",
                    "browserVersion": "latest"
        })
        login_and_load_fachmann_page(self.driver)
        wait_until_page_loaded(self.driver)
        self.refreshed = True

    def __del__(self):
        if (debug):
            print("Shutting down...")
        try:
            self.driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    customcollector = CustomCollector()
    metrics = customcollector.collect_metrics()
    print(metrics)
