
import sqlite3, numpy as np, pandas as pd, header, queries, tqdm, re,copy
from textstat import textstat
from collections import defaultdict

boxes = [[] for _ in range(header.NUM_BINS)]
boxes_1sts = [[] for _ in range(header.NUM_BINS)]

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute(
        f'''
            SELECT BODY_TEXT
            FROM Posts
            WHERE (THREAD_ID BETWEEN ? AND ?)
        ''',
            (start,end)
        )

        for (body_text,) in tqdm.tqdm(list(cur.fetchall())):
            boxes[i].append(textstat.flesch_kincaid_grade(body_text))

        cur.execute(
            f'''
                    SELECT BODY_TEXT
                    FROM Posts
                    WHERE (THREAD_ID BETWEEN ? AND ?)
                        AND IS_1ST_IN_THREAD=TRUE
                ''',
            (start, end)
        )

        for (body_text,) in tqdm.tqdm(list(cur.fetchall())):
            boxes_1sts[i].append(textstat.flesch_kincaid_grade(body_text))

conn.close()

#

import matplotlib.pyplot as plt, boxplot

fig, (ax,ax_1sts) = plt.subplots(2,figsize=(9, 6))

ax.set_title(f'''All Posts’ Reading Levels (Top) and Threads’ 1st Posts’ Reading Levels (Bottom)\nFlesch–Kincaid Grade''', fontweight='bold')

ax.set_ylabel('Flesch–Kincaid Grade')
ax.set_ylim([1,8])

ax_1sts.set_ylabel('Flesch–Kincaid Grade')
ax_1sts.set_ylim([1,8])

# get dictionary returned from boxplot https://stackoverflow.com/questions/18861075/overlaying-the-numeric-value-of-median-variance-in-boxplots
bp_dict = ax.boxplot(boxes)
bp_1sts_dict = ax_1sts.boxplot(boxes)

xes = range(1, 1+len(boxes))
ax.set_xticks(xes, header.BINS_LABELS)
ax_1sts.set_xticks(xes, header.BINS_LABELS)

boxplot.plot_text(ax,boxes,bp_dict,-0.25,mode=2)
boxplot.plot_text(ax_1sts,boxes_1sts,bp_1sts_dict,-0.5,mode=2)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(range(len(header.BINS_SEPARATORS_TIMESTAMPS)),header.BINS_SEPARATORS_LABELS)

plt.subplots_adjust(top=0.825)

plt.savefig('graphs/dual_box_post_thread_reading_level.png',dpi=header.IMG_DPI)

plt.show()
