#!/usr/bin/env python3
"""Chromium-Regressionen mit lokalen HA-Attrappen; keine realen Geräteaufrufe."""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OTHER_CARD = """
  window.OtherIrrigationCard = class extends HTMLElement {};
  customElements.define('irrigation-card', window.OtherIrrigationCard);
  window.customCards = window.customCards || [];
  window.customCards.push({type:'irrigation-card',name:'Irrigation Card'});
"""
TEST_JS = r"""
async () => {
  const results = [], check = (name, pass) => results.push({name, pass:!!pass});
  const attack = '<img src=x onerror="window.__injected=1">';
  const fixture = ({width=350,running=true,manual=true,valve=true,config={}}={}) => {
    document.body.style.width = width+'px';
    const card = document.createElement('irrigation-control-card'), calls=[], states={}, entities={};
    const add=(id,key,state,attributes={},device='zone1')=>{
      entities[id]={entity_id:id,translation_key:key,device_id:device,platform:'hydrawise'};
      states[id]={state,attributes,last_changed:new Date().toISOString()};
    };
    if(running)add('binary_sensor.zone_running','watering','off');
    if(manual)add('switch.zone_manual','manual_watering','off');
    if(valve)add('valve.zone','','closed');
    add('switch.zone_auto','auto_watering','on');
    add('sensor.zone_remaining','watering_time','5',{unit_of_measurement:'min'});
    add('sensor.zone_water','daily_active_water_use','20',{unit_of_measurement:'L'});
    states['switch.gartenpumpe']={state:'off',attributes:{friendly_name:'Pumpe'}};
    const hass={states,entities,language:'de',locale:{language:'de-DE'},
      devices:{zone1:{name:'Rasen',model:'Zone',via_device_id:'controller'},controller:{name:'Hydrawise',model:'Controller'}},
      callService:async(domain,service,data)=>calls.push({domain,service,data})};
    card.setConfig({show_image:false,...config});document.body.appendChild(card);card.hass=hass;
    return {card,hass,calls};
  };
  const turn=()=>new Promise(resolve=>setTimeout(resolve,0));
  const clean=root=>!root.querySelector('script, [data-injected]') &&
    ![...root.querySelectorAll('*')].some(el=>[...el.attributes].some(a=>/^on/i.test(a.name)));
  for(const width of [350,800]){
    const {card,hass,calls}=fixture({width});let root=card.shadowRoot;
    check(width+': Zone und Dauer-Tasten vorhanden',root.querySelector('h3')?.textContent==='Rasen' && root.querySelectorAll('[data-start]').length===4);
    const button=[...root.querySelectorAll('[data-start]')].find(b=>b.dataset.min==='5');
    button.click();await turn();root=card.shadowRoot;
    check(width+': Klick sendet ausschließlich gewählte Dauer und Ziel',calls.length===1&&calls[0].domain==='hydrawise'&&calls[0].data.duration===5&&calls[0].data.entity_id==='binary_sensor.zone_running');
    check(width+': Stopp trotz ausstehender Startbestätigung bedienbar',!!root.querySelector('[data-stop]')&&!root.querySelector('[data-stop]').disabled);
    root.querySelector('[data-stop]').click();await turn();
    check(width+': Stopp trifft die zugeordnete manuelle Entität',calls.some(c=>c.service==='turn_off'&&c.data.entity_id==='switch.zone_manual'));
    const auto=card.shadowRoot.querySelector('[data-toggle="switch.zone_auto"]');auto.click();await turn();
    check(width+': Automatik verwendet HA-Dienst und eindeutiges Ziel',calls.some(c=>c.service==='turn_off'&&c.data.entity_id==='switch.zone_auto'));
    const pump=card.shadowRoot.querySelector('[data-toggle="switch.gartenpumpe"]');pump.click();await turn();
    check(width+': Pumpe verwendet nur konfigurierte Entität',calls.some(c=>c.service==='turn_on'&&c.data.entity_id==='switch.gartenpumpe'));
    card.remove();

    const bad=fixture({width,config:{title:attack,subtitle:attack,pump_title:attack,show_image:true,image_url:'x" onerror="window.__injected=1'}});
    bad.hass.devices.zone1.name=attack;
    const id='sensor.water" onclick="window.__injected=1';
    bad.hass.entities[id]={entity_id:id,device_id:'zone1',platform:'hydrawise',translation_key:'daily_active_water_use'};
    bad.hass.states[id]={state:attack,attributes:{unit_of_measurement:attack}};
    bad.card._sig='';bad.card.hass=bad.hass;root=bad.card.shadowRoot;
    check(width+': manipulierte Titel und Gerätenamen bleiben Text',root.querySelector('h1').textContent===attack&&root.querySelector('h3').textContent===attack);
    check(width+': keine injizierten Elemente oder Event-Attribute',clean(root)&&window.__injected!==1);
    check(width+': Bild-URL kann Attribut nicht verlassen',!root.querySelector('img').hasAttribute('onerror'));
    const target=[...root.querySelectorAll('[data-more]')].find(el=>el.dataset.more===id), seen=[];
    bad.card.addEventListener('hass-more-info',e=>seen.push(e.detail.entityId));target.click();
    check(width+': Entity-Klick erhält ursprüngliche ID',seen[0]===id);
    check(width+': reine Darstellung erzeugt keine Steuerungsaufrufe',bad.calls.length===0);
    bad.card.remove();

    for(const fallback of [{running:false,valve:false},{running:false,manual:false}]){
      const f=fixture({width,...fallback}),start=f.card.shadowRoot.querySelector('[data-start]');
      check(width+': Fallback-Start nennt Controller-Vorgabe statt Minuten',f.card.shadowRoot.querySelectorAll('[data-start]').length===1&&start.dataset.min==='0'&&start.textContent.includes('Controller-Vorgabe'));
      start.click();await turn();
      check(width+': Standardlauf sendet nur expliziten Schalter-/Ventilauftrag',f.calls.length===1&&!('duration' in f.calls[0].data)&&!!f.calls[0].data.entity_id);
      f.card.remove();
    }
    const missing=fixture({width,manual:false,valve:false});
    missing.card._pending.zone1={kind:'start',accepted:false,until:Date.now()+90000};missing.card._sig='';missing.card.hass=missing.hass;
    check(width+': fehlendes Stopp-Ziel bleibt gesperrt',missing.card.shadowRoot.querySelector('[data-stop]').disabled);
    missing.card.remove();
  }
  return results;
}
"""


def main():
    with sync_playwright() as p:
        executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        browser = p.chromium.launch(**({"executable_path": executable} if executable else {}))
        page = browser.new_page(viewport={"width": 1000, "height": 1000})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        # Externe Bilder werden für diese Tests nicht abgerufen.
        page.route("**/*", lambda route: route.abort())
        page.set_content("<html><body></body></html>")
        source = (ROOT / "irrigation-control-card.js").read_text()
        page.add_script_tag(content=source, type="module")
        page.wait_for_function("() => customElements.get('irrigation-control-card')")
        results = page.evaluate(TEST_JS)
        results.append({"name": "Keine JavaScript-Fehler", "pass": not errors})
        results.append({
            "name": "Eigenständige Karte lässt alten Tag und alte Metadaten frei",
            "pass": page.evaluate("""() => !customElements.get('irrigation-card') &&
              !window.customCards.some(c=>c.type==='irrigation-card')"""),
        })
        for other_first in (True, False):
            coexist = browser.new_page()
            coexist_errors = []
            coexist.on("pageerror", lambda error: coexist_errors.append(str(error)))
            coexist.route("**/*", lambda route: route.abort())
            coexist.set_content("<html><body></body></html>")
            if other_first:
                coexist.add_script_tag(content=OTHER_CARD, type="module")
                coexist.add_script_tag(content=source, type="module")
            else:
                coexist.add_script_tag(content=source, type="module")
                coexist.add_script_tag(content=OTHER_CARD, type="module")
            # Inline-Module laufen asynchron: erst prüfen, wenn beide Karten registriert sind.
            coexist.wait_for_function("() => customElements.get('irrigation-control-card') && customElements.get('irrigation-card')")
            prefix = "Andere Karte zuerst" if other_first else "Eigene Karte zuerst"
            coexist_checks = coexist.evaluate("""() => {
              const own = customElements.get('irrigation-control-card');
              const other = customElements.get('irrigation-card');
              const entries = window.customCards.filter(c=>c.type==='irrigation-control-card');
              const a=document.createElement('irrigation-control-card');
              const b=document.createElement('irrigation-card');
              window.__ownClass=own;
              return [
                {name:'getrennte Konstruktoren',pass:!!own&&!!other&&own!==other},
                {name:'anderer Tag bleibt Eigentum der anderen Karte',pass:other===window.OtherIrrigationCard&&b.constructor===other},
                {name:'neuer Tag erzeugt bedienbare eigene Karte',pass:a.constructor===own&&!!a.shadowRoot&&typeof a.setConfig==='function'},
                {name:'beide Picker-Einträge und korrekter Repository-Link',pass:entries.length===1&&entries[0].name==='Irrigation Control Card'&&entries[0].documentationURL==='https://github.com/BeGiBue/home-assistant-irrigation-control-card'&&window.customCards.filter(c=>c.type==='irrigation-card').length===1},
              ];
            }""")
            for check in coexist_checks:
                results.append({"name": prefix + ": " + check["name"], "pass": check["pass"]})
            coexist.add_script_tag(content=source, type="module")
            results.append({
                "name": prefix + ": erneutes Laden bleibt ohne doppelte Registrierung",
                "pass": coexist.evaluate("""() => customElements.get('irrigation-control-card')===window.__ownClass&&
                  customElements.get('irrigation-card')===window.OtherIrrigationCard&&
                  window.customCards.length===2"""),
            })
            results.append({"name": prefix + ": keine JavaScript-Fehler", "pass": not coexist_errors})
            errors.extend(coexist_errors)
            coexist.close()
        out = ROOT / "tests" / "out"
        out.mkdir(exist_ok=True)
        for width in (350, 800):
            page.set_viewport_size({"width": width, "height": 1000})
            page.evaluate("""width => {
              document.body.style.cssText='margin:0;width:'+width+'px;--primary-text-color:#212121;--secondary-text-color:#727272;--card-background-color:#fff;';
              const c=document.createElement('irrigation-control-card');
              c.setConfig({title:'Bewässerung',zones:['zone1'],show_image:true});document.body.appendChild(c);
              c.hass={language:'de',states:{'binary_sensor.zone':{state:'on'},'switch.manual':{state:'on'},'sensor.remaining':{state:'12',attributes:{unit_of_measurement:'min'},last_changed:new Date().toISOString()},'switch.auto':{state:'on'}},
                devices:{zone1:{name:'Rasen',model:'Zone'}},entities:{a:{entity_id:'binary_sensor.zone',device_id:'zone1',platform:'hydrawise',translation_key:'watering'},b:{entity_id:'switch.manual',device_id:'zone1',platform:'hydrawise',translation_key:'manual_watering'},c:{entity_id:'sensor.remaining',device_id:'zone1',platform:'hydrawise',translation_key:'watering_time'},d:{entity_id:'switch.auto',device_id:'zone1',platform:'hydrawise',translation_key:'auto_watering'}},callService:async()=>{}};
              window.__preview=c;
            }""", width)
            page.wait_for_timeout(100)
            page.screenshot(path=str(out / f"irrigation-{width}.png"), full_page=True)
            page.evaluate("window.__preview.remove()")
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
