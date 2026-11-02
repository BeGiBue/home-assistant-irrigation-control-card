<p align="center">
  <img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-irrigation-control-card/main/images/irrigation-card-logo-160.png" alt="Irrigation Control Card" width="160">
</p>

<h1 align="center">Irrigation Control Card</h1>

<p align="center">
  Custom-Card zur Bewässerungssteuerung mit <strong>Hunter Hydrawise</strong> in Home Assistant.
</p>

<p align="center">
  <strong>Version 3.0.1</strong><br>
  <a href="https://github.com/BeGiBue/home-assistant-irrigation-control-card/actions/workflows/validate.yml"><img src="https://github.com/BeGiBue/home-assistant-irrigation-control-card/actions/workflows/validate.yml/badge.svg" alt="HACS validation"></a>
</p>

## Vorschau

**Aktive Bewässerung: Rasen – schmal (350 px)**

<img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-irrigation-control-card/main/screenshots/irrigation-watering-350-light.png" width="350" alt="Rasen wird bewässert, Beete bleiben bereit, 350 px Kartenbreite, helles Theme">

**Aktive Bewässerung: Rasen – breit (800 px)**

<img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-irrigation-control-card/main/screenshots/irrigation-watering-800-light.png" width="800" alt="Rasen wird bewässert, Beete bleiben bereit, 800 px Kartenbreite, helles Theme">

## Funktionen

- Zonen werden direkt als **Hydrawise-Geräte** ausgewählt – mehrere Zonen über den nativen Geräte-Picker hinzufügen, entfernen und sortieren
- Ohne Auswahl erscheinen automatisch alle Hydrawise-Zonen
- Alle Entitäten einer Zone werden selbst gefunden (Entity-Registry, `translation_key`) – unabhängig von Sprache und Entity-IDs
- Jeder Wert und jeder Schalter erscheint nur, wenn die zugehörige Entität existiert – fehlende Sensoren werden ausgeblendet statt mit „—“ angezeigt
- Pro Zone: Status (Bereit / Bewässert / Pausiert / Offline), nächster Zyklus, heute bewässert, Automatik-Schalter
- Manueller Start mit wählbarer Dauer (Standard 5 / 10 / 15 / 30 min) über `hydrawise.start_watering`
- Laufende Zone: Restzeit mit Fortschrittsbalken und Stopp-Taste; die Restzeit wird zwischen den Hydrawise-Abfragen minütlich heruntergezählt
- Nach Start/Stopp fordert die Card sofort ein Update an (Hydrawise fragt sonst nur alle 5 Minuten ab)
- Optionale Pumpe (z. B. `switch.gartenpumpe`) direkt schalten
- Statistiken: heute bewässert, Wasserverbrauch (nur mit passender Entität), optional Leistung und Energie eines Leistungsmessers; dazu Controller-Status und Regensensor
- Eingebettetes Gerätebild; optional eigenes Bild oder Bildanzeige abschalten
- Unterstützt helle und dunkle Home-Assistant-Themes
- Feste Kartenhöhe: richtet sich immer nach dem Inhalt und ist im Layout-Editor nicht verstellbar; nur die Breite (4 – 12 Spalten) ist frei
- Optimiert für Hochformat und Touch – iPhone, iPad und Raspberry-Pi-Kiosk: Schrift und Anordnung passen sich automatisch der Kartenbreite an (Zonen und Kacheln ab ausreichender Breite nebeneinander)

## Voraussetzungen

Die Integration [Hunter Hydrawise](https://www.home-assistant.io/integrations/hydrawise/) ist eingerichtet. Sie legt pro Zone ein Gerät mit diesen Entitäten an (Beispiel Zone „Rasen“):

```text
valve.rasen
switch.rasen_manuelle_bewasserung
switch.rasen_automatische_bewasserung
sensor.rasen_nachster_zyklus
sensor.rasen_bewasserungszeit          (verbleibende Bewässerungszeit)
binary_sensor.rasen_bewasserung
sensor.rasen_tagliche_aktive_bewasserungszeit
```

Die Card liest diese Zuordnung aus dem Gerät – die Entity-IDs müssen nicht eingetragen werden.

## Installation über HACS

Das Projekt ist im offiziellen HACS-Katalog verfügbar ([hacs/default #12053](https://github.com/hacs/default/pull/12053)).
Ein benutzerdefiniertes Repository ist für die reguläre Installation nicht erforderlich.

1. HACS öffnen und nach **Irrigation Control Card** suchen.
2. Die Karte auswählen und herunterladen.
3. Browser vollständig neu laden; in der Companion-App gegebenenfalls den Frontend-Cache zurücksetzen.

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=BeGiBue&repository=home-assistant-irrigation-control-card&category=plugin)

### Bestehende Custom-Repository-Installation auf den HACS-Katalog umstellen

1. In der HACS-Suche prüfen, dass **Irrigation Control Card** im offiziellen Katalog verfügbar ist. Falls der
   Eintrag noch fehlt, zuerst HACS und seine Repository-Informationen aktualisieren und mit der Umstellung warten.
2. Unter **HACS → ⋮ → Benutzerdefinierte Repositories** nur den Eintrag für
   `BeGiBue/home-assistant-irrigation-control-card` entfernen.
3. **Die bestehende Installation nicht deinstallieren.** Dashboard-Ressource, Karten und
   YAML-Konfigurationen beibehalten.
4. HACS neu laden bzw. **Informationen aktualisieren**, anschließend die weiterhin installierte
   Karte und angebotene Updates prüfen.
5. Nach einem Update das Frontend vollständig neu laden und vorhandene Dashboard-Karten prüfen.

Für den Katalogwechsel müssen Karten nicht neu angelegt werden. Vorhandene
Entitätszuordnungen und Konfigurationsschlüssel bleiben erhalten. Die unten beschriebene
Umbenennung von Kartentyp und Ressource ist ein eigener Migrationsschritt.
Eine Major-Version bedeutet **nicht automatisch Breaking Changes**; Version 3.0.0 enthält
jedoch bewusst die folgende notwendige Umstellung.

## Bestehende Karten auf den neuen Namen umstellen

Ab Version 3.0.0 heißt das Projekt **Irrigation Control Card**. Der bisherige Kartentyp
`custom:irrigation-card` kollidiert mit der Karte von `kratochj/hassio-irrigation-card`.
Deshalb registriert dieses Projekt ausschließlich `irrigation-control-card`; ein Alias für
den alten Namen würde die Kollision beibehalten.

Diese Schritte nach Installation der neuen Version ausführen:

1. Dashboard-Konfiguration sichern. Die vorhandene HACS-Installation, Karten und
   Entitätszuordnungen **nicht deinstallieren oder neu anlegen**.
2. Den bestehenden HACS-Eintrag prüfen: Das Repository heißt jetzt
   `https://github.com/BeGiBue/home-assistant-irrigation-control-card`.
   Falls HACS noch den bisherigen Repository-Namen führt, die Informationen aktualisieren.
   Falls die Custom-Repository-Liste korrigiert werden muss, nur deren alten Eintrag entfernen
   und die neue URL als **Dashboard** hinzufügen; die installierte Karte dabei behalten.
3. Unter **Einstellungen → Dashboards → Ressourcen** prüfen, dass die zu **diesem Projekt**
   gehörende Ressource auf `irrigation-control-card.js` zeigt und als JavaScript-Modul geladen
   wird. Die von HACS bereitgestellte URL verwenden. Bleibt das Installationsverzeichnis gleich,
   nur den Dateinamen `irrigation-card.js` ersetzen und Verzeichnis sowie vorhandene
   Cache-Parameter beibehalten. Das Verzeichnis nicht allein wegen der Repository-Umbenennung
   auf einen vermuteten Namen ändern. Bei manueller Installation die neue Datei in das
   bisherige Verzeichnis kopieren und die entsprechende Ressourcen-URL aktualisieren.
4. In allen **Karten dieses Projekts** ausschließlich den Typ ändern:

   ```yaml
   type: custom:irrigation-control-card
   ```

   Bisher stand dort `type: custom:irrigation-card`. Alle anderen Optionen, Geräte-IDs,
   Entitäten und die Position der Karte im Dashboard bleiben erhalten.
5. Alte Ressourcen dieses Projekts nicht zusätzlich laden. Ressourcen und Konfigurationen
   der anderen Irrigation Card von `kratochj` unverändert lassen; deren gleichnamige
   JavaScript-Datei nicht versehentlich entfernen oder ersetzen.
6. Browser vollständig neu laden, gegebenenfalls Frontend-Cache der Companion-App leeren.
   Anschließend Darstellung, Editor und Entitätszuordnungen prüfen.

## Card hinzufügen

Minimal – alle Hydrawise-Zonen automatisch:

```yaml
type: custom:irrigation-control-card
```

Mit ausgewählten Zonen (Geräte-IDs, am einfachsten im grafischen Editor wählen):

```yaml
type: custom:irrigation-control-card
title: Bewässerung
subtitle: Hunter Hydrawise
zones:
  - 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d
  - 6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a
pump_entity: switch.gartenpumpe
pump_title: Gartenpumpe
durations: ["5", "10", "15", "30"]
image_url: /local/images/rasen.jpg
```

## Optionen

Alle Optionen sind im grafischen Editor mit Standardfeldern von Home Assistant einstellbar (Textfelder, Auswahllisten, Schalter, Schieberegler, Geräte- und Entity-Picker).

| Option | Werte | Standard | Beschreibung |
|---|---|---|---|
| **Allgemein** | | | |
| `title` | Text | `Bewässerung` | Haupttitel |
| `subtitle` | Text | `Hunter Hydrawise` | Untertitel; leer = Name des Controllers |
| `scale` | `0.8` – `1.8` | `1` | Skaliert die gesamte Card, z. B. für Kiosk-Displays |
| **Bild** | | | |
| `show_image` | `true` \| `false` | `true` | Bild anzeigen |
| `image_mode` | `banner` \| `background` | `banner` | `banner`: Foto hinter dem Titel. `background`: blass im Kartenhintergrund. |
| `image_url` | URL | leer | Eigenes Bild, z. B. `/local/images/rasen.jpg`. Leer = eingebettetes Standardbild. |
| **Zonen** | | | |
| `zones` | Liste von Geräte-IDs | leer | Hydrawise-Zonen in Anzeigereihenfolge. Leer = alle Zonen. |
| `durations` | Liste von Minuten | `5, 10, 15, 30` | Start-Tasten (max. 6, je 1 – 1440 min); eigene Werte möglich |
| **Pumpe** | | | |
| `show_pump` | `true` \| `false` | `true` | Pumpe anzeigen |
| `pump_entity` | Entität | `switch.gartenpumpe` | Pumpe (`switch`, `valve`, `input_boolean`); ohne Entität keine Anzeige |
| `pump_title` | Text | `Gartenpumpe` | Bezeichnung der Pumpe |
| **Statistiken** | | | |
| `show_stats` | `true` \| `false` | `true` | Heute bewässert, Wasserverbrauch und Leistungsmesser anzeigen |
| `daily_time_entity` | Entität | automatisch | Tägliche Bewässerungszeit überschreiben |
| `water_use_entity` | Entität | automatisch | Wasserverbrauch überschreiben. Hydrawise legt ihn nur mit Durchflusssensor an – ohne Entität wird kein Verbrauch angezeigt. |
| `power_entity` | Entität | leer | Leistungsmesser – aktuelle Leistung (`device_class: power`), z. B. Messsteckdose der Pumpe. Kachel wird orange, sobald Leistung anliegt. |
| `energy_entity` | Entität | leer | Leistungsmesser – Energie (`device_class: energy`), z. B. kWh-Zähler der Messsteckdose |
| **Controller** | | | |
| `show_controller` | `true` \| `false` | `true` | Controller-Status und Regensensor anzeigen |
| `status_entity` | Entität | automatisch | Controller-Status überschreiben |
| `rain_entity` | Entität | automatisch | Regensensor überschreiben (z. B. ein eigener Sensor) |

Die Akzentfarbe lässt sich per Theme mit `--irrigation-color` anpassen.

## Grafischer Editor

Die Card verwendet Home Assistants eingebauten Formular-Editor (`getConfigForm()`) mit den aufklappbaren Gruppen **Allgemein**, **Bild**, **Zonen**, **Pumpe**, **Statistiken** und **Controller**. Zonen werden im Geräte-Picker ausgewählt, der nur Hydrawise-Zonen anbietet; die Startdauern sind eine Mehrfachauswahl, in die eigene Minutenwerte eingetippt werden können.

## Layout / Größe

Im Sections-Dashboard ist die Breite von 4 bis 12 Spalten einstellbar. Die Höhe ist fest: Die Card meldet `rows: auto` und ist immer genau so hoch wie ihr Inhalt. Eine im Layout-Editor eingestellte Zeilenzahl ändert die Card nicht.

## Bedienung

| Element | Aktion |
|---|---|
| Dauer-Taste (z. B. „10 min“) | `hydrawise.start_watering` mit dieser Dauer; nur bei passendem Hydrawise-Ziel |
| Start – Controller-Vorgabe | Standardlauf über Hydrawise, manuellen Schalter oder Ventil; keine zugesicherte Minutenzahl durch die Karte |
| Stopp | schaltet `switch.<zone>_manuelle_bewasserung` aus |
| Automatik | schaltet `switch.<zone>_automatische_bewasserung` (aus = Hydrawise pausiert die Zone für 365 Tage) |
| Pumpe | schaltet die Pumpen-Entität um |
| Kacheln, Zeilen, Status-Pill | öffnen den Mehr-Info-Dialog |

### Wirkung der Bedienung

Start, Stopp, Automatik und Pumpenschalter lösen Home-Assistant-Dienste aus und können reale
Ventile, Bewässerungszonen und Pumpen bedienen. Die Karte verwendet die angemeldete HA-Sitzung;
Berechtigungen werden serverseitig von Home Assistant und der Geräteintegration geprüft.
Den Zugriff auf ein bedienbares Dashboard entsprechend vergeben und Entitätszuordnungen vor
realer Bedienung prüfen.

## Grenzen und Datenaktualität

- Benötigt Home Assistant mit Custom-Card-Unterstützung und einen aktuellen Browser. Es wird keine Hydrawise-Integration mitgeliefert.
- Hydrawise-Zustände können zeitverzögert eintreffen. Die minütliche Restzeit ist zwischen den Controller-Abfragen eine Schätzung; nach einer Aktion fordert die Karte eine Aktualisierung an.
- Ohne Durchflusssensor bzw. Verbrauchsentität steht keine Verbrauchsanzeige zur Verfügung. Statistiken und Animationen ersetzen keine unabhängige Überwachung des Wasserflusses.
- Minutentasten werden nur angeboten, wenn die Zone über `hydrawise.start_watering` mit einer Dauer gestartet werden kann. Fehlt das passende Ziel oder sind keine gültigen Dauern konfiguriert, heißt der Start ausdrücklich **Controller-Vorgabe**. Dabei gelten die Laufzeit-/Abschaltregeln des Controllers; die Karte implementiert keinen eigenen Abschalttimer.
- Während einer ausstehenden Startbestätigung bleibt **Stopp** verfügbar, sofern ein bedienbares Stopp-Ziel existiert. Ein Stoppauftrag wartet auf den bereits gesendeten Startauftrag und wird danach abgesetzt. Ein unbeantworteter Auftrag gibt auch nach Ablauf der Wartezeit keinen weiteren Start frei. Die Anzeige allein bestätigt keinen geschlossenen Wasserfluss; bei Cloud-Ausfall den Controller bzw. die Anlage direkt prüfen.
- Das Abschalten der Automatik kann die Zone laut Hydrawise-Integration für 365 Tage pausieren. Den Controller-Zustand nach Änderungen prüfen.
- Eine separat konfigurierte Pumpe ist unabhängig von den Zonen bedienbar. Die Karte bildet keine eigene Pumpen-/Ventilverriegelung oder Trockenlaufsicherung ab.
- Eigene Bild-URLs werden vom Browser geladen. Externe Bildanbieter können dessen IP-Adresse und übliche Verbindungsmetadaten erhalten; lokale Bilder unter `/local/…` vermeiden diesen externen Abruf. Keine Zugangsdaten in Bild-URLs eintragen.

## Bild

Das Standardbild (zugeschnitten und gespiegelt) ist direkt in der JavaScript-Datei eingebettet, da HACS nur `irrigation-control-card.js` installiert. Mit `show_image: false` wird es ausgeblendet.

## Änderungen

[CHANGELOG.md](CHANGELOG.md) und [RELEASE_NOTES_3.0.0.md](RELEASE_NOTES_3.0.0.md) dokumentieren
Version 3.0.0 und die Migration.

## Hinweise zu Marken

Dieses Projekt ist ein unabhängiges Community-Projekt und steht in keiner Verbindung zu Hunter Industries oder Home Assistant. **Hunter** und **Hydrawise** sind Marken ihrer jeweiligen Rechteinhaber.

## Lizenz

GNU Affero General Public License v3.0 only (**AGPL-3.0-only**). Details stehen in [`LICENSE`](LICENSE).

## Entwicklung und Tests

Die Karte ist eine einzelne JavaScript-Datei ohne npm-Laufzeitabhängigkeiten und ohne Build-Schritt.

```bash
node --check irrigation-control-card.js
node --test --test-isolation=none tests/security.test.mjs
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/browser_security.py
```

Die Browserprüfung verwendet HA-Attrappen und gemockte Dienste, prüft 350/800 px Breite und legt Vorschauen
unter `tests/out/` ab. Es werden keine realen Ventile oder Pumpen geschaltet.
