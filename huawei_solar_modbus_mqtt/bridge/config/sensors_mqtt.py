# huawei_solar_modbus_mqtt/bridge/config/sensors_mqtt.py

"""Home Assistant MQTT Discovery definitions for numeric and text sensors.

Each entry's ``key`` matches the transformed MQTT payload. Optional readings
use a Jinja ``default`` in ``value_template`` so entities remain available when
hardware or registers are absent.
"""

from typing import Any

# Numerische Sensoren mit unit_of_measurement
# Diese erscheinen in HA als sensor.{entity_id} mit numerischem State
NUMERIC_SENSORS: list[dict[str, Any]] = [
    # === Core Power Values ===
    # Diese 4 Sensoren sind die wichtigsten - immer enabled, keine defaults nötig
    # (werden in transform.py via CRITICAL_DEFAULTS auf 0 gesetzt falls fehlend)
    {
        "name": "Active Power",  # AC-Ausgangsleistung des Inverters
        "key": "power_active",
        "unit_of_measurement": "W",
        "device_class": "power",  # HA erkennt automatisch als Leistung
        "state_class": "measurement",  # Momentanwert (steigt/fällt)
        "icon": "mdi:solar-power",
        "enabled": True,
    },
    {
        "name": "DC Power",  # DC-Eingangsleistung von PV-Strings
        "key": "power_input",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:solar-panel",
        "enabled": True,
    },
    {
        "name": "Grid Power",  # Netzleistung vom Smart Meter (pos=Bezug, neg=Einspeisung)
        "key": "meter_power_active",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:transmission-tower",
        "enabled": False,
    },
    {
        "name": "Battery Power",  # Batterie-Leistung (pos=Laden, neg=Entladen)
        "key": "battery_power",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:battery-charging",
        "value_template": "{{ value_json.battery_power | default(0) }}",
        "enabled": False,
    },
    # === Energy Values ===
    # Energie-Counter für Home Assistant Energy Dashboard
    {
        "name": "Solar Daily Yield",  # Tagesertrag (resettet um Mitternacht)
        "key": "energy_yield_day",
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",  # Counter (mit Filter gegen falsche Resets!)
        "icon": "mdi:solar-power",
        "enabled": True,
    },
    {
        "name": "Solar Total Yield",  # Gesamtertrag seit Installation
        "key": "energy_yield_accumulated",
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",  # Lifetime-Counter (niemals fällt)
        "icon": "mdi:solar-power",
        "enabled": True,
    },
    {
        "name": "Grid Energy Exported",  # Total eingespeiste Energie
        "key": "energy_grid_exported",
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:transmission-tower-export",
        "value_template": "{{ value_json.energy_grid_exported | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Grid Energy Imported",  # Total bezogene Energie
        "key": "energy_grid_accumulated",
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:transmission-tower-import",
        "enabled": False,
    },
    # === Battery ===
    # Alle Batterie-Sensoren haben default(), da optional (keine LUNA2000),
    # und sind standardmäßig deaktiviert.
    {
        "name": "Battery SOC",  # State of Charge in %
        "key": "battery_soc",
        "unit_of_measurement": "%",
        "device_class": "battery",  # HA zeigt Batterie-Icon mit %
        "state_class": "measurement",
        "icon": "mdi:battery",
        "value_template": "{{ value_json.battery_soc | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Battery Charge Today",  # Geladene Energie heute
        "key": "battery_charge_day",
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",  # Resettet täglich
        "icon": "mdi:battery-plus",
        "value_template": "{{ value_json.battery_charge_day | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Battery Discharge Today",  # Entladene Energie heute
        "key": "battery_discharge_day",
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",  # Resettet täglich
        "icon": "mdi:battery-minus",
        "value_template": "{{ value_json.battery_discharge_day | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Battery Total Charge",  # Total geladene Energie (Lifetime)
        "key": "battery_charge_total",
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "value_template": "{{ value_json.battery_charge_total | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Battery Total Discharge",  # Total entladene Energie (Lifetime)
        "key": "battery_discharge_total",
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "value_template": "{{ value_json.battery_discharge_total | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Battery Bus Voltage",  # DC-Bus Spannung
        "key": "battery_bus_voltage",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.battery_bus_voltage | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Battery Bus Current",  # DC-Bus Strom
        "key": "battery_bus_current",
        "unit_of_measurement": "A",
        "device_class": "current",
        "state_class": "measurement",
        "value_template": "{{ value_json.battery_bus_current | default(0) }}",
        "enabled": False,
    },
    # === PV Strings ===
    # Alle PV-Strings sind standardmäßig aktiviert.
    {
        "name": "PV1 Voltage",
        "key": "voltage_PV1",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_PV1 | default(0) }}",  # Nachts = 0
        "enabled": True,
    },
    {
        "name": "PV1 Current",
        "key": "current_PV1",
        "unit_of_measurement": "A",
        "device_class": "current",
        "state_class": "measurement",
        "value_template": "{{ value_json.current_PV1 | default(0) }}",  # Nachts = 0
        "enabled": True,
    },
    {
        "name": "PV2 Voltage",
        "key": "voltage_PV2",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_PV2 | default(0) }}",
        "enabled": True,
    },
    {
        "name": "PV2 Current",
        "key": "current_PV2",
        "unit_of_measurement": "A",
        "device_class": "current",
        "state_class": "measurement",
        "value_template": "{{ value_json.current_PV2 | default(0) }}",
        "enabled": True,
    },
    {
        "name": "PV3 Voltage",
        "key": "voltage_PV3",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_PV3 | default(0) }}",
        "enabled": True,
    },
    {
        "name": "PV3 Current",
        "key": "current_PV3",
        "unit_of_measurement": "A",
        "device_class": "current",
        "state_class": "measurement",
        "value_template": "{{ value_json.current_PV3 | default(0) }}",
        "enabled": True,
    },
    {
        "name": "PV4 Voltage",
        "key": "voltage_PV4",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_PV4 | default(0) }}",
        "enabled": True,
    },
    {
        "name": "PV4 Current",
        "key": "current_PV4",
        "unit_of_measurement": "A",
        "device_class": "current",
        "state_class": "measurement",
        "value_template": "{{ value_json.current_PV4 | default(0) }}",
        "enabled": True,
    },
    # === Inverter Diagnostics ===
    # Diagnose-Werte, entity_category="diagnostic"
    {
        "name": "Inverter Temperature",
        "key": "inverter_temperature",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "value_template": "{{ value_json.inverter_temperature | default(0) }}",
        "enabled": True,
        "entity_category": "diagnostic",  # Unter "Diagnose" gruppiert
    },
    {
        "name": "Inverter Efficiency",  # DC→AC Wirkungsgrad in %
        "key": "inverter_efficiency",
        "unit_of_measurement": "%",
        "state_class": "measurement",
        "icon": "mdi:gauge",
        "value_template": "{{ value_json.inverter_efficiency | default(0) }}",
        "enabled": True,
    },
    {
        "name": "Day Peak Power",  # Maximale Leistung heute
        "key": "power_active_peak_day",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "value_template": "{{ value_json.power_active_peak_day | default(0) }}",
        "enabled": True,
    },
    {
        "name": "Reactive Power",  # Blindleistung in var
        "key": "power_reactive",
        "unit_of_measurement": "var",
        "device_class": "reactive_power",
        "state_class": "measurement",
        "value_template": "{{ value_json.power_reactive | default(0) }}",
        "enabled": True,
    },
    {
        "name": "Power Factor",  # Leistungsfaktor (cos φ)
        "key": "power_factor",
        "unit_of_measurement": "",  # Dimensionslos (-1 bis +1)
        "state_class": "measurement",
        "icon": "mdi:sine-wave",
        "value_template": "{{ value_json.power_factor | default(0) }}",
        "enabled": True,
    },
    {
        "name": "Insulation Resistance",  # Isolationswiderstand (Sicherheit)
        "key": "inverter_insulation_resistance",
        "unit_of_measurement": "MΩ",
        "state_class": "measurement",
        "icon": "mdi:lightning-bolt-circle",
        "value_template": "{{ value_json.inverter_insulation_resistance | default(0) }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    # === Grid Voltages ===
    # 3-Phasen System: Alle 3 Phasen + Line-to-Line
    # 1-Phasen System: Nur Phase A hat Wert, Rest = 0 (default)
    {
        "name": "Grid Voltage Phase A",  # Phase-zu-Neutral
        "key": "voltage_grid_A",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_grid_A | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Grid Voltage Phase B",  # Nur 3-Phasen
        "key": "voltage_grid_B",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_grid_B | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Grid Voltage Phase C",  # Nur 3-Phasen
        "key": "voltage_grid_C",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_grid_C | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Line Voltage A-B",  # Phase-zu-Phase (√3 × Phase-zu-Neutral)
        "key": "voltage_line_AB",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_line_AB | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Line Voltage B-C",
        "key": "voltage_line_BC",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_line_BC | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Line Voltage C-A",
        "key": "voltage_line_CA",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_line_CA | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Grid Frequency",  # 50 Hz (EU) oder 60 Hz (US/JP)
        "key": "frequency_grid",
        "unit_of_measurement": "Hz",
        "device_class": "frequency",
        "state_class": "measurement",
        "value_template": "{{ value_json.frequency_grid | default(50) }}",  # Default 50 Hz
        "enabled": False,
    },
    # === Smart Meter Values ===
    # Alle optional (nur mit SDongleA/DDSU666)
    {
        "name": "Meter Reactive Power",
        "key": "meter_reactive_power",
        "unit_of_measurement": "var",
        "device_class": "reactive_power",
        "state_class": "measurement",
        "value_template": "{{ value_json.meter_reactive_power | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Power Phase A",  # 3-Phasen Details vom Meter
        "key": "power_meter_A",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:transmission-tower",
        "value_template": "{{ value_json.power_meter_A | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Power Phase B",
        "key": "power_meter_B",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:transmission-tower",
        "value_template": "{{ value_json.power_meter_B | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Power Phase C",
        "key": "power_meter_C",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:transmission-tower",
        "value_template": "{{ value_json.power_meter_C | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Line Voltage A-B",  # Spannungen vom Meter
        "key": "voltage_meter_line_AB",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_meter_line_AB | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Line Voltage B-C",
        "key": "voltage_meter_line_BC",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_meter_line_BC | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Line Voltage C-A",
        "key": "voltage_meter_line_CA",
        "unit_of_measurement": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "value_template": "{{ value_json.voltage_meter_line_CA | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Current Phase A",  # Ströme vom Meter
        "key": "current_meter_A",
        "unit_of_measurement": "A",
        "device_class": "current",
        "state_class": "measurement",
        "value_template": "{{ value_json.current_meter_A | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Current Phase B",
        "key": "current_meter_B",
        "unit_of_measurement": "A",
        "device_class": "current",
        "state_class": "measurement",
        "value_template": "{{ value_json.current_meter_B | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Current Phase C",
        "key": "current_meter_C",
        "unit_of_measurement": "A",
        "device_class": "current",
        "state_class": "measurement",
        "value_template": "{{ value_json.current_meter_C | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Meter Frequency",  # Frequenz vom Meter
        "key": "frequency_meter",
        "unit_of_measurement": "Hz",
        "device_class": "frequency",
        "state_class": "measurement",
        "value_template": "{{ value_json.frequency_meter | default(50) }}",
        "enabled": False,
    },
    {
        "name": "Meter Power Factor",  # Leistungsfaktor vom Meter
        "key": "power_factor_meter",
        "unit_of_measurement": "",
        "state_class": "measurement",
        "icon": "mdi:sine-wave",
        "value_template": "{{ value_json.power_factor_meter | default(0) }}",
        "enabled": False,
    },
    # === Static Device Info ===
    {
        "name": "Rated Power",  # Nennleistung (z.B. 10000 W)
        "key": "rated_power",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:gauge",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    # === Battery Limits ===
    {
        "name": "Battery Max Charge Power",
        "key": "battery_max_charge_power",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:battery-plus",
        "value_template": "{{ value_json.battery_max_charge_power | default(0) }}",
        "enabled": False,
    },
    {
        "name": "Battery Max Discharge Power",
        "key": "battery_max_discharge_power",
        "unit_of_measurement": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:battery-minus",
        "value_template": "{{ value_json.battery_max_discharge_power | default(0) }}",
        "enabled": False,
    },
    # === Multi-Module Battery ===
    {
        "name": "Battery Unit 1 SOC",
        "key": "battery_unit1_soc",
        "unit_of_measurement": "%",
        "device_class": "battery",
        "state_class": "measurement",
        "icon": "mdi:battery-70",
        "value_template": "{{ value_json.battery_unit1_soc | default(0) }}",
        "enabled": False,  # Nur bei Multi-Modul
        "entity_category": "diagnostic",
    },
    {
        "name": "Battery Unit 2 SOC",
        "key": "battery_unit2_soc",
        "unit_of_measurement": "%",
        "device_class": "battery",
        "state_class": "measurement",
        "icon": "mdi:battery-70",
        "value_template": "{{ value_json.battery_unit2_soc | default(0) }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
    # === Optimizer Monitoring ===
    {
        "name": "Optimizers Total",
        "key": "optimizers_total",
        "unit_of_measurement": "",
        "state_class": "measurement",
        "icon": "mdi:chip",
        "value_template": "{{ value_json.optimizers_total | default(0) }}",
        "enabled": False,  # Nur bei Optimizer-Setup
        "entity_category": "diagnostic",
    },
    {
        "name": "Optimizers Online",
        "key": "optimizers_online",
        "unit_of_measurement": "",
        "state_class": "measurement",
        "icon": "mdi:check-network",
        "value_template": "{{ value_json.optimizers_online | default(0) }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
    {
        "name": "Failsafe Active Power Limit",
        "key": "failsafe_active_power_limit",
        "unit_of_measurement": "kW",
        "device_class": "power",
        "state_class": "measurement",
        "value_template": "{{ value_json.failsafe_active_power_limit | default(0) }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
    {
        "name": "Fast Power Scheduling",
        "key": "fast_power_scheduling",
        "value_template": "{{ value_json.fast_power_scheduling | default(0) }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
    {
        "name": "Grid Code",
        "key": "grid_code",
        "value_template": "{{ value_json.grid_code | default(0) }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
]

# Text-Sensoren ohne unit_of_measurement
# Für Status-Strings, Modellnamen, etc.
TEXT_SENSORS: list[dict[str, Any]] = [
    {
        "name": "Inverter Status",  # Status-Code als String
        "key": "inverter_status",
        "icon": "mdi:information",
        "value_template": "{{ value_json.inverter_status | default('unknown') }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Battery Status",  # Batterie-Status (0=offline, 1=standby, 2=running, 3=fault)
        "key": "battery_status",
        "icon": "mdi:battery-heart",
        "value_template": "{{ value_json.battery_status | default('unknown') }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
    {
        "name": "Meter Status",  # Meter-Status (0=offline, 1=normal)
        "key": "meter_status",
        "icon": "mdi:meter-electric",
        "value_template": "{{ value_json.meter_status | default('unknown') }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
    {
        "name": "Model Name",  # z.B. "SUN2000-10KTL-M1"
        "key": "model_name",
        "icon": "mdi:information",
        "value_template": "{{ value_json.model_name | default('N/A') }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Serial Number",  # Seriennummer
        "key": "serial_number",
        "icon": "mdi:barcode",
        "value_template": "{{ value_json.serial_number | default('N/A') }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Inverter State 1",  # Bitfeld (siehe Huawei Doku)
        "key": "inverter_state_1",
        "value_template": "{{ value_json.inverter_state_1 | default('') }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Inverter State 2",  # Bitfeld (siehe Huawei Doku)
        "key": "inverter_state_2",
        "value_template": "{{ value_json.inverter_state_2 | default('') }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Inverter Startup Time",  # Timestamp (HA zeigt als Datum/Zeit)
        "key": "startup_time",
        "device_class": "timestamp",
        "value_template": "{{ value_json.startup_time | default(None) }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Inverter Shutdown Time",
        "key": "shutdown_time",
        "device_class": "timestamp",
        "value_template": "{{ value_json.shutdown_time | default(None) }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
    {
        "name": "Inverter System Time",
        "key": "system_time",
        "device_class": "timestamp",
        "value_template": "{{ value_json.system_time | default(None) }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
    # === Alarm Registers ===
    {
        "name": "Alarm 1",
        "key": "alarm1",
        "icon": "mdi:alert-circle",
        "value_template": "{{ value_json.alarm1 | default('0') }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Alarm 2",
        "key": "alarm2",
        "icon": "mdi:alert-circle",
        "value_template": "{{ value_json.alarm2 | default('0') }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Alarm 3",
        "key": "alarm3",
        "icon": "mdi:alert-circle",
        "value_template": "{{ value_json.alarm3 | default('0') }}",
        "enabled": True,
        "entity_category": "diagnostic",
    },
    {
        "name": "Fault Code",
        "key": "fault_code",
        "value_template": "{{ value_json.fault_code | default(0) }}",
        "enabled": False,
        "entity_category": "diagnostic",
    },
]

# By default, enable only the RO/RW sensor entities listed in the supplied
# inverter specification. Other discovered entities remain available to enable
# manually in Home Assistant.
SPECIFICATION_ENABLED_SENSOR_KEYS = frozenset(
    {
        "power_active",
        "power_reactive",
        "power_input",
        "power_active_peak_day",
        "power_factor",
        "inverter_efficiency",
        "voltage_PV1",
        "current_PV1",
        "voltage_PV2",
        "current_PV2",
        "voltage_PV3",
        "current_PV3",
        "voltage_PV4",
        "current_PV4",
        "inverter_status",
        "fault_code",
        "inverter_temperature",
        "inverter_insulation_resistance",
        "energy_yield_day",
        "energy_yield_accumulated",
        "startup_time",
        "shutdown_time",
        "system_time",
        "failsafe_active_power_limit",
        "fast_power_scheduling",
    },
)

for sensor in NUMERIC_SENSORS + TEXT_SENSORS:
    sensor["enabled"] = sensor["key"] in SPECIFICATION_ENABLED_SENSOR_KEYS
