"""Reference wrapper; candidates never replace or import this executor."""
from pathlib import Path
from src.policy import load, rank as execute

def rank(query, broker):
    return execute(query, broker, load(Path(__file__).with_name('policy.json')))
