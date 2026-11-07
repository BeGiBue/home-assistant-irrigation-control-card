<p align="center">
  <img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-irrigation-control-card/main/images/irrigation-card-logo-160.png" alt="Irrigation Control Card" width="160">
</p>

# Irrigation Control Card

**English** | [Deutsch](https://github.com/BeGiBue/home-assistant-irrigation-control-card#deutsch)

## English

Home Assistant card for controlling irrigation with **Hunter Hydrawise**.

<img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-irrigation-control-card/main/screenshots/irrigation-watering-350-light.png" width="350" alt="Lawn being watered, 350 px wide, light theme">

### Features

- Select zones as Hydrawise devices; without a selection all Hydrawise zones appear
- Finds each zone's entities by itself, independent of language and entity IDs; missing sensors are hidden
- Per zone: status (Ready / Irrigating / Paused / Offline), next cycle, watered today and automatic switch
- Manual start with selectable durations (default 5 / 10 / 15 / 30 min); running zones show remaining time and a stop button
- Optional pump switch, statistics for water use, power and energy, controller status and rain sensor
- Built for portrait and touch: iPhone, iPad and Raspberry Pi kiosk; follows your theme

The card is shown in German when Home Assistant is set to German, and in English otherwise.

### Requirements

- The [Hunter Hydrawise](https://www.home-assistant.io/integrations/hydrawise/) integration is set up. It creates one device per zone; the card reads the entities from that device, so no entity IDs need to be entered.

### Operation

| Element | Action |
|---|---|
| Duration button (e.g. "10 min") | `hydrawise.start_watering` with this duration; only with a matching Hydrawise target |
| Start – controller default | Default run via Hydrawise, the manual switch or the valve; the card does not guarantee a number of minutes |
| Stop | Turns off `switch.<zone>_manual_watering` |
| Automatic | Toggles `switch.<zone>_automatic_watering` (off = Hydrawise pauses the zone for 365 days) |
| Pump | Toggles the pump entity |
| Tiles, rows, status pill | Open the more-info dialog |

Start, stop, automatic and pump switches call Home Assistant services and can operate real valves, zones and pumps. The card uses the signed-in session; Home Assistant and the device integration check permissions on the server. Grant access to an operable dashboard accordingly and check entity assignments before real use.

Independent community project, not affiliated with Hunter Industries or Home Assistant. **Hunter** and **Hydrawise** are trademarks of their respective owners. License: [AGPL-3.0-only](https://github.com/BeGiBue/home-assistant-irrigation-control-card/blob/main/LICENSE).

## Deutsch

[English](https://github.com/BeGiBue/home-assistant-irrigation-control-card#english) | **Deutsch**

Home-Assistant-Karte zur Bewässerungssteuerung mit **Hunter Hydrawise**.

<img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-irrigation-control-card/main/screenshots/irrigation-watering-350-light.png" width="350" alt="Rasen wird bewässert, 350 px breit, helles Theme">

### Funktionen

- Zonen als Hydrawise-Geräte auswählen; ohne Auswahl erscheinen alle Hydrawise-Zonen
- Findet die Entitäten jeder Zone selbst, unabhängig von Sprache und Entity-IDs; fehlende Sensoren werden ausgeblendet
- Pro Zone: Status (Bereit / Bewässert / Pausiert / Offline), nächster Zyklus, heute bewässert und Automatik-Schalter
- Manueller Start mit wählbarer Dauer (Standard 5 / 10 / 15 / 30 min); laufende Zonen zeigen Restzeit und Stopp-Taste
- Optionaler Pumpenschalter, Statistiken zu Wasserverbrauch, Leistung und Energie, Controller-Status und Regensensor
- Optimiert für Hochformat und Touch: iPhone, iPad und Raspberry-Pi-Kiosk; folgt dem Theme

Die Karte erscheint auf Deutsch, wenn Home Assistant auf Deutsch eingestellt ist, sonst auf Englisch.

### Voraussetzungen

- Die Integration [Hunter Hydrawise](https://www.home-assistant.io/integrations/hydrawise/) ist eingerichtet. Sie legt pro Zone ein Gerät an; die Karte liest die Entitäten aus diesem Gerät, Entity-IDs müssen nicht eingetragen werden.

### Bedienung

| Element | Aktion |
|---|---|
| Dauer-Taste (z. B. „10 min“) | `hydrawise.start_watering` mit dieser Dauer; nur bei passendem Hydrawise-Ziel |
| Start – Controller-Vorgabe | Standardlauf über Hydrawise, manuellen Schalter oder Ventil; keine zugesicherte Minutenzahl durch die Karte |
| Stopp | schaltet `switch.<zone>_manuelle_bewasserung` aus |
| Automatik | schaltet `switch.<zone>_automatische_bewasserung` (aus = Hydrawise pausiert die Zone für 365 Tage) |
| Pumpe | schaltet die Pumpen-Entität um |
| Kacheln, Zeilen, Status-Pill | öffnen den Mehr-Info-Dialog |

Start, Stopp, Automatik und Pumpenschalter lösen Home-Assistant-Dienste aus und können reale Ventile, Bewässerungszonen und Pumpen bedienen. Die Karte verwendet die angemeldete Sitzung; Berechtigungen prüfen Home Assistant und die Geräteintegration serverseitig. Den Zugriff auf ein bedienbares Dashboard entsprechend vergeben und Entitätszuordnungen vor realer Bedienung prüfen.

Unabhängiges Community-Projekt, ohne Verbindung zu Hunter Industries oder Home Assistant. **Hunter** und **Hydrawise** sind Marken ihrer jeweiligen Rechteinhaber. Lizenz: [AGPL-3.0-only](https://github.com/BeGiBue/home-assistant-irrigation-control-card/blob/main/LICENSE).
