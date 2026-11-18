import json


def analyze(payload):
    limit = payload['maxBytes']
    records = payload['records']
    if type(limit) is not int or limit < 1 or not isinstance(records, list):
        raise ValueError('Provide a positive integer byte limit and an array of records')
    batches = []
    current = None
    for index, record in enumerate(records):
        line = json.dumps(record, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n'
        size = len(line.encode('utf-8'))
        if size > limit:
            raise ValueError(f'Record {index} needs {size} bytes, above the limit of {limit}')
        if current is None or current['bytes'] + size > limit:
            current = {'start': index, 'count': 0, 'bytes': 0}
            batches.append(current)
        current['count'] += 1
        current['bytes'] += size
    return {'records': len(records), 'totalBytes': sum(batch['bytes'] for batch in batches), 'batches': batches}

if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys
    try:
        path, = sys.argv[1:]
        result = analyze(json.loads(Path(path).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        sys.exit(2)
