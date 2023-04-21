
from datetime import datetime
from collections import defaultdict

NARROW_FONT = {'fontname':'Arial Narrow'}

'''
SCATTER_COLORS = (
    'red','orange','yellow','green','cyan','blue','purple'
)
'''

IMG_DPI = 144

DB_FILE_NAME = 'sqlite.db'

NUM_SAMPLES_PER_BIN = 10
BIN_SIZE = 50000
NUM_BINS = 14

BINS_LABELS = tuple([f'{1+i}{defaultdict(lambda:"th",{1:"st",2:"nd",3:"rd"})[1+i]} {round(BIN_SIZE/1000)}K\nThreads' for i in range(NUM_BINS)])

SAMPLE_IDS = tuple([BIN_SIZE / NUM_SAMPLES_PER_BIN * (i + 0.5) for i in range(NUM_BINS * NUM_SAMPLES_PER_BIN)])

BINS_IDS_RANGES = tuple([(1 + i * BIN_SIZE,1 + (i+1) * BIN_SIZE) for i in range(NUM_BINS)])

if NUM_BINS == 7:
    BINS_SEPARATORS_TIMESTAMPS = (
        1533919860, # 1
        1581647760, # 100 000
        1599343140, # 200 000
        1613595000, # 300 000
        1632447360, # 400 000
        1652498760, # 500 000
        1667931960, # 600 000
        1681419300, # 700 000
    )

elif NUM_BINS == 14:
    BINS_SEPARATORS_TIMESTAMPS = (
        1533919860, # 1
    1570465879,
        1581647760, # 100 000
    1591155259,
        1599343140, # 200 000
    1606602880,
        1613595000, # 300 000
    1621550891,
        1632447360, # 400 000
    1643046982,
        1652498760, # 500 000
    1660721856,
        1667931960, # 600 000
    1674564517,
        1681419300, # 700 000
    )

BINS_SEPARATORS_LABELS = tuple([datetime.utcfromtimestamp(epoch).strftime("%d/%b\n%Y") for epoch in BINS_SEPARATORS_TIMESTAMPS])

BINS_TIMESPANS = tuple([BINS_SEPARATORS_TIMESTAMPS[i+1] - epoch for i,epoch in enumerate(BINS_SEPARATORS_TIMESTAMPS[:-1])])

SUBFORUMS_NAMES = (
    'Looksmaxing',
    'Looksmaxing Questions',
    'Moneymaking & Success',
    'Cryptocurrency',
    'Ratings',
    'Offtopic',
)

STACKS_DIMS = (10, 5)
BOX_DIMS = (10, 6)
SCATTER_DIMS = (9, 6)

STACKS_FRAME_1_LINE_TITLE = {'top':.775, 'bottom':.175, 'left':0.075, 'right':0.95}
SCATTER_FRAME_1_LINE_TITLE = {'top':.925, 'bottom':.1, 'left':.1, 'right':1.05}
SCATTER_FRAME_2_LINE_TITLE = {'top':.9, 'bottom':.1, 'left':.1, 'right':1.05}
BOX_FRAME_1_LINE_TITLE = {'top':.875, 'bottom':.075, 'left':.075, 'right':0.95}
BOX_FRAME_2_LINE_TITLE = {'top':.85, 'bottom':.075, 'left':.075, 'right':0.95}
BOX_FRAME_3_LINE_TITLE = {'top':.825, 'bottom':.075, 'left':.075, 'right':0.95}

COLOR_BAR_TICKS_POSITIONS = (
    BINS_SEPARATORS_TIMESTAMPS[0],
    datetime.strptime('1/1/2019','%d/%m/%Y').timestamp(),
    datetime.strptime('1/1/2020','%d/%m/%Y').timestamp(),
    datetime.strptime('1/1/2021','%d/%m/%Y').timestamp(),
    datetime.strptime('1/1/2022','%d/%m/%Y').timestamp(),
    datetime.strptime('1/1/2023','%d/%m/%Y').timestamp(),
    BINS_SEPARATORS_TIMESTAMPS[-1],
)

if __name__ == '__main__':
    print('Days Span of Each Set of 100K Looksmax Threads')
    print([seconds / 60 / 60 / 24 for seconds in BINS_TIMESPANS])
    print()
    print('Threads to Pick')
    print(SAMPLE_IDS)
