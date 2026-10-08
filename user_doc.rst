.. index:: Plugins; openmeteo
.. index:: openmeteo


===============================
openmeteo
===============================


.. image:: webif/static/img/plugin_logo.png
   :alt: openmeteo logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Das Plugin ``openmeteo`` fragt Wetterdaten von der `Open-Meteo API <https://open-meteo.com/>`_ ab.
Die API ist kostenlos und benoetigt keinen API-Key für den nicht-kommerziellen Gebrauch
(max. 10 Calls pro Stunde).

Unterstützt werden aktuelle Wetterdaten, eine Stundenvorhersage,
15-Minuten-Daten (nur Zentraleuropa und Nordamerika) und eine Tagesvorhersage
für bis zu 16 Tage.


Anforderungen
=============

SmartHomeNG
-----------

SmartHomeNG Version **1.10** oder höher.

Erforderliche Python Module
---------------------------

* ``requests`` -- für die HTTP-Anfragen an die API

Notwendige Software
-------------------

Keine zusätzliche Software erforderlich. Eine Internetverbindung ist nötig,
um die Wetterdaten abzurufen.


Konfiguration
=============

Plugin Parameter
----------------

.. list-table::
   :header-rows: 1
   :widths: 20 40

   * - Parameter
     - Beschreibung
   * - ``latitude`` (``float``, mandatory)
     - Breitengrad des Ortes, z.B. ``52.52``
   * - ``longitude`` (``float``, mandatory)
     - Längengrad des Ortes, z.B. ``13.41``
   * - ``cycle`` (``int``, default: ``900``)
     - Intervall in Sekunden zwischen zwei API-Abfragen.
       Der kostenlose Account erlaubt max. 10 Calls/Stunde,
       daher sollte der Wert nicht unter 360 liegen.
   * - ``forecast_days`` (``int``, default: ``7``)
     - Anzahl der Vorhersage-Tage (1–16).
   * - ``timezone`` (``str``, default: ``Europe/Berlin``)
     - Zeitzone für die Vorhersagedaten.
       ``auto`` verwendet die Zeitzone der Koordinaten.
   * - ``temperature_unit`` (``str``, default: ``celsius``)
     - Temperatureinheit: ``celsius`` oder ``fahrenheit``.
   * - ``wind_speed_unit`` (``str``, default: ``kmh``)
     - Windeinheit: ``kmh``, ``mph``, ``ms`` oder ``knot``.
   * - ``pause_item`` (``str``, default: ``''``)
     - Item-Pfad zum Starten/Stoppen des Plugins.


Item Attribute
--------------

.. list-table::
   :header-rows: 1
   :widths: 20 40

   * - Attribut
     - Beschreibung
   * - ``om_matchstring`` (``str``)
     - Statische Pfadangabe im Open-Meteo JSON-Antwort.
       Beispiel: ``current/temperature_2m``.
   * - ``om_matchstring_`` (``str``)
     - Matchstring mit Template-Variablen für dynamische Pfade in Structs
       (wird von ``om_matchstring`` überschrieben).
       Beispiel: ``"daily/{..:_day}/temperature_2m_max"``.
   * - ``om_wmo_text`` (``str``, valid: ``''``, ``de``, ``en``)
     - Wenn auf ``de`` oder ``en`` gesetzt, wird der numerische
       WMO weather_code in einen Text umgewandelt
       (nur bei Items, deren matchstring auf ``_code`` endet).


Beispielkonfiguration
---------------------

Plugin in ``etc/plugin.d/openmeteo.yaml``::

    plugin: openmeteo
    openmeteo:
        latitude: 52.52
        longitude: 13.41
        cycle: 900
        forecast_days: 7
        timezone: Europe/Berlin
        temperature_unit: celsius
        wind_speed_unit: kmh

Items in ``items.yaml`` -- aktuelle Wetterdaten::

    weather:
        current:
            struct: openmeteo.current

Items mit Tages- und Stundenvorhersage (Struct-Templates)::

    weather:
        current:
            struct: openmeteo.current
        daily:
            struct: openmeteo.daily
        hourly:
            struct: openmeteo.hourly

Individuelle Items mit manuellem matchstring::

    weather:
        temp_heute:
            type: num
            om_matchstring: current/temperature_2m
        weather_text_heute:
            type: str
            om_matchstring: current/weather_code
            om_wmo_text: de
        max_temp_morgen:
            type: num
            om_matchstring: daily/1/temperature_2m_max
        niederschlagswahrscheinlichkeit_stunde_3:
            type: num
            om_matchstring: hourly/3/precipitation_probability
        solar_strahlung_stunde_5:
            type: num
            om_matchstring: hourly/5/shortwave_radiation
        bodentemperatur:
            type: num
            om_matchstring: hourly/0/soil_temperature_0cm


Funktionen
----------

``force_update()``
~~~~~~~~~~~~~~~~~~

Loest einen sofortigen Abruf der Wetterdaten von der API aus und
aktualisiert alle Items. Kann aus einem Script oder einer Logik
aufgerufen werden::

    sh.openmeteo.force_update()


Alle verfügbaren Wetter-Felder
==============================

Die Open-Meteo API liefert Daten in den Kategorien
**current** (aktuell), **hourly** (stündlich, Index 0–N),
**daily** (täglich, Index 0 = heute, 1 = morgen, usw.) und
**location** (Standortinfo).

Alle Felder koennen als ``om_matchstring`` verwendet werden.


current (aktuelle Wetterdaten)
------------------------------

.. note:: Aktuelle Bedingungen basieren auf 15-Minuten-Daten.
          Jeder Wettervariablen, die in hourly verfügbar ist,
          ist ebenfalls als current verfügbar.

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Temperatur
     - ``current/temperature_2m``
     - Lufttemperatur in 2m Höhe (°C/°F)
   * - Rel. Luftfeuchtigkeit
     - ``current/relative_humidity_2m``
     - In 2m Höhe (%)
   * - Taupunkt
     - ``current/dew_point_2m``
     - Taupunkttemperatur in 2m Höhe (°C/°F)
   * - Wahrgenommene Temperatur
     - ``current/apparent_temperature``
     - Empfindungstemperatur (°C/°F)
   * - Tag/Nacht
     - ``current/is_day``
     - 1 = Tag, 0 = Nacht
   * - Niederschlag
     - ``current/precipitation``
     - Gesamtniederschlag (mm/inch)
   * - Regen
     - ``current/rain``
     - Regen aus großskaligen Systemen (mm)
   * - Schauer
     - ``current/showers``
     - Konvektiver Niederschlag (mm)
   * - Schneefall
     - ``current/snowfall``
     - Schneemenge in cm
   * - Schneehoehe
     - ``current/snow_depth``
     - Schnee auf dem Boden (m)
   * - Wettercode
     - ``current/weather_code``
     - WMO Weather Interpretation Code
   * - Bewölkung gesamt
     - ``current/cloud_cover``
     - Gesamtbewölkung (%)
   * - Bewölkung tief
     - ``current/cloud_cover_low``
     - Tieftauben und Nebel bis 3 km (%)
   * - Bewölkung mittlere Höhe
     - ``current/cloud_cover_mid``
     - Wolken 3 bis 8 km Höhe (%)
   * - Bewölkung hoch
     - ``current/cloud_cover_high``
     - Hochwolken ab 8 km Höhe (%)
   * - Meereshöhen-Druck
     - ``current/pressure_msl``
     - Auf Meereshoehe reduziert (hPa)
   * - Oberflächendruck
     - ``current/surface_pressure``
     - Druck an der Oberfläche (hPa)
   * - Windgeschwindigkeit
     - ``current/wind_speed_10m``
     - In 10m Höhe (km/h, mph, m/s, knot)
   * - Windgeschwindigkeit 80m
     - ``current/wind_speed_80m``
     - In 80m Höhe
   * - Windgeschwindigkeit 120m
     - ``current/wind_speed_120m``
     - In 120m Höhe
   * - Windgeschwindigkeit 180m
     - ``current/wind_speed_180m``
     - In 180m Höhe
   * - Windrichtung 10m
     - ``current/wind_direction_10m``
     - Meteorologisch in Grad (°)
   * - Windrichtung 80m
     - ``current/wind_direction_80m``
     - In 80m Höhe (°)
   * - Windrichtung 120m
     - ``current/wind_direction_120m``
     - In 120m Höhe (°)
   * - Windrichtung 180m
     - ``current/wind_direction_180m``
     - In 180m Höhe (°)
   * - Windböen 10m
     - ``current/wind_gusts_10m``
     - Boehen in 10m Höhe
   * - UV-Index
     - ``current/uv_index``
     - Aktuelle UV-Index
   * - UV-Index klaren Himmels
     - ``current/uv_index_clear_sky``
     - Bei wolkenlosen Bedingungen
   * - Sichtweite
     - ``current/visibility``
     - Sichtweite in Metern
   * - Dunstdauer
     - ``current/sunshine_duration``
     - Sekunden bis zur vorherigen Stunde
   * - Nassglas-Thermometer
     - ``current/wet_bulb_temperature_2m``
     - In 2m Höhe (°C)
   * - Verdunstung
     - ``current/evapotranspiration``
     - Von Boden und Pflanzen (mm)
   * - Referenzverdunstung ET0
     - ``current/et0_fao_evapotranspiration``
     - Nach FAO-56 Penman-Monteith (mm)
   * - Dampfdruckdefizit
     - ``current/vapour_pressure_deficit``
     - VPD in kPa
   * - Wasser-Dampf-Säule
     - ``current/column_water_vapour``
     - Integrierter Wasserdampf (kg/m²)
   * - Gefrierlinien-Hoehe
     - ``current/freezing_level_height``
     - Hoehe der 0°C-Linie (m)


daily (Tagesvorhersage)
-----------------------

Matchstring-Syntax: ``daily/N/<feld>`` wobei ``N`` = 0 (heute), 1 (morgen), … bis 15.

Standard-Variablen
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring (N = Tag-Index)
     - Beschreibung
   * - Wettercode
     - ``daily/N/weather_code``
     - Schwerebedingung des Tages (WMO)
   * - Max. Temperatur
     - ``daily/N/temperature_2m_max``
     - Tagesmaximum (°C)
   * - Min. Temperatur
     - ``daily/N/temperature_2m_min``
     - Tagesminimum (°C)
   * - Max. wahrgenommene Temp.
     - ``daily/N/apparent_temperature_max``
     - Höchste Empfindungstemp. (°C)
   * - Min. wahrgenommene Temp.
     - ``daily/N/apparent_temperature_min``
     - Niedrigste Empfindungstemp. (°C)
   * - Sonnenaufgang
     - ``daily/N/sunrise``
     - ISO 8601 Timestamp
   * - Sonnenuntergang
     - ``daily/N/sunset``
     - ISO 8601 Timestamp
   * - Daemmerungsdauer
     - ``daily/N/daylight_duration``
     - Anzahl Sekunden Tageslicht
   * - Dunstdauer
     - ``daily/N/sunshine_duration``
     - Sekunden mit direkter Strahlung > 120 W/m²
   * - Mondaufgang
     - ``daily/N/moonrise``
     - ISO 8601 Timestamp
   * - Monduntergang
     - ``daily/N/moonset``
     - ISO 8601 Timestamp
   * - Mondphase
     - ``daily/N/moon_phase``
     - 0/1=Neu, 0.25=Erstes Viertel, 0.5=Voll, 0.75=Letztes Viertel
   * - Max. UV-Index
     - ``daily/N/uv_index_max``
     - Tagesmaximum des UV-Index
   * - Max. UV-Index klaren Himmels
     - ``daily/N/uv_index_clear_sky_max``
     - Bei wolkenlosen Bedingungen
   * - Regen gesamt
     - ``daily/N/rain_sum``
     - Summe des Regens (mm)
   * - Schauer gesamt
     - ``daily/N/showers_sum``
     - Summe der Schauer (mm)
   * - Schneefall gesamt
     - ``daily/N/snowfall_sum``
     - Summe Schneefall (cm)
   * - Niederschlag gesamt
     - ``daily/N/precipitation_sum``
     - Kumulierter Niederschlag (mm)
   * - Niederschlagsstunden
     - ``daily/N/precipitation_hours``
     - Stunden mit Niederschlag
   * - Max. Niederschlagwahrscheinlichkeit
     - ``daily/N/precipitation_probability_max``
     - Hoechste stündliche Wahrscheinlichkeit (%)
   * - Min. Windgeschwindigkeit
     - ``daily/N/wind_speed_10m_min``
     - Tägliches Minimum der Windgeschwindigkeit
   * - Max. Windgeschwindigkeit
     - ``daily/N/wind_speed_10m_max``
     - Tägliches Maximum der Windgeschwindigkeit
   * - Max. Windböen
     - ``daily/N/wind_gusts_10m_max``
     - Tagesmaximum der Windboehen
   * - Dominante Windrichtung
     - ``daily/N/wind_direction_dominant_10m``
     - Vorherrschende Windrichtung (°)
   * - Kurzwellenstrahlung
     - ``daily/N/shortwave_radiation_sum``
     - Tagesummen in MJ/m²
   * - Referenzverdunstung ET0
     - ``daily/N/et0_fao_evapotranspiration``
     - Tägliches ET0 (mm)


Zusaetzliche daily-Variablen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nicht standardmaessig aktiv, aber über ``om_matchstring`` anfragbar:

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Mittlere Temperatur
     - ``daily/N/temperature_2m_mean``
     - Mittlere Tagestemperatur (°C)
   * - Mittlere wahrgenommene Temp.
     - ``daily/N/apparent_temperature_mean``
     - Mittel der Empfindungstemp. (°C)
   * - Mittlere Bewölkung
     - ``daily/N/cloud_cover_mean``
     - Mittel der Bewölkung (%)
   * - Max. Bewölkung
     - ``daily/N/cloud_cover_max``
     - Hoechsste Bewoelkung (%)
   * - Min. Bewölkung
     - ``daily/N/cloud_cover_min``
     - Niedrigste Bewölkung (%)
   * - Mittl. Taupunkt
     - ``daily/N/dew_point_2m_mean``
     - Mittel Taupunkt (°C)
   * - Max. Taupunkt
     - ``daily/N/dew_point_2m_max``
     - Hoechster Taupunkt (°C)
   * - Min. Taupunkt
     - ``daily/N/dew_point_2m_min``
     - Niedrigster Taupunkt (°C)
   * - Mittl. Niederschlagwahrscheinlichkeit
     - ``daily/N/precipitation_probability_mean``
     - Mittel der Niederschlagswahrscheinlichkeit (%)
   * - Min. Niederschlagwahrscheinlichkeit
     - ``daily/N/precipitation_probability_min``
     - Niedrigste Niederschlagswahrscheinlichkeit (%)
   * - Mittlere Rel. Luftfeuchtigkeit
     - ``daily/N/relative_humidity_2m_mean``
     - Mittel (%)
   * - Max. Rel. Luftfeuchtigkeit
     - ``daily/N/relative_humidity_2m_max``
     - Maximum (%)
   * - Min. Rel. Luftfeuchtigkeit
     - ``daily/N/relative_humidity_2m_min``
     - Minimum (%)
   * - Schneefall-Wasseräquivalent
     - ``daily/N/snowfall_water_equivalent_sum``
     - Wasseräquivalent (mm)
   * - Mittl. MSL-Druck
     - ``daily/N/pressure_msl_mean``
     - Mittel (hPa)
   * - Max. MSL-Druck
     - ``daily/N/pressure_msl_max``
     - Maximum (hPa)
   * - Min. MSL-Druck
     - ``daily/N/pressure_msl_min``
     - Minimum (hPa)
   * - Mittl. Oberflaechendruck
     - ``daily/N/surface_pressure_mean``
     - Mittel (hPa)
   * - Max. Oberflaechendruck
     - ``daily/N/surface_pressure_max``
     - Maximum (hPa)
   * - Min. Oberflaechendruck
     - ``daily/N/surface_pressure_min``
     - Minimum (hPa)
   * - Mittlere Windböen
     - ``daily/N/wind_gusts_10m_mean``
     - Mittel
   * - Mittlere Windgeschwindigkeit
     - ``daily/N/wind_speed_10m_mean``
     - Mittel
   * - Min. Windböen
     - ``daily/N/wind_gusts_10m_min``
     - Minimum
   * - Mittl. Nassglas-Temp.
     - ``daily/N/wet_bulb_temperature_2m_mean``
     - Mittel (°C)
   * - Max. Nassglas-Temp.
     - ``daily/N/wet_bulb_temperature_2m_max``
     - Maximum (°C)
   * - Min. Nassglas-Temp.
     - ``daily/N/wet_bulb_temperature_2m_min``
     - Minimum (°C)
   * - Max. VPD
     - ``daily/N/vapour_pressure_deficit_max``
     - Höchstes Dampfdruckdefizit (kPa)
   * - Mittlere CAPE
     - ``daily/N/cape_mean``
     - Mittel (J/kg)
   * - Max. CAPE
     - ``daily/N/cape_max``
     - Maximum (J/kg)
   * - Min. CAPE
     - ``daily/N/cape_min``
     - Minimum (J/kg)


hourly (Stundenvorhersage)
--------------------------

Matchstring-Syntax: ``hourly/H/<feld>`` wobei ``H`` = 0, 1, 2, …

Basisdaten
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Temperatur
     - ``hourly/H/temperature_2m``
     - Lufttemperatur in 2m Höhe (°C)
   * - Rel. Luftfeuchtigkeit
     - ``hourly/H/relative_humidity_2m``
     - In 2m Höhe (%)
   * - Taupunkt
     - ``hourly/H/dew_point_2m``
     - Taupunkttemperatur (°C)
   * - Wahrgenommene Temperatur
     - ``hourly/H/apparent_temperature``
     - Empfindungstemperatur (°C)
   * - Nassglas-Temperatur
     - ``hourly/H/wet_bulb_temperature_2m``
     - In 2m Höhe (°C)
   * - MSL-Druck
     - ``hourly/H/pressure_msl``
     - Druck reduziert auf Meereshoehe (hPa)
   * - Oberflaechendruck
     - ``hourly/H/surface_pressure``
     - An der Oberfläche (hPa)
   * - Bewölkung geamt
     - ``hourly/H/cloud_cover``
     - Gesamtbewölkung (%)
   * - Bewölkung tie
     - ``hourly/H/cloud_cover_low``
     - Tieftauben und Nebel bis 3 km (%)
   * - Bewölkung mittlere Hoehe
     - ``hourly/H/cloud_cover_mid``
     - Wolken 3 bis 8 km Höhe (%)
   * - Bewölkung hoch
     - ``hourly/H/cloud_cover_high``
     - Hochwolken ab 8 km Höhe (%)
   * - Windgeschwindigkeit 10m
     - ``hourly/H/wind_speed_10m``
     - In 10m Hoehe
   * - Windgeschwindigkeit 80m
     - ``hourly/H/wind_speed_80m``
     - In 80m Hoehe
   * - Windgeschwindigkeit 120m
     - ``hourly/H/wind_speed_120m``
     - In 120m Hoehe
   * - Windgeschwindigkeit 180m
     - ``hourly/H/wind_speed_180m``
     - In 180m Hoehe
   * - Windrichtung 10m
     - ``hourly/H/wind_direction_10m``
     - Meteorologisch in Grad (°)
   * - Windrichtung 80m
     - ``hourly/H/wind_direction_80m``
     - In 80m Hoehe (°)
   * - Windrichtung 120m
     - ``hourly/H/wind_direction_120m``
     - In 120m Hoehe (°)
   * - Windrichtung 180m
     - ``hourly/H/wind_direction_180m``
     - In 180m Hoehe (°)
   * - Windböen 10m
     - ``hourly/H/wind_gusts_10m``
     - Boehen in 10m Hoehe
   * - Temperatur 80m
     - ``hourly/H/temperature_80m``
     - In 80m Hoehe (°C)
   * - Temperatur 120m
     - ``hourly/H/temperature_120m``
     - In 120m Hoehe (°C)
   * - Temperatur 180m
     - ``hourly/H/temperature_180m``
     - In 180m Hoehe (°C)
   * - Wettercode
     - ``hourly/H/weather_code``
     - WMO Weather Interpretation Code
   * - Tag/Nacht
     - ``hourly/H/is_day``
     - 1 = Tag, 0 = Nacht
   * - Dunstdauer
     - ``hourly/H/sunshine_duration``
     - Sekunden mit direkter Strahlung (s)
   * - Sichtweite
     - ``hourly/H/visibility``
     - Sichtweite in Metern
   * - UV-Index
     - ``hourly/H/uv_index``
     - UV-Index für die Stunde
   * - UV-Index klaren Himmels
     - ``hourly/H/uv_index_clear_sky``
     - Bei wolkenlosen Bedingungen


Niederschlag
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Niederschlag gesamt
     - ``hourly/H/precipitation``
     - Gesamtsunne (mm)
   * - Regen
     - ``hourly/H/rain``
     - Großskaliger Regen (mm)
   * - Schauer
     - ``hourly/H/showers``
     - Konvektive Schauer (mm)
   * - Schneefall
     - ``hourly/H/snowfall``
     - Schneemenge (cm)
   * - Schneehoehe
     - ``hourly/H/snow_depth``
     - Schnee auf dem Boden (m)
   * - Niederschlagwahrscheinlichkeit
     - ``hourly/H/precipitation_probability``
     - Wahrscheinlichkeit > 0.1 mm (%)


Solar-Strahlung
~~~~~~~~~~~~~~~~

.. note:: Solarstrahlung ist ein Mittelwert der vorherigen Stunde.
          Fuegen Sie ``_instant`` an den Feldnamen an, um den Momentanwert
          zum angegebenen Zeitpunkt zu erhalten.
          Fuer ``global_tilted_irradiance`` gibt es die Parameter ``tilt``
          und ``azimuth`` zur Anpassung.

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Kurzwellenstrahlung GHI
     - ``hourly/H/shortwave_radiation``
     - Globale horizontale Strahlung (W/m²)
   * - Kurzwellenstrahlung (momentan)
     - ``hourly/H/shortwave_radiation_instant``
     - Momentanwert in W/m²
   * -Direkte Strahlung
     - ``hourly/H/direct_radiation``
     - Auf Horizontal (W/m²)
   * - Direkte Strahlung (momentan)
     - ``hourly/H/direct_radiation_instant``
     - Momentanwert in W/m²
   * - Diffuse Strahlung DHI
     - ``hourly/H/diffuse_radiation``
     - Diffus auf Horizontal (W/m²)
   * - Diffuse Strahlung (momentan)
     - ``hourly/H/diffuse_radiation_instant``
     - Momentanwert in W/m²
   * - Direkte Normaleinstrahlung DNI
     - ``hourly/H/direct_normal_irradiance``
     - Senkrecht zur Sonne (W/m²)
   * - DNI (momentan)
     - ``hourly/H/direct_normal_irradiance_instant``
     - Momentanwert in W/m²
   * - Schiefeinstrahlung GTI
     - ``hourly/H/global_tilted_irradiance``
     - Auf geneigte Flaeche (W/m²)
   * - GTI (momentan)
     - ``hourly/H/global_tilted_irradiance_instant``
     - Momentanwert in W/m²
   * - Terrestrische Strahlung
     - ``hourly/H/terrestrial_radiation``
     - Ausstrahlung des Erdbodens (W/m²)
   * - Terrestrische Strahlung (momentan)
     - ``hourly/H/terrestrial_radiation_instant``
     - Momentanwert in W/m²


Boden-Temperaturen und -Feuchtigkeit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Bodentemperatur 0 cm
     - ``hourly/H/soil_temperature_0cm``
     - Oberflaeche (Land) / Wasser (°C)
   * - Bodentemperatur 6 cm
     - ``hourly/H/soil_temperature_6cm``
     - In 6 cm Tiefe (°C)
   * - Bodentemperatur 18 cm
     - ``hourly/H/soil_temperature_18cm``
     - In 18 cm Tiefe (°C)
   * - Bodentemperatur 54 cm
     - ``hourly/H/soil_temperature_54cm``
     - In 54 cm Tiefe (°C)
   * - Bodenfeuchte 0–1 cm
     - ``hourly/H/soil_moisture_0_to_1cm``
     - Volumetrische Mischungsrate (m³/m³)
   * - Bodenfeuchte 1–3 cm
     - ``hourly/H/soil_moisture_1_to_3cm``
     - (m³/m³)
   * - Bodenfeuchte 3–9 cm
     - ``hourly/H/soil_moisture_3_to_9cm``
     - (m³/m³)
   * - Bodenfeuchte 9–27 cm
     - ``hourly/H/soil_moisture_9_to_27cm``
     - (m³/m³)
   * - Bodenfeuchte 27–81 cm
     - ``hourly/H/soil_moisture_27_to_81cm``
     - (m³/m³)


Zusaetzliche Variablen
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Verdunstung
     - ``hourly/H/evapotranspiration``
     - Von Boden und Pflanzen (mm)
   * - Referenzverdunstung ET0
     - ``hourly/H/et0_fao_evapotranspiration``
     - FAO-56 Penman-Monteith (mm)
   * - Dampfdruckdefizit (VPD)
     - ``hourly/H/vapour_pressure_deficit``
     - In kPa (>1.6 = hohe Transpiration)
   * - Wasser-Dampf-Saeule
     - ``hourly/H/column_water_vapour``
     - Integrierter Wasserdampf (kg/m²)
   * - CAPE
     - ``hourly/H/cape``
     - Konvektive verfügbare Energie (J/kg)
   * - Lifted Index
     - ``hourly/H/lifted_index``
     - Konvektiver Unwetterparameter
   * - Convective Inhibition
     - ``hourly/H/cinc``
     - Konvektive Hemmung (J/kg)
   * - Gefrierlinien-Hoehe
     - ``hourly/H/freezing_level_height``
     - Hoehe der 0°C-Linie (m)
   * - Grenzschichten-Hoehe PBL
     - ``hourly/H/boundary_layer_height``
     - Hoehe der planetaren Grenzschicht (m)
   * - Zeitpunkt
     - ``hourly_time/H``
     - ISO 8601 Zeitstempel der Stunde


Druckniveau-Variablen (Pressure Levels)
----------------------------------------

Verfügbar fuer folgende Druckhoehen:
1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300,
250, 200, 150, 100, 70, 50, 30 hPa.

Beispiel: ``hourly/H/temperature_850hPa``

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Temperatur
     - ``hourly/H/temperature_<level>hPa``
     - Lufttemperatur an der Druckhoehe (°C)
   * - Rel. Luftfeuchtigkeit
     - ``hourly/H/relative_humidity_<level>hPa``
     - In %
   * - Taupunkt
     - ``hourly/H/dew_point_<level>hPa``
     - Taupunkttemperatur (°C)
   * - Bewölkung
     - ``hourly/H/cloud_cover_<level>hPa``
     - Aus relativer Feuchtigkeit abgeleitet (%)
   * - Windgeschwindigkeit
     - ``hourly/H/wind_speed_<level>hPa``
     - An der Druckhoehe
   * - Windrichtung
     - ``hourly/H/wind_direction_<level>hPa``
     - An der Druckhoehe (°)
   * - Geopotentielle Hoehe
     - ``hourly/H/geopotential_height_<level>hPa``
     - Hoehe in Meter ueber Meeresspiegel


location (Standort-Informationen)
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Feld
     - matchstring
     - Beschreibung
   * - Breitengrad
     - ``location/latitude``
     - Latitude (vom Server bestaetigt)
   * - Laengengrad
     - ``location/longitude``
     - Longitude
   * - Zeitzone
     - ``location/timezone``
     - IANA-Timezone-Name
   * - Zeitzone-Kuerzel
     - ``location/timezone_abbreviation``
     - Abkuerzung (z.B. UTC, CET)
   * - Hoehe
     - ``location/elevation``
     - Hoehenlage des Ortes (m)


Struct Templates
================

Das Plugin stellt folgende ready-to-use Struct-Templates bereit:

* **``openmeteo.current``** -- Alle aktuellen Wetterdaten
* **``openmeteo.daily``** -- Tagesvorhersage für heute bis Tag-6
  (``daily.day0`` bis ``daily.day6``)
* **``openmeteo.hourly``** -- Stundenvorhersage für die nächsten 24 Stunden
  (``hourly.hour0`` bis ``hourly.hour23``)

Einzelne zusaetzliche Felder (z.B. Solarstrahlung, Bodenfeuchte,
Druckniveau-Variablen) koennen ueber individuelle Items mit
``om_matchstring`` hinzugefuegt werden.


WMO Weather Codes
=================

.. list-table::
   :header-rows: 1

   * - Code
     - Deutsch
     - Englisch
   * - 0
     - Klarer Himmel
     - Clear sky
   * - 1
     - Meisten sonnig
     - Mainly clear
   * - 2
     - Teilweise bewölkt
     - Partly cloudy
   * - 3
     - Bewölkt
     - Overcast
   * - 45
     - Nebel
     - Fog
   * - 48
     - Reifnebel
     - Depositing rime fog
   * - 51
     - Leichter Nieselregen
     - Slight drizzle
   * - 53
     - Mäßiger Nieselregen
     - Moderate drizzle
   * - 55
     - Dichter Nieselregen
     - Dense drizzle
   * - 56
     - Unterkuhlter leichter Nieselregen
     - Freezing drizzle, slight
   * - 57
     - Unterkuhlter dichter Nieselregen
     - Freezing drizzle, dense
   * - 61
     - Leichter Regen
     - Slight rain
   * - 63
     - Mäßiger Regen
     - Moderate rain
   * - 65
     - Starker Regen
     - Heavy rain
   * - 66
     - Leichter Eisregen
     - Freezing rain, slight
   * - 67
     - Starker Eisregen
     - Freezing rain, heavy
   * - 71
     - Leichter Schneefall
     - Slight snow fall
   * - 73
     - Mäßiger Schneefall
     - Moderate snow fall
   * - 75
     - Starker Schneefall
     - Heavy snow fall
   * - 77
     - Schneegriesel
     - Snow grains
   * - 80
     - Leichte Regenschauer
     - Slight rain showers
   * - 81
     - Mäßige Regenschauer
     - Moderate rain showers
   * - 82
     - Heftige Regenschauer
     - Violent rain showers
   * - 85
     - Leichte Schneeschauer
     - Slight snow showers
   * - 86
     - Starke Schneeschauer
     - Heavy snow showers
   * - 95
     - Gewitter
     - Thunderstorm
   * - 96
     - Gewitter mit leichtem Hagel
     - Thunderstorm with slight hail
   * - 99
     - Gewitter mit starkem Hagel
     - Thunderstorm with heavy hail


Version History
===============

1.0.0
-----

Erste Version des Plugins.
