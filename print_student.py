#!/bin/env python

from lab_defs import Student, Experiment, teaching_length
from lab_mc import all_experiments, cohort
from get_barcodes import get_barcode

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

from brand import swansea_logo, logo_width, get_styles

def get_header(semester, styles, level=2, lang="en"):
    title1 = localise(lang, "Department of Physics • Lab Diary", strings)
    title2 = "Level {} • {}–{} TB{}"

    contents = [[[swansea_logo],
                [Paragraph(title1, styles["Title"]),
                 Paragraph(title2.format(level, date.today().year,
                                         date.today().year + 1,
                                         semester),
                           styles["Title"])]]]
    table = Table(contents, [logo_width, (210 - 15 - 25) * mm - logo_width])
    table_style = [('VALIGN', (0,0), (-1,-1), 'MIDDLE')]
    table.setStyle(table_style)
    return [table, Spacer(0, 5 * mm)]


def build_document(students, dates, semester, filename, level=2, include_names=True):
#    print("build_document", include_names)
    buf = io.BytesIO()
    
    output_doc = SimpleDocTemplate(
        buf,
        rightMargin = 30 * mm,
        leftMargin = 15 * mm,
        topMargin = 15 * mm,
        bottomMargin = 15 * mm,
        pagesize = A4,
        )
    
    styles = get_styles()

    Story = []
    header = {"en": get_header(semester, styles, level, "en"),
              "cy": get_header(semester, styles, level, "cy")}

    for student in students:
        Story.extend(print_student(student, dates, semester, styles, header[student.lang], include_names))
        Story.append(PageBreak())
    del Story[-1]
    
    output_doc.build(Story)
    with open(filename, 'wb') as f:
        f.write(buf.getvalue())

submission_report = Experiment("", '<font face="FuturaHeavy">4pm</font>: Submission of lab report', "")
submission_both = Experiment("", '<font face="FuturaHeavy">4pm</font>: Submission of report and lab diary', "")
submission_diary = Experiment("", '<font face="FuturaHeavy">4pm</font>: Submission of lab diary', "")

def add_row(i, student, experiment, day, table_content, table_style, styles, extra_rows):
    '''Add a single row to the table. Unless there is report write up time, in which case add two
    (using recursion), and return extra row count so that rows remain in sync.)'''
    canonical_experiment = (all_experiments[experiment.acronym]
	                    if experiment.acronym != ""
			    else experiment)
    line = [day.isoformat(),
            canonical_experiment.number,
            Paragraph(localise(student.lang, canonical_experiment.title, strings) +
                      ("" if canonical_experiment.writeup else "*"), styles["Normal"]),
                      canonical_experiment.acronym]
    table_content.append(line)
    if i % 2 == 1:
        table_style.append(('BACKGROUND', (0, i + extra_rows), (-1, i + extra_rows), light_grey))

    handin = False
    diary = False
    if ("Report write-up time" in canonical_experiment.title):
        if (i + 1) % teaching_length == 0:
            handin = True
            diary = True
            add_row(i, student, submission_both, day + timedelta(days=1), table_content, table_style, styles, extra_rows + 1)
        else:
            handin = True
            add_row(i, student, submission_report, day + timedelta(days=1), table_content, table_style, styles, extra_rows + 1)

    if "Presentations" in canonical_experiment.title:
        handin = True
        diary = True
        add_row(i, student, submission_diary, day + timedelta(days=1), table_content, table_style, styles, extra_rows + 1)

    if handin:
        extra_rows += 1
    if diary:
        table_style.append(('SPAN', (4, i + extra_rows - 1), (-1, i + extra_rows)))
        table_content[-2].append(get_barcode(student.number, i))
        
    return extra_rows
    
    
def print_student(student, dates, semester, styles, header, include_names=True):
#    print("print_student", include_names)
    Story = []
    Story.extend(header)

#    barcode = code39.Standard39("{} {}".format(student.name, student.number), barWidth = 0.3 * mm)
#    barcode.barHeight = 15 * mm
#    barcode.hAlign = "CENTER"

    pair_text = localise(student.lang, "Pair", strings)
    cohort_text = localise(student.lang, "Cohort", strings)
    cohort_letter = ['A', 'B', 'C', 'D'][cohort(student.pair_number - 1)]
    if include_names:
        Story.append(Paragraph("{} {}, {} {}, {} {}".format(student.number, student.name,
                                                            pair_text, student.pair_number,
                                                            cohort_text, cohort_letter),
                               styles["Heading1"]))
    else:
        Story.append(Paragraph("{} {}".format(pair_text, student.pair_number), styles["Heading1"]))
        
    #    Story.append(barcode)
    Story.append(Spacer(0, 5 * mm))
    
    if semester == 1:
        experiments = student.tb1_experiments
    elif semester == 2:
        experiments = student.tb2_experiments
    elif semester == "1+2":
        experiments = student.tb1_experiments + student.tb2_experiments
    else:
        raise InvalidArgumentException("Bad semester")

    col_heads = ["Date", "Number", "Title", "Code"] + (["Page", "Mark", "Marker"]
                                                       if include_names
                                                       else [])
    table_content = [[localise(student.lang, col_head, strings) 
                      for col_head in col_heads]]
    table_style = [('BACKGROUND', (0,0), (-1,0), medium_grey),
                   ('INNERGRID', (0,0), (-1,-1), 0.25, black),
                   ('BOX', (0,0), (-1,-1), 0.25, black),
                   ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                   ('FONTNAME', (0,0), (-1,-1), 'Futura'),
                   ('FONTSIZE', (0,0), (-1,-1), 11),
                   ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                   ('BOTTOMPADDING', (0,0), (-1,-1), 5)]

    extra_rows = 1 # Header row
    for i, (day, experiment) in enumerate(zip(dates, experiments)):
        extra_rows = add_row(i, student, experiment, day, table_content, table_style, styles, extra_rows)

    row_heights = [8 * mm] * len(table_content)
    table = Table(table_content,
                  colWidths=[None,None,75*mm, None] + ([13 * mm, 13 * mm, 16 * mm] if include_names else []),
                  rowHeights=row_heights)
        
    table.setStyle(table_style)
    table.hAlign = 'CENTER'
    
    Story.append(table)

    Story.append(Paragraph(localise(student.lang,"* Do not write up these experiments", strings), 
                           styles["Normal"]))
    
    return Story


if __name__ == "__main__":
    
    test_student = Student("360117", 
                           "Ed Bennett", 
                           [Experiment(201, "Numerical Analysis", "NA", writeup=False)], 
                           [Experiment("", "LabVIEW", "LV", writeup=False)], 
                           0,
                           False)
    build_document([test_student, test_student], [date.today()], 1, "test.pdf")
    
