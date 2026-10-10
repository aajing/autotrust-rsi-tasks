"""Evaluator-owned declarative policy admission and model-mediated ranking.

Candidates are data, never imported Python. Every final score is a fresh native
S1 probability; candidate parameters influence only the evidence and question.
Public benchmark labels may inform artifact fitting and selection in Work.
"""
import json
import math
import re
from pathlib import Path

FEATURES = ('rating', 'position', 'text_length', 'lexical_overlap', 'centered_rating', 'rating_extremity')


def finite(x):
    return type(x) in (int, float) and math.isfinite(x)


def admit(policy):
    if not isinstance(policy, dict) or set(policy) != {'version', 'max_history', 'intro', 'question', 'selector'}:
        raise ValueError('Strict policy schema: no code, outputs, lookups, IDs or paths')
    if type(policy['version']) is not int or policy['version'] != 1:
        raise ValueError('Unsupported policy version')
    if type(policy['max_history']) is not int or not 1 <= policy['max_history'] <= 7:
        raise ValueError('History count must fit the fixed 8-image envelope')
    for name in ('intro', 'question'):
        s = policy[name]
        if not isinstance(s, str) or not 1 <= len(s) <= 512 or any(ord(x) < 32 and x not in '\n\t' for x in s):
            raise ValueError('Global prompt must contain 1..512 printable characters')
    s = policy['selector']
    if not isinstance(s, dict):
        raise ValueError('Selector must be an object')
    if s.get('kind') == 'linear':
        if set(s) != {'kind', 'weights'} or not isinstance(s['weights'], list) or len(s['weights']) != len(FEATURES) or any(not finite(v) for v in s['weights']):
            raise ValueError('Invalid linear history selector')
    elif s.get('kind') == 'mlp':
        if set(s) != {'kind', 'layers'} or not isinstance(s['layers'], list) or len(s['layers']) != 3:
            raise ValueError('MLP requires two hidden layers and one output')
        previous, count = len(FEATURES), 0
        for i, layer in enumerate(s['layers']):
            if not isinstance(layer, dict) or set(layer) != {'weight', 'bias'}:
                raise ValueError('Invalid layer schema')
            w, b = layer['weight'], layer['bias']
            if not isinstance(w, list) or not isinstance(b, list) or len(w) != len(b) or not 1 <= len(w) <= 32 or (i == 2 and len(w) != 1):
                raise ValueError('Invalid layer width')
            if any(not isinstance(row, list) or len(row) != previous or any(not finite(x) for x in row) for row in w) or any(not finite(x) for x in b):
                raise ValueError('Invalid or nonfinite layer coefficients')
            count += len(w) * (previous + 1)
            previous = len(w)
        if count > 4096:
            raise ValueError('Too many numeric parameters')
    else:
        raise ValueError('Unsupported history selector')
    return policy


def load(path):
    path = Path(path)
    if path.stat().st_size > 262144:
        raise ValueError('Policy file exceeds 256 KiB')
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('Duplicate JSON key')
            d[k] = v
        return d
    return admit(json.loads(path.read_text(), object_pairs_hook=pairs))


def features(history, candidate, index, count, mean_rating):
    def words(row):
        return set(re.findall(r'\w+', row.get('text', '').casefold()))
    a, b = words(history), words(candidate)
    overlap = len(a & b) / len(a | b) if a or b else 0.0
    rating = history['rating']
    return [rating / 10, index / max(1, count - 1), min(len(history.get('text', '')), 2048) / 2048,
            overlap, (rating - mean_rating) / 10, abs(rating - mean_rating) / 10]


def priority(selector, values):
    if selector['kind'] == 'linear':
        result = sum(w*x for w, x in zip(selector['weights'], values))
    else:
        for i, layer in enumerate(selector['layers']):
            values = [sum(w*x for w, x in zip(row, values)) + b for row, b in zip(layer['weight'], layer['bias'])]
            if any(not math.isfinite(x) for x in values):
                raise ValueError('Nonfinite selector activation')
            if i < 2:
                values = [max(0, x) for x in values]
        result = values[0]
    if not math.isfinite(result):
        raise ValueError('Nonfinite selector priority')
    return result


def rank(query, broker, policy):
    """Fixed executor: no candidate callback, score transform or state access."""
    admit(policy)
    history = query['history']
    mean = sum(h['rating'] for h in history) / len(history)
    scores = {}
    for candidate in query['candidates']:
        selected = sorted(range(len(history)), key=lambda i: (-priority(policy['selector'], features(history[i], candidate, i, len(history), mean)), i))[:policy['max_history']]
        # Keep original presentation order once the evidence subset is chosen.
        parts = [policy['intro'] + '\n']
        for i in sorted(selected):
            h = history[i]
            parts.append(f"User rating {h['rating']}/10. ")
            if 'text' in h:
                parts.append('Generation prompt: ' + h['text'] + '\n')
            if 'image' in h:
                parts.append({'image': h['image']})
        parts.append('\nCandidate image: ')
        if 'text' in candidate:
            parts.append('Generation prompt: ' + candidate['text'] + '\n')
        if 'image' in candidate:
            parts.append({'image': candidate['image']})
        probability = broker.decide(parts, policy['question'])
        if not finite(probability) or not 0 <= probability <= 1:
            raise ValueError('Invalid native model probability')
        scores[candidate['handle']] = probability
    return scores
