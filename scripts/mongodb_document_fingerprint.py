import sys
from collections import Sequence, Mapping

import pymongo


def get_fingerprint(doc, fingerprint=None):
    if fingerprint is None:
        fingerprint = {}

    if isinstance(doc, Sequence) and not isinstance(doc, basestring):
        list_fingerprint = fingerprint.setdefault('__items__', {})

        for sub_doc in doc:
            get_fingerprint(sub_doc, list_fingerprint)

    elif isinstance(doc, Mapping):
        for key, value in doc.items():
            key_fingerprint = fingerprint.setdefault(key, {})
            get_fingerprint(value, key_fingerprint)
    else:
        types = fingerprint.setdefault('__types__', set())
        types.add(type(doc).__name__)

    return fingerprint


def format_fingerprint(fingerprint):
    result = {}

    types = fingerprint.pop('__types__', None)
    if types:
        types = ','.join(sorted(types))

    items = fingerprint.pop('__items__', None)

    if not fingerprint:
        if not (items and types):
            if items:
                return [format_fingerprint(items)]
            if types:
                return types
            return None

    result = {
        key: format_fingerprint(value)
        for key, value in fingerprint.items()
    }

    if items:
        result['__items__'] = items

    if types:
        result['__types__'] = types

    return result


def main():
    mongo = pymongo.MongoClient('mongodb://127.0.0.1:27017')
    db = mongo.get_database('NAME')

    query = {'namespace.object_id': 'UUID'}

    fingerprint = {}
    page_size = 1000
    page = 0
    max_page = 1 + db.events.find(query).count() / page_size
    while True:
        events = db.events.find(query, limit=page_size, skip=page * page_size)
        events = list(events)
        if not events:
            break

        print 'Page #{} of {}'.format(page + 1, max_page)
        sys.stdout.flush()

        get_fingerprint(events, fingerprint)

        page += 1

    from pprint import pprint
    pprint(format_fingerprint(fingerprint))


if __name__ == '__main__':
    main()
