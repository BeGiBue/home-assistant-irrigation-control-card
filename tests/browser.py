#!/usr/bin/env python3
"""Chromium-Tests für Aktualisierung, Bedienung und Layout mit lokalen HA-Attrappen; keine realen Geräteaufrufe.

  python tests/browser.py

Benötigt: pip install -r requirements-dev.txt  und  playwright install chromium
(oder PLAYWRIGHT_CHROMIUM_EXECUTABLE auf einen vorhandenen Chromium/Chrome setzen).
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

PAGE = """<!doctype html><meta charset="utf-8"><style>
body{margin:0;padding:14px;background:#e9edf1;font-family:Roboto,Inter,sans-serif;font-size:14px;
--primary-text-color:#141414;--secondary-text-color:#6b6f76;--primary-color:#009ac7;--success-color:#43a047;
--warning-color:#ff9800;--error-color:#e53935;--card-background-color:#fff}
</style><div id="w"></div><script>
window.__errors = [];
window.addEventListener('error', (e) => window.__errors.push(String(e.message || e)));
window.addEventListener('unhandledrejection', (e) => window.__errors.push('rejection: ' + e.reason));
customElements.define('ha-card',class extends HTMLElement{constructor(){super();this.attachShadow({mode:'open'}).innerHTML=
  '<style>:host{display:block;background:#fff;border-radius:16px;border:1px solid #dfe3e8;box-sizing:border-box;padding:0}</style><slot></slot>'}});
customElements.define('ha-icon',class extends HTMLElement{connectedCallback(){(this.shadowRoot||this.attachShadow({mode:'open'})).innerHTML=
  '<style>:host{display:inline-flex;width:var(--mdc-icon-size,24px);height:var(--mdc-icon-size,24px)}i{flex:1;border-radius:30%;background:currentColor;opacity:.55}</style><i></i>'}});
// Zwei Zonen an einem Hydrawise-Controller, dazu Pumpe und Leistungsmesser
window.world = () => {
  const states = {}, entities = {}, now = new Date().toISOString();
  const add = (id, key, state, attributes = {}, device) => {
    entities[id] = {entity_id: id, translation_key: key, device_id: device, platform: 'hydrawise'};
    states[id] = {state: String(state), attributes, last_changed: now};
  };
  for (const [z, n] of [['zone1', 'rasen'], ['zone2', 'beet']]) {
    add(`binary_sensor.${n}_running`, 'watering', 'off', {}, z);
    add(`switch.${n}_manual`, 'manual_watering', 'off', {}, z);
    add(`switch.${n}_auto`, 'auto_watering', 'on', {}, z);
    add(`sensor.${n}_remaining`, 'watering_time', '0', {unit_of_measurement: 'min'}, z);
    add(`sensor.${n}_next`, 'next_cycle', new Date(Date.now() + 5 * 3600e3).toISOString(), {}, z);
    add(`sensor.${n}_water`, 'daily_active_water_use', '20', {unit_of_measurement: 'L'}, z);
  }
  add('binary_sensor.controller_status', '', 'on', {}, 'controller');
  add('binary_sensor.controller_rain', 'rain_sensor', 'off', {}, 'controller');
  states['switch.gartenpumpe'] = {state: 'off', attributes: {friendly_name: 'Pumpe'}, last_changed: now};
  states['sensor.pumpe_leistung'] = {state: '0', attributes: {unit_of_measurement: 'W'}, last_changed: now};
  const devices = {zone1: {name: 'Rasen', model: 'Zone', via_device_id: 'controller'}, zone2: {name: 'Beet', model: 'Zone', via_device_id: 'controller'}, controller: {name: 'Hydrawise', model: 'Controller'}};
  return {states, entities, devices};
};
window.fixture = ({width = 400, config = {}, language = 'de', fail = false, hold = false} = {}) => {
  const w = document.getElementById('w');
  w.replaceChildren();
  w.style.width = width + 'px';
  const card = document.createElement('irrigation-control-card'), events = [], calls = [], pending = [], W = window.world();
  card.addEventListener('hass-more-info', (e) => events.push(e.detail.entityId));
  const mk = () => ({states: {...W.states}, entities: W.entities, devices: W.devices, language, locale: {language},
    callService: (domain, service, data) => { calls.push({domain, service, data}); if (hold) return new Promise((res) => pending.push(res)); return fail ? Promise.reject(new Error('x')) : Promise.resolve(); }});
  card.setConfig({pump_entity: 'switch.gartenpumpe', power_entity: 'sensor.pumpe_leistung', ...config});
  w.appendChild(card);
  card.hass = mk();
  const set = (id, state, attributes) => { W.states[id] = {state: String(state), attributes: attributes || W.states[id]?.attributes || {}, last_changed: new Date().toISOString()}; card.hass = mk(); };
  return {card, events, calls, pending, W, set, push: () => { card.hass = mk(); }};
};
</script>"""

TEST_JS = r"""
async () => {
  const results = [], check = (name, pass) => results.push({name, pass: !!pass});
  const turn = (ms = 0) => new Promise((r) => setTimeout(r, ms));
  const frames = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const {fixture} = window;
  const q = (card, sel) => card.shadowRoot.querySelector(sel);
  const qa = (card, sel) => [...card.shadowRoot.querySelectorAll(sel)];
  const text = (el) => el?.textContent.replace(/\s+/g, ' ').trim();
  const hc = (card) => q(card, 'ha-card');
  const H = (card) => hc(card).getBoundingClientRect().height;
  const setW = (w) => { document.getElementById('w').style.width = w + 'px'; };
  const zone = (card, id) => q(card, `[data-zone="${id}"]`);
  const errorsWithoutConsole = () => window.__errors.length;

  // --- Aufbau und Aktualisieren ohne Neuaufbau ---
  {
    const f = fixture();
    await turn(20);
    const card = hc(f.card), main = q(f.card, 'main'), img = q(f.card, '.pic'), z1 = zone(f.card, 'zone1'), z2 = zone(f.card, 'zone2'), pump = q(f.card, '.pump');
    check('Aufbau: zwei Zonen, Pumpe, Kacheln, Bild', z1 && z2 && pump && img && qa(f.card, '.tiles .tile').length >= 3 && text(z1.querySelector('h3')) === 'Rasen');
    check('Aufbau: kein Leerraum-Text zwischen den Elementen', [...main.childNodes].every((n) => n.nodeType === 1) && [...z1.childNodes].every((n) => n.nodeType === 1));
    const auto = q(f.card, '[data-toggle="switch.beet_auto"]');
    auto.focus();
    f.set('sensor.rasen_water', '35', {unit_of_measurement: 'L'});
    f.set('switch.gartenpumpe', 'on');
    f.set('sensor.pumpe_leistung', '640', {unit_of_measurement: 'W'});
    check('neue Werte: Karte, Inhalt, Bild, Zonen und Pumpe bleiben dieselben Elemente',
      hc(f.card) === card && q(f.card, 'main') === main && q(f.card, '.pic') === img && zone(f.card, 'zone1') === z1 && zone(f.card, 'zone2') === z2 && q(f.card, '.pump') === pump);
    check('neue Werte: Texte und Zustände folgen', /35/.test(text(q(f.card, '[data-more="sensor.rasen_water"]'))) && pump.classList.contains('on') && q(f.card, '[data-more="sensor.pumpe_leistung"]').classList.contains('tone-warning'));
    check('neue Werte: Tastaturfokus bleibt', f.card.shadowRoot.activeElement === auto);
    // Zone läuft: Bereich der Zone wechselt, die andere Zone bleibt unberührt
    const z2html = z2.innerHTML;
    f.set('sensor.rasen_remaining', '12', {unit_of_measurement: 'min'});
    f.set('binary_sensor.rasen_running', 'on');
    check('laufende Zone zeigt Restzeit und Stopp, Zone bleibt dasselbe Element', zone(f.card, 'zone1') === z1 && z1.classList.contains('running') && /12/.test(text(z1.querySelector('.rt'))) && !!z1.querySelector('[data-stop]') && !z1.querySelector('[data-start]'));
    check('andere Zone bleibt unverändert', zone(f.card, 'zone2') === z2 && z2.innerHTML === z2html);
    const chip = q(f.card, '.chip.big');
    check('Kopfsymbol zeigt den Lauf an', chip.classList.contains('live'));
    f.set('sensor.rasen_remaining', '11', {unit_of_measurement: 'min'});
    check('Restzeit ändert sich: Symbol und Balken bleiben dieselben Elemente (Animation läuft weiter)', q(f.card, '.chip.big') === chip && /11/.test(text(z1.querySelector('.rt'))));
    // angeglichen == frisch aufgebaut
    const morphed = hc(f.card).innerHTML, cls = hc(f.card).className;
    f.card._built = false; f.card._sig = ''; f.card._update();
    check('angeglichener Inhalt entspricht einem frischen Aufbau', hc(f.card).innerHTML === morphed && hc(f.card).className === cls && hc(f.card) !== card);
    const before = hc(f.card);
    f.push();
    check('gleiche Werte: nichts wird angefasst', hc(f.card) === before && zone(f.card, 'zone1') === q(f.card, '.zone'));
    f.set('binary_sensor.rasen_running', 'off');
    check('Zone fertig: Dauer-Tasten kehren zurück', qa(f.card, '[data-zone="zone1"] [data-start]').length === 4 && !q(f.card, '.chip.big').classList.contains('live'));
    // Zone verschwindet und kehrt zurück
    const saved = f.W.devices.zone1; delete f.W.devices.zone1; const ents = {...f.W.entities};
    for (const k of Object.keys(f.W.entities)) if (f.W.entities[k].device_id === 'zone1') delete f.W.entities[k];
    f.push();
    check('Zone entfällt: nur noch eine Zone', qa(f.card, '.zone').length === 1 && text(q(f.card, '.zone h3')) === 'Beet');
    f.W.devices.zone1 = saved; Object.assign(f.W.entities, ents); f.push();
    const fresh1 = hc(f.card).innerHTML; f.card._built = false; f.card._sig = ''; f.card._update();
    check('Zone kehrt zurück: beide Zonen da, Inhalt wie frisch aufgebaut', qa(f.card, '.zone h3').map(text).sort().join() === 'Beet,Rasen' && hc(f.card).innerHTML === fresh1);
  }

  // --- Bedienung ---
  {
    const f = fixture();
    await turn(20);
    q(f.card, '[data-more="sensor.rasen_water"] b').click();
    q(f.card, '[data-zone="zone2"] .pill b').click();
    check('Tippen auf Werte öffnet die Entität (auch auf inneren Elementen)', JSON.stringify(f.events) === JSON.stringify(['sensor.rasen_water', 'binary_sensor.beet_running']));
    q(f.card, '.pump ha-icon').click();
    q(f.card, '[data-toggle="switch.rasen_auto"]').click();
    await turn();
    check('Pumpe und Automatik schalten die passende Entität', f.calls.length === 2 && f.calls[0].service === 'turn_on' && f.calls[0].data.entity_id === 'switch.gartenpumpe' && f.calls[1].service === 'turn_off' && f.calls[1].data.entity_id === 'switch.rasen_auto');
    const b = q(f.card, '[data-zone="zone2"] [data-start][data-min="10"]');
    b.querySelector('b').click();
    await turn();
    check('Start sendet Zone und Dauer', f.calls.length === 3 && f.calls[2].domain === 'hydrawise' && f.calls[2].data.entity_id === 'binary_sensor.beet_running' && f.calls[2].data.duration === 10);
    check('nach dem Start: „Startet …“ mit Stopp, Zone 1 weiter startbar', text(q(f.card, '[data-zone="zone2"] .pill')) !== text(q(f.card, '[data-zone="zone1"] .pill')) && !!q(f.card, '[data-zone="zone2"] [data-stop]') && qa(f.card, '[data-zone="zone1"] [data-start]').length === 4);
    f.set('sensor.beet_water', '21', {unit_of_measurement: 'L'});
    check('Wartezustand übersteht neue Werte', !!q(f.card, '[data-zone="zone2"] [data-stop]') && !q(f.card, '[data-zone="zone2"] [data-start]'));
    f.set('binary_sensor.beet_running', 'on');
    q(f.card, '[data-zone="zone2"] [data-stop]').click();
    await turn();
    check('Stopp trifft die manuelle Entität der Zone', f.calls.some((c) => c.service === 'turn_off' && c.data.entity_id === 'switch.beet_manual'));
    const n = f.calls.length;
    for (let i = 0; i < 6; i++) f.set('sensor.rasen_water', String(40 + i), {unit_of_measurement: 'L'});
    q(f.card, '[data-toggle="switch.rasen_auto"]').click();
    await turn();
    check('nach mehreren Aktualisierungen löst ein Tipp genau einen Aufruf aus', f.calls.length === n + 1);
  }
  {
    const f = fixture({hold: true});
    const b = q(f.card, '[data-zone="zone1"] [data-start][data-min="5"]');
    b.click(); b.click();
    q(f.card, '[data-zone="zone1"] [data-start]')?.click();
    await turn();
    check('schnelles Mehrfachtippen startet nur einmal', f.calls.filter((c) => c.domain === 'hydrawise').length === 1);
    f.pending.forEach((r) => r());
    await turn();
  }
  {
    const f = fixture({fail: true});
    const orig = console.error; console.error = () => {};
    q(f.card, '[data-zone="zone1"] [data-start][data-min="5"]').click();
    await turn(10);
    console.error = orig;
    check('Fehler beim Start: Dauer-Tasten kehren zurück', qa(f.card, '[data-zone="zone1"] [data-start]').length === 4);
  }
  {
    const f = fixture();
    f.set('switch.gartenpumpe', 'unavailable');
    const pump = q(f.card, '.pump');
    pump.querySelector('ha-icon').click(); pump.click();
    f.set('binary_sensor.rasen_running', 'unavailable'); f.set('switch.rasen_manual', 'unavailable');
    const d = q(f.card, '[data-zone="zone1"] [data-start]');
    d.querySelector('b').click();
    await turn();
    check('gesperrte Schaltflächen lösen nichts aus (auch nicht über innere Elemente)', pump.disabled && d.disabled && f.calls.length === 0);
  }

  // --- Bild ---
  {
    const f = fixture({config: {image_url: 'http://127.0.0.1:9/kaputt.png'}});
    for (let i = 0; i < 60 && !f.card._badImg?.size; i++) await turn(50);
    check('eigenes Bild nicht ladbar: eingebautes Bild erscheint', q(f.card, '.pic')?.getAttribute('src').startsWith('data:image/') && !q(f.card, '.banner').classList.contains('noimg'));
    f.card.setConfig({image_url: 'http://127.0.0.1:9/kaputt.png', title: 'Neu', pump_entity: 'switch.gartenpumpe'}); f.push();
    check('nicht ladbare Adresse bleibt gemerkt (kein erneuter Ladeversuch)', q(f.card, '.pic').getAttribute('src').startsWith('data:image/') && text(q(f.card, 'h1')) === 'Neu');
    const b = fixture({config: {image_mode: 'background'}});
    check('Bild als Hintergrund', hc(b.card).classList.contains('bgm') && !!q(b.card, '.bgimg') && !q(b.card, '.banner'));
    b.set('sensor.rasen_water', '22', {unit_of_measurement: 'L'});
    check('Hintergrundbild bleibt bei neuen Werten dasselbe Element', hc(b.card).classList.contains('bgm') && !!q(b.card, '.bgimg'));
    const g = fixture({config: {show_image: false}});
    check('Bild abschaltbar', !q(g.card, '.pic') && !q(g.card, '.banner'));
    const h = fixture({config: {image_url: 42}});
    check('Bildadresse, die kein Text ist, stört nicht', q(h.card, '.pic').getAttribute('src').startsWith('data:image/'));
  }

  // --- Sprache, leere Karte ---
  {
    const e = fixture({language: 'en'});
    check('Englisch: Texte folgen der Sprache', /Ready|Idle/i.test(text(q(e.card, '.zone .pill'))));
    const f = fixture();
    f.W.entities = {}; for (const k of Object.keys(f.W.devices)) delete f.W.devices[k]; f.push();
    check('ohne Hydrawise-Geräte: Hinweis statt Zonen', !!q(f.card, '.empty') && !q(f.card, '.zone'));
  }

  // --- Breiten, Schriftstufen, Scrollleiste ---
  {
    for (const w of [260, 300, 350, 400, 600, 800, 1100]) {
      const f = fixture({width: w});
      await frames();
      const m = q(f.card, 'main').getBoundingClientRect();
      const over = qa(f.card, 'main *').filter((el) => { const r = el.getBoundingClientRect(); return r.width > 0 && !el.classList.contains('pic') && (r.right > m.right + 1 || r.left < m.left - 1); });
      check(`${w} px: nichts ragt aus der Karte`, over.length === 0);
    }
    const g = fixture({width: 395});
    await frames();
    const fs = () => g.card.style.getPropertyValue('--fs');
    check('395 px: Schrift 14 px', fs() === '14px');
    setW(408); await frames();
    check('408 px (innerhalb der Hysterese): Schrift bleibt', fs() === '14px');
    setW(414); await frames();
    check('414 px: Schrift 15 px', fs() === '15px');
    g.set('sensor.rasen_water', '23', {unit_of_measurement: 'L'});
    check('Schriftstufe übersteht neue Werte', fs() === '15px');
    for (const mode of ['banner', 'background']) {
      const swing = [];
      for (let W = 250; W <= 1100; W += 10) {
        const a = fixture({width: W, config: {image_mode: mode}}); await frames(); const h1 = H(a.card);
        setW(W - 15); await frames(); const h2 = H(a.card);
        if (h1 <= h2 + .3) continue;
        const mid = (h1 + h2) / 2; let n = 0, cur = W - 15;
        for (let i = 0; i < 12; i++) { const want = H(a.card) > mid ? W - 15 : W; if (want !== cur) { cur = want; setW(cur); n++; } await frames(); }
        if (n > 4) swing.push(W);
      }
      check(`Scrollleiste (${mode}): Höhe pendelt bei keiner Breite` + (swing.length ? ' (' + swing.join(',') + ')' : ''), swing.length === 0);
    }
  }
  await turn(50);
  check('keine Fehler-Ereignisse (auch kein „ResizeObserver loop“)', window.__errors.length === 0);
  if (window.__errors.length) results.push({name: 'Fehler: ' + window.__errors.join(' | '), pass: false});
  return results;
}
"""


def launch(p):
    executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    return p.chromium.launch(**({"executable_path": executable, "args": ["--no-sandbox"]} if executable else {}))


def main():
    source = (ROOT / "irrigation-control-card.js").read_text(encoding="utf8")
    errors = []
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page(viewport={"width": 1200, "height": 1000})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(PAGE)
        page.add_script_tag(content=source, type="module")
        page.wait_for_function("() => customElements.get('irrigation-control-card')")
        results = page.evaluate(TEST_JS)
        results.append({"name": "keine JavaScript-Fehler", "pass": not errors})
        browser.close()
    for result in results:
        print(("PASS " if result["pass"] else "FAIL ") + result["name"])
    failures = sum(not result["pass"] for result in results)
    print(f"\n{len(results)} Prüfungen, {failures} Fehler")
    if errors:
        print(errors)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
