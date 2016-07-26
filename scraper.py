import datetime
import scraperwiki
import lxml.html

today_dt = datetime.datetime.now().strftime('%Y-%m-%d')

page_urlf = lambda page: "http://www.vdc-sy.info/index.php/en/martyrs/{page}/c29ydGJ5PWEua2lsbGVkX2RhdGV8c29ydGRpcj1ERVNDfGFwcHJvdmVkPXZpc2libGV8ZXh0cmFkaXNwbGF5PTB8".format(page=page)
URLf = lambda n: "http://www.vdc-sy.info/index.php/en/details/martyrs/{n}".format(n=n)

def add_to_db(items):
    scraperwiki.sqlite.save(unique_keys=['index'], data=items, table_name="data")
    scraperwiki.sqlite.commit()

def init():
    scraperwiki.sqlite.execute("""CREATE TABLE IF NOT EXISTS data ("index" INTEGER)""")

def get_last_index():
    init()
    row = scraperwiki.sql.select("""* from data order by "index" desc limit 1""")
    return max(row[0]['index']-1000,0) if row else 0

def all_saved_indices():
    init()
    rows = scraperwiki.sql.select(""" "index" from data""")
    return [row['index'] for row in rows]

# get_text = lambda row: [item.text.strip() for item in row]
get_text = lambda row: [item.text_content().strip() for item in row]
def quick_load_by_page(n):
    html = scraperwiki.scrape(page_urlf(n))
    root = lxml.html.fromstring(html)
    x = root.cssselect("table")
    if len(x) == 0:
        return
    rows = x[0]
    keys = get_text(rows[0])
    all_vals = [get_text(row) for row in rows[1:]]

    has_index = lambda item: len(item) and len(item[0]) and len(item.items())
    indices = [row[0][0].items()[0][1].split('/')[-1] if has_index(row) else None for row in rows[1:]]

    keys = ["index"] + keys
    all_vals = [[ind] + vals for ind,vals in zip(indices, all_vals) if ind is not None]
    items = [dict(zip(keys, vals)) for vals in all_vals]
    return items

def get_last_page_number():
    html = scraperwiki.scrape(page_urlf(1))
    root = lxml.html.fromstring(html)
    num = root.cssselect('.tablePgaination')[0][-1].values()[0].split('martyrs/')[1].split('/')[0]
    return int(num)

def quick_load_all(max_repeats=150):
    last_page_num = get_last_page_number()
    all_inds = all_saved_indices()
    print 'Loaded {0} existing martyrs'.format(len(all_inds))
    repeats = 0
    for i in xrange(1, last_page_num+1):
        if repeats >= max_repeats:
            break
        print 'Parsing page {0}'.format(i)
        items = quick_load_by_page(i)
        old_items = items
        items = [item for item in items if int(item['index']) not in all_inds]
        repeats += (len(old_items) - len(items))
        add_to_db(items)
        print 'Wrote {0} new martyrs'.format(len(items))

def inds_by_page(n):
    html = scraperwiki.scrape(page_urlf(n))
    root = lxml.html.fromstring(html)
    x = root.cssselect("table")
    if len(x) == 0:
        return
    rows = x[0]
    has_index = lambda item: len(item) and len(item[0]) and len(item.items())
    indices = [row[0][0].items()[0][1].split('/')[-1] if has_index(row) else None for row in rows[1:]]
    return [int(x) for x in indices if x is not None]

def all_page_indices(n):
    last_page_num = get_last_page_number()
    indices = []
    for i in xrange(1, last_page_num+1):
        indices.extent(inds_by_page(n))
    return indices

def load_all(save_every=100, print_every=20):
    init()
    inds = all_page_indices()
    open('tmp.txt', 'w').write('\n'.join(inds))
    items = []
    count = 0
    for i,ind in enumerate(inds):
        item = load_martyr_by_index(ind)
        if item is not None:
            items.append(item)
        if i % print_every == 0:
            print '{0} of {1}'.format(i, len(inds))
        if len(items) == save_every:
            add_to_db(items)
            print 'Wrote {0} new martyrs'.format(len(items))
            count += len(items)
            items = []
    add_to_db(items)
    count += len(items)
    print 'Found {0} total martyrs'.format(count)

def load_recent(save_every=100, max_overlaps=50):
    all_inds = all_saved_indices()
    print 'Loaded {0} existing martyrs'.format(len(all_inds))
    i = 1
    overlaps = 0
    items = []
    repeat_items = []
    count = 0
    while overlaps < max_overlaps:
        print 'Parsing page {0}'.format(i)
        inds = inds_by_page(i)
        for ind in inds:
            is_overlap = False
            if ind in all_inds:
                is_overlap = True
                overlaps += 1
                # continue
            item = load_martyr_by_index(ind)
            if item is not None:
                if is_overlap:
                    repeat_items.append(item)
                    continue
                items.append(item)
                if len(items) == save_every:
                    add_to_db(items)
                    count += len(items)
                    print 'Wrote {0} new martyrs'.format(len(items))
                    items = []
        i += 1
    add_to_db(items)
    count += len(items)
    print 'Wrote {0} total martyrs'.format(count)
    print 'Found {0} repeat martyrs that I will not be updating (should probably check these for updates...)'.format(len(repeat_items))

def load_martyr_by_index(n):
    # Read in a page
    html = scraperwiki.scrape(URLf(n))
    root = lxml.html.fromstring(html)
    x = root.cssselect("table")
    if len(x) == 0:
        return
    tbl = x[0]
    items = [[elem.text for elem in row.getchildren()] for row in tbl.getchildren() if row.getchildren()]
    items = [(item[0], item[1].strip()) for item in items if len(item) == 2 and item[1] is not None and len(item[1]) > 0]
    obj = dict(items)
    obj['index'] = n
    return obj

# def dt_lt_dt(dt1, dt2, days_offset=0):
#     y1,m1,d1 = [int(x) for x in dt1.split('-')]
#     y2,m2,d2 = [int(x) for x in dt2.split('-')]
#     d2 -= max(days_offset, 1)
#     return y1 < y2 or (y1 == y2 and m1 < m2) or (y1 == y2 and m1 == m2 and d1 < d2)

# SAVE_EVERY_N = 100
# def scrape():
#     martyrs = []
#     i = 0
#     last_dt = None
#     START_INDEX = get_last_index() + 1
#     print "Starting at index {0}".format(START_INDEX)
#     j = START_INDEX
#     total_count = 0
#     do_quit_soon = False
#     while not (do_quit_soon and martyr is None and i >= 20) and i <= 1000:
#         martyr = load_martyr_by_index(j)
#         if martyr is None:
#             if do_quit_soon:
#                 i += 1
#         else:
#             if 'Date of death' in martyr:
#                 last_dt = martyr['Date of death']
#                 # if within 2 days of today, prepare to quit
#                 if not dt_lt_dt(last_dt, today_dt, 2):
#                     do_quit_soon = True
#             i = 0
#             martyrs.append(martyr)
#         j += 1
#         if j % 10 == 0 and j > START_INDEX + 1:
#             print "Up to date {0}, index {1}...".format(last_dt, j)
#         if len(martyrs) == SAVE_EVERY_N:
#             total_count += len(martyrs)
#             add_to_db(martyrs)
#             martyrs = []
#             print "Saving checkpoint."
#     total_count += len(martyrs)
#     print "Found {0} new martyrs.".format(total_count)
#     add_to_db(martyrs)

if __name__ == '__main__':
    # scrape()

    # load_recent()

    quick_load_all()
