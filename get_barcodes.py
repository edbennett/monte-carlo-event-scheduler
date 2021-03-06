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
    barcodes = {True: {}, False: {}}
    with open(filename, 'r') as f:
        barcode_reader = csv.reader(f, delimiter='\t')
        for record in barcode_reader:
            if len(record) == 2:
                barcodes[False][record[0]] = code39.Standard39(
                    record[1], barWidth=0.3 * mm, barHeight=14 * mm
                )
                barcodes[True][record[0]] = code39.Standard39(
                    record[1], barWidth=0.3 * mm, barHeight=7 * mm
                )
    return barcodes


barcodes1 = process("barcodes1.csv")
barcodes2 = process("barcodes2.csv")
barcodesAB = process("barcodesAB.csv")
barcodesCD = process("barcodesCD.csv")

barcodes_all = {5: barcodesAB,
                10: barcodes1,
                16: barcodesCD,
                21: barcodes2}


def get_barcode(student_number, week, narrow):
    return barcodes_all[week][narrow][student_number]
