import sys

def getArticle(url):
    import re
    wikiPageRegex = r'(https?://)?en\.wikipedia\.org/wiki/(.+)' # Requires English wikipedia URL.
    match = re.match(wikiPageRegex, arg)
    if match != None:
        return match.group(2)
    else:
        return None

def isValidWikiURL(url):
    return getArticle(url) != None

def makeURL(article):
    return "http://en.wikipedia.org/wiki/" + article

# Verify a single argument is provided. The first element of sys.argv will always be 'getting_to_philosophy.py'.
if len(sys.argv) != 2:
    print('Error: please provide a single argument, e.g. "python getting_to_philosophy.py STARTING_LINK"')
    sys.exit(0)

# Verify the argument is a valid URL.
arg = sys.argv[1]
if not isValidWikiURL(arg):
    print('Error: please provide a valid English wiki article URL, e.g. "en.wikipedia.org/wiki/ARTICLE"')
    sys.exit(0)

# Everything looks good; let's get to philosophy!
rootArticle = getArticle(arg)

MAX_HOPS = 100
TARGET_ARTICLE = 'Philosophy'

sequence = list() # Ordered sequence of articles we visit on the way to Philosophy.
visited = set() # Small optimiztion; also keep articles we've seen already in a structure that supports fast(er) lookup.

# We'll recursively pull the current article, add it to our sequence, and continue crawling on the first article
# linked from the current article's main body (decrementing hopsRemaining along the way).
# Stop when no more hops remain, a cycle is detected, the current article has no links, or we hit a dead link.
# (Or when we get to our target!)
def crawl(currArticle, hopsRemaining):
    import requests # Pull webpage.
    import bs4 # Parse webpage.

    def addArticle(article):
        sequence.append(currArticle)
        visited.add(currArticle)

    if currArticle in visited: # Cycle detected.
        print("Cycle detected.")
        return
    else:
        addArticle(currArticle)

    if currArticle == TARGET_ARTICLE: # Hooray! We're done.
        return

    response = requests.get(makeURL(currArticle))
    if response.status_code != requests.codes.ok: # Dead link, or something else bad has happened.
        print("Request error at: " + makeURL(currArticle))
        return

    soup = bs4.BeautifulSoup(response.text)
    link = soup.select('#mw-content-text > p:first-of-type > a:first-of-type')

    if len(link) == 0: # No link found.
        return

    nextArticle = link[0].attrs.get('title')
    if hopsRemaining > 0:
        crawl(nextArticle, hopsRemaining - 1)
    elif nextArticle == TARGET_ARTICLE: # "Off-by-one"; even though we have no more hops we found the target so add it.
        addArticle(nextArticle)

crawl(rootArticle, MAX_HOPS)

def printSequence():
    urls = [makeURL(article) for article in sequence]
    printstring = '\n'.join(urls)
    if sequence[-1] == TARGET_ARTICLE:
        printstring += '\nSUCCESS: ' + `len(sequence) - 1` + ' hops'
    else:
        printstring += '\nFAILURE: ' + TARGET_ARTICLE + ' not found'

    print(printstring)

printSequence()
