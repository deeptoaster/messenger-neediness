#!/usr/bin/python
import itertools as it
import json
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

DELAYED_MESSAGE_THRESHOLD_S = 600
DOUBLE_MESSAGE_THRESHOLD_S = 600
INBOX_DIR = Path("messages/inbox")

chats = [
    chat
    for chat in INBOX_DIR.iterdir()
    if len(sys.argv) < 2 or chat.name.partition("_")[0] in sys.argv[1:]
]
for chat in chats:
    messages = pd.concat(
        pd.json_normalize(json.load(open(chat_path)), "messages")[
            ["sender_name", "timestamp_ms", "content"]
        ]
        for chat_path in it.takewhile(
            lambda chat_path: chat_path.exists(),
            (chat / f"message_{chat_index}.json" for chat_index in it.count(1)),
        )
    )[::-1]
    messages["timestamp"] = pd.to_datetime(messages["timestamp_ms"], unit="ms")
    messages["delayed"] = (
        messages["timestamp_ms"].diff() >= DELAYED_MESSAGE_THRESHOLD_S * 1000
    ) & (messages["sender_name"] != messages["sender_name"].shift())
    messages["double"] = (
        messages["timestamp_ms"].diff() >= DOUBLE_MESSAGE_THRESHOLD_S * 1000
    ) & (messages["sender_name"] == messages["sender_name"].shift())
    messages = messages.set_index("timestamp").drop("timestamp_ms", "columns")
    messages_aggregated = messages.groupby("sender_name").resample("D").sum().unstack(0)
    messages_aggregated["double"].plot.area(subplots=True)
    messages_aggregated["delayed"].plot.area(subplots=True)
plt.show()
