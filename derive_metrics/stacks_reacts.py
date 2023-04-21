
import sqlite3, numpy as np, pandas as pd, header, queries
from collections import defaultdict

import boxplot

prefixes_counts = defaultdict(lambda: np.zeros(header.NUM_BINS))
bars_widths = header.BINS_TIMESPANS

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:
    cur = conn.cursor()
    cur.execute('''SELECT REACT_TYPE,Count(*) AS Frequency FROM Reacts GROUP BY REACT_TYPE ORDER BY Count(*) DESC''')
    reacts_types = [result[0] for result in cur.fetchall() if result[0]]
    print(reacts_types)
    for r_type in reacts_types:
        for i,(start,end) in enumerate(header.BINS_IDS_RANGES):
            cur.execute('''
            SELECT Count()
            FROM Reacts
            WHERE REACT_TYPE=?
                AND 0<(SELECT Count()
                    FROM Posts
                    WHERE Posts.POST_ID=Reacts.POST_ID
                        AND (Posts.THREAD_ID BETWEEN ? AND ?)
                )
            ''',(r_type,start,end))
            prefixes_counts[r_type][i] = cur.fetchone()[0]

    print(prefixes_counts)

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))
ax_t = ax.twiny()
ax.set_ylabel('Number of Reacts')

bottom_offsets = np.zeros(header.NUM_BINS)

x_ticks = [header.BINS_SEPARATORS_TIMESTAMPS[0] + sum(header.BINS_TIMESPANS[:bindex]) + header.BINS_TIMESPANS[bindex]/2 for bindex in range(header.NUM_BINS)]

t_range = [header.BINS_SEPARATORS_TIMESTAMPS[0], header.BINS_SEPARATORS_TIMESTAMPS[-1]]

ax.set_aspect('auto')

#ax.set_ylim([0, header.NUM_SAMPLES_PER_BIN])

ax.set_xticks(x_ticks, header.BINS_LABELS)
ax.set_xlim(t_range)

ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(header.BINS_SEPARATORS_TIMESTAMPS,header.BINS_SEPARATORS_LABELS)
ax_t.set_xlim(t_range)

for prefix, nums_threads_by_bin in prefixes_counts.items():
    ax.bar(x_ticks, nums_threads_by_bin, header.BINS_TIMESPANS, label=prefix if prefix else '<none>', bottom=bottom_offsets)
    bottom_offsets += nums_threads_by_bin

ax.set_title("React Volume by Type by Bin", fontweight='bold')
ax.legend(loc="lower left")

boxplot.stagger(ax)
boxplot.stagger(ax_t)

plt.subplots_adjust(**header.STACKS_FRAME_1_LINE_TITLE)

plt.savefig('graphs/stacks_reacts.png',dpi=header.IMG_DPI)

plt.show()
