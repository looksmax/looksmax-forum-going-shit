
import sqlite3, numpy as np, pandas as pd, header, queries
from collections import defaultdict
from datetime import datetime

heatmap = np.zeros([header.NUM_BINS,24])
cols_widths = header.BINS_TIMESPANS

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute('''SELECT POST_DATE FROM Threads WHERE THREAD_ID BETWEEN ? AND ?''',(start,end))
        for (epoch,) in cur.fetchall():
            hour = datetime.utcfromtimestamp(epoch).hour
            heatmap[i][hour] += .5
            heatmap[i][(hour+1) % 24] += .25
            heatmap[i][(hour-1) % 24] += .25

conn.close()

#

heatmap = np.rot90(heatmap)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 6))

ax.set_title("Number of Threads Started per UTC Hour by Bin\nSmoothed by 1 Hour", fontweight='bold')
ax.set_ylabel('UTC Hour')

X,Y = np.meshgrid(
    np.cumsum(np.append([header.BINS_SEPARATORS_TIMESTAMPS[0]], cols_widths)),
    np.cumsum(np.append([0], np.ones(24)))
)

ax.pcolormesh(X,Y,heatmap) # displays matrix

ax.set_yticks(np.arange(0, 24, 1.0))
ax.invert_yaxis()

x_ticks = [header.BINS_SEPARATORS_TIMESTAMPS[0] + sum(header.BINS_TIMESPANS[:bindex]) + header.BINS_TIMESPANS[bindex]/2 for bindex in range(header.NUM_BINS)]
t_range = [header.BINS_SEPARATORS_TIMESTAMPS[0], header.BINS_SEPARATORS_TIMESTAMPS[-1]]
ax.set_aspect('auto')
ax.set_xticks(x_ticks, header.BINS_LABELS)
ax.set_xlim(t_range)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(header.BINS_SEPARATORS_TIMESTAMPS,header.BINS_SEPARATORS_LABELS)
ax_t.set_xlim(t_range)

plt.subplots_adjust(top=0.825)

plt.savefig('graphs/heatmap_thread_post_UTC_times.png',dpi=header.IMG_DPI)

plt.show()
