# tests/test_register_validation.py

"""Validation tests for register names, mappings, and sensor definitions."""


class TestRegisterNamesValid:
    """Verify register names are recognized by the huawei_solar library."""

    PDF_REGISTER_NAMES = {
        "active_power",
        "reactive_power",
        "input_power",
        "day_active_power_peak",
        "power_factor",
        "efficiency",
        "pv_01_voltage",
        "pv_01_current",
        "pv_02_voltage",
        "pv_02_current",
        "pv_03_voltage",
        "pv_03_current",
        "pv_04_voltage",
        "pv_04_current",
        "device_status",
        "fault_code",
        "internal_temperature",
        "insulation_resistance",
        "daily_yield_energy",
        "accumulated_yield_energy",
        "system_time",
        "startup_time",
        "shutdown_time",
        "failsafe_active_power_limit",
        "fast_power_scheduling",
        "grid_code_value",
    }

    def test_all_essential_registers_exist_in_library(self):
        from huawei_solar.registers import REGISTERS

        from huawei_solar_modbus_mqtt.bridge.config.registers import ESSENTIAL_REGISTERS, SPECIFICATION_REGISTERS

        missing = [n for n in ESSENTIAL_REGISTERS if n not in REGISTERS and n not in SPECIFICATION_REGISTERS]
        assert not missing, f"Not in library: {missing}"

    def test_every_pdf_ro_rw_register_is_polled(self):
        from huawei_solar_modbus_mqtt.bridge.config.registers import ESSENTIAL_REGISTERS

        assert self.PDF_REGISTER_NAMES <= set(ESSENTIAL_REGISTERS)

    def test_specification_registers_have_addresses_and_wire_types(self):
        from huawei_solar_modbus_mqtt.bridge.config.registers import SPECIFICATION_REGISTERS

        assert {
            name: (register.address, register.format, register.gain)
            for name, register in SPECIFICATION_REGISTERS.items()
        } == {
            "failsafe_active_power_limit": (42405, "i", 1000),
            "fast_power_scheduling": (45086, "H", 1),
            "grid_code_value": (42000, "H", 1),
        }

    def test_no_underscore_soc_register_names(self):
        from huawei_solar_modbus_mqtt.bridge.config.registers import ESSENTIAL_REGISTERS

        invalid = [r for r in ESSENTIAL_REGISTERS if r.endswith("_soc")]
        assert not invalid, f"Use _state_of_capacity: {invalid}"


class TestRegisterMappingsConsistent:
    """Verify REGISTER_MAPPING keys match ESSENTIAL_REGISTERS."""

    def test_mapping_keys_match_essential_registers(self):
        from huawei_solar_modbus_mqtt.bridge.config.mappings import REGISTER_MAPPING
        from huawei_solar_modbus_mqtt.bridge.config.registers import ESSENTIAL_REGISTERS

        reg_set = set(ESSENTIAL_REGISTERS)
        map_set = set(REGISTER_MAPPING.keys())
        assert reg_set == map_set, f"Mismatch: {reg_set ^ map_set}"


class TestSensorsConsistent:
    """Verify sensor definitions match REGISTER_MAPPING values."""

    def test_sensor_keys_match_mapping_values(self):
        from huawei_solar_modbus_mqtt.bridge.config.mappings import REGISTER_MAPPING
        from huawei_solar_modbus_mqtt.bridge.config.sensors_mqtt import NUMERIC_SENSORS, TEXT_SENSORS

        sensor_keys = {s["key"] for s in NUMERIC_SENSORS + TEXT_SENSORS if s.get("key")}
        mqtt_keys = set(REGISTER_MAPPING.values())
        unmatched = sensor_keys - mqtt_keys
        assert unmatched.issubset({"status"}), f"Unmatched: {unmatched}"

    def test_battery_unit3_sensor_removed(self):
        from huawei_solar_modbus_mqtt.bridge.config.sensors_mqtt import NUMERIC_SENSORS, TEXT_SENSORS

        all_keys = {s["key"] for s in NUMERIC_SENSORS + TEXT_SENSORS if s.get("key")}
        assert "battery_unit3_soc" not in all_keys

    def test_battery_unit1_and_unit2_sensors_present(self):
        from huawei_solar_modbus_mqtt.bridge.config.sensors_mqtt import NUMERIC_SENSORS, TEXT_SENSORS

        all_keys = {s["key"] for s in NUMERIC_SENSORS + TEXT_SENSORS if s.get("key")}
        assert "battery_unit1_soc" in all_keys
        assert "battery_unit2_soc" in all_keys

    def test_only_specification_ro_rw_sensors_are_enabled_by_default(self):
        from huawei_solar_modbus_mqtt.bridge.config.sensors_mqtt import (
            NUMERIC_SENSORS,
            SPECIFICATION_ENABLED_SENSOR_KEYS,
            TEXT_SENSORS,
        )

        sensors = NUMERIC_SENSORS + TEXT_SENSORS
        enabled_keys = {sensor["key"] for sensor in sensors if sensor["enabled"]}
        expected_keys = {
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
        }

        assert SPECIFICATION_ENABLED_SENSOR_KEYS == expected_keys
        assert enabled_keys == expected_keys
        assert all(sensor["enabled"] is False for sensor in sensors if sensor["key"] not in enabled_keys)
        assert all(sensor["enabled"] is False for sensor in sensors if sensor["name"].startswith(("Grid ", "Meter ")))
