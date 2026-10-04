# Supporting Multiple huABus Instances

## Overview

Multiple instances can monitor separate inverters and publish them as separate Home Assistant devices. The implementation uses both a per-instance MQTT state topic (`mqtt_topic`) and an optional stable discovery identifier (`instance_id`). Changing only `mqtt_topic` is not sufficient: Home Assistant discovery topics and entity/device identifiers must also be unique.

This does **not** make it safe to open multiple simultaneous Modbus TCP connections to the same inverter. Use separate inverter endpoints unless a supported proxy/shared-connection arrangement is in place.

Line numbers below are current at the time of this update and may shift with later edits.

## Configure each instance

In `huawei_solar_modbus_mqtt/config.yaml:25-55`, `instance_id` is an optional add-on setting. It defaults to an empty string to preserve the original single-instance discovery identities. For every additional instance, set a stable, distinct ID using lowercase letters, digits, `_` or `-` (maximum 32 characters). The ID is read/exported by `run.sh:97-101`, loaded from `/data/options.json` or `HUAWEI_INSTANCE_ID` by `bridge/config_manager.py:44-97`, exposed by `ConfigManager.instance_id` at lines 190-193, and validated at lines 233-281. `main()` calls `config.validate()` at `bridge/main.py:808-823` and exits before startup if any setting is invalid.

Set a different `mqtt_topic` and `instance_id` for each running instance. For example:

| Instance   | `instance_id` | `mqtt_topic`       | Modbus host     |
| ---------- | ------------- | ------------------ | --------------- |
| Inverter 1 | `inv_1`       | `huawei`      | `192.168.1.120` |
| Inverter 2 | `inverter_2`  | `huaweiInverter_2` | `192.168.1.121` |

The current add-on defaults are `mqtt_topic: "huawei"` and `instance_id: ""`. Saved Home Assistant options override add-on defaults. `ConfigManager` reads `/data/options.json` when it exists and only uses environment variables when it does not; it does not merge both sources. The startup script exports the same topic as `HUAWEI_MQTT_TOPIC` for MQTT Last Will and disconnect handling.

## What the implementation isolates

`initialize_bridge()` passes `config.mqtt_topic` and `config.instance_id` to `publish_discovery_configs()` at `huawei_solar_modbus_mqtt/bridge/main.py:703-726`.

The discovery publisher in `bridge/mqtt_client.py:147-263` scopes all Home Assistant identity fields:

- Sensor discovery topic: `homeassistant/sensor/{node_id}/{sensor_key}/config` (line 205).
- Sensor `unique_id`: `huawei_solar_{instance_id}_{sensor_key}` when an ID is set (line 157).
- Device identifier: `huawei_solar_modbus_{instance_id}` (line 223).
- Status discovery topic and unique ID use the same instance node/suffix (lines 239-258).
- Sensor state and availability topics continue to use `mqtt_topic` and `{mqtt_topic}/status`.

When `instance_id` is empty, the generated discovery topics, unique IDs, and device identifier preserve the existing single-instance values. For example, `instance_id: inverter_2` and `sensor_key: power_active` produce `homeassistant/sensor/huawei_solar_inverter_2/power_active/config` and unique ID `huawei_solar_inverter_2_power_active`.

## Validation and tests

Regression tests cover options-file/environment loading and instance-ID validation in `tests/test_config_manager.py`; legacy and per-instance discovery topics/payloads in `tests/test_mqtt_client.py`; startup pass-through and rejection of invalid configuration in `tests/test_main.py`; and shell export in `tests/test_run.bats`.

The Python test suite can be run with `uv run pytest`. The BATS startup-script tests require `bats` to be installed and run with `bats tests/test_run.bats`.

## Deployment and migration notes

- Use a distinct stable `instance_id`, `mqtt_topic`, and Modbus host for each instance.
- Changing an existing instance from an empty ID or renaming its ID changes Home Assistant discovery identity. Clear the old retained discovery config messages by publishing empty retained payloads to the previous discovery topics; back up entity customizations first.
- A distinct `instance_id` does not allow two Supervisor add-ons with the same slug. Installing two separate entries through Supervisor requires separate add-on definitions with distinct slugs. Multiple independently configured containers do not have that packaging requirement.
- The current add-on metadata uses `name: huawei_inv_1` and `slug: huawei_inv_1` (`config.yaml:1-3`).
- Never run separate instances that connect directly to the same inverter unless a supported connection-sharing setup is used.

## Exact implementation locations

| Concern                                          | Current location                                                                  |
| ------------------------------------------------ | --------------------------------------------------------------------------------- |
| Add-on topic/instance options and schema         | `huawei_solar_modbus_mqtt/config.yaml:25-55`                                      |
| Add-on environment exports                       | `huawei_solar_modbus_mqtt/run.sh:97-101`                                          |
| Config file/environment loading and validation   | `huawei_solar_modbus_mqtt/bridge/config_manager.py:44-97`, `:186-193`, `:233-281` |
| Startup discovery handoff                        | `huawei_solar_modbus_mqtt/bridge/main.py:703-726`                                 |
| Startup config validation                        | `huawei_solar_modbus_mqtt/bridge/main.py:808-823`                                 |
| Discovery topics and identity payloads           | `huawei_solar_modbus_mqtt/bridge/mqtt_client.py:147-263`                          |
| Config and validation tests                      | `tests/test_config_manager.py:28-110`, `:180-260`, `:301-345`, `:445-539`         |
| Discovery tests                                  | `tests/test_mqtt_client.py:205-255`, `:352-424`                                   |
| Startup validation and discovery call-site tests | `tests/test_main.py:88-120`                                                       |
| Shell export tests                               | `tests/test_run.bats:232-263`                                                     |
