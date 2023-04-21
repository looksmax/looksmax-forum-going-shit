
import sqlite3, numpy as np, pandas as pd, header, queries, tqdm, re,copy
from collections import defaultdict

import boxplot

boxes = [[] for _ in range(header.NUM_BINS)]

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute(
        f'''
            SELECT POST_DATE,JOIN_DATE
            FROM Threads
            JOIN Members ON Members.MEMBER_ID=Threads.MEMBER_ID
            WHERE (THREAD_ID BETWEEN ? AND ?)
                AND 0<(
                    SELECT Count()
                    FROM Members
                    WHERE Members.MEMBER_ID=Threads.MEMBER_ID
                )
        ''',
            (start,end)
        )

        for (post_date,join_date) in tqdm.tqdm(list(cur.fetchall())):
            boxes[i].append((post_date - join_date) / 60 / 60 / 24)

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=header.BOX_DIMS)

ax.set_title(f'''Account Ages of Thread Starters (Days)\nAges at Post Times''', fontweight='bold')

ax.set_ylabel('Account Ages (Days)')
#ax.set_yscale('log')
ax.set_ylim([0,1700])

# get dictionary returned from boxplot https://stackoverflow.com/questions/18861075/overlaying-the-numeric-value-of-median-variance-in-boxplots
bp_dict = ax.boxplot(boxes)

xes = range(1, 1+len(boxes))
ax.set_xticks(xes, header.BINS_LABELS,**header.NARROW_FONT)

boxplot.plot_text(ax,boxes,bp_dict,-15)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(range(len(header.BINS_SEPARATORS_TIMESTAMPS)),header.BINS_SEPARATORS_LABELS,**header.NARROW_FONT)

plt.subplots_adjust(**header.BOX_FRAME_2_LINE_TITLE)

plt.savefig('graphs/box_thread_starter_account_age.png',dpi=header.IMG_DPI)

plt.show()
