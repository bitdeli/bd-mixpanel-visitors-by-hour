from bitdeli import Profiles, Title, Description, set_theme
from textutil import Percent
from itertools import chain
from datetime import datetime
from collections import Counter

CHART_HOURS = 30 * 24
COMPARE_DAYS = 7
COMPARE = COMPARE_DAYS * 24
WINDOW = 48
text = {'window': WINDOW,
        'compare': COMPARE_DAYS}

set_theme('builder')

def average(window):
    total = sum(freq for hour, freq in window)
    return total, int(round(total / float(len(window))))

def hourly_stats(profiles):
    hours = Counter()
    for i, profile in enumerate(profiles):
        events = chain.from_iterable(profile['events'].itervalues())
        hours.update(frozenset(hour for hour, freq in events))
    limit = max(hours) - CHART_HOURS * 24
    return [(datetime.utcfromtimestamp(hour * 3600).isoformat(), freq)
            for hour, freq in sorted(hours.iteritems()) if hour > limit]

def hourly_visitors(profiles):
    stats = hourly_stats(profiles)
    text['total'], text['avg'] = average(stats[-WINDOW:])
    old_total, old_avg = average(stats[-(COMPARE + WINDOW):-COMPARE])
    text['change'] = Percent((text['total'] - old_total) / float(old_total))
    yield {'type': 'line',
           'label': 'hourly users',
           'data': stats,
           'size': (9, 7)}
    yield {'type': 'text',
           'label': 'Avg. hourly users (past %dh)' % WINDOW,
           'color': 2,
           'size': (3, 2),
           'data': {'head': text['avg']}}

Profiles().map(hourly_visitors).show()

Title('{total:,} users seen during the past {window} hours', text)

Description("""
Compared to a corresponding window {compare} days ago, the number of users has {change.verb} by {change}. On average {avg} users have produced events every hour during the past {window} hours.
""", text)

