
import sqlite3, numpy as np, pandas as pd, header, queries, tqdm, re,copy
from textstat import textstat
from collections import defaultdict

x = []
y = []
categories = []
colors = []

import matplotlib
cmap = matplotlib.cm.get_cmap('viridis')

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute(
        f'''
            SELECT POST_DATE, JOIN_DATE,
                (
                    SELECT Count(*) FROM Posts
                    WHERE Posts.THREAD_ID=T.THREAD_ID
                        AND IS_1ST_IN_THREAD=FALSE
                ) N_REPLIES
            FROM Threads T
            JOIN Members ON Members.MEMBER_ID=T.MEMBER_ID
            WHERE (THREAD_ID BETWEEN ? AND ?)
                AND 0<(
                    SELECT Count(*) FROM Members
                    WHERE Members.MEMBER_ID=T.MEMBER_ID
                )
        ''',
            (start,end)
        )

        for (post_epoch,join_epoch,n_replies) in tqdm.tqdm(list(cur.fetchall())):
            x.append(n_replies)
            y.append((post_epoch - join_epoch) / 60 / 60 / 24)
            categories.append(header.BINS_LABELS[i])
            colors.append(cmap(i / (header.NUM_BINS-1)))

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 6))

ax.set_title(f'''Thread’s Number of Replies (X, log scale) vs\nThread Starter’s Account Age (Y, Days)''', fontweight='bold')

ax.set_xlabel('Number of Replies')
ax.set_xscale('log')
#ax.set_xlim([1,15])

ax.set_ylabel('Thread Starter’s Account Age (Days)')
#ax.set_yscale('log')
#ax.set_ylim([0,1000])

ALPHA = 0.75

for cat in header.BINS_LABELS:
    ax.scatter(
        x=[x for i,x in enumerate(x) if categories[i] == cat],
        y=[x for i,x in enumerate(y) if categories[i] == cat],
        label=cat,
        c=[x for i,x in enumerate(colors) if categories[i] == cat],
        alpha=ALPHA
    )

plt.subplots_adjust(top=0.9)

ax.legend(loc="upper right")

plt.savefig('graphs/scatter_thread_replies_count_vs_thread_starter_account_age.png',dpi=header.IMG_DPI)

plt.show()
