import datetime
import scraperwiki
import lxml.html

today_dt = datetime.datetime.now().strftime('%Y-%m-%d')

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

def dt_lt_dt(dt1, dt2, days_offset=0):
    y1,m1,d1 = [int(x) for x in dt1.split('-')]
    y2,m2,d2 = [int(x) for x in dt2.split('-')]
    d2 -= max(days_offset, 1)
    return y1 < y2 or (y1 == y2 and m1 < m2) or (y1 == y2 and m1 == m2 and d1 < d2)

SAVE_EVERY_N = 100
def scrape():
    martyrs = []
    i = 0
    last_dt = None
    START_INDEX = get_last_index() + 1
    print "Starting at index {0}".format(START_INDEX)
    j = START_INDEX
    total_count = 0
    do_quit_soon = False
    while not (do_quit_soon and martyr is None and i >= 20) and i <= 1000:
        martyr = load_martyr_by_index(j)
        if martyr is None:
            if do_quit_soon:
                i += 1
        else:
            if 'Date of death' in martyr:
                last_dt = martyr['Date of death']
                # if within 2 days of today, prepare to quit
                if not dt_lt_dt(last_dt, today_dt, 2):
                    do_quit_soon = True
            i = 0
            martyrs.append(martyr)
        j += 1
        if j % 10 == 0 and j > START_INDEX + 1:
            print "Up to date {0}, index {1}...".format(last_dt, j)
        if len(martyrs) == SAVE_EVERY_N:
            total_count += len(martyrs)
            add_to_db(martyrs)
            martyrs = []
            print "Saving checkpoint."
    total_count += len(martyrs)
    print "Found {0} new martyrs.".format(total_count)
    add_to_db(martyrs)

if __name__ == '__main__':
    scrape()
