'''
import sys
print(sys.path)
'''
import sqlite3, numpy as np, pandas as pd, header, queries, tqdm, re,copy
from collections import defaultdict

HOURS_THRESHOLD = 48

boxes = [[] for _ in range(header.NUM_BINS)]

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute(
        f'''
            SELECT (
                SELECT (
                    SELECT Count(*)
                    FROM Reacts
                    WHERE Reacts.POST_ID = Posts.POST_ID
                        AND REACT_DATE <= Posts.POST_DATE + {60*60*HOURS_THRESHOLD}
                ) REACTS_COUNT
                FROM Posts
                WHERE Posts.THREAD_ID = Threads.THREAD_ID
                    AND IS_1ST_IN_THREAD = TRUE
            ) REACTS_COUNT
            FROM Threads
            WHERE (THREAD_ID BETWEEN ? AND ?)
        ''',
            (start,end)
        )

        for (n_reacts,) in tqdm.tqdm(list(cur.fetchall())):
            boxes[i].append(n_reacts)

conn.close()

#

import matplotlib.pyplot as plt, boxplot

fig, ax = plt.subplots(figsize=(9, 6))

ax.set_title(f'''Number of Reacts on 1st Post in Thread in 1st {HOURS_THRESHOLD} Hours''', fontweight='bold')

ax.set_ylabel('Number of Reacts')
#ax.set_yscale('log')
ax.set_ylim([-1,10])

# get dictionary returned from boxplot https://stackoverflow.com/questions/18861075/overlaying-the-numeric-value-of-median-variance-in-boxplots
bp_dict = ax.boxplot(boxes)

xes = range(1, 1+len(boxes))
ax.set_xticks(xes, header.BINS_LABELS)

boxplot.plot_text(ax,boxes,bp_dict,-0.1,1)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(range(len(header.BINS_SEPARATORS_TIMESTAMPS)),header.BINS_SEPARATORS_LABELS)

plt.subplots_adjust(top=0.85)

plt.savefig('graphs/box_thread_1st_message_reacts_count_48h.png',dpi=header.IMG_DPI)

plt.show()
