
import copy

dictionary = {

    'Craniofacial Anatomical and Medical Terms': [
        'maxilla', 'maxillary', 'mandible', 'mandibular', 'ramus', 'gonion', 'gonial', 'menton', 'tragus', 'tragion',
        'cranium', 'craniofacial', 'cranial', 'cephalic', 'brachycephalic', 'mesocephalic', 'dolichocephalic', 'fossae',
        'fossa',
        'zygo', 'zygoma', 'zygomatic', 'bizygo', 'bizygomatic',
        'nasal', 'vomer', 'alar', 'nasion', 'radix',
        'orbit', 'orbital', 'infraorbital', 'supraorbital', 'glabella', 'ocular',
        'frontal', 'temporal', 'occiput', 'occipital',
        'esr', 'es ratio', 'fwhr', 'midface', 'chin to philtrum', 'chin-to-philtrum', 'interpupillary', 'canthal',
        'canthus', 'canthi', 'palpebral', 'pfl',
        'ossification', 'osteogenisis', 'remodeling', 'fracture', 'osteoblast', 'osteoclast', 'resorption', 'formation',
        'osteotomy', 'suture',
        'buccal', 'dental', 'palate', 'palatal', 'molar', 'incisor', 'occlusion', 'malocclusion', 'canine',
        'intermolar',
        'brow ridge', 'nose bridge', 'nasal spine', 'cheekbone', 'saggital', 'transverse', 'wisdom teeth',
        'wisdom tooth', 'extraction',
        'xray', 'x-ray', 'x ray', 'ceph', 'cephalogram', 'cephalometric',
        'mse','fagga','agga','soft tissue',
        'bonemass','bone mass','bone density',
    ],
    'Incel- and Blackpill-Related Terms' : [
        'chad','stacy','becky','melvin','eugene','stacylite','chadlite','brad','normie','megachad','gigachad','terachad','turbochad',
        'truecel','incel','inkwell','fatcel','wristcel','shortcel','braincel','copecel','bloatcel','oldcel','gymcel','oldcel','framecel','youngcel','volcel',
        'doomer','coomer','boomer',"greycel",'graycel',
        'rotter','dweller','neet','psl','looksmax','lookism',
        'cope','rope','copium','coping','coper','megacope','gigacope','teracope','turbocope','copemax','ropemax','roping','roper',
        'tallfag','manlet','turbomanlet','framelet','lanklet','lank',
        'mog','mogger','moggee','heightmog','framemog','iqmog','looksmog','facemog','racemog',
        'subhuman','sub5','subfive','sub 5','sub-5','sub-five','sub five',
        'moid','foid','femoid',
        'softmax','hardmax',
        'virgin','sexless','kissless','hugless','khhv','virginity','get laid','getting laid','tlf',
        'blackpill','bluepill','redpill',
        'blackpilled','bluepilled','redpilled','faceandlms','hypergamy','hypergamous',
        'wojak','pepe','soyjak','froglet','dickcel','dickpill','dicklet','cutlet',
        'jfl','looksmaxx','bloatmaxx','bloatmax','fatmax',
    ],
    'Insults and Slurs (Non-Ethnic)' : [
        'soycuck','cuck',
        'retard','dumbass','idiot','moron','imbecile','dumb fuck',
        'faggot','fag',
        'autist','sperg',
        'street shitter',
        'cunt','tranny',
    ],
    'Racial and Ethnic Non-Slurs' : [
        'caucasoid','mongoloid','negroid','australoid',
        'black','white','brown','jew','paki','jewish','pakistani','jewed',
        'african','asian','indian','european','abo','aboriginal',
        'korean','bbc','bwc','japanese','jap','chinese',
        'ethnic','deathnic','race','racial','ethnicity',
        'hispanic','latino','arab','arabic','nordic','slavic','nord','slav','anglo',
    ],
    'Racial and Ethnic Slurs' : [
        'nigger','sheboon','niglet','negro',
        'gook','chink','noodle','noodlewhore',
        'cumskin','mayo','cracker',
        'skitskin','curry','rice',
        'kike','goy','goyim',
        'spic',
    ],
    'Male Model Names' : [
        'chico','gandy','opry',"o'pry",'lachowski','barrett','nessman','maher',
    ],
}

def add_plurals(words):
    for word in copy.copy(words):
        if word[-1] in ('s','x'):
            words.append(word + 'es')
            continue
        elif word[-1] == 'y':
            words.append(word[:-1] + 'ies')
            continue
        words.append(word + 's')

for classification in dictionary:
    add_plurals(dictionary[classification])

#

import sqlite3, numpy as np, pandas as pd, header, queries, re, tqdm
from collections import defaultdict

num_specials_by_type_by_bin = defaultdict(lambda:np.zeros(header.NUM_BINS))
num_words_by_bin = np.zeros(header.NUM_BINS)

print('Initialized 2 numpy arrays.')

bars_widths = header.BINS_TIMESPANS

conn = sqlite3.connect('../' + header.DB_FILE_NAME)
print("Opened database successfully.")
with conn:

    cur = conn.cursor()

    for i,(start,end) in enumerate(header.BINS_IDS_RANGES):

        cur.execute('''
        SELECT BODY_TEXT
        FROM Posts
        WHERE THREAD_ID BETWEEN ? AND ?''',(start,end))

        print(f'cursor executed SQL for bin {1+i}')

        for (body_text,) in tqdm.tqdm(list(cur.fetchall())):
            for key in dictionary:
                insults_regex_matches = re.findall(rf'\b({"|".join(dictionary[key])})\b', body_text.lower())
                #print(num_specials_by_type_by_bin['Racial and Ethnic Slurs'])
                #print(key)
                num_specials_by_type_by_bin[key][i] += len(insults_regex_matches)

            num_words_by_bin[i] += len(re.findall(r'\w+', body_text))

conn.close()

num_specials_by_type_per_1000_words_by_bin = { k : 1000 * v / num_words_by_bin for k,v in num_specials_by_type_by_bin.items() }

print(num_specials_by_type_by_bin)

#

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 6))
ax_t = ax.twiny()
ax.set_ylabel('Average Number of Occurrences per 1000 Words')

x_ticks = [header.BINS_SEPARATORS_TIMESTAMPS[0] + sum(header.BINS_TIMESPANS[:bindex]) + header.BINS_TIMESPANS[bindex]/2 for bindex in range(header.NUM_BINS)]

t_range = [header.BINS_SEPARATORS_TIMESTAMPS[0], header.BINS_SEPARATORS_TIMESTAMPS[-1]]
ax.set_aspect('auto')
ax.set_ylim([0, 32.5])
ax.set_xticks(x_ticks, header.BINS_LABELS)
ax.set_xlim(t_range)

ax_t.plot(range(1), np.zeros(1))
ax_t.set_xticks(header.BINS_SEPARATORS_TIMESTAMPS,header.BINS_SEPARATORS_LABELS)
ax_t.set_xlim(t_range)

bottom_offsets = np.zeros(header.NUM_BINS)

for classification, nums_special_terms_by_bin in num_specials_by_type_per_1000_words_by_bin.items():
    ax.bar(x_ticks, nums_special_terms_by_bin, header.BINS_TIMESPANS, label=classification, bottom=bottom_offsets)
    bottom_offsets += nums_special_terms_by_bin
    print('stack')

ax.set_title("Average Frequency of Special Vocabulary (Per 1000 Words)", fontweight='bold')

ax.legend(loc="upper right")

plt.savefig('graphs/stacks_vocabulary_per_1000.png',dpi=header.IMG_DPI)

plt.show()
