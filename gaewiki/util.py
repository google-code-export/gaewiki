# encoding=utf-8

import logging
import re
import urllib

import data
import settings


def parse_page(page_content):
    options = {}
    parts = page_content.split('---', 1)
    if len(parts) == 2:
        for line in parts[0].split('\n'):
            if not line.startswith('#'):
                kv = line.split(':', 1)
                if len(kv) == 2:
                    k = kv[0].strip()
                    v = kv[1].strip()
                    if k.endswith('s'):
                        v = re.split(',\s*', v)
                    options[k] = v
    options['text'] = parts[-1]
    return options


def pageurl(title):
    if type(title) == unicode:
        title = title.encode('utf-8')
    elif type(title) != str:
        title = str(title)
    return '/' + urllib.quote(title.replace(' ', '_'))


WIKI_WORD_PATTERN = re.compile('\[\[([^]|]+\|)?([^]]+)\]\]')

def wikify(text, title=None):
    text, count = WIKI_WORD_PATTERN.subn(lambda x: wikify_one(x, title), text)
    text = re.sub(r'\.  ', '.&nbsp; ', text)
    text = re.sub(u' (—|--) ', u'&nbsp;— ', text)
    return text

def wikify_one(pat, real_page_title):
    """
    Wikifies one link.
    """
    page_title = pat.group(2)
    if pat.group(1):
        page_name = pat.group(1).rstrip('|')
    else:
        page_name = page_title

    # interwiki
    if ':' in page_name:
        parts = page_name.split(':', 1)
        if ' ' not in parts[0]:
            if page_name == page_title:
                page_title = parts[1]
            if parts[0] == 'List':
                return list_pages_by_label(parts[1])
            if parts[0] == 'ListChildren':
                return list_pages_by_label('gaewiki:parent:' + (parts[1] or real_page_title))
            iwlink = setting.get(u'interwiki-' + parts[0])
            if iwlink:
                return '<a class="iw iw-%s" href="%s" target="_blank">%s</a>' % (parts[0], iwlink.replace('%s', urllib.quote(parts[1].encode('utf-8'))), page_title)

    return '<a class="int" href="%s">%s</a>' % (pageurl(page_name), page_title)

def list_pages_by_label(label):
    pages = data.get_by_label(label)
    text = u'\n'.join(['- <a class="int" href="%s">%s</a>' % (pageurl(p.title), p.title) for p in pages])
    return text