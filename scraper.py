import scraperwiki
import lxml.html

URLf = lambda n: "http://www.vdc-sy.info/index.php/en/details/martyrs/{n}".format(n=n)

def add_to_db(items):
    scraperwiki.sqlite.save(unique_keys=['index'], data=items, table_name="data")

def get_last_index():
    scraperwiki.sqlite.execute("""CREATE TABLE IF NOT EXISTS data ("index" INTEGER)""")
    row = scraperwiki.sql.select("""* from data order by "index" desc""")
    return row[0]['index'] if row else 0

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

MAX_FAILS = 10
def scrape():
    martyrs = []
    i = 0
    START_INDEX = get_last_index() + 1
    print "Starting at index {0}".format(START_INDEX)
    j = START_INDEX
    while i < MAX_FAILS:
        martyr = load_martyr_by_index(j)
        if martyr is None:
            i += 1
        else:
            i = 0
            martyrs.append(martyr)
        j += 1
        if j % 10 == 0 and j > START_INDEX + 1:
            print "Up to index {0}...".format(j)
    print "Found {0} new martyrs.".format(len(martyrs))
    add_to_db(martyrs)

if __name__ == '__main__':
    scrape()
