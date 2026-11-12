# Changelog

## 3.1.2 - 2026-11-12

- New values no longer rebuild the card: only changed texts and attributes are set. Keyboard focus, running animations (remaining-time bar, sprinkler symbol) and the loaded image stay in place, and the kiosk has less to redraw. / Neue Werte bauen die Karte nicht mehr neu auf: Es werden nur geänderte Texte und Attribute gesetzt. Tastaturfokus, laufende Animationen (Restzeit-Balken, Regner-Symbol) und das geladene Bild bleiben erhalten, und der Kiosk muss weniger neu zeichnen.
- A custom image that cannot be loaded is remembered and replaced by the built-in image without retrying on every update; an invalid image setting no longer breaks the card. / Ein nicht ladbares eigenes Bild wird gemerkt und durch das eingebaute ersetzt, ohne bei jeder Aktualisierung neu zu laden; eine ungültige Bildeinstellung bringt die Karte nicht mehr zum Absturz.
- The width is evaluated in the next frame (no "ResizeObserver loop" messages). / Die Breite wird im nächsten Bild ausgewertet (keine „ResizeObserver loop“-Meldungen).
- Fixed: a renamed zone was only shown after the next value change. / Behoben: Eine umbenannte Zone erschien erst nach der nächsten Wertänderung.
- Browser tests for updates, controls and layout added. / Browser-Tests für Aktualisierung, Bedienung und Layout ergänzt.

## 3.1.1 - 2026-11-08

- Fixed: the card could jitter (font size and height switching back and forth quickly) when its width was close to a font step (e.g. 400 px) and the page scrollbar appeared and disappeared as a result. The font step is now chosen with ±12 px hysteresis and no longer flips on small width changes. / Behoben: Die Card konnte zappeln (Schrift und Höhe wechselten schnell hin und her), wenn ihre Breite knapp an einer Schriftstufe lag (z. B. 400 px) und die Scrollleiste der Seite dadurch ein- und ausgeblendet wurde. Die Schriftstufe wird jetzt mit ±12 px Hysterese gewählt und kippt bei kleinen Breitenänderungen nicht mehr.
- The taller banner from 600 px card width uses the same hysteresis. / Das höhere Banner ab 600 px Kartenbreite nutzt dieselbe Hysterese.

## 3.1.0 - 2026-11-07

- The card and its editor now appear in English by default and in German when Home Assistant is set to German. / Karte und Editor erscheinen jetzt standardmäßig auf Englisch und auf Deutsch, wenn Home Assistant auf Deutsch eingestellt ist.
- The default title and pump label follow the Home Assistant language; values already saved in a card stay unchanged. / Standardtitel und Pumpenbezeichnung folgen der Sprache von Home Assistant; bereits gespeicherte Werte bleiben unverändert.
- README shortened and available in English and German. / README gekürzt und auf Englisch und Deutsch verfügbar.

## 3.0.1

- Aufräumarbeiten ohne Funktionsänderung: interne Hilfsfunktionen für Start-/Stopp-Abschluss, Stopp-Ziel und Online-Prüfung zusammengeführt, toter Code entfernt. Konfiguration, Kartentyp (`custom:irrigation-control-card`) und Verhalten bleiben unverändert.
- Repository verschlankt: alte Release-Notes (1.0.0–2.0.0), nicht mehr benötigte Logo-Dateien, das ungenutzte Quellbild des Standardbildes und der Einmal-Publisher für 3.0.0 entfernt.

## 3.0.0

- Umbenennung in **Irrigation Control Card**, damit HACS und der Karteneditor das Projekt von der bereits vorhandenen Irrigation Card von `kratochj` unterscheiden.
- **Breaking Change:** Custom-Element und YAML-Typ heißen jetzt `irrigation-control-card` bzw. `custom:irrigation-control-card`; die JavaScript-Datei heißt `irrigation-control-card.js`. Der alte Tag wird wegen der Namenskollision nicht als Alias registriert.
- Repository, Dokumentationslink, HACS-Verknüpfung, Badges und Bild-URLs auf `https://github.com/BeGiBue/home-assistant-irrigation-control-card` umgestellt.
- Migration dokumentiert: vorhandene Installation und Karten behalten, die Ressource dieses Projekts aktualisieren und nur deren YAML-Typ ändern. Entitätszuordnungen und sonstige Konfigurationsschlüssel bleiben erhalten. Ressourcen der anderen Irrigation Card dürfen dabei nicht entfernt werden.
- Die Aufnahme in den offiziellen HACS-Katalog ist weiterhin ausstehend ([hacs/default #12053](https://github.com/hacs/default/pull/12053)). Der Wechsel von Custom Repositories zur regulären HACS-Suche erfolgt erst nach bestätigter Katalogverfügbarkeit und ohne Deinstallation.
- Eine Major-Version bedeutet nicht automatisch Breaking Changes; diese Version enthält jedoch ausdrücklich die erforderliche Umbenennung von Kartentyp und Ressource. Die bisherigen Sicherheitskorrekturen bleiben erhalten.

## 2.0.0

- Version 2.0.0 zur Weiterentwicklung und Vorbereitung des Wechsels in den offiziellen HACS-Katalog; die Aufnahme ist noch ausstehend ([hacs/default #12053](https://github.com/hacs/default/pull/12053)).
- Reguläre Installation über die HACS-Suche als Standardweg nach der Aufnahme dokumentiert. Bis zur tatsächlichen Katalogverfügbarkeit bleibt das benutzerdefinierte Repository der aktuelle Installationsweg.
- Migration bestehender Custom Repositories nach der Aufnahme beschrieben: Katalogverfügbarkeit prüfen, nur den benutzerdefinierten Eintrag entfernen, die Installation nicht deinstallieren und Dashboard-Konfigurationen sowie Ressourcen behalten.
- Die Major-Version bedeutet nicht automatisch Breaking Changes; Kartentyp und vorhandene Konfigurationsschlüssel bleiben erhalten. Sie bestätigt keine bereits erfolgte Katalogaufnahme.
- README auf Funktionen, Konfiguration, Bedienung, technische Voraussetzungen und Grenzen ausgerichtet; unnötige Erklärungen zu optischer Anordnung entfernt.
- Sicherheitskorrektur: Minutentasten nur mit dauerfähigem Hydrawise-Ziel; Standardläufe ohne solche Dauerübergabe sind ausdrücklich als „Controller-Vorgabe“ gekennzeichnet. Ungültige Dauern und stille Fallbacks von Minutenstarts werden zurückgewiesen.
- Sicherheitskorrektur: Stopp bleibt während der Startbestätigung bedienbar, sofern ein gültiges Ziel existiert; Aufträge werden geordnet und Wartezustände erst nach Dienstannahme bestätigt.
- Sicherheitskorrektur: Ein noch unbeantworteter Start-/Stoppauftrag bleibt auch nach 90 Sekunden gesperrt und gibt keinen konkurrierenden Start frei.
- Registry-/Aktionsindizes gegen geerbte Objektschlüssel gehärtet, Dokumentationslink korrigiert und Security-/Browser-Regressionstests mit gemockten Diensten ergänzt.

## 1.1.4

- Neue, im Browser erstellte Vorschauen aus dem unveränderten Original-Code in der README.
- Vorschau-Bilder über absolute Raw-URLs für die Anzeige in GitHub und HACS eingebunden.
- Versionsangaben für das Patch-Release aktualisiert.

Keine Änderungen an der Funktionsweise der Karte oder Integration.

## 1.1.3 - 2026-10-08

### Entfernt

- Option `layout` (auto/wide/compact): Sie hatte seit 1.1.0 keine Wirkung mehr, die Card passt sich automatisch der Breite an. Vorhandene `layout`-Einträge werden ignoriert.
- Leerer Platzhalter `images/.keepfolder`.

## 1.1.2 - 2026-10-08

### Geändert

- Feste Kartenhöhe: Die Card ist immer so hoch wie ihr Inhalt (`rows: auto`) und lässt sich im Layout-Editor nicht mehr in der Höhe verstellen oder strecken; nur die Breite ist frei.

## 1.1.1 - 2026-10-08

### Geändert

- Kachel „Aktive Zonen“ im Statistik-Bereich entfernt; laufende Zonen sind an ihrer Hervorhebung und dem Status „Bewässert“ erkennbar.

## 1.1.0 - 2026-10-08

### Geändert

- Neue Reihenfolge: Pumpe direkt unter dem Titel, darunter die Zonen, dann die Statistiken (Heute bewässert, Verbrauch, aktive Zonen) und zuletzt Controller-Status und Regensensor.
- Pumpe und Controller-Kacheln einzeilig: Titel links, Wert bzw. Zustand und Schalter am rechten Rand.
- Controller-Kacheln breit in zwei Spalten; eine übrige Kachel nutzt die volle Breite.

- Alle Einstellungen im grafischen Editor mit Standardfeldern, gegliedert in Allgemein, Bild, Zonen, Pumpe, Statistiken und Controller.
- Startdauern als Mehrfachauswahl (eigene Werte möglich) statt Freitext; Textangaben wie `5, 10, 15` funktionieren weiterhin.
- Leistungsmesser: neue Optionen `power_entity` (Leistung) und `energy_entity` (Energie) mit Kacheln im Statistik-Bereich.
- Neue Optionen `show_pump`, `show_stats`, `daily_time_entity` und `water_use_entity`; `show_controller` blendet nur noch Controller-Status und Regensensor aus.

### Behoben

- Alle Sensoren und Schalter erscheinen nur, wenn die Entität tatsächlich existiert – auch nächster Zyklus, Restzeit und Automatik (vorher teils mit „—“).
- „Nächster Zyklus“ zeigte bei Terminen am Folgetag doppelt „Morgen … morgen“.

## 1.0.0 - 2026-10-07

- Erste Veröffentlichung der Irrigation Card für Hunter Hydrawise.
- Zonen als Hydrawise-Geräte im nativen Geräte-Picker wählbar; ohne Auswahl alle Zonen automatisch.
- Entitäten werden über die Entity-Registry (`translation_key`) zugeordnet.
- Manueller Start mit wählbaren Dauern (5 / 10 / 15 / 30 min), Stopp, Automatik-Schalter, Restzeit mit Fortschrittsbalken.
- Sofortiges Update nach Start/Stopp; Restzeit wird zwischen den Abfragen heruntergezählt.
- Controller-Kacheln (Status, Regensensor, Tageswerte, aktive Zonen) und optionale Pumpe.
- Eingebettetes Standardbild (Hunter MP Rotator) als Banner oder im Kartenhintergrund, eigene Bild-URL möglich.
- Glas-Look, Light/Dark Mode, optimiert für Hochformat, Touch und Kiosk (`layout`, `scale`).
