
import sqlite3, numpy as np, pandas as pd, header, queries
from collections import defaultdict

import boxplot

HOURS_THRESHOLD = 8

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
                ''' SELECT POST_DATE
                    FROM Posts
                    WHERE THREAD_ID=?
                    ORDER BY POST_DATE asc''',
                (thread_id,)
            )
            posts = list(cur.fetchall())

            last_active_epoch = thread_epoch
            for (post_epoch,) in posts:
                if post_epoch - last_active_epoch > 60 * 60 * HOURS_THRESHOLD:
                    break
                last_active_epoch = post_epoch

            boxes[i].append((last_active_epoch - thread_epoch) / 60)

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=header.BOX_DIMS)

ax.set_title(f'''Thread Lifespan (Minutes, Log Scale)
time between the initial post and the 1st reply that isn’t
followed by a subsequent reply within {HOURS_THRESHOLD} hours''', fontweight='bold')

ax.set_ylabel('Thread Lifespan (Minutes, Log Scale)')
ax.set_yscale('log')
ax.set_ylim([4,700])

# get dictionary returned from boxplot https://stackoverflow.com/questions/18861075/overlaying-the-numeric-value-of-median-variance-in-boxplots
bp_dict = ax.boxplot(boxes)

xes = range(1, 1+len(boxes))
ax.set_xticks(xes, header.BINS_LABELS,**header.NARROW_FONT)

boxplot.plot_text(ax,boxes,bp_dict,-0.1,1)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(range(len(header.BINS_SEPARATORS_TIMESTAMPS)),header.BINS_SEPARATORS_LABELS,**header.NARROW_FONT)

plt.subplots_adjust(**header.BOX_FRAME_3_LINE_TITLE)

plt.savefig('graphs/box_thread_lifespan.png',dpi=header.IMG_DPI)

plt.show()
