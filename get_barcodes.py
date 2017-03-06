#!/usr/bin/env python

import pickle
import io

from lab_defs import teaching_length
from lab_mc import experiments, tutorials
experiments["LVT"] = tutorials["LVT"]

from reportlab.lib.units import mm

import csv
from lab_mc import cohort
from reportlab.graphics.barcode import code39


def process(filename):
    barcodes = {}
    with open(filename, 'r') as f:
        barcode_reader = csv.reader(f, delimiter='\t')
        for record in barcode_reader:
            #print(record)
            if len(record) == 2:
                barcodes[record[0]] = code39.Standard39(record[1], barWidth=0.3 * mm, barHeight=14 * mm)
    return barcodes
                
barcodes1 = process("barcodes1.csv")
barcodes2 = process("barcodes2.csv")
barcodesA = process("barcodesA.csv")
barcodesC = process("barcodesC.csv")

barcodes_all = [barcodesA, barcodes1, barcodesC, barcodes2]

event = {5: 0, 10: 1, 16: 2, 21: 3}

def get_barcode(student_number, week):
     return barcodes_all[event[week]][student_number]
