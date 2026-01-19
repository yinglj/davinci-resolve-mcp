"""ScriptToShots POC

Simple heuristic parser to convert natural-language script into a shot list.
This POC focuses on clarity and testability rather than advanced NLP.
"""

from typing import List, Dict
import re

SENTENCE_SPLIT_REGEX = re.compile(r'(?<=[.!?])\s+')

SHOT_TYPE_KEYWORDS = {
    'close': ['close up', 'cu', 'close-up', 'closeup'],
    'wide': ['wide shot', 'wide', 'ws', 'establishing'],
    'medium': ['medium shot', 'medium', 'ms'],
    'insert': ['insert'],
    'pan': ['pan to', 'pan'],
    'tilt': ['tilt'],
}


def _guess_duration_from_text(text: str) -> int:
    """Simple heuristic: estimate duration in seconds based on word/sentence counts."""
    text = text.strip()
    if not text:
        return 2
    sentences = SENTENCE_SPLIT_REGEX.split(text)
    sentences = [s for s in sentences if s.strip()]
    num_sentences = len(sentences)
    num_words = len(text.split())

    if num_sentences >= 3 or num_words > 50:
        return 8
    if num_sentences == 2 or (20 <= num_words <= 50):
        return 5
    return 3


def _detect_shot_type(text: str) -> str:
    t = text.lower()
    for shot_type, keys in SHOT_TYPE_KEYWORDS.items():
        for k in keys:
            if k in t:
                return shot_type
    return 'unknown'


def parse_script_to_shots(script_text: str) -> List[Dict]:
    """Parse script text into a list of shot dicts.

    Output dict fields:
      - id: shot sequential id (e.g., shot_001)
      - summary: short summary (first sentence or truncated)
      - duration: estimated duration in seconds (int)
      - shot_type: guessed shot type
      - notes: original text for that shot
      - assets_needed: empty list for now
    """
    # Normalize newlines
    text = script_text.replace('\r\n', '\n').strip()
    if not text:
        return []

    # Split into paragraphs by blank lines or explicit shot separators
    blocks = []
    # Recognize "Shot 1:", numbered lists, or blank-line separated paragraphs
    lines = text.split('\n')
    current = []
    for line in lines:
        striped = line.strip()
        if re.match(r'^(shot\s*\d+[:\.-]?)', striped, re.I):
            # Start new block when a shot heading appears
            if current:
                blocks.append(' '.join(current).strip())
                current = [re.sub(r'^(shot\s*\d+[:\.-]?)', '', striped, flags=re.I).strip()]
            else:
                current = [re.sub(r'^(shot\s*\d+[:\.-]?)', '', striped, flags=re.I).strip()]
        elif striped == '':
            if current:
                blocks.append(' '.join(current).strip())
                current = []
        else:
            # Scene headings like INT./EXT. usually indicate a new block
            if re.match(r'^(int\.|ext\.|scene\s+\d+)', striped, re.I):
                if current:
                    blocks.append(' '.join(current).strip())
                current = [striped]
            else:
                current.append(striped)
    if current:
        blocks.append(' '.join(current).strip())

    # As fallback if no blocks found, split by sentences into shots
    if not blocks:
        sentences = SENTENCE_SPLIT_REGEX.split(text)
        blocks = [s.strip() for s in sentences if s.strip()]

    # Optionally further split long blocks into multiple shots by sentence
    shots = []
    shot_counter = 1
    for blk in blocks:
        # If block is very long, split into sentences of reasonable size
        sentences = SENTENCE_SPLIT_REGEX.split(blk)
        if len(sentences) > 2:
            # create per-sentence shots
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                shot = {
                    'id': f'shot_{shot_counter:03d}',
                    'summary': (s if len(s) <= 120 else (s[:117] + '...')),
                    'duration': _guess_duration_from_text(s),
                    'shot_type': _detect_shot_type(s),
                    'notes': s,
                    'assets_needed': []
                }
                shots.append(shot)
                shot_counter += 1
        else:
            s = blk
            shot = {
                'id': f'shot_{shot_counter:03d}',
                'summary': (s if len(s) <= 120 else (s[:117] + '...')),
                'duration': _guess_duration_from_text(s),
                'shot_type': _detect_shot_type(s),
                'notes': s,
                'assets_needed': []
            }
            shots.append(shot)
            shot_counter += 1

    return shots
