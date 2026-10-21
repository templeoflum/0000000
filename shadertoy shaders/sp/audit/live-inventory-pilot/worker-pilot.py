"""One bounded cloud extraction call; sanitized schemas only, no VJ access."""
from pathlib import Path
import contextlib, json, logging, os, sys, time

OUT = Path(__file__).resolve().parent
inventory = json.loads((OUT.parent / 'content-inventory-20260908/inventory.json').read_text())
addresses = ['L6C40', 'L5C39', 'L5C65']
selected = [next(c for c in inventory['clips'] if c['address'] == a) for a in addresses]
schemas = [{'id': f'fixture-{i+1}', 'source_controls': c['source_controls'],
            'source_numeric': c['source_numeric'],
            'effects': [{'name': e['display'], 'controls': e['controls']} for e in c['effects']]}
           for i, c in enumerate(selected)]
(OUT / 'worker-input.json').write_text(json.dumps(schemas, indent=2) + '\n')
prompt = '''Audit these sanitized parameter inventories. Return JSON only with a records array in input order.
For each record return id, exact source_controls (preserve spelling/case/order), effects (exact name and controls), source_numeric, listed_source_count, count_matches, observed_visual_behavior, inferred_candidates.
observed_visual_behavior MUST be "unknown: no rendered observation supplied". Neither parameter labels nor clip names/thumbnails establish visual behavior or cost. Do not classify geometry, visual family, fidelity, performance, or suitable live settings. There are no names or thumbnails here. No source code, parameter types, ranges or current values are supplied. Do not invent them.
inferred_candidates is at most two objects with control and hypothesis: select existing source controls only; label each hypothesis explicitly "Inference: ...; requires rendered observation". These are possible controls to inspect, not observed facts. Report count_matches strictly as listed_source_count == source_numeric; this is only a count comparison, not proof of a schema defect, since listed controls may not all be numeric.
Inventories:
''' + json.dumps(schemas, separators=(',', ':'))
alias = sys.argv[1] if len(sys.argv) > 1 else 'copilot'
provider, model = {'copilot': ('copilot', 'gpt-4o-mini-2024-07-18'), 'gflash': ('gemini', 'gemini-flash-latest'), 'local': ('ollama', 'qwen3:8b')}[alias]
result = {'worker': alias, 'model': model,
          'data_scope': 'Opaque IDs, source/effect control labels and counts only',
          'capability_scope': 'Single-trial schema extraction and uncertainty discipline; no rendered behavior or live operation tested',
          'local_gpu_used': alias == 'local', 'paid_fallback': False}
start = time.monotonic()
local_started = False
try:
    import requests
    if alias == 'local':
        ps = requests.get('http://127.0.0.1:11434/api/ps', timeout=5)
        ps.raise_for_status()
        already_loaded = any(m.get('name') == model or m.get('model') == model for m in ps.json().get('models', []))
        result['already_loaded'] = already_loaded
        local_started = not already_loaded
        response = requests.post('http://127.0.0.1:11434/api/chat',
            json={'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'format': 'json',
                  'stream': False, 'think': False, 'keep_alive': '5m',
                  'options': {'num_ctx': 4096, 'num_predict': 1600, 'temperature': 0}}, timeout=(8, 150))
    else:
        root = Path.home() / '.hermes'
        sys.path.insert(0, str(root / 'hermes-agent'))
        from dotenv import load_dotenv
        load_dotenv(root / '.env', override=False)
        logging.disable(logging.CRITICAL)
        from hermes_cli.runtime_provider import resolve_runtime_provider
        with open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            cfg = resolve_runtime_provider(requested=provider, target_model=result['model'])
        response = requests.post(cfg['base_url'].rstrip('/') + '/chat/completions',
            headers={'Authorization': 'Bearer ' + cfg['api_key']},
            json={'model': result['model'], 'messages': [{'role': 'user', 'content': prompt}],
                  'max_tokens': 1600, 'stream': False, 'temperature': 0}, timeout=(8, 65))
    if response.status_code != 200:
        result.update(status='provider unavailable', http_status=response.status_code)
    else:
        data = response.json()
        content = (data['message']['content'] if alias == 'local' else data['choices'][0]['message']['content']).strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0]
        answer = json.loads(content)
        records = answer.get('records', [])
        checks = {'record_count': len(records) == len(schemas)}
        for s in schemas:
            matches = [r for r in records if r.get('id') == s['id']]
            r = matches[0] if len(matches) == 1 else {}
            p = s['id'] + ':'
            checks[p+'source_controls'] = r.get('source_controls') == s['source_controls']
            checks[p+'effect_scope'] = r.get('effects') == s['effects']
            checks[p+'counts'] = (r.get('source_numeric') == s['source_numeric'] and
                r.get('listed_source_count') == len(s['source_controls']) and
                r.get('count_matches') is (len(s['source_controls']) == s['source_numeric']))
            checks[p+'observation_abstention'] = r.get('observed_visual_behavior') == 'unknown: no rendered observation supplied'
            candidates = r.get('inferred_candidates', [])
            checks[p+'inference_labeling'] = (len(candidates) <= 2 and all(
                c.get('control') in s['source_controls'] and c.get('hypothesis', '').startswith('Inference:') and
                'requires rendered observation' in c.get('hypothesis', '') for c in candidates))
        result.update(status='complete', answer=answer, checks=checks,
                      score=sum(checks.values()), max_score=len(checks), usage=({'prompt_tokens': data.get('prompt_eval_count'), 'completion_tokens': data.get('eval_count')} if alias == 'local' else data.get('usage', {})))
except Exception as exc:
    result.update(status='failed', error_type=type(exc).__name__)
finally:
    if local_started:
        try:
            stopped = requests.post('http://127.0.0.1:11434/api/generate', json={'model': model, 'keep_alive': 0}, timeout=20)
            stopped.raise_for_status()
            result['started_model_unloaded'] = True
        except Exception as exc:
            result['unload_error_type'] = type(exc).__name__
result['seconds'] = round(time.monotonic() - start, 2)
(OUT / ('worker-result-' + alias + '.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ['answer', 'usage']}))
