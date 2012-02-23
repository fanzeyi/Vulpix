# -*- coding: utf-8 -*-

import re
import string
import datetime

# Configuration for urlize() function
LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']

# list of possible strings used for bullets in bulleted lists
DOTS = ['&middot;', '*', '\xe2\x80\xa2', '&#149;', '&bull;', '&#8226;']

unencoded_ampersands_re = re.compile(r'&(?!(\w+|#\d+);)')
word_split_re = re.compile(r'(\s+)')
punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
    ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
    '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')
link_target_attribute_re = re.compile(r'(<a [^>]*?)target=[^\s>]+')
html_gunk_re = re.compile(r'(?:<br clear="all">|<i><\/i>|<b><\/b>|<em><\/em>|<strong><\/strong>|<\/?smallcaps>|<\/?uppercase>)', re.IGNORECASE)
hard_coded_bullets_re = re.compile(r'((?:<p>(?:%s).*?[a-zA-Z].*?</p>\s*)+)' % '|'.join([re.escape(x) for x in DOTS]), re.DOTALL)
trailing_empty_content_re = re.compile(r'(?:<p>(?:&nbsp;|\s|<br \/>)*?</p>\s*)+\Z')

def submitstatus(value):
    if value == 0:
        cla = "pe"
        status = "Pending"
    elif value == 1:
        cla = "ac"
        status = "Accepted"
    elif value == 2:
        cla = "wa"
        status = "Wrong Answer"
    elif value == 3:
        cla = "tle"
        status = "Time Limit Exceeded"
    elif value == 4:
        cla = "mle"
        status = "Memory Limit Exceeded"
    elif value == 5:
        cla = "re"
        status = "Runtime Error"
    elif value == 6:
        cla = "ce"
        status = "Compile Error"
    else:
        cla = "unknown"
        status = "Unknown"
    return "<span class=\"status %s\">%s</span>" % (cla, status)

def autolink(text, trim_url_limit=None, nofollow=False):
    """
    Converts any URLs in text into clickable links. Works on http://, https:// and
    www. links. Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right thing.

    If trim_url_limit is not None, the URLs in link text will be limited to
    trim_url_limit characters.

    If nofollow is True, the URLs in link text will get a rel="nofollow" attribute.

    Copy from https://github.com/livid/v2ex/blob/master/v2ex/templatetags/filters.py#L35
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (x[:limit] + (len(x) >=limit and '...' or ''))  or x
    words = word_split_re.split(text)
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or ('@' not in middle and not middle.startswith('http://') and \
                    len(middle) > 0 and middle[0] in string.letters + string.digits and \
                    (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                middle = '<a href="http://%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if middle.startswith('http://') or middle.startswith('https://'):
                middle = '<a href="%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if '@' in middle and not middle.startswith('www.') and not ':' in middle \
                and simple_email_re.match(middle):
                middle = '<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return ''.join(words)

def datetimeformat(value, format='%m/%d/%Y %H:%M'):
    return value.strftime(format)

def get_contest_status(contest):
    if contest.invisible:
        return "Invisible"
    now = datetime.datetime.now()
    if now >= contest.start_time and now <= contest.end_time:
        return "Running"
    if now <= contest.start_time:
        return "Waiting"
    if now >= contest.end_time:
        return "Finished"
    return "Unknown"

def get_prev_page(start):
    prev = get_now_page(start) - 10
    return prev if prev >= 0 else 0

def get_now_page(start):
    start = int(start)
    now = start / 10 * 10
    return now

def get_next_page(start):
    return get_now_page(start) + 10

def get_page_nav(pages, start):
    now = start / 10
    dotdot = lambda a: "<li class=\"disabled\"><a href=\"#\">...</a></li>"
    button = lambda page: "<li><a href=\"?start=%d\">%d</a></li>" % (page * 10, page + 1)
    activebutton = lambda page: "<li class=\"active\"><a href=\"?start=%d\">%d</a></li>" % (page * 10, page + 1)
    result = []
    for i in range(pages if pages <= 4 else 4):
        if i == now:
            result.append(activebutton(i))
        else:
            result.append(button(i))
    if now == 3 and pages > 4:
        result.append(button(4))
    if now > 3:
        if now > 4:
            result.append(dotdot(1))
            result.append(button(now - 1))
        result.append(activebutton(now))
        if now + 1 < pages:
            result.append(button(now + 1))
    if now + 1 < pages - 1:
        result.append(dotdot(1))
        result.append(button(pages - 1))
    return result

filters = {
    'submitstatus' :  submitstatus, 
    'autolink'     :  autolink,
    'datetimeformat' : datetimeformat, 
    'get_contest_status' : get_contest_status, 
    'get_prev_page' : get_prev_page, 
    'get_next_page' : get_next_page, 
    'get_page_nav' : get_page_nav, 
}
