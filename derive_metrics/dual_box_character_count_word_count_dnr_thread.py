
import sqlite3, numpy as np, pandas as pd, header, queries, tqdm, re,copy
from collections import defaultdict

keywords = [
    'dnr','dn r','dnrd','dn rd',"didn't read","not a word","not a pixel","readn't",'not read','not rd','tldr','not gonna read',"ain't readin","not readin",
    "think i'm readin","ain't gonna read","ain't gon read","not gon read",'0 words','not a molecule',
]
def add_smart_apostrophes(words):
    for word in copy.copy(words):
        if "'" in word:
            words.append(word.replace("'","’"))
            continue
        words.append(word.replace("’","'"))

add_smart_apostrophes(keywords)

boxes = [[] for _ in range(header.NUM_BINS)]

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        CRITERION = "Lower(Trim(Trim(Trim(P.BODY_TEXT),'\n'),'\r')) LIKE ?"

        cur.execute(
        f''' SELECT BODY_TEXT as T,THREAD_ID as I
            FROM Posts
            WHERE (I BETWEEN ? AND ?)
                AND IS_1ST_IN_THREAD=TRUE
                AND 0<(
                    SELECT Count()
                    FROM Posts as P
                    WHERE P.THREAD_ID=I
                        AND ({' OR '.join([CRITERION for kw in keywords])} OR {CRITERION})
                        AND P.IS_1ST_IN_THREAD=FALSE)''',
            (start,end,*([f'%{kw}%' for kw in keywords] + ['0'])) # without % around
        )

        for (body_text,_) in tqdm.tqdm(list(cur.fetchall())):
            #print(body_text)
            boxes[i].append(len(re.findall(r'\w+', body_text)))

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 6))

ax.set_title(f'''Word Counts of the 1st Posts in Threads that\nReceive at Least 1 “dnr” Reply''', fontweight='bold')

ax.set_ylabel('1st Post’s Word Count')
#ax.set_yscale('log')
ax.set_ylim([0,600])

# get dictionary returned from boxplot https://stackoverflow.com/questions/18861075/overlaying-the-numeric-value-of-median-variance-in-boxplots
bp_dict = ax.boxplot(boxes)

xes = range(1, 1+len(boxes))
ax.set_xticks(xes, header.BINS_LABELS)

means = [np.mean(np.array(lifespans)) for lifespans in boxes]
ax.scatter(x=xes, y=means, c='r')

for i,line in enumerate(bp_dict['medians']):
    V_OFFSET = -10
    # get position data for median line
    x1, y1 = line.get_xydata()[0] # top of median line
    x2, y2 = line.get_xydata()[1]  # top of median line

    # overlay median value
    ax.text((x1+x2)/2, y1+V_OFFSET, 'Median=\n%g words' % y1, horizontalalignment='center', verticalalignment='top',fontsize=8,**header.NARROW_FONT)

    # overlay mean value
    ax.text((x1+x2)/2, means[i]-V_OFFSET, 'Mean=\n%.1f words' % means[i], horizontalalignment='center', verticalalignment='bottom',fontsize=8,**header.NARROW_FONT)

ax_t = ax.twiny()
ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(range(len(header.BINS_SEPARATORS_TIMESTAMPS)),header.BINS_SEPARATORS_LABELS)

plt.subplots_adjust(top=0.825)

plt.savefig('graphs/dual_box_character_count_word_count_dnr_thread.png',dpi=header.IMG_DPI)

plt.show()
