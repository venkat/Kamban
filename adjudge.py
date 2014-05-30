#!/usr/bin/env python
import sys
import optparse
import re
import urllib2
import stemmer


stop_words = ['a','able','about','across','after','all','almost','also','am','among','an','and','any','are','as','at','be','because','been','but','by','can','cannot','could','dear','did','do','does','either','else','ever','every','for','from','get','got','had','has','have','he','her','hers','him','his','how','however','i','if','in','into','is','it','its','just','least','let','like','likely','may','me','might','most','must','my','neither','no','nor','not','of','off','often','on','only','or','other','our','own','rather','said','say','says','she','should','since','so','some','than','that','the','their','them','then','there','these','they','this','tis','to','too','twas','us','wants','was','we','were','what','when','where','which','while','who','whom','why','will','with','would','yet','you','your']

stop_words = dict.fromkeys(stop_words)

def singularize(word):
    """Return the singular form of a word
 
    &gt;&gt;&gt; singularize('rabbits')
    'rabbit'
    &gt;&gt;&gt; singularize('potatoes')
    'potato'
    &gt;&gt;&gt; singularize('leaves')
    'leaf'
    &gt;&gt;&gt; singularize('knives')
    'knife'
    &gt;&gt;&gt; singularize('spies')
    'spy'
    """
    sing_rules = [lambda w: w[-3:] == 'ies' and w[:-3] + 'y',
                  lambda w: w[-4:] == 'ives' and w[:-4] + 'ife',
                  lambda w: w[-3:] == 'ves' and w[:-3] + 'f',
                  lambda w: w[-2:] == 'es' and w[:-2],
                  lambda w: w[-1:] == 's' and w[:-1],
                  lambda w: w,
                  ]
    word = word.strip()
    singleword = [f(word) for f in sing_rules if f(word) is not False][0]
    return singleword

def get_categories(text):
    cats = re.findall('"(.*?)"', text)
    t = []
    for cat in cats:
        if 'wikipedia' in cat.lower() or 'articles' in cat.lower() or 'all pages' in cat.lower() or 'hidden categories' in cat.lower():
            continue
        if 'categories requiring' in cat.lower():
            continue
        if  cat.lower() == 'categories' or cat.lower() == 'parent categories':
            continue
        else:
            t.append(cat)
    return t

def download_categories(category):
    url = 'http://en.wikipedia.org/wiki/Category:%s' % category.replace(' ','_')
    #print url
    request = urllib2.Request(url)
    request.add_header('User-Agent', '  Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101') 
    try:
        data = urllib2.urlopen(request).read()
    except urllib2.HTTPError:
        return []

    text = re.findall('wgCategories=\[(.*?)\]', data)
    #print 'in download_categories', text
    if not text:
        return []
    else:
        return get_categories(text[0])

def get_first_category(given_word, categories, cur_level, max_level):
    cur_level += 1
    #print cur_level, max_level
    cat = categories[0]
    for c in categories:
        if len(c.split()) == 1 and (given_word.lower() not in c.lower()):
            #print 'returning!', c 
            cat = c
            return cat
    if cur_level > max_level:
        #print 'max_level', max_level, cur_level, cat
        return cat
        return cat
    new_categories = download_categories(cat) 
    if not new_categories:
        #print 'no new_categories', max_level, cur_level, cat
        return cat
    else:
        return get_first_category(given_word, new_categories, cur_level, max_level)

def is_place(word, category):
    place_cats = ['countr', 'city', 'cities', 'settlement', 'capitals', 'asia', 'europe', 'australia', 'afria', 'america', 'antartica']
    for place_cat in place_cats:
        if place_cat.lower() in category.lower():
            return True

def read_words(eng_dict, data, debug):
    words = []
    for line in data.split('\n'):
        line = line.replace('-',' ').replace('(', ' ').replace(')', ' ').replace('/', ' ').replace('.', ' ').replace("'",'')
        words.extend(a.lower().strip(' ,".-!?;:').strip() for a in line.split())
    
    word_count = 0
    eng_word_count = 0
    eng_words = {}
    non_eng_words = {}
    word_reoccurance_count = 0
    seen_words = {}
    categories_count = 0
    categories_reoccurance_count = 0
    seen_categories = {}
    non_wiki_word_count = 0
    non_wiki_words = {}
    disambig_word_count = 0
    disambig_words = {}
    places = {}
    places_count = 0
    stop_words_count = 0
    
    total_words = len(words)
    if debug:
        print total_words

    p = stemmer.PorterStemmer()

    for cur_word_pos, word in enumerate(words):
        #print 'WORD', word
        if debug:
            print cur_word_pos
        
        stemmed_word = p.stem(word, 0 , len(word)-1)
        singular_word = singularize(word)

        if len(word) == 1 or re.findall('^[0-9]+$', word):
            continue
        
        if word in stop_words or (stemmed_word in stop_words) or (singular_word in stop_words):
            stop_words_count += 1

        word_count += 1
        if word in seen_words:
            word_reoccurance_count += 1
        seen_words[word] = None
        if word in eng_dict or (stemmed_word in eng_dict) or (singular_word in eng_dict):
            #print 'ENGWORD', word
            eng_word_count += 1
            eng_words[word] = None
            continue
        else:
            non_eng_words[word] = None

        if word in stop_words or (stemmed_word in stop_words):
            continue

        data = None
        try:
            request = urllib2.Request('http://en.wikipedia.org/wiki/%s' % word.capitalize())
            request.add_header('User-Agent', '  Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101') 
            data = urllib2.urlopen(request).read()
        except SystemExit, KeyboardInterrupt:
            raise
        except:
            pass
        
        if not data:
            #print 'no data', word
            non_wiki_word_count += 1
            non_wiki_words[word] = None
            continue

        if 'page lists articles associated with the same title.' in data and 'Disambiguation' in data:
            #print 'Disambiguation', word
            disambig_word_count += 1
            disambig_words[word] = None
            continue

        #print 'wgCategories' in data
        categories = re.findall('wgCategories=\[(.*?)\]', data)
    
        if categories:
            #print categories[0]
            categories = get_categories(categories[0])
        #print 'categories', categories
        first_cat = None
        if categories:
            first_cat = get_first_category(word, categories, 0, 3)
        #print 'FIRST CAT', first_cat , "WORD", word
        if first_cat:
            if is_place(word, first_cat):
                if word not in places:
                    places_count += 1
                    places[word] = None
                    
            if first_cat in seen_categories:
                categories_reoccurance_count += 1
            else:
                categories_count += 1
                seen_categories[first_cat] = word
        
    print 'word_count', word_count
    print 'eng_word_count', eng_word_count 
    print 'word_reoccurance_count', word_reoccurance_count
    print 'categories_count', categories_count
    print 'categories', seen_categories 
    print 'categories_reoccurance_count', categories_reoccurance_count
    print 'non_wiki_word_count', non_wiki_word_count
    print 'disambig_word_count', disambig_word_count
    print 'non_wiki_words', non_wiki_words
    print 'disambig_words', disambig_words 
    print 'places_count', places_count
    print 'places', places

def main(data, debug):
    eng_words = dict.fromkeys([a.lower().strip() for a in open('/usr/share/dict/words')])
    words = read_words(eng_words,data, debug)
if __name__ == "__main__":
    parser = optparse.OptionParser()

    parser.add_option("-i", "--infile", help="input file", default=None)
    parser.add_option("-d", "--debug", help="debug print", default=False, action="store_true")

    (options, args) = parser.parse_args()

    if not options.infile:
        print "input file needed. try --help"
        sys.exit(2)
        
    data = open(options.infile).read()


    main(data, options.debug)
