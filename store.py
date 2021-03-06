import sys, os
import json
import tables

from config import projects

MAX_SIZE = 1000 # 1000 characters

def parse_args(argv):
    args = {
        'facets': [],
        'dest': None,
    }

    pos = 1
    arguments = len(argv) - 1
    if arguments < 1:
        print('Wrong usage, exiting...', file=sys.stderr)
        sys.exit(1)

    while arguments >= pos:
        if argv[pos] == '--facets':
            args['facets'] = argv[pos+1].split(',')
            pos+=2
        else:
            args['dest'] = argv[pos]
            pos+=1

    return args

args = parse_args(sys.argv)

if args['dest'] is None:
    print('Please, provide a file name destination, exiting...', file=sys.stderr)
    sys.exit(1)

columns = projects + ["HTTPServer", "OPENDAP"] + args['facets']
schema = dict(zip(columns, [tables.StringCol(MAX_SIZE)]*len(columns)))

# Create file, table and arrays
f = tables.open_file(args['dest'], mode='w')
filt = tables.Filters(complevel=1, shuffle=True)
files = f.create_table(f.root, 'files', schema, 'files', filters=filt, expectedrows=100000000)

# Populate table and arrays
row = files.row
for line in sys.stdin:
    d = json.loads(line.rstrip('\n'))
    for c in columns:
        if c in d:
            row[c] = d[c]
    row.append()

files.flush()

# Index table
#for eva_aggregation in projects:
#    files.colinstances[eva_aggregation].create_csindex()
files.colinstances['_eva_ensemble_aggregation'].create_csindex()
files.colinstances['_eva_no_frequency'].create_csindex()

f.flush()
