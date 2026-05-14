#!/usr/bin/env python3
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timedelta

STATE_PATH = pathlib.Path(__file__).resolve().parent.parent / 'memory' / 'janice-chat-watch-state.json'
CHAT_ID = '77'
ALLOWED_SENDERS = {'+4528272620', '+4528861200'}
WAKE_PATTERN = re.compile(r'^\s*hej\s+jason\b', re.IGNORECASE)
DIRECT_PATTERN = re.compile(r'(?:^|\b)(hej\s+jason|jason[,!:]?|skriv\s+lige|kan\s+du|vil\s+du|lav\s+en\s+task|tilføj\s+(?:en\s+)?(?:task|opgave|chore)|opret\s+(?:en\s+)?(?:task|opgave|chore))', re.IGNORECASE)


def normalize_sender(value: str) -> str:
    digits = ''.join(ch for ch in str(value or '') if ch.isdigit())
    if digits.startswith('45') and len(digits) == 10:
        return '+' + digits
    if len(digits) == 8:
        return '+45' + digits
    return str(value or '').strip()


def is_allowed_sender(sender: str) -> bool:
    return normalize_sender(sender) in {normalize_sender(x) for x in ALLOWED_SENDERS}


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {'last_rowid': 0, 'awake_until': None}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


def send_chat(text):
    subprocess.run(['imsg', 'send', '--chat-id', CHAT_ID, '--text', text], check=False)


def parse_messages(since_rowid):
    out = subprocess.check_output(['imsg', 'history', '--chat-id', CHAT_ID, '--limit', '20', '--json'], text=True)
    msgs = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except Exception:
            continue
        if int(item.get('id', 0) or 0) > since_rowid:
            msgs.append(item)
    msgs.sort(key=lambda x: int(x.get('id', 0) or 0))
    return msgs


def main():
    state = load_state()
    last_rowid = int(state.get('last_rowid') or 0)
    awake_until_raw = state.get('awake_until')
    awake_until = None
    if awake_until_raw:
        try:
            awake_until = datetime.fromisoformat(awake_until_raw)
        except Exception:
            awake_until = None

    msgs = parse_messages(last_rowid)
    for msg in msgs:
        rowid = int(msg.get('id', 0) or 0)
        state['last_rowid'] = max(int(state.get('last_rowid') or 0), rowid)

        if msg.get('is_from_me'):
            continue
        sender = str(msg.get('sender') or '').strip()
        sender_norm = normalize_sender(sender)
        text = str(msg.get('text') or '').strip()
        if not sender or not text:
            continue

        if (WAKE_PATTERN.search(text) or DIRECT_PATTERN.search(text)) and is_allowed_sender(sender_norm):
            awake_until = datetime.now() + timedelta(minutes=15)
            state['awake_until'] = awake_until.isoformat()
            if WAKE_PATTERN.search(text):
                send_chat('Hej — jeg lytter. — Jason')
            continue

        if (WAKE_PATTERN.search(text) or DIRECT_PATTERN.search(text)) and not is_allowed_sender(sender_norm):
            send_chat('Jeg reagerer kun på Nikolaj og Janice. — Jason')
            continue

    save_state(state)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'watcher error: {e}', file=sys.stderr)
        sys.exit(1)
