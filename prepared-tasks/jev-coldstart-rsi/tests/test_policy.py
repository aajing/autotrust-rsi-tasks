"""CPU fixtures for the actual declarative boundary; no GPU/model score claims."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from src.policy import admit, load, rank
from src.task import ROOT, read_jsonl


class RecordingBroker:
    def __init__(self):
        self.requests = []
    def decide(self, parts, question):
        self.requests.append((parts, question))
        return len(self.requests) / 21


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.b0 = load(ROOT / 'baseline/policy.json')
        self.queries = read_jsonl(ROOT / 'data/public/dev.jsonl')

    def test_every_score_is_fresh_broker_probability(self):
        for query in self.queries[:6]:
            broker = RecordingBroker()
            scores = rank(query, broker, self.b0)
            self.assertEqual(len(broker.requests), 20)
            self.assertEqual(scores, {c['handle']: (i + 1) / 21 for i, c in enumerate(query['candidates'])})
            for parts, _ in broker.requests:
                self.assertLessEqual(sum(isinstance(p, dict) for p in parts), 6)
            selected_ratings = [p for p in broker.requests[0][0] if isinstance(p, str) and p.startswith('User rating')]
            self.assertEqual(selected_ratings, [f"User rating {h['rating']}/10. " for h in query['history'][:5]])

    def test_attack_fields_and_types_are_rejected(self):
        for key in ('scores', 'ratings', 'answer_table', 'callback', 'file', 'source', 'user_id'):
            p = copy.deepcopy(self.b0); p[key] = {'c0': 10}
            with self.assertRaises(ValueError): admit(p)
        for n in (0, 8, True, 3.5):
            p = copy.deepcopy(self.b0); p['max_history'] = n
            with self.assertRaises(ValueError): admit(p)
        for bad in (float('nan'), float('inf'), '0', True):
            p = copy.deepcopy(self.b0); p['selector']['weights'][0] = bad
            with self.assertRaises(ValueError): admit(p)
        p = copy.deepcopy(self.b0); p['intro'] = 'a' * 513
        with self.assertRaises(ValueError): admit(p)

    def test_load_rejects_duplicate_keys_and_oversized_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'policy.json'
            p.write_text('{"version":1,"version":1}')
            with self.assertRaises(ValueError): load(p)
            p.write_text(' ' * 262145)
            with self.assertRaises(ValueError): load(p)

    def test_mlp_changes_evidence_without_returning_scores(self):
        p = copy.deepcopy(self.b0)
        p['selector'] = {'kind': 'mlp', 'layers': [
            {'weight': [[1, 0, 0, 0, 0, 0]], 'bias': [0]},
            {'weight': [[1]], 'bias': [0]}, {'weight': [[1]], 'bias': [0]}]}
        p['max_history'] = 1
        query = next(q for q in self.queries if q['cell'] == 'text-20')
        broker = RecordingBroker(); scores = rank(query, broker, p)
        selected = [s for s in broker.requests[0][0] if isinstance(s, str) and s.startswith('User rating')]
        self.assertEqual(selected, [f"User rating {max(h['rating'] for h in query['history'])}/10. "])
        self.assertEqual(len(scores), 20)
        p['selector']['layers'][-1]['bias'] = [0, 1]
        with self.assertRaises(ValueError): admit(p)

    def test_invalid_native_output_is_unscored_not_replaced(self):
        class InvalidBroker:
            def decide(self, *args): return float('nan')
        with self.assertRaises(ValueError): rank(self.queries[0], InvalidBroker(), self.b0)


if __name__ == '__main__': unittest.main()
