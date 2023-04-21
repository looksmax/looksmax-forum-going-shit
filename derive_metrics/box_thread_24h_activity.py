'''
import sys
print(sys.path)
'''
import sqlite3, numpy as np, pandas as pd, header, queries
from collections import defaultdict

import boxplot

HOURS_THRESHOLD = 24

boxes = [[] for _ in range(header.NUM_BINS)]

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute(
        ''' SELECT THREAD_ID, POST_DATE
            FROM Threads
            WHERE THREAD_ID BETWEEN ? AND ?''',
            (start,end)
        )

        threads = list(cur.fetchall())

        for (thread_id,thread_epoch) in threads:
            cur.execute(
                ''' SELECT Count()
                    FROM Posts
                    WHERE THREAD_ID=?
                        AND POST_DATE<=?
                        AND IS_1ST_IN_THREAD=FALSE''',
                (thread_id,thread_epoch + 60*60*24*HOURS_THRESHOLD)
            )

            boxes[i].append(cur.fetchone()[0])

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=header.BOX_DIMS)

ax.set_title(f'''Number of Replies in Thread in 1st {HOURS_THRESHOLD} Hours''', fontweight='bold')

ax.set_ylabel('Number of Replies')
#ax.set_yscale('log')
ax.set_ylim([-1,50])

# get dictionary returned from boxplot https://stackoverflow.com/questions/18861075/overlaying-the-numeric-value-of-median-variance-in-boxplots
bp_dict = ax.boxplot(boxes)

xes = range(1, 1+len(boxes))
ax.set_xticks(xes, header.BINS_LABELS,**header.NARROW_FONT)

boxplot.plot_text(ax,boxes,bp_dict,-1)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(range(len(header.BINS_SEPARATORS_TIMESTAMPS)),header.BINS_SEPARATORS_LABELS,**header.NARROW_FONT)

plt.subplots_adjust(**header.BOX_FRAME_1_LINE_TITLE)

plt.savefig('graphs/box_thread_24h_activity.png',dpi=header.IMG_DPI)

plt.show()
