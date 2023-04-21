
import sqlite3, numpy as np, pandas as pd, header, queries
from collections import defaultdict

import boxplot

title_begin_char_types_counts = defaultdict(lambda: np.zeros(header.NUM_BINS))
bars_widths = header.BINS_TIMESPANS

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute('''
        SELECT Count()
        FROM Threads
        WHERE 1==(SELECT Count() FROM Posts WHERE Posts.THREAD_ID=Threads.THREAD_ID)
            AND (THREAD_ID BETWEEN ? AND ?)''',(start,end))
        title_begin_char_types_counts['0 Replies'][i] = cur.fetchone()[0]

        cur.execute('''
                SELECT Count()
                FROM Threads
                WHERE 0=(SELECT Count() FROM Posts WHERE Posts.THREAD_ID=Threads.THREAD_ID AND Posts.MEMBER_ID != Threads.MEMBER_ID)
                    AND 1<(SELECT Count() FROM Posts WHERE Posts.THREAD_ID=Threads.THREAD_ID)
                    AND (THREAD_ID BETWEEN ? AND ?)''', (start, end))
        title_begin_char_types_counts['Failed Bump = Has Only Replies by the OP'][i] = cur.fetchone()[0]

        cur.execute('''
                        SELECT Count()
                        FROM Threads
                        WHERE 0<(SELECT Count() FROM Posts WHERE Posts.THREAD_ID=Threads.THREAD_ID AND Posts.MEMBER_ID != Threads.MEMBER_ID)
                            AND Threads.MEMBER_ID=(SELECT MEMBER_ID FROM Posts WHERE Posts.THREAD_ID=Threads.THREAD_ID ORDER BY Posts.POST_DATE asc
                                LIMIT 1,1)
                            AND (THREAD_ID BETWEEN ? AND ?)''', (start, end))
        title_begin_char_types_counts['Successful Bump = Has Replies by Members Other Than the OP, After OP Replied'][i] = cur.fetchone()[0]

        computed_key = 'Bump Not Needed = Has Replies by Members Other Than the OP, 1st Reply Not by OP'
        title_begin_char_types_counts[computed_key][i] = header.NUM_SAMPLES_PER_BIN - sum(title_begin_char_types_counts[k][i] for k in title_begin_char_types_counts if k != computed_key)

    print(title_begin_char_types_counts)

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=header.STACKS_DIMS)
ax_t = ax.twiny()
ax.set_ylabel('Number of Threads in Sample')

bottom_offsets = np.zeros(header.NUM_BINS)

x_ticks = [header.BINS_SEPARATORS_TIMESTAMPS[0] + sum(header.BINS_TIMESPANS[:bindex]) + header.BINS_TIMESPANS[bindex]/2 for bindex in range(header.NUM_BINS)]

t_range = [header.BINS_SEPARATORS_TIMESTAMPS[0], header.BINS_SEPARATORS_TIMESTAMPS[-1]]
ax.set_aspect('auto')
ax.set_ylim([0, header.NUM_SAMPLES_PER_BIN])
ax.set_xticks(x_ticks, header.BINS_LABELS)
ax.set_xlim(t_range)

ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(header.BINS_SEPARATORS_TIMESTAMPS,header.BINS_SEPARATORS_LABELS)
ax_t.set_xlim(t_range)

for char_type, nums_threads_by_bin in title_begin_char_types_counts.items():
    ax.bar(x_ticks, nums_threads_by_bin, header.BINS_TIMESPANS, label=char_type, bottom=bottom_offsets)
    bottom_offsets += nums_threads_by_bin

ax.set_title("NoReplyPill Brutality by Bin", fontweight='bold')

ax.legend(loc="upper left")

boxplot.stagger(ax)
boxplot.stagger(ax_t)

plt.subplots_adjust(**header.STACKS_FRAME_1_LINE_TITLE)

plt.savefig('graphs/stacks_noreply_threads.png',dpi=header.IMG_DPI)

plt.show()
