# Oklyn for Home Assistant

Custom integration for Oklyn pool controllers with HACS support.

## Features

- Config flow (UI setup)
- Sensors: pH, ORP/Redox, water temperature, air temperature, salt
- Pump mode select: off / auto / on
- Pump running binary sensor
- Aux 1 mode sensor + Aux 1 active binary sensor
- Aux 2 mode sensor + Aux 2 active binary sensor
- Writable Aux 1 switch only when the endpoint is in simple on/off mode
- Last update timestamps as attributes

## Installation with HACS

1. Create a new GitHub repository and upload the contents of this package.
2. In Home Assistant, open HACS.
3. Add the GitHub repository as a custom repository of type **Integration**.
4. Install the integration.
5. Restart Home Assistant.
6. Go to **Settings -> Devices & Services -> Add Integration**.
7. Search for **Oklyn**.

## Configuration

The config flow asks for:
- API token
- Device ID (defaults to `my`)
- Update interval in seconds

## Auxiliary logic

Oklyn auxiliary outputs can be used either as:
- a simple on/off switch
- a regulation/electrolyzer mode such as `regulredox`

For that reason, this integration always exposes mode and active-state entities.
A writable switch is only exposed for Aux 1 when the returned command is `on` or `off`.

## Repository structure

- `custom_components/oklyn/` Home Assistant integration
- `hacs.json` HACS metadata
- `brand/` icon assets


## Version 3

This package includes the latest compatibility fixes for Home Assistant 2026.x, including the OptionsFlow and DataUpdateCoordinator updates.


## Icon

The integration icon is included at `custom_components/oklyn/brand/icon.png` and `brand/icon.png`.
