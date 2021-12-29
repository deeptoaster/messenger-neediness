#!/usr/bin/python
import itertools as it
import json
import matplotlib.pyplot as plt
import pandas as pd
import sys

DELAYED_MESSAGE_THRESHOLD = pd.Timedelta(600, "s")
DOUBLE_MESSAGE_THRESHOLD = pd.Timedelta(600, "s")

for chat in json.load(open(sys.argv[1]))["chats"]["list"]:
    if (
        len(sys.argv) < 3
        or "name" in chat
        and chat["name"] in sys.argv[2:]
        or str(chat["id"]) in sys.argv[2:]
    ):
        messages = pd.json_normalize(chat, "messages")[["date", "from"]]
        messages["timestamp"] = pd.to_datetime(messages["date"])
        messages["delayed"] = (
            messages["timestamp"].diff() >= DELAYED_MESSAGE_THRESHOLD
        ) & (messages["from"] != messages["from"].shift())
        messages["double"] = (
            messages["timestamp"].diff() >= DOUBLE_MESSAGE_THRESHOLD
        ) & (messages["from"] == messages["from"].shift())
        messages["count"] = 1
        messages = messages.set_index("timestamp").drop("date", axis="columns")
        messages_aggregated = messages.groupby("from").resample("D").sum().unstack(0)
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
