#!/usr/bin/python
import itertools as it
import json
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

DELAYED_MESSAGE_THRESHOLD = pd.Timedelta(600, "s")
DOUBLE_MESSAGE_THRESHOLD = pd.Timedelta(600, "s")

for chat in Path(sys.argv[1]).iterdir():
    if len(sys.argv) < 3 or chat.name.partition("_")[0] in sys.argv[2:]:
        messages = pd.concat(
            pd.json_normalize(json.load(open(chat_path)), "messages")[
                ["sender_name", "timestamp_ms"]
            ]
            for chat_path in it.takewhile(
                lambda chat_path: chat_path.exists(),
                (chat / f"message_{chat_index}.json" for chat_index in it.count(1)),
            )
        )[::-1]
        messages.sender_name = messages.sender_name.apply(
            lambda name: name.encode("raw_unicode_escape").decode("utf-8")
        )
        messages["timestamp"] = pd.to_datetime(messages["timestamp_ms"], unit="ms")
        messages["delayed"] = (
            messages["timestamp"].diff() >= DELAYED_MESSAGE_THRESHOLD
        ) & (messages["sender_name"] != messages["sender_name"].shift())
        messages["double"] = (
            messages["timestamp"].diff() >= DOUBLE_MESSAGE_THRESHOLD
        ) & (messages["sender_name"] == messages["sender_name"].shift())
        messages["count"] = 1
        messages = messages.set_index("timestamp").drop("timestamp_ms", axis="columns")
        messages_aggregated = (
            messages.groupby("sender_name").resample("D").sum().unstack(0)
        )
        messages_aggregated["delayed"].plot.area(
            sharey=True, subplots=True, title="Delayed Messages", xlabel="Date"
        )
        messages_aggregated["double"].plot.area(
            sharey=True, subplots=True, title="Double Messages", xlabel="Date"
        )
        messages_aggregated["count"].plot.area(
            sharey=True, subplots=True, title="Message Count", xlabel="Date"
        )
plt.show()
