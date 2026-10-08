#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2026-      MIWE77
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import time
import requests
import requests.adapters
from typing import Callable, Optional
from urllib3.util import Retry

from lib.model.smartplugin import SmartPlugin

from .webif import WebInterface


class OpenMeteo(SmartPlugin):
    """
    Main class of the Plugin. Fetches weather data from the Open-Meteo API.
    No API key required for non-commercial use.
    """

    PLUGIN_VERSION = '1.0.0'

    _base_url = 'https://api.open-meteo.com/v1/forecast'

    _valid_current_fields = frozenset({
        # Temperature & Humidity
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "apparent_temperature",
        # Pressure
        "pressure_msl",
        "surface_pressure",
        # Clouds & Atmospheric
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "cloud_cover_high",
        "visibility",
        # Wind & Gusts
        "wind_speed_10m",
        "wind_speed_80m",
        "wind_speed_120m",
        "wind_speed_180m",
        "wind_direction_10m",
        "wind_direction_80m",
        "wind_direction_120m",
        "wind_direction_180m",
        "wind_gusts_10m",
        # Precipitation & Weather Code
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        # Solar & Daylight
        "is_day",
        # Soil Conditions
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_temperature_18cm",
        "soil_temperature_54cm",
        "soil_moisture_0_to_1cm",
        "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm",
        "soil_moisture_9_to_27cm",
        "soil_moisture_27_to_81cm",
        "moonrise",
        "moonset",
        "moon_phase",
    })

    _valid_hourly_fields = frozenset({
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "apparent_temperature",
        "pressure_msl",
        "surface_pressure",
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "cloud_cover_high",
        "wind_speed_10m",
        "wind_speed_80m",
        "wind_speed_120m",
        "wind_speed_180m",
        "wind_direction_10m",
        "wind_direction_80m",
        "wind_direction_120m",
        "wind_direction_180m",
        "wind_gusts_10m",
        "shortwave_radiation",
        "direct_radiation",
        "direct_normal_irradiance",
        "diffuse_radiation",
        "global_tilted_irradiance",
        "vapour_pressure_deficit",
        "cape",
        "evapotranspiration",
        "et0_fao_evapotranspiration",
        "precipitation",
        "snowfall",
        "precipitation_probability",
        "rain",
        "showers",
        "weather_code",
        "snow_depth",
        "freezing_level_height",
        "visibility",
        "soil_temperature_0cm",
        "soil_temperature_6cm",
        "soil_temperature_18cm",
        "soil_temperature_54cm",
        "soil_moisture_0_to_1cm",
        "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm",
        "soil_moisture_9_to_27cm",
        "soil_moisture_27_to_81cm",
        "is_day",
        "uv_index",
        "uv_index_clear_sky",
        "wet_bulb_temperature"
    })

    _valid_daily_fields = frozenset({
        "apparent_temperature_max",
        "apparent_temperature_mean",
        "apparent_temperature_min",
        "daylight_duration",
        "et0_fao_evapotranspiration",
        "precipitation_hours",
        "precipitation_probability_max",
        "precipitation_probability_mean",
        "precipitation_probability_min",
        "precipitation_sum",
        "rain_sum",
        "shortwave_radiation_sum",
        "showers_sum",
        "snowfall_sum",
        "sunrise",
        "sunset",
        "sunshine_duration",
        "temperature_2m_max",
        "temperature_2m_mean",
        "temperature_2m_min",
        "uv_index_clear_sky_max",
        "uv_index_max",
        "weather_code",
        "wind_direction_10m_dominant",
        "wind_gusts_10m_max",
        "wind_speed_10m_max",
        "moonrise",
        "moonset",
        "moon_phase",
        
    })

    _valid_15m_fields = frozenset({
        "apparent_temperature",
        "cape",
        "dew_point_2m",
        "diffuse_radiation",
        "direct_normal_irradiance",
        "direct_radiation",
        "freezing_level_height",
        "global_tilted_irradiance",
        "global_tilted_irradiance_instant",
        "lightning_potential",
        "precipitation",
        "rain",
        "relative_humidity_2m",
        "shortwave_radiation",
        "showers",
        "snowfall",
        "snowfall_height",
        "sunshine_duration",
        "temperature_2m",
        "visibility",
        "weather_code",
        "wind_direction_10m",
        "wind_direction_80m",
        "wind_gusts_10m",
        "wind_speed_10m",
        "wind_speed_80m",
    })

    _valid_api_params = frozenset({
        "apikey",               # commercial API key for reserved resources
        "cell_selection",       # grid-cell selection: land, sea, nearest
        "current",              # current weather variables to return
        "daily",                # daily weather variable aggregations
        "elevation",            # manual elevation for statistical downscaling
        "end_date",             # end of date interval (yyyy-mm-dd)
        "end_hour",             # end of hourly interval (ISO8601)
        "end_minutely_15",      # end of 15-min interval (ISO8601)
        "forecast_days",        # number of forecast days (default 7, max 16)
        "forecast_hours",       # number of forecast hours
        "forecast_minutely_15", # number of forecast 15-min steps
        "hourly",               # hourly weather variables to return
        "latitude",             # WGS84 latitude (required)
        "longitude",            # WGS84 longitude (required)
        "models",               # weather model selection (default auto)
        "past_days",            # number of past days to include (0-92)
        "past_hours",           # number of past hours to include
        "past_minutely_15",     # number of past 15-min steps to include
        "precipitation_unit",   # precipitation unit: mm or inch
        "start_date",           # start of date interval (yyyy-mm-dd)
        "start_hour",           # start of hourly interval (ISO8601)
        "start_minutely_15",    # start of 15-min interval (ISO8601)
        "temperature_unit",     # temperature unit: celsius or fahrenheit
        "timeformat",           # timestamp format: iso8601 or unixtime
        "timezone",             # timezone (default GMT, or auto)
        "wind_speed_unit",      # wind speed unit: kmh, ms, mph, kn
    })

    _default_current_fields = frozenset({
        "apparent_temperature",
        "relative_humidity_2m",
        "surface_pressure",
        "temperature_2m",
        "weather_code",
        "wind_gusts_10m",
        "wind_speed_10m",
    })

    _default_hourly_fields = frozenset({
        "apparent_temperature",
        "cloud_cover",
        "precipitation",
        "precipitation_probability",
        "relative_humidity_2m",
        "surface_pressure",
        "temperature_2m",
        "weather_code",
        "wind_gusts_10m",
        "wind_speed_10m",
    })

    _default_daily_fields = frozenset({
        "apparent_temperature_max",
        "apparent_temperature_min",
        "precipitation_probability_max",
        "precipitation_sum",
        "sunrise",
        "sunset",
        "temperature_2m_max",
        "temperature_2m_min",
        "uv_index_max",
        "weather_code",
        "wind_direction_10m_dominant",
        "wind_gusts_10m_max",
        "wind_speed_10m_max",
    })

    _wmo_de = {
        0:  'Klarer Himmel',
        1:  'Meistens sonnig',
        2:  'Teilweise bewölkt',
        3:  'Bewölkt',
        45: 'Nebel',
        48: 'Reifnebel',
        51: 'Leichter Nieselregen',
        53: 'Mäßiger Nieselregen',
        55: 'Dichter Nieselregen',
        56: 'Unterkuhlter leichter Nieselregen',
        57: 'Unterkuhlter dichter Nieselregen',
        61: 'Leichter Regen',
        63: 'Mäßiger Regen',
        65: 'Starker Regen',
        66: 'Leichter Eisregen',
        67: 'Starker Eisregen',
        71: 'Leichter Schneefall',
        73: 'Mäßiger Schneefall',
        75: 'Starker Schneefall',
        77: 'Schneegriesel',
        80: 'Leichte Regenschauer',
        81: 'Mäßige Regenschauer',
        82: 'Heftige Regenschauer',
        85: 'Leichte Schneeschauer',
        86: 'Starke Schneeschauer',
        95: 'Gewitter',
        96: 'Gewitter mit leichtem Hagel',
        99: 'Gewitter mit starkem Hagel',
    }

    _wmo_en = {
        0:  'Clear sky',
        1:  'Mainly clear',
        2:  'Partly cloudy',
        3:  'Overcast',
        45: 'Fog',
        48: 'Depositing rime fog',
        51: 'Slight drizzle',
        53: 'Moderate drizzle',
        55: 'Dense drizzle',
        56: 'Freezing drizzle, slight',
        57: 'Freezing drizzle, dense',
        61: 'Slight rain',
        63: 'Moderate rain',
        65: 'Heavy rain',
        66: 'Freezing rain, slight',
        67: 'Freezing rain, heavy',
        71: 'Slight snow fall',
        73: 'Moderate snow fall',
        75: 'Heavy snow fall',
        77: 'Snow grains',
        80: 'Slight rain showers',
        81: 'Moderate rain showers',
        82: 'Violent rain showers',
        85: 'Slight snow showers',
        86: 'Heavy snow showers',
        95: 'Thunderstorm',
        96: 'Thunderstorm with slight hail',
        99: 'Thunderstorm with heavy hail',
    }

    def __init__(self, sh=None, **kwargs):
        """
        Initializes the plugin.

        Plugins have to use the new way of getting parameter values:
        use the SmartPlugin method get_parameter_value(parameter_name).
        """
        super().__init__()

        lat = self.get_parameter_value('latitude')
        lon = self.get_parameter_value('longitude')
        if lat and lon:
            self._lat = lat
            self._lon = lon
        else:
            self.logger.debug('__init__: latitude/longitude not set, using shng system values.')
            self._lat = self.get_sh().lat
            self._lon = self.get_sh().lon

        self._cycle = self.get_parameter_value('cycle')
        self._timezone = self.get_parameter_value('timezone')
        self._temp_unit = self.get_parameter_value('temperature_unit')
        self._wind_unit = self.get_parameter_value('wind_speed_unit')
        self._wmo_default = self.get_parameter_value('lang') or ''

        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'smarthomeNG-OpenMeteo/1.0'
        })

        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        self._session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

        self._data = {}
        self._max_day = 0
        self._max_past_day = 0
        self._need_current_fields = set()
        self._need_hourly_fields = set()
        self._need_daily_fields = set()
        self._wmo_code_matchstrings = set()

        self._valid_fields_by_section = {
            'current': self._valid_current_fields,
            'hourly': self._valid_hourly_fields,
            'daily': self._valid_daily_fields,
        }

        self.init_webinterface(WebInterface)

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'run()'}))

        self.scheduler_add(
            'poll',
            self._update_loop,
            prio=5,
            cycle=self._cycle,
            offset=2
        )

        self.alive = True

        if self._pause_item:
            self._pause_item(False, self.get_fullname())

    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'stop()'}))
        self.alive = False

        self.scheduler_remove_all()
        self._session.close()

        if self._pause_item:
            self._pause_item(True, self.get_fullname())

    def parse_item(self, item) -> Optional[Callable]:
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        Registers items via SmartPlugin.add_item() with matchstring as mapping
        and plugin-specific data in config_data_dict.

        :param item: The item to process.
        """
        path = item.property.path

        # Special handling for pause item
        if path == self._pause_item_path:
            self.logger.debug("pause item %s registered", path)
            self._pause_item = item
            self.add_item(item, updating=True)
            return self.update_item

        # Retrieve matchstring attribute (tries 'om_matchstring', falls back to 'om_matchstring_')
        conf = item.conf
        om_ms = self.get_iattr_value(conf, 'om_matchstring') or self.get_iattr_value(conf, 'om_matchstring_')

        if not om_ms:
            return None

        self.logger.debug("parse item: %s", item.property.path)

        if self._register_field_demand(om_ms):
            self.add_item(item, mapping=om_ms, updating=True)
            self.logger.debug("Register item %s for plugin with mapping %s", path, om_ms)
            return # self.update_item

        # self.logger.info("om_matchstring=%s not valid. Item %s will be ignored.", om_ms, path)
        return None

    def parse_logic(self, logic):
        """
        Default plugin parse_logic method
        """
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Item has been updated.

        This method is called, if the value of an item has been updated by SmartHomeNG.
        It should write the changed value out to the device (hardware/interface) that
        is managed by this plugin.

        To prevent a loop, the changed value should only be written to the device, if
        the plugin is running and the value was changed outside of this plugin(-instance).

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        if self.alive and caller != self.get_fullname():
            self.logger.info(
                f"update_item: '{item.property.path}' has been changed outside this plugin "
                f"by caller '{self.callerinfo(caller, source)}'"
            )

    def _update_loop(self):
        """
        Polls the Open-Meteo API and updates all registered items.
        Called by the scheduler which is set within run() method.
        """
        if not self.alive:
            return

        self._fetch_data()
        self._update_items()

    def _register_field_demand(self, matchstring: str) -> bool:
        """
        Extracts the API field demands from a matchstring and marks
        the corresponding data sections as needed.
        """
        if not matchstring:
            return False

        parts = matchstring.split('/', 2)
        section = parts[0]
        valid_fields = self._valid_fields_by_section.get(section)
        if valid_fields is None:
            return False

        match section:
            case 'current':
                if len(parts) <= 1:
                    return False

                field = parts[1]

                if field and field != 'time' and field in valid_fields:
                    self._need_current_fields.add(field)
                    if field == 'weather_code':
                        self._wmo_code_matchstrings.add(matchstring)
                    return True
                else:
                    self.logger.debug(f"{field=} not in valid fields for 'current'")

            case 'hourly':
                if len(parts) != 3:
                    return False

                hour_idx = self._safe_int(parts[1])
                past_hours = (-hour_idx + 23) // 24 if hour_idx is not None and hour_idx < 0 else 0
                if past_hours > self._max_past_day:
                    self._max_past_day = past_hours

                field = parts[2]
                if field and field != 'time' and field in valid_fields:
                    self._need_hourly_fields.add(field)
                    if field == 'weather_code':
                        self._wmo_code_matchstrings.add(matchstring)
                    return True
                else:
                    self.logger.debug(f"{field=} not in valid fields for 'hourly'")

            case 'daily':
                if len(parts) != 3:
                    return False

                day_idx = self._safe_int(parts[1])
                if day_idx is not None:
                    if day_idx > self._max_day:
                        self._max_day = day_idx
                    if day_idx < 0 and -day_idx > self._max_past_day:
                        self._max_past_day = -day_idx

                field = parts[2]
                if field and field != 'time' and field in valid_fields:
                    self._need_daily_fields.add(field)
                    if field == 'weather_code':
                        self._wmo_code_matchstrings.add(matchstring)
                    return True
                else:
                    self.logger.debug(f"{field=} not in valid fields for 'daily'")

        return False

    def _build_params(self) -> dict:
        """
        Builds the Open-Meteo API request parameters dict based on registered item demands.
        """
        forecast_days = max(1, self._max_day + 1)
        past_days = self._max_past_day

        params = {
            'latitude': self._lat,
            'longitude': self._lon,
            'timezone': self._timezone,
            'temperature_unit': self._temp_unit,
            'wind_speed_unit': self._wind_unit,
            'precipitation_unit': 'mm',
            'forecast_days': forecast_days,
        }

        if past_days:
            params['past_days'] = past_days

        current_fields_raw = (
            self._need_current_fields if self._need_current_fields
            else self._default_current_fields
        )

        current_fields = current_fields_raw & self._valid_current_fields
        dropped_c = current_fields_raw - self._valid_current_fields

        if dropped_c:
            self.logger.warning(f'current: drop invalid fields {sorted(dropped_c)}')
        if current_fields:
            params['current'] = ','.join(sorted(current_fields))

        hourly_fields_raw = (
            self._need_hourly_fields if self._need_hourly_fields
            else self._default_hourly_fields
        )

        hourly_fields = hourly_fields_raw & self._valid_hourly_fields
        dropped_h = hourly_fields_raw - self._valid_hourly_fields

        if dropped_h:
            self.logger.warning(f'hourly: drop invalid fields {sorted(dropped_h)}')
        params['hourly'] = ','.join(sorted(hourly_fields))

        daily_fields_raw = (
            self._need_daily_fields if self._need_daily_fields
            else self._default_daily_fields
        )

        daily_fields = daily_fields_raw & self._valid_daily_fields
        dropped_d = daily_fields_raw - self._valid_daily_fields

        if dropped_d:
            self.logger.warning(f'daily: drop invalid fields {sorted(dropped_d)}')
        params['daily'] = ','.join(sorted(daily_fields))

        return params

    def _fetch_data(self):
        """
        Requests the weather information at api.open-meteo.com
        """
        self._data = {}

        params = self._build_params()
        self.logger.debug(f'Requesting with params: {params}')

        try:
            response = self._session.get(self._base_url, params=params, timeout=30)
        except Exception as e:
            self.logger.warning(f'Request failed: {e}')
            return

        if response.ok:
            self._data = response.json()
            self.last_fetch_ts = int(time.time())
            self.logger.debug(f'Received data for {self.get_instance_name()}')
        else:
            self.logger.error(
                f'Open-Meteo API returned status {response.status_code}: {response.text}'
            )

    def _get_value(self, matchstring):
        """
        Uses string matchstring as a path to navigate to the requested value
        in the fetched API data.

        Supported paths:
            current/<field>
            hourly/<index>/<field>      # positive: hours ahead, negative: hours ago
            hourly_time/<index>
            daily/<index>/<field>       # positive: days ahead, negative: days ago
            daily_time/<index>
            location/<field>
        """
        parts = matchstring.split('/')
        if not parts:
            return None

        section = parts[0]

        if section == 'current':
            if 'current' not in self._data or len(parts) < 2:
                return None
            field = parts[1]
            return self._data['current'].get(field)

        elif section == 'hourly':
            if 'hourly' not in self._data or len(parts) < 3:
                return None
            idx = self._safe_int(parts[1])
            if idx is None:
                return None
            field = parts[2]
            if field not in self._data['hourly']:
                return None
            values = self._data['hourly'][field]
            n = len(values)
            return values[idx] if -n <= idx < n else None

        elif section == 'hourly_time':
            if 'hourly' not in self._data or len(parts) < 2:
                return None
            idx = self._safe_int(parts[1])
            if idx is None:
                return None
            times = self._data['hourly'].get('time', [])
            n = len(times)
            return times[idx] if -n <= idx < n else None

        elif section == 'daily':
            if 'daily' not in self._data or len(parts) < 3:
                return None
            idx = self._safe_int(parts[1])
            if idx is None:
                return None
            field = parts[2]
            if field not in self._data['daily']:
                return None
            values = self._data['daily'][field]
            n = len(values)
            return values[idx] if -n <= idx < n else None

        elif section == 'daily_time':
            if 'daily' not in self._data or len(parts) < 2:
                return None
            idx = self._safe_int(parts[1])
            if idx is None:
                return None
            times = self._data['daily'].get('time', [])
            n = len(times)
            return times[idx] if -n <= idx < n else None

        elif section == 'location':
            field = parts[1] if len(parts) > 1 else ''
            return self._data.get(field)

        else:
            return self._data.get(section)

    def _safe_int(self, val):
        """
        Safely converts a value to int.

        :param val: value to convert
        :return: int or None
        """
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    def _get_wmo_text(self, code, lang):
        """
        Converts a WMO weather code to a text description.

        :param code: WMO weather code (int)
        :param lang: 'de' or 'en'
        :return: text description
        """
        try:
            code = int(code)
        except (TypeError, ValueError):
            return f'Unknown ({code})'
        table = self._wmo_de if lang == 'de' else self._wmo_en
        return table.get(code, f'Unknown ({code})')

    def _update_items(self):
        """
        Updates all registered items with the data from the last API response.

        Iterates over unique matchstrings (mappings), resolves the value from the
        JSON once per matchstring, and writes it to every item that shares this
        matchstring -- same pattern as the piratewthr plugin.
        """
        for matchstring in self.get_mappings():
            items = self.get_items_for_mapping(matchstring)
            if not items:
                continue

            try:
                value = self._get_value(matchstring)
            except Exception as e:
                self.logger.error(f'error resolving "{matchstring}": {e}')
                continue

            if value is None:
                self.logger.debug(f'No data for "{matchstring}", skipping item update')
                continue

            for item in items:
                if self._wmo_default and matchstring in self._wmo_code_matchstrings and isinstance(value, int):
                    value = self._get_wmo_text(value, self._wmo_default)

                item(value, self.get_fullname(), matchstring)
                self.logger.debug(f'{item.property.path} = {value} ({matchstring})')

    def force_update(self):
        """
        Can be called from a script to trigger an immediate data refresh.
        """
        if self.alive:
            self._fetch_data()
            self._update_items()
