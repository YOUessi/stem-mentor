"""Curated read-only visible givens; never include teacher-only proof steps."""
import json
from functools import lru_cache
from pathlib import Path
from .catalog import PROBLEMS

PATH=Path(__file__).resolve().parents[2] / 'knowledge' / 'study_visuals.json'

@lru_cache(maxsize=1)
def visuals():
    data=json.loads(PATH.read_text(encoding='utf8'))
    if set(data)-set(PROBLEMS):
        raise ValueError('Visualization refers to unknown problem')
    for pid,card in data.items():
        if not card.get('latex') or len(card['latex'])>350:
            raise ValueError('Missing or oversized curated formula '+pid)
        scene=card.get('geometry')
        if scene and scene.get('kind') not in ('two_foci','conic'):
            raise ValueError('Unsupported public geometry scene '+pid)
    return data


def visual_for(problem_id):
    return visuals().get(problem_id)
