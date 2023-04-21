
import requests, header, random, sqlite3, re
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime, timezone

SLEEP_DURATION = 0.125
BACKOFF_DURATION = 5
TIMEOUT_DURATION = 5

conn = sqlite3.connect(header.DB_FILE_NAME)
print("Opened database successfully.")

SAMPLING_SPREAD = round(header.BIN_SIZE / header.NUM_SAMPLES_PER_BIN / 4)

def get_thread_url(id_number:int):
    return 'https://looksmax.org/threads/' + str(id_number)

def is_1st_in_thread(url:str):
    return not re.match(r".*?/page-\d+/?", url)

def fetch_page(url:str):
    print('Fetch ' + url)
    try:
        response = requests.get(url,timeout=TIMEOUT_DURATION)
    except requests.exceptions.Timeout or requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout or requests.exceptions.ReadTimeout:
        response = fetch_page(url)
    return response

def thread_url_get_current_pagination_num(url:str):
    try:
        NUGGET = '/page-'
        return int(url[url.index(NUGGET) + len(NUGGET):])
    except ValueError:
        return 1

def get_posts_reacts_page_url(id_number:int):
    return f'https://looksmax.org/posts/{id_number}/reactions'

# { threads

def thread_get_post_timestamp(soup:BeautifulSoup):
    return int(soup.select('.p-description a.u-concealed > time[data-time]')[0]['data-time'])

def thread_get_author_id(soup:BeautifulSoup):
    return int(soup.select('.p-description [data-user-id]')[0]['data-user-id']) # a[data-user-id].username.u-concealed

def thread_get_num_paginations(soup:BeautifulSoup):
    last_pagination_button = soup.select('ul.pageNav-main > li:last-child > a')
    if not last_pagination_button:
        return 1
    return int(last_pagination_button[0].get_text())

def thread_get_subforum(soup:BeautifulSoup):
    return soup.select('ul.p-breadcrumbs > li > a > span[itemprop="name"]')[-1].get_text().strip()

def thread_get_prefix_and_title_text(soup:BeautifulSoup):
    prefixed_title_text = soup.select('.p-body-header > .p-title > h1.p-title-value')[0].get_text()
    prefix = soup.select('.p-body-header > .p-title > h1.p-title-value > span:not(.label-append)')
    prefix_text = prefix[0].get_text().strip() if prefix else ''
    return prefix_text, prefixed_title_text.strip()[len(prefix_text):].strip()

# threads }

# { posts

def get_all_posts_on_page(soup:BeautifulSoup):
    posts = soup.select('article.message.message--post')
    return [{
        'REACTS_COUNT' : post_get_reacts_total(post),
        'POST_ID' : post_get_post_id(post),
        'POST_DATE' : post_get_post_timestamp(post),
        'BODY_TEXT' : post_get_body_plain_text(post),
        'IS_1ST_IN_THREAD' : post_get_ordinal_number(post) == 1,
        'member' : {
            'MEMBER_ID' : post_get_author_id(post),
            'NAME' : post_get_author_name(post),
            'JOIN_DATE' : post_get_author_joined_when(post),
            'POSTS_COUNT' : post_get_author_posts_count(post),
            'REP_SCORE' : post_get_author_rep_count(post),
        },
    } for post in posts]

def post_get_reacts_total(soup:BeautifulSoup):
    bar = soup.select('.reactionsBar .reactionsBar-link')
    if not bar:
        return 0
    bar = bar[0]
    reacts_bar_txt = bar.get_text().strip()
    n_listed = len(bar.select('bdi')) # 0 when react bar not present
    if not (
            reacts_bar_txt.endswith(' other person')
            or reacts_bar_txt.endswith(' others')
    ):
        return n_listed
    n_more_reacted = int(reacts_bar_txt[reacts_bar_txt.rindex('and ')+4:reacts_bar_txt.rindex(' other')].strip())
    return n_listed + n_more_reacted

def post_get_post_timestamp(soup:BeautifulSoup):
    return int(soup.select('ul.message-attribution-main > li.u-concealed > a > time[data-time]')[0]['data-time'])

def post_get_post_id(soup:BeautifulSoup):
    return int(soup['data-content'][soup['data-content'].index('-')+1:])

def post_get_body_plain_text(soup:BeautifulSoup):
    return soup.select('article.message-body > .bbWrapper')[0].get_text()

def post_get_ordinal_number(soup:BeautifulSoup):
    return int(soup.select('ul.message-attribution-opposite.message-attribution-opposite--list > li:last-child > a')[0].get_text().strip()[1:])

def post_get_author_id(soup:BeautifulSoup):
    try:
        return int(soup.select('.message-cell.message-cell--user h4.message-name > [data-user-id]')[0]['data-user-id'])
    except IndexError:
        return int(soup.select('.message-cell.message-cell--user h4.message-name > span')[0].get_text().replace('Deleted member ','').strip())

def post_get_author_name(soup:BeautifulSoup):
    return soup.select('.message-cell.message-cell--user h4.message-name span')[0].get_text().strip()

def post_get_author_joined_when(soup:BeautifulSoup):
    try:
        return int(datetime.strptime(soup.select('div.message-userExtras > dl > dd')[0].get_text().strip(),'%b %d, %Y').replace(tzinfo=timezone.utc).timestamp())
    except IndexError:
        return None

def post_get_author_posts_count(soup:BeautifulSoup):
    try:
        return int(soup.select('div.message-userExtras > dl > dd')[1].get_text().strip().replace(',',''))
    except IndexError:
        return None

def post_get_author_rep_count(soup:BeautifulSoup):
    try:
        return int(soup.select('div.message-userExtras > dl > dd')[2].get_text().strip().replace(',',''))
    except IndexError:
        return None

# posts }

# { reacts

def get_all_reacts_on_page(soup:BeautifulSoup):
    reacts = soup.select('ol.block-body.js-reactionList-0 > li.block-row.block-row--separated > div.contentRow')
    return [{
        'REACT_DATE': react_get_timestamp(react),
        'REACT_TYPE': react_get_type(react),
        'MEMBER_ID': react_get_reactor_id(react),
    } for react in reacts]

def react_get_reactor_id(soup:BeautifulSoup):
    return int(soup.select('[data-user-id]')[0]['data-user-id'])

def react_get_timestamp(soup:BeautifulSoup):
    return int(soup.select('[data-time]')[0]['data-time'])

def react_get_type(soup:BeautifulSoup):
    return soup.select('.contentRow-extra > span.reaction > img')[0]['alt']

# reacts }

with conn:
    def main():

        cur = conn.cursor()

        for sam_index,id_center in enumerate(header.SAMPLE_IDS):

            sample_fulfilled = False
            while not sample_fulfilled:
                sample_fulfilled = True

                sam_id = int(id_center + random.randint(-SAMPLING_SPREAD,+SAMPLING_SPREAD))
                thread_url = get_thread_url(sam_id)

                has_more_pages = True
                while has_more_pages:
                    has_more_pages = False

                    sleep(SLEEP_DURATION)

                    page = fetch_page(thread_url)
                    thread_url = page.url

                    if page.status_code >= 400:
                        sample_fulfilled = False
                        if page.status_code == 404:
                            print('^ gives 404. Will retry.')
                        elif page.status_code >= 500:
                            print(f'^ gives 5xx. Will retry after {BACKOFF_DURATION + SLEEP_DURATION} secs.')
                            #raise Exception('Server Error!')
                            sleep(BACKOFF_DURATION)
                        else:
                            print(f'^ gives 4xx. Will retry after {BACKOFF_DURATION + SLEEP_DURATION} secs.')
                            sleep(BACKOFF_DURATION)
                        break

                    soup = BeautifulSoup(page.text, 'html.parser')

                    if is_1st_in_thread(thread_url):

                        subforum = thread_get_subforum(soup)

                        if subforum not in header.SUBFORUMS_NAMES:
                            sample_fulfilled = False
                            break

                        prefix,title = thread_get_prefix_and_title_text(soup)

                        sql_args = (
                            sam_id,
                            thread_get_author_id(soup),
                            thread_get_post_timestamp(soup),
                            subforum,
                            prefix,
                            title
                        )
                        print('^ scraped data = ' + str(sql_args))
                        conn.execute('''INSERT INTO Threads (THREAD_ID,MEMBER_ID,POST_DATE,SUBFORUM,PREFIX,TITLE_TEXT) VALUES (?,?,?,?,?,?)''',sql_args)

                    for post_data in get_all_posts_on_page(soup):
                        n_reacts = post_data['REACTS_COUNT']
                        post_id = post_data['POST_ID']
                        conn.execute('''INSERT INTO Posts (POST_ID,THREAD_ID,POST_DATE,MEMBER_ID,BODY_TEXT,IS_1ST_IN_THREAD,REACTS_COUNT) VALUES (?,?,?,?,?,?,?)''',
                                     (post_id,sam_id,post_data['POST_DATE'],post_data['member']['MEMBER_ID'],post_data['BODY_TEXT'],post_data['IS_1ST_IN_THREAD'],n_reacts))

                        if not all([not member_prop_val is None for member_prop_val in post_data['member'].values()]):
                            continue # not all member data found such as with DM#6129=“Julius the Great”
                        cur.execute('''SELECT Count() FROM Members WHERE MEMBER_ID=?''',
                                    (post_data['member']['MEMBER_ID'],)
                        )
                        does_member_exist_in_DB = cur.fetchone()[0] > 0
                        if not does_member_exist_in_DB:
                            conn.execute(
                                '''INSERT INTO Members (MEMBER_ID,NAME,JOIN_DATE,POSTS_COUNT,REP_SCORE) VALUES (?,?,?,?,?)''',
                                (post_data['member']['MEMBER_ID'], post_data['member']['NAME'], post_data['member']['JOIN_DATE'], post_data['member']['POSTS_COUNT'],post_data['member']['REP_SCORE']))

                        # { reacts

                        if n_reacts:
                            sleep(SLEEP_DURATION)

                            reacts_page = fetch_page(get_posts_reacts_page_url(post_id))
                            reacts_page_soup = BeautifulSoup(reacts_page.text, 'html.parser')

                            for react_data in get_all_reacts_on_page(reacts_page_soup):
                                conn.execute(
                                    '''INSERT INTO Reacts (POST_ID,MEMBER_ID,REACT_DATE,REACT_TYPE) VALUES (?,?,?,?)''',
                                    (post_id, react_data['MEMBER_ID'], react_data['REACT_DATE'], react_data['REACT_TYPE'])
                                )

                        # reacts }

                    # { pagination
                    cur_page_num = thread_url_get_current_pagination_num(thread_url)
                    num_pages = thread_get_num_paginations(soup)
                    if cur_page_num < num_pages:
                        has_more_pages = True
                        next_page_num = cur_page_num + 1
                        thread_url = thread_url[:thread_url.rfind('/')] + '/page-' + str(next_page_num)
                        print(f'^ paginate to page {next_page_num} out of {num_pages}')
                    # pagination }

                if sample_fulfilled:
                    print(f'^ fulfills sample {1+sam_index} out of {len(header.SAMPLE_IDS)}.')
    main()

conn.close()
