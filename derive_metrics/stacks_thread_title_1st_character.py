
import sqlite3, numpy as np, pandas as pd, header, queries, re
from collections import defaultdict

title_begin_char_types_counts = defaultdict(lambda: np.zeros(header.NUM_BINS))
bars_widths = header.BINS_TIMESPANS

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:
    def regexp(expr, item):
        reg = re.compile(expr)
        return reg.search(item) is not None
    conn.create_function("REGEXP", 2, regexp)

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute('''SELECT Count() FROM Threads WHERE TITLE_TEXT REGEXP '^[A-Z]' AND (THREAD_ID BETWEEN ? AND ?)''',(start,end))
        title_begin_char_types_counts['Uppercase Letter'][i] = cur.fetchone()[0]

        cur.execute('''SELECT Count() FROM Threads WHERE TITLE_TEXT REGEXP '^[a-z]' AND (THREAD_ID BETWEEN ? AND ?)''',(start,end))
        title_begin_char_types_counts['Lowercase Letter'][i] = cur.fetchone()[0]

        title_begin_char_types_counts['Non-Letter'][i] = header.NUM_SAMPLES_PER_BIN - title_begin_char_types_counts['Uppercase Letter'][i] - title_begin_char_types_counts['Lowercase Letter'][i]

    print(title_begin_char_types_counts)

conn.close()

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 6))
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

ax.set_title("Thread’s Title’s 1st Character’s Type by Bin", fontweight='bold')
ax.legend(loc="lower left")

plt.savefig('graphs/stacks_thread_title_1st_character.png',dpi=header.IMG_DPI)

plt.show()
