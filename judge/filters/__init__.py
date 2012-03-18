# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/filters/__init__.py
# CREATED: 01:48:10 08/03/2012
# MODIFIED: 04:21:53 19/03/2012
# DESCRIPTION: jinja2 filters

import re
import string
import datetime

# Configuration for urlize() function
LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']

# list of possible strings used for bullets in bulleted lists
DOTS = ['&middot;', '*', '\xe2\x80\xa2', '&#149;', '&bull;', '&#8226;']

word_split_re = re.compile(r'(\s+)')
punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
    ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
    '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')

CONTEST_STATUS = {
    1 : ("success", "Running"), 
    2 : ("info", "Waiting"), 
    3 : ("default", "Finished"), 
    4 : ("warning", "Invisible"), 
    5 : ("important", "Unknown"), 
}
SUBMIT_STATUS  = {
    0 : ("info", "Pending"), 
    1 : ("success", "Accepted"), 
    2 : ("important", "Wrong Answer"), 
    3 : ("warning", "Time Limit Exceeded"), 
    4 : ("warning", "Memory Limit Exceeded"), 
    5 : ("inverse", "Runtime Error"), 
    6 : ("default", "Compile Error"), 
    7 : ("default", "No Output"), 
}
ALPHA_STATUS = {
    "a" : 1, 
    "w" : 2, 
    "t" : 3, 
    "m" : 4, 
    "r" : 5, 
    "c" : 6, 
    "n" : 7, 
}

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

def avatar_img(link, size = 45):
    if link != "/static/img/avatar.png":
        link = link + "&s=100"
    return "<img src=\"%s\" width=\"%d\" height=\"%d\" />" % (link, size, size)

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
    if pages - 1 > 3 and now + 1 < pages - 1:
        result.append(dotdot(1))
        result.append(button(pages - 1))
    return result

def datetimeformat(value, format='%m/%d/%Y %H:%M'):
    return value.strftime(format)

def get_contest_status(contest):
    return "<span class=\"label label-%s\">%s</span>" % (CONTEST_STATUS[contest.status])

def get_submit_status(submit):
    if not submit:
        return "-"
    cla, status = SUBMIT_STATUS[submit.status]
    return "<span class=\"label label-%s\">%s</span>" % (cla, status)

def lang2text(lang):
    if lang == 1:
        return "pascal"
    elif lang == 2:
        return "c"
    elif lang == 3:
        return "cpp"

def lang2humantext(lang):
    if lang == 1:
        return "Pascal"
    elif lang == 2:
        return "C"
    elif lang == 3:
        return "C++"

def alpha2status(alpha):
    cla, status = SUBMIT_STATUS[ALPHA_STATUS[str(alpha.lower())]]
    return "<span class=\"label label-%s\">%s</span>" % (cla, status)

filters = {
    'autolink'       : autolink, 
    'avatar_img'     : avatar_img, 
    'get_prev_page'  : get_prev_page, 
    'get_next_page'  : get_next_page, 
    'get_page_nav'   : get_page_nav, 
    'datetimeformat' : datetimeformat, 
    'get_contest_status' : get_contest_status, 
    'get_submit_status' : get_submit_status, 
    'lang2text'      : lang2text, 
    'lang2humantext' : lang2humantext, 
    'alpha2status'   : alpha2status, 
}
