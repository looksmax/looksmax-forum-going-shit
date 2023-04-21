
import sqlite3, numpy as np, pandas as pd, header, queries
from collections import defaultdict

import boxplot

boxes = [[] for _ in range(header.NUM_BINS)]

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute(
        ''' SELECT THREAD_ID
            FROM Threads
            WHERE THREAD_ID BETWEEN ? AND ?''',
            (start,end)
        )

        threads = list(cur.fetchall())

        for (thread_id,) in threads:
            cur.execute(
                ''' SELECT MEMBER_ID
                    FROM Posts
                    WHERE THREAD_ID=?
                    ORDER BY POST_DATE asc''',
                (thread_id,)
            )
            results = list(cur.fetchall())
            m_ids = [r[0] for r in results]
            boxes[i].append(len(set(m_ids)) / len(results))

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 6))

ax.set_title(f'''Thread Conversationality
Ratio of Thread’s Unique Participants to Thread’s Total Posts
Smaller Numbers = More Conversational''', fontweight='bold')

ax.set_ylabel('Ratio of Thread’s Unique Participants to Thread’s Total Posts')
#ax.set_yscale('log')
#ax.set_ylim([4,700])

# get dictionary returned from boxplot https://stackoverflow.com/questions/18861075/overlaying-the-numeric-value-of-median-variance-in-boxplots
bp_dict = ax.boxplot(boxes)

xes = range(1, 1+len(boxes))
ax.set_xticks(xes, header.BINS_LABELS)

boxplot.plot_text(ax,boxes,bp_dict,-0.05,1)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(range(len(header.BINS_SEPARATORS_TIMESTAMPS)),header.BINS_SEPARATORS_LABELS)

plt.subplots_adjust(top=0.8)

plt.savefig('graphs/box_thread_unique_participants_count_over_posts_count.png',dpi=header.IMG_DPI)

plt.show()
