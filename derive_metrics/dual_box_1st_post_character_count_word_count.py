
import sqlite3, numpy as np, pandas as pd, header, queries, tqdm, re,copy
from textstat import textstat
from collections import defaultdict

boxes = [[] for _ in range(header.NUM_BINS)]
boxes_words = [[] for _ in range(header.NUM_BINS)]

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute(
        f'''
            SELECT _BODY_LENGTH, BODY_TEXT
            FROM Posts
            WHERE (THREAD_ID BETWEEN ? AND ?)
                AND IS_1ST_IN_THREAD=TRUE
        ''',
            (start,end)
        )

        for (n_chars,body_text) in tqdm.tqdm(list(cur.fetchall())):
            boxes[i].append(n_chars)
            boxes_words[i].append(len(re.findall(r'\w+', body_text)))

conn.close()

#

import matplotlib.pyplot as plt
import boxplot

fig, (ax,ax_words) = plt.subplots(2,figsize=(9, 6))

ax.set_title(f'''Threads’ 1st Posts’ Character Counts (Top) and Word Counts (Bottom)''', fontweight='bold')

ax.set_ylabel('Number of Characters')
#ax.set_yscale('log')
ax.set_ylim([10,350])

# get dictionary returned from boxplot https://stackoverflow.com/questions/18861075/overlaying-the-numeric-value-of-median-variance-in-boxplots
bp_dict = ax.boxplot(boxes)

ax_words.set_ylabel('Number of Words')
#ax.set_yscale('log')
ax_words.set_ylim([0,75])

bp_words_dict = ax_words.boxplot(boxes_words)

xes = range(1, 1+len(boxes))
ax.set_xticks(xes, header.BINS_LABELS)
ax_words.set_xticks(xes, header.BINS_LABELS)

boxplot.plot_text(ax,boxes,bp_dict,-10,mode=2)
boxplot.plot_text(ax_words,boxes_words,bp_words_dict,-2.5,mode=2)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(range(len(header.BINS_SEPARATORS_TIMESTAMPS)),header.BINS_SEPARATORS_LABELS)

plt.subplots_adjust(top=0.85)

plt.savefig('graphs/dual_box_1st_post_character_count_word_count.png',dpi=header.IMG_DPI)

plt.show()
