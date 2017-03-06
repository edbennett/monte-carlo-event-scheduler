#!/usr/bin/env python

import pickle
import io

from lab_defs import teaching_length
from lab_mc import experiments, tutorials, null_experiment
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

from collections import Counter
from itertools import zip_longest 
from datetime import date

def get_header(semester, styles, level=2):
    title1 = "Department of Physics • Experiment List"
    title2 = "Level {} • {}–{} TB{}"

    contents = [[[swansea_logo],
                [Paragraph(title1, styles["Title"]),
                 Paragraph(title2.format(level, date.today().year,
                                         date.today().year + 1,
                                         semester),
                           styles["Title"])]]]
    table = Table(contents, [130, (210 - 15 - 15) * mm - 130])
    table_style = [('VALIGN', (0,0), (-1,-1), 'MIDDLE')]
    table.setStyle(table_style)
    return [table, Spacer(0, 5 * mm)]

def build_table(experiments_by_week, semester, styles):
    if semester == 1:
        dates = semester1_dates
        experiments_by_week = experiments_by_week[:teaching_length]
    elif semester == 1:
        dates = semester2_dates
        experiments_by_week = experiments_by_week[teaching_length:]
    elif semester == "1+2":
        dates = semester1_dates + semester2_dates
    else:
        raise ValueError("Invalid semester")

    contents = [["Week"] + [e.acronym for e in sorted(experiments.values())]]
    table_style = [('BACKGROUND', (0,0), (-1,0), medium_grey),
                   ('INNERGRID', (0,0), (-1,-1), 0.25, black),
                   ('BOX', (0,0), (-1,-1), 0.25, black),
                   ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                   ('FONTNAME', (0,0), (-1,-1), 'Futura'),
                   ('FONTSIZE', (0,0), (-1,-1), 11),
                   ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                   ('BOTTOMPADDING', (0,0), (-1,-1), 5)]
    for week_index, week in enumerate(experiments_by_week):
        current_row = [dates[week_index]]
        counter = Counter(week)
        if week_index % 2 == 1:
            table_style.append(('BACKGROUND', (0,week_index+1), (-1,week_index+1), light_grey))
        for experiment_index, experiment in enumerate(sorted(experiments.values())):
            c = counter[experiment]
            current_row.append("{}".format(c))
            if c == 0:
                table_style.append(('TEXTCOLOR', 
                                    (experiment_index+1,week_index+1),
                                    (experiment_index+1,week_index+1), 
                                    medium_grey))
        contents.append(current_row)
    return contents, table_style

def build_document(experiments_by_week, semester, level, filename):
    buf = io.BytesIO()

    output_doc = SimpleDocTemplate(
        buf,
        rightMargin = 15 * mm,
        leftmargin = 15 * mm,
        topMargin = 15 * mm,
        bottomMargin = 30 * mm,
        pagesize = A4,
        )

    styles = get_styles()

    Story = get_header(semester, styles, level)
    table_content, table_style = build_table(experiments_by_week, semester, styles)
    
    table = Table(table_content)
    table.setStyle(table_style)
    table.hAlign = 'CENTER'
    Story.append(table)

    output_doc.build(Story)
    with open(filename, 'wb') as f:
        f.write(buf.getvalue())



if __name__ == "__main__":
    with open("schedule.dat", "rb") as f:
        pairs = pickle.load(f)

    experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))
    build_document(experiments_by_week, "1+2", 2, "list.pdf")
