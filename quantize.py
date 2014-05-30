import re
import sys

details = {}
for line in sys.stdin:
    line = line.strip()
    name = re.findall('^(.*?) ', line)[0]
    data = re.sub('^(.*?) ','',line)
    data = eval(data)
    details[name] = data

eng_word_ratio = details['eng_word_count']/float(details['word_count'])
word_recurrance_ratio = details['word_reoccurance_count']/float(details['word_count'])
categories_ratio = details['categories_count']/float(details['word_count'])
categories_reoccurance_ratio = details['categories_reoccurance_count']/float(details['word_count'])
wiki_fail_ratio = (details['non_wiki_word_count']+details['disambig_word_count'])/float(details['word_count'])
places_ratio = details['places_count']/float(details['word_count'])

print 'eng_word_ratio', eng_word_ratio
print 'word_recurrance_ratio', word_recurrance_ratio
print 'categories_ratio', categories_ratio
print 'categories_reoccurance_ratio', categories_reoccurance_ratio
print 'wiki_fail_ratio', wiki_fail_ratio
print 'places_ratio', places_ratio

#print 'creativity index', 10*(5*categories_ratio+categories_reoccurance_ratio+wiki_fail_ratio+10*places_ratio) - (eng_word_ratio+word_recurrance_ratio)
print 'creativity index', 10*(5*categories_ratio+wiki_fail_ratio+10*places_ratio) - (eng_word_ratio+word_recurrance_ratio+categories_reoccurance_ratio)

