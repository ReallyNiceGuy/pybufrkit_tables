#!/usr/bin/python3

# Pass the path for the end of the definition:
# To convert table version 11 of centre 85 and subcentre 0,
# you should pass:
# /somewhere/definitions/bufr/tables/0/local/11/85/0
# The code will parse the path and recover the
# version, centre and subcentre from the last 3 directories

from pathlib import Path
import sys
import csv
import json
import re

def float_or_int(value):
    i = int(value)
    f = float(value)
    if i == f:
        return i
    return f

def parse_path(the_path):
    subcentre = the_path.stem
    centre = the_path.parent.stem
    version = the_path.parent.parent.stem
    return (version, '0' if centre == 'wmo' else centre , subcentre)


def elements_to_tableB(the_path):
    fieldnames = [
        'id',
        'ec_name',
        'ec_type',
        'desc',
        'type',
        'exponent',
        'offset',
        'size',
        'crex_type',
        'crex_exponent',
        'crex_size',
    ]

    tableB = {}
    with open(the_path / 'element.table', newline='') as csvfile:
        reader = csv.DictReader(csvfile,  fieldnames=fieldnames, delimiter='|')

        for row in reader:
            tableB[row['id']] = [row['desc'], row['type'], int(row['exponent']), float_or_int(row['offset']), int(row['size']), row['crex_type'], int(row['crex_exponent']), int(row['crex_size'])]

    return tableB


def sequence_to_tableD(the_path):
    chars_to_remove = re.compile('[\t\n\] ["]')
    tableD = {}
    with open(the_path / 'sequence.def') as f:
        for row in f:
            the_id, the_list = re.sub(chars_to_remove, '', row).split('=')
            tableD[the_id] = the_list.split(",")
    return tableD


def codetable_to_list(the_file):
    result = []
    with open(the_file) as f:
        for row in f:
            value, _, desc = row.strip().split(' ', maxsplit=2)
            result.append([value, desc])
    return result


def codetables_to_code_and_flag(the_path):
    code_and_flag = {}
    # might not exist
    codetables_path = the_path / 'codetables'
    if codetables_path.is_dir():
        for entry in codetables_path.iterdir():
            if entry.is_file() and entry.suffix == '.table':
                code_and_flag[f'{entry.stem:0>6}'] = codetable_to_list(entry)

    return code_and_flag


if __name__ == "__main__":
    input_path = Path(sys.argv[1])
    version, centre, subcentre = parse_path(input_path)

    output_path = Path(sys.argv[2]) / f'{centre}_{subcentre}' / version
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / 'tableB.json', 'w') as f:
        json.dump(elements_to_tableB(input_path), f)
    with open(output_path / 'tableD.json', 'w') as f:
        json.dump(sequence_to_tableD(input_path), f)
    with open(output_path / 'code_and_flag.json', 'w') as f:
        json.dump(codetables_to_code_and_flag(input_path), f)