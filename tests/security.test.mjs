import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(process.env.IRRIGATION_TEST_CARD || new URL('../irrigation-control-card.js', import.meta.url), 'utf8');
const attack = '<img src=x onerror="window.__injected=1">';
function fixture({ running = true, manual = true, valve = true, config = {}, call } = {}) {
  const classes = new Map(), calls = [];
  const ctx = vm.createContext({
    HTMLElement: class {
      attachShadow() { this.shadowRoot = { innerHTML: '', querySelector: () => null, querySelectorAll: () => [], addEventListener() {} }; }
      dispatchEvent() {}
    },
    customElements: { get: n => classes.get(n), define: (n, c) => classes.set(n, c) },
    window: {}, console: { info() {}, error() {} },
    CustomEvent: class {}, setTimeout: () => 1, clearTimeout() {}, setInterval: () => 1, clearInterval() {},
  });
  vm.runInContext(source, ctx);
  const Card = classes.get('irrigation-control-card'), card = new Card();
  const entities = {}, states = {};
  const add = (id, key, value, attributes = {}, device = 'zone1') => {
    entities[id] = { entity_id: id, device_id: device, platform: 'hydrawise', translation_key: key };
    states[id] = { state: value, attributes, last_changed: new Date().toISOString() };
  };
  if (running) add('binary_sensor.zone_running', 'watering', 'off');
  if (manual) add('switch.zone_manual', 'manual_watering', 'off');
  if (valve) add('valve.zone', '', 'closed');
  add('switch.zone_auto', 'auto_watering', 'on');
  add('sensor.zone_remaining', 'watering_time', '5', { unit_of_measurement: 'min' });
  add('sensor.zone_water', 'daily_active_water_use', '20', { unit_of_measurement: 'L' });
  add('binary_sensor.rain', 'rain_sensor', 'off', {}, 'controller');
  states['switch.gartenpumpe'] = { state: 'off', attributes: { friendly_name: 'Pumpe' } };
  const hass = {
    states, entities, language: 'de', locale: { language: 'de-DE' },
    devices: { zone1: { model: 'Zone', name: 'Rasen', via_device_id: 'controller' }, controller: { model: 'Controller', name: 'Hydrawise' } },
    callService: async (domain, service, data) => { calls.push({ domain, service, data }); return call?.(domain, service, data); },
  };
  card.setConfig(config); card.hass = hass;
  return { card, hass, calls, zone: card._zones[0] };
}

test('Konfigurationswerte und Bildattribute können kein HTML erzeugen', () => {
  const { card } = fixture({ config: { title: attack, subtitle: attack, pump_title: attack, image_url: 'x" onerror="window.__injected=1' } });
  const html = card.shadowRoot.innerHTML;
  assert.ok(!html.includes(attack));
  assert.ok(!html.includes('src="x" onerror='));
  assert.match(html, /&lt;img src=x onerror=&quot;/);
});
test('Registry-Namen, Entity-IDs, Zustände und Einheiten bleiben escaped', () => {
  const { card, hass } = fixture({ config: { subtitle: '', pump_title: '' } });
  hass.devices.zone1.name = attack; hass.devices.controller.name = attack;
  hass.states['switch.gartenpumpe'].attributes.friendly_name = attack;
  hass.states['sensor.zone_water'].attributes.unit_of_measurement = attack;
  const id = 'sensor.water" onclick="window.__injected=1';
  hass.entities[id] = { entity_id: id, device_id: 'zone1', platform: 'hydrawise', translation_key: 'daily_active_water_use' };
  hass.states[id] = { state: attack, attributes: { unit_of_measurement: attack } };
  card._sig = ''; card.hass = hass;
  assert.ok(!card.shadowRoot.innerHTML.includes(attack));
  assert.ok(!card.shadowRoot.innerHTML.includes('data-more="sensor.water" onclick='));
  assert.match(card.shadowRoot.innerHTML, /&quot; onclick=&quot;/);
});
test('Dauern sind eindeutig, begrenzt und numerisch', () => {
  const { card } = fixture({ config: { durations: ['30', '5', 'NaN', 'Infinity', '-1', '0', '1.5', attack, '1440', '1441', '5'] } });
  assert.deepEqual(Array.from(card._durations()), [5, 30, 1440]);
  card._config.durations = [1,2,3,4,5,6,7];
  assert.equal(card._durations().length, 6);
});
test('Minutenstart verwendet ausschließlich Hydrawise-Ziel und gewählte Dauer', async () => {
  const { card, zone, calls } = fixture();
  await card._start(zone, 5);
  assert.deepEqual(JSON.parse(JSON.stringify(calls)), [{ domain: 'hydrawise', service: 'start_watering', data: { entity_id: 'binary_sensor.zone_running', duration: 5 } }]);
});
for (const [name, options, domain, service, target] of [
  ['manueller Schalter', { running: false, valve: false }, 'homeassistant', 'turn_on', 'switch.zone_manual'],
  ['Ventil', { running: false, manual: false }, 'valve', 'open_valve', 'valve.zone'],
]) {
  test(name + ': keine irreführenden Minutentasten oder stillen Dauer-Fallbacks', async () => {
    const { card, zone, calls } = fixture(options);
    assert.ok(!card.shadowRoot.innerHTML.includes('data-min="5"'));
    assert.match(card.shadowRoot.innerHTML, /Controller-Vorgabe/);
    assert.equal(await card._start(zone, 5), false);
    assert.equal(calls.length, 0);
    await card._start(zone, 0);
    assert.deepEqual(JSON.parse(JSON.stringify(calls)), [{ domain, service, data: { entity_id: target } }]);
  });
}
test('Leere Dauer-Auswahl kennzeichnet den Controller-Standardlauf', () => {
  const { card } = fixture({ config: { durations: [] } });
  assert.match(card.shadowRoot.innerHTML, /data-min="0"/);
  assert.match(card.shadowRoot.innerHTML, /Controller-Vorgabe/);
});
test('Ungültige Dauer, fehlendes Ziel oder Offline-Zustand lösen keinen Start aus', async () => {
  const { card, zone, calls, hass } = fixture();
  for (const duration of [-1, NaN, Infinity, 1.5, 1441, '5']) assert.equal(await card._start(zone, duration), false);
  assert.equal(await card._start(undefined, 5), false);
  hass.states[zone.running].state = 'unavailable';
  assert.equal(await card._start(zone, 5), false);
  assert.equal(calls.length, 0);
});
test('Doppelter Start bleibt während ausstehender Bestätigung gesperrt', async () => {
  const { card, zone, calls } = fixture();
  await card._start(zone, 5); await card._start(zone, 10);
  assert.equal(calls.length, 1);
});
test('Unbeantwortete Aufträge geben nach abgelaufener Wartezeit keinen weiteren Start frei', async () => {
  let finish;
  const { card, zone, calls } = fixture({ call: () => new Promise(resolve => { finish = resolve; }) });
  const starting = card._start(zone, 5);
  card._pending[zone.id].until = Date.now() - 1;
  card._sig = ''; card._update();
  assert.equal(card._pending[zone.id].accepted, false);
  assert.equal(await card._start(zone, 10), false);
  assert.equal(calls.length, 1);
  finish(); await starting;
  assert.ok(card._pending[zone.id].until > Date.now());
});
test('Fehlgeschlagener Start räumt eigenen Wartezustand auf', async () => {
  const { card, zone } = fixture({ call: async () => { throw new Error('rejected'); } });
  assert.equal(await card._start(zone, 5), false);
  assert.equal(card._pending[zone.id], undefined);
});
test('Stopp ist bereits während der Startbestätigung sichtbar und bedienbar', () => {
  const { card, zone } = fixture();
  card._pending[zone.id] = { kind: 'start', until: Date.now() + 90000, accepted: false };
  const html = card._zone(zone);
  assert.match(html, /data-stop="zone1"/);
  assert.ok(!/<button class="stop"[^>]*disabled/.test(html));
});
test('Stopp nach ausstehendem Start wird geordnet und nur einmal gesendet', async () => {
  let finishStart;
  const { card, zone, calls } = fixture({ call: (_domain, service) => service === 'start_watering' ? new Promise(resolve => { finishStart = resolve; }) : undefined });
  const starting = card._start(zone, 5), stopping = card._stop(zone);
  assert.equal(card._pending[zone.id].kind, 'stop');
  assert.equal(card._pending[zone.id].accepted, false);
  assert.equal(calls.length, 1);
  assert.equal(await card._stop(zone), false);
  finishStart(); await Promise.all([starting, stopping]);
  assert.equal(calls.length, 2);
  assert.equal(calls[1].service, 'turn_off');
  assert.equal(calls[1].data.entity_id, 'switch.zone_manual');
});
test('Fehlendes Stopp-Ziel verursacht keinen ungezielten Service-Aufruf', async () => {
  const { card, zone, calls } = fixture({ manual: false, valve: false });
  card._pending[zone.id] = { kind: 'start', until: Date.now() + 90000, accepted: false };
  assert.match(card._zone(zone), /<button class="stop"[^>]*disabled/);
  assert.equal(await card._stop(zone), false);
  assert.equal(calls.length, 0);
});
test('Ventil-Stopp verwendet nur die gewählte verfügbare Entität', async () => {
  const { card, zone, calls } = fixture({ manual: false });
  await card._stop(zone);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].service, 'close_valve');
  assert.equal(calls[0].data.entity_id, 'valve.zone');
});
test('Unbekannte reservierte YAML-Geräte-IDs werden ignoriert', () => {
  const { card } = fixture({ config: { zones: ['constructor', '__proto__', 'toString'] } });
  assert.equal(card._zones.length, 0);
});
test('Pumpenschalter verwendet HA-Sitzung und eindeutiges Ziel', () => {
  const { card, calls } = fixture(); card._toggle('switch.gartenpumpe');
  assert.equal(calls[0].domain, 'homeassistant');
  assert.equal(calls[0].service, 'turn_on');
  assert.equal(calls[0].data.entity_id, 'switch.gartenpumpe');
});


// Load the actual script unchanged to check its own scope isolation on reload.
// The registry rejects duplicate tags/constructors just like the browser.
function registrationContext() {
  const classes = new Map();
  const ctx = vm.createContext({
    HTMLElement: class {}, window: {}, console: { info() {} },
    customElements: {
      get: name => classes.get(name),
      define: (name, cls) => {
        assert.ok(!classes.has(name), `Tag already registered: ${name}`);
        assert.ok(![...classes.values()].includes(cls), 'Constructor already registered');
        classes.set(name, cls);
      },
    },
  });
  const loadOwn = () => vm.runInContext(source, ctx);
  const loadOther = () => vm.runInContext(`
    window.OtherIrrigationCard = class extends HTMLElement {};
    customElements.define('irrigation-card', window.OtherIrrigationCard);
    window.customCards = window.customCards || [];
    window.customCards.push({type:'irrigation-card',name:'Irrigation Card'});
  `, ctx);
  return { classes, ctx, loadOwn, loadOther };
}
function assertMetadata(ctx) {
  const entries = ctx.window.customCards.filter(c => c.type === 'irrigation-control-card');
  assert.equal(entries.length, 1);
  assert.equal(entries[0].name, 'Irrigation Control Card');
  assert.equal(entries[0].documentationURL, 'https://github.com/BeGiBue/home-assistant-irrigation-control-card');
}
test('Eigenständige Karte registriert ausschließlich den neuen eindeutigen Tag', () => {
  const { classes, ctx, loadOwn } = registrationContext();
  loadOwn();
  assert.equal(classes.has('irrigation-control-card'), true);
  assert.equal(classes.has('irrigation-card'), false);
  assert.equal(ctx.window.customCards.some(c => c.type === 'irrigation-card'), false);
  assertMetadata(ctx);
});
for (const otherFirst of [true, false]) {
  test(`Andere Irrigation Card ${otherFirst ? 'zuerst' : 'danach'}: beide Registrierungen bleiben unabhängig`, () => {
    const { classes, ctx, loadOwn, loadOther } = registrationContext();
    if (otherFirst) { loadOther(); loadOwn(); }
    else { loadOwn(); loadOther(); }
    assert.equal(classes.size, 2);
    assert.equal(classes.get('irrigation-card'), ctx.window.OtherIrrigationCard);
    assert.notEqual(classes.get('irrigation-control-card'), classes.get('irrigation-card'));
    assert.equal(ctx.window.customCards.filter(c => c.type === 'irrigation-card').length, 1);
    assertMetadata(ctx);
  });
}
test('Erneutes Laden erzeugt weder doppelte Registrierungen noch Kartenmetadaten', () => {
  const { classes, ctx, loadOwn, loadOther } = registrationContext();
  loadOther(); loadOwn();
  const registered = classes.get('irrigation-control-card');
  loadOwn();
  assert.equal(classes.size, 2);
  assert.equal(classes.get('irrigation-control-card'), registered);
  assert.equal(classes.get('irrigation-card'), ctx.window.OtherIrrigationCard);
  assert.equal(ctx.window.customCards.length, 2);
  assertMetadata(ctx);
});
