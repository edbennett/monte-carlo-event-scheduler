#!/usr/bin/env python

import io

from lab_defs import teaching_length
from lab_mc import experiments, tutorials, null_experiment, cohort
experiments["LVT"] = tutorials["LVT"]

from print_student import get_styles, swansea_logo

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Flowable, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from colours import swansea_blue, light_grey, medium_grey, black

from pdfrw import PdfReader, PdfDict
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from weeks import semester1_dates, semester2_dates
from get_students_by_week import get_students_by_pair, get_pairs_by_week
from bare_print_marking import get_dates
from loadstore import load_pairs
from assign_students import get_students, match_students
from weeks import all_dates

from sys import argv

from collections import Counter
from itertools import zip_longest 
from datetime import date

def get_header(styles, year=date.today().year, level=2):
    title1 = "Department of Physics • Marking List"
    title2 = "Level {} • {}–{}"

    contents = [[[swansea_logo],
                [Paragraph(title1, styles["Title"]),
                 Paragraph(title2.format(level, year,
                                         year + 1),
                           styles["Title"])]]]
    table = Table(contents, [130, (210 - 15 - 15) * mm - 130])
    table_style = [('VALIGN', (0,0), (-1,-1), 'MIDDLE')]
    table.setStyle(table_style)
    return [table, Spacer(0, 5 * mm)]


def print_experiment(title, students, to_date, styles):
    story = [Paragraph(title, styles['Heading2'])]
    student_details = []
    for student in students:
        student_experiments = student.tb1_experiments + student.tb2_experiments
        cohort_letter = ['A', 'B', 'C', 'D'][cohort(student.pair_number - 1)]
        student_details.append((student_experiments[all_dates.index(to_date)].acronym,
                                student.number, student.name, cohort_letter))
    student_details.sort()

    for student_detail in student_details:
        line = " • {} {} {} {}".format(*student_detail)
        element = Paragraph(line, styles['Normal'])
        story.append(element)

    return story

def print_week(to_date, from_date, experiments_by_week, students, experiments_to_mark, styles):
    if len(experiments_to_mark) > 1:
        thing_to_mark = "Experiment"
    else:
        thing_to_mark = experiments_to_mark[0].acronym
        
    story = [Paragraph(("{}s to be marked on week of {}, from week of {}. "
                        "Acronym indicates what experiment is being done this week. "
                        "Letter is cohort."
                       ).format(thing_to_mark, to_date, from_date), styles['Normal'])]
    for experiment in sorted(experiments_to_mark):
        found_pairs = get_pairs_by_week(from_date, experiment.acronym, all_dates, experiments_by_week)
        found_students = get_students_by_pair(students.values(), found_pairs)
        if len(found_students) > 0:
            story += print_experiment(experiment.title, found_students, to_date, styles)

    return story


def build_document(experiments_by_week, to_date, from_date, students,
                   experiments_to_mark, filename):
    buf = io.BytesIO()

    output_doc = SimpleDocTemplate(
        buf,
        rightMargin = 15 * mm,
        leftmargin = 15 * mm,
        topMargin = 15 * mm,
        bottomMargin = 25 * mm,
        pagesize = A4,
        )

    styles = get_styles()

    Story = get_header(styles)
    Story += print_week(to_date, from_date, experiments_by_week, students,
                        experiments_to_mark, styles)
    
    output_doc.build(Story)
    with open(filename, 'wb') as f:
        f.write(buf.getvalue())



if __name__ == "__main__":
    if len(argv) in [2, 5, 8]:
        experiments_to_mark = [experiments[argv.pop()]]
        filename_prefix = "mark_{}".format(experiments_to_mark[0].acronym)
    else:
        experiments_to_mark = experiments.values()
        filename_prefix = "marking"

    to_date, from_date = get_dates(argv)

    pairs = load_pairs("schedule.dat")
    students = get_students("students.csv")
    match_students(students, pairs)
    
    experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))
    
    build_document(experiments_by_week, to_date, from_date, students, experiments_to_mark,
                   "{}_{}_on_{}.pdf".format(filename_prefix, from_date, to_date))
