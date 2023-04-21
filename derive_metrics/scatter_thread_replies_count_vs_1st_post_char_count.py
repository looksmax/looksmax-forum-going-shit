
import sqlite3, numpy as np, pandas as pd, header, queries, tqdm, re,copy
from textstat import textstat
from collections import defaultdict

import boxplot

x = []
y = []
z = []

import matplotlib
cmap = matplotlib.cm.get_cmap('viridis')

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute(
        f'''
            SELECT _BODY_LENGTH,POST_DATE,
                (
                    SELECT Count(*) FROM Posts
                    WHERE Posts.THREAD_ID=P.THREAD_ID
                        AND IS_1ST_IN_THREAD=FALSE
                ) N_REPLIES
            FROM Posts P
            WHERE (THREAD_ID BETWEEN ? AND ?)
                AND IS_1ST_IN_THREAD=TRUE
        ''',
            (start,end)
        )

        for (body_length,epoch,n_replies) in tqdm.tqdm(list(cur.fetchall())):
            x.append(n_replies)
            y.append(body_length)
            z.append(epoch)

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=header.SCATTER_DIMS)

ax.set_title(f'''Thread’s Number of Replies (X, log scale) vs\nThread’s 1st Post’s Character Count (Y, log scale)''', fontweight='bold')

ax.set_xlabel('Thread’s Number of Replies')
ax.set_xscale('log')
#ax.set_xlim([1,15])

ax.set_ylabel('Thread’s 1st Post’s Character Count')
ax.set_yscale('log')
#ax.set_ylim([0,20])

ALPHA = 0.75

scatter = ax.scatter(
    x=x,
    y=y,
    c=z,
    cmap=cmap,
    alpha=ALPHA
)

boxplot.color_bar(fig,scatter)

plt.subplots_adjust(**header.SCATTER_FRAME_2_LINE_TITLE)

plt.savefig('graphs/scatter_thread_replies_count_vs_1st_post_char_count.png',dpi=header.IMG_DPI)

plt.show()
