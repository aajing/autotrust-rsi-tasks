"""Original task-local adaptation of the pinned JEV recommendation recipe."""
import json
from pathlib import Path

def rank(query, broker):
    config=json.loads(Path(__file__).with_name('policy.json').read_text())
    history=query['history'][:config['max_history']]
    scores={}
    for candidate in query['candidates']:
        parts=['Previously rated generated images, in a fixed non-temporal presentation order:\n']
        for h in history:
            parts.append(f"User rating {h['rating']}/10. ")
            if 'text' in h: parts.append('Generation prompt: '+h['text']+'\n')
            if 'image' in h: parts.append({'image':h['image']})
        parts.append('\nCandidate image: ')
        if 'text' in candidate: parts.append('Generation prompt: '+candidate['text']+'\n')
        if 'image' in candidate: parts.append({'image':candidate['image']})
        scores[candidate['handle']]=broker.decide(parts,config['question'])
    return scores
