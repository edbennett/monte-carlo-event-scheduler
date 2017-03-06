#!/usr/bin/env python

import pickle
import io

from lab_defs import teaching_length
from lab_mc import experiments, tutorials, null_experiment
experiments["LVT"] = tutorials["LVT"]

from print_student import get_styles, swansea_logo
from assign_students import get_students, match_students
from loadstore import load_pairs

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Flowable, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Futura', 'Futura-Book.ttf'))

from pdfrw import PdfReader, PdfDict
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from weeks import semester1_dates, semester2_dates

from collections import Counter
from itertools import zip_longest 
from datetime import date

class MySimpleDocTemplate(SimpleDocTemplate):
     def addPageTemplates(self,pageTemplates):
         '''fix up the one and only Frame'''
         if pageTemplates:
             f = pageTemplates[0].frames[0]
             f._leftPadding=f._rightPadding=f._topPadding=f._bottomPadding=0
             #f._reset()
             f._geom()
         SimpleDocTemplate.addPageTemplates(self,pageTemplates)

def build_table(contents):
    table_style = [('ALIGN', (0,0), (-1,-1), 'CENTER'),
                   ('FONTNAME', (0,0), (-1,-1), 'Futura'),
                   ('FONTSIZE', (0,0), (-1,-1), 11),
                   ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                   ('TOPPADDING', (0,0), (-1,-1), 0),
                   ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                   ('RIGHTPADDING', (0,0), (-1,-1), 0),
                   ('LEFTPADDING', (0,0), (-1,-1), 0)]
    #table = Table(contents, colWidths=49 * mm, rowHeights=30 * mm)
    
    return contents, table_style

def build_document(contents, filename):
    buf = io.BytesIO()

    output_doc = MySimpleDocTemplate(
        buf,
        rightMargin = 5 * mm,
        leftMargin = 5 * mm,
        topMargin = 13 * mm,
        bottomMargin = 13 * mm,
        pagesize = A4,
        )

    Story = []
    table_content, table_style = build_table(contents)
    
    table = Table(table_content, colWidths=[49 * mm] * 4, rowHeights=30 * mm)
    table.setStyle(table_style)
    table.hAlign = 'CENTER'
    Story.append(table)

    output_doc.build(Story)
    with open(filename, 'wb') as f:
        f.write(buf.getvalue())



import csv
from collections import defaultdict
from lab_mc import cohort
from reportlab.graphics.barcode import code39

pairs = load_pairs("schedule.dat")        
students = get_students("students.csv")
match_students(students, pairs)

def process(filename):
    barcodes = {}
    with open(filename, 'r') as f:
        barcode_reader = csv.reader(f, delimiter='\t')
        for record in barcode_reader:
            #print(record)
            if len(record) == 2:
                barcodes[record[0]] = code39.Standard39(record[1], barWidth=0.3 * mm, barHeight=20 * mm)
    return barcodes
                
barcodes1 = process("barcodes1.csv")
barcodes2 = process("barcodes2.csv")
barcodesA = process("barcodesA.csv")
barcodesC = process("barcodesC.csv")


table = []

for student in students.values():
    cohort_letter = ['A', 'B', 'C', 'D'][cohort(student.pair_number - 1)]
    row = []
    row.append('{1} {0}'.format(student.number, cohort_letter))

    if cohort_letter == 'A':
        row.append(barcodesA[student.number])

    row.append(barcodes1[student.number])

    if cohort_letter == 'C':
        row.append(barcodesC[student.number])

    if len(student.tb2_experiments) > 1:
        row.append(barcodes2[student.number])

    table.append(row)
    
build_document(sorted(table), "barcodes.pdf")


