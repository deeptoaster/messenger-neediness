#!/usr/bin/python
import itertools as it
import json
import pandas as pd
from pathlib import Path
import sys

INBOX_DIR = Path("messages/inbox")

chats = [
    chat
    for chat in INBOX_DIR.iterdir()
    if len(sys.argv) < 2 or chat.name.partition("_")[0] in sys.argv[1:]
]
for chat in chats:
    messages = pd.concat(
        pd.json_normalize(json.load(open(chat_path)), "messages")
        for chat_path in it.takewhile(
            lambda chat_path: chat_path.exists(),
            (chat / f"message_{chat_index}.json" for chat_index in it.count(1)),
        )
    )
    print(messages)
