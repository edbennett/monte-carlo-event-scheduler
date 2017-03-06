#!/bin/env python

from lab_defs import Student, Experiment, teaching_length
from lab_mc import all_experiments, experiments, cohort
from loadstore import load_pairs
from assign_students import get_students, match_students
from weeks import all_dates, semester1_dates, semester2_dates

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Flowable, PageBreak, ParagraphAndImage, Spacer
from reportlab.graphics.barcode import code39
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

import io

from datetime import date, timedelta

from loc import localise, strings

from sys import argv

from brand import swansea_logo, logo_width, get_styles

def get_header(semester, styles, level=2, lang="en"):
    title1 = localise(lang, "Department of Physics • Mark Sheet", strings)
    title2 = "Level {} • {}–{} TB{}"

    ay = (date.today() - timedelta(days=180)).year
    contents = [[[swansea_logo],
                [Paragraph(title1, styles["Title"]),
                 Paragraph(title2.format(level, ay,
                                         ay + 1,
                                         semester),
                           styles["Title"])]]]
    table = Table(contents, [logo_width, (210 - 25 - 15) * mm - logo_width])
    table_style = [('VALIGN', (0,0), (-1,-1), 'MIDDLE')]
    table.setStyle(table_style)
    return [table, Spacer(0, 5 * mm)]

def build_document(semester, students, experiments_to_mark, filename, level=2):
    buf = io.BytesIO()
    
    output_doc = SimpleDocTemplate(
        buf,
        rightMargin = 15 * mm,
        leftMargin = 15 * mm,
        topMargin = 15 * mm,
        bottomMargin = 15 * mm,
        pagesize = A4,
        )
    
    styles = get_styles()

    Story = []
    header = get_header(semester, styles, level, "en")

    for experiment in experiments_to_mark:
        Story.extend(print_experiment(experiment, students, semester, styles, header))
        Story.append(PageBreak())
    del Story[-1]
    
    output_doc.build(Story)
    with open(filename, 'wb') as f:
        f.write(buf.getvalue())


def add_row(i, student, day, next_experiment, table_content, table_style, styles, extra_rows):
    cohort_letter = ['A', 'B', 'C', 'D'][cohort(student.pair_number - 1)]
    line = [day.isoformat(), student.number, student.name, student.pair_number,
            cohort_letter, next_experiment] + [None] * 3
    table_content.append(line)
    if i % 2 == 1:
        table_style.append(('BACKGROUND', (0, i + extra_rows), (-1, i + extra_rows), light_grey))

    return extra_rows


def get_instances(experiment, students, semester):
    instances = []
    for student in students.values():
        if semester == "1":
            experiments = student.tb1_experiments
            dates = semester1_dates
        elif semester == "2":
            experiments = student.tb2_experiments
            dates = semester2_dates
        elif semester == "1+2":
            experiments = student.tb1_experiments + student.tb2_experiments
            dates = all_dates
        else:
            raise InvalidArgumentException("Bad semester")

        if experiment in experiments:
            experiment_index = experiments.index(experiment)
            next_experiment = experiments[experiment_index + 1]
            if next_experiment.title.startswith("Report"):
                next_experiment = "REPORT"
                mark_offset = 0
            else:
                next_experiment = next_experiment.acronym
                mark_offset = 1
                
            instances.append((dates[experiment_index + mark_offset] + timedelta(days=(1 - mark_offset)),
                              student, next_experiment))
    return instances

def print_experiment(experiment, students, semester, styles, header):
    Story = []
    Story.extend(header)

    Story.append(Paragraph("{} {}".format(experiment.acronym, experiment.title),
                           styles["Heading1"]))
        
    Story.append(Spacer(0, 5 * mm))
    
    col_heads = ["Mark Date", "Number", "Name", "Pair", "Cohort", "Next Exp.", "Mark", "Special", "On BB"]

    table_content = [col_heads]
    
    table_style = [('BACKGROUND', (0,0), (-1,0), medium_grey),
                   ('INNERGRID', (0,0), (-1,-1), 0.25, black),
                   ('BOX', (0,0), (-1,-1), 0.25, black),
                   ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                   ('FONTNAME', (0,0), (-1,-1), 'Futura'),
                   ('FONTSIZE', (0,0), (-1,-1), 11),
                   ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                   ('BOTTOMPADDING', (0,0), (-1,-1), 5)]

    extra_rows = 1 # Header row
    for i, (day, student, next_experiment) in enumerate(sorted(get_instances(experiment, students, semester))):
        extra_rows = add_row(i, student, day, next_experiment, table_content, table_style, styles, extra_rows)

    row_heights = [8 * mm] * len(table_content)
    table = Table(table_content,
                  rowHeights=row_heights)
        
    table.setStyle(table_style)
    table.hAlign = 'CENTER'
    
    Story.append(table)

    return Story


if __name__ == "__main__":
    if len(argv) > 2:
        experiments_to_mark = [all_experiments[argv.pop()]]
        filename_prefix = "marksheet_{}".format(experiments_to_mark[0].acronym)
    else:
        experiments_to_mark = experiments.values()
        filename_prefix = "marksheet"

    semester = argv.pop()
    filename = filename_prefix + "_TB{}.pdf".format(semester)
    pairs = load_pairs("schedule.dat")
    students = get_students("students.csv")
    match_students(students, pairs)

    build_document(semester, students, experiments_to_mark, filename)
