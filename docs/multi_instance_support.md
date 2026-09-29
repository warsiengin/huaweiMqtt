# Supporting Multiple huABus Instances

## Purpose

This guide explains what must change if multiple huABus installations should publish data as separate Home Assistant devices. The recommendations are not implemented by this document; it maps the current behavior to the files that would need updates.

This is useful when monitoring multiple inverters. It does **not** make it safe to open multiple simultaneous Modbus TCP connections to the same inverter. The project README documents Huawei's single-active-Modbus-connection limitation.

## Current behavior

The add-on already has a configurable `mqtt_topic`. The startup script exports it as `HUAWEI_MQTT_TOPIC`, and data and availability messages use that topic. Separate instances can therefore have separate data topics today, for example `inverter-east` and `inverter-west`.

However, MQTT discovery identity is currently shared by all instances:

- Sensor discovery topics are hard-coded as `homeassistant/sensor/huawei_solar/{key}/config`.
- Sensor unique IDs are hard-coded as `huawei_solar_{key}`.
- The device identifier is hard-coded as `huawei_solar_modbus`.
- The status entity has a fixed discovery topic and unique ID.

Because Home Assistant uses discovery topics, unique IDs, and device identifiers to track entities and devices, changing only `mqtt_topic` does not isolate multiple instances. Discovery messages can overwrite one another or cause entities to be associated with the same device.

## Recommended changes and locations

### 1. Add a stable per-instance ID

**Files:**

- `huawei_solar_modbus_mqtt/config.yaml`
- `huawei_solar_modbus_mqtt/bridge/config_manager.py`
- `huawei_solar_modbus_mqtt/run.sh`

Add an option such as `instance_id` to both the add-on `options` and `schema` in `config.yaml`. Read it in `run.sh` and export it, for example as `HUAWEI_INSTANCE_ID`. Add a corresponding `ConfigManager` property and environment-variable fallback in `config_manager.py` if configuration is read outside the add-on startup script.

Each running copy must have a distinct, stable ID, such as `inverter_east` or `inverter_west`. Validate the allowed characters and document that changing this ID later changes the entity/device identity.

Continue to give each instance a distinct `mqtt_topic`; this separates the state and availability messages. For example:

| Instance | Instance ID | MQTT topic |
| --- | --- | --- |
| East inverter | `inverter_east` | `inverter-east` |
| West inverter | `inverter_west` | `inverter-west` |

### 2. Make discovery topics and entity IDs instance-specific

**File:** `huawei_solar_modbus_mqtt/bridge/mqtt_client.py`

Thread the instance ID into discovery publishing, then incorporate it into:

- Sensor discovery topic in `_publish_sensor_configs()` (currently uses the fixed `homeassistant/sensor/huawei_solar/...` prefix).
- Sensor `unique_id` in `_build_sensor_config()` (currently `huawei_solar_{sensor['key']}`).
- The device `identifiers` list in `publish_discovery_configs()` (currently `huawei_solar_modbus`).
- Status discovery topic and `unique_id` in `_publish_status_sensor()`.

Every entity from one instance must use the same instance-specific device identifier, and entities from different instances must have distinct unique IDs. Preserve the existing default identity for a single installation where practical, to avoid needlessly renaming current entities.

### 3. Pass the identity through startup

**Files:**

- `huawei_solar_modbus_mqtt/bridge/main.py`
- `huawei_solar_modbus_mqtt/bridge/mqtt_client.py`

`initialize_bridge()` in `main.py` currently calls `publish_discovery_configs(config.mqtt_topic)`. Update that call and the discovery helper signatures to pass the instance ID as well as the state topic. Alternatively, pass a small immutable identity/config object rather than adding unrelated positional arguments.

The MQTT connection and retained Last Will status topic in `mqtt_client.py` already use `HUAWEI_MQTT_TOPIC`. Ensure the configured topic remains consistent with the topic passed to discovery and publishing.

### 4. Make duplicate Home Assistant add-ons installable

**File:** `huawei_solar_modbus_mqtt/config.yaml`

Home Assistant identifies an add-on by its `slug`; this repository currently defines one fixed slug, `huawei_solar_modbus_mqtt`. If the goal is to install multiple copies from the add-on store, distinct add-on definitions with distinct slugs and names are needed (for example, separately packaged variants or maintained forks). The per-instance ID solves MQTT/Home Assistant identity collisions; it does not by itself create another installable add-on entry.

If using multiple separately packaged copies, keep their configuration schema and supported versions aligned. If instead running multiple containers outside Supervisor, configure each container's environment/options independently.

### 5. Test instance isolation and configuration

**Tests:**

- `tests/test_mqtt_client.py`: verify two instance IDs create different discovery topics, entity unique IDs, device identifiers, and status discovery identities. Also verify the default identity remains compatible if preserving it.
- `tests/test_config_manager.py`: verify instance ID loading, defaulting, and validation.
- `tests/test_run.bats`: if startup-script behavior is covered there, verify that the configured ID is exported to the process environment.
- `tests/test_main.py`: verify that `initialize_bridge()` passes the configured instance identity into discovery publishing.

Prefer assertions against the generated discovery payloads and topics, not just assertions that helper functions were called.

## Retained discovery migration

Changing discovery topics or unique IDs can leave old retained discovery messages and old entities behind in Home Assistant. Before deploying an identity scheme to an existing installation, plan to remove the previous retained discovery configs (or publish the appropriate empty retained payloads to the old discovery topics), then allow Home Assistant to recreate entities with the new IDs. Back up or record entity customizations before doing this migration.

## Safety and operational notes

- Use a different `instance_id` and `mqtt_topic` for every instance.
- Use separate Modbus host addresses when monitoring separate inverters.
- Do not run two instances that both connect directly to the same inverter unless a Modbus proxy or another supported connection-sharing arrangement is in place.
- A separate add-on slug is a packaging/installability requirement; it is not a substitute for unique MQTT discovery identity.

## Current code locations at a glance

| Concern | Current location |
| --- | --- |
| Add-on options, schema, and slug | `huawei_solar_modbus_mqtt/config.yaml` |
| Add-on options exported as environment variables | `huawei_solar_modbus_mqtt/run.sh` |
| Environment-backed config properties | `huawei_solar_modbus_mqtt/bridge/config_manager.py` |
| Startup discovery call | `huawei_solar_modbus_mqtt/bridge/main.py` (`initialize_bridge`) |
| MQTT state and Last Will topics | `huawei_solar_modbus_mqtt/bridge/mqtt_client.py` (`_get_mqtt_client`, `publish_data`, `publish_status`) |
| Discovery topics and identity fields | `huawei_solar_modbus_mqtt/bridge/mqtt_client.py` (`_build_sensor_config`, `_publish_sensor_configs`, `publish_discovery_configs`, `_publish_status_sensor`) |
| MQTT discovery behavior tests | `tests/test_mqtt_client.py` |
| Configuration tests | `tests/test_config_manager.py` |
