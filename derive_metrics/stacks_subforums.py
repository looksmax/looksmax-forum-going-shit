
import sqlite3, numpy as np, pandas as pd, header, queries
from collections import defaultdict

subforums_counts = defaultdict(lambda: np.zeros(header.NUM_BINS))
bars_widths = header.BINS_TIMESPANS

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:
    cur = conn.cursor()

    for subforum_name in header.SUBFORUMS_NAMES:
        for i,(start,end) in enumerate(header.BINS_IDS_RANGES):
            cur.execute('''SELECT Count() FROM Threads WHERE SUBFORUM=? AND (THREAD_ID BETWEEN ? AND ?)''',(subforum_name,start,end))
            subforums_counts[subforum_name][i] = cur.fetchone()[0]

    print(subforums_counts)

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 6))
ax_t = ax.twiny()
ax.set_ylabel('Number of Threads in Sample')

bottom_offsets = np.zeros(header.NUM_BINS)

x_ticks = [header.BINS_SEPARATORS_TIMESTAMPS[0] + sum(header.BINS_TIMESPANS[:bindex]) + header.BINS_TIMESPANS[bindex]/2 for bindex in range(header.NUM_BINS)]

t_range = [header.BINS_SEPARATORS_TIMESTAMPS[0], header.BINS_SEPARATORS_TIMESTAMPS[-1]]
ax.set_aspect('auto')
ax.set_ylim([0, header.NUM_SAMPLES_PER_BIN])
ax.set_xticks(x_ticks, header.BINS_LABELS)
ax.set_xlim(t_range)

ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(header.BINS_SEPARATORS_TIMESTAMPS,header.BINS_SEPARATORS_LABELS)
ax_t.set_xlim(t_range)

for subforum_name, nums_threads_by_bin in subforums_counts.items():
    ax.bar(x_ticks, nums_threads_by_bin, header.BINS_TIMESPANS, label=subforum_name, bottom=bottom_offsets)
    bottom_offsets += nums_threads_by_bin

ax.set_title("Subforum Distribution by Bin", fontweight='bold')

ax.legend(loc="upper left")

plt.savefig('graphs/stacks_subforums.png',dpi=header.IMG_DPI)

plt.show()
