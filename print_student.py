#!/bin/env python

from lab_defs import Student, Experiment
from lab_mc import all_experiments

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Flowable, PageBreak, ParagraphAndImage, Spacer
from reportlab.graphics.barcode import code39
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from reportlab.pdfbase import pdfmetrics 
from reportlab.pdfbase.ttfonts import TTFont 

from reportlab.lib.colors import CMYKColor
swansea_blue = CMYKColor(1, 0.53, 0.04, 0.19)
light_grey = CMYKColor(0, 0, 0, 0.1)
medium_grey = CMYKColor(0, 0, 0, 0.2)
black = CMYKColor(0, 0, 0, 1)

from pdfrw import PdfReader, PdfDict
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

import io

from datetime import date


class PdfImage(Flowable):
    '''from http://stackoverflow.com/questions/31712386/loading-matplotlib-object-into-reportlab/'''
    def __init__(self, img_data, width=200, height=200):
        self.img_width = width
        self.img_height = height
        self.img_data = img_data

    def wrap(self, width, height):
        return self.img_width, self.img_height

    def drawOn(self, canv, x, y, _sW=0):
        if _sW > 0 and hasattr(self, 'hAlign'):
            a = self.hAlign
            if a in ('CENTER', 'CENTRE', TA_CENTER):
                x += 0.5*_sW
            elif a in ('RIGHT', TA_RIGHT):
                x += _sW
            elif a not in ('LEFT', TA_LEFT):
                raise ValueError("Bad hAlign value " + str(a))
        canv.saveState()
        img = self.img_data
        if isinstance(img, PdfDict):
            xscale = self.img_width / img.BBox[2]
            yscale = xscale
            self.img_height = img.BBox[3] * yscale
#            yscale = self.img_height / img.BBox[3]

            canv.translate(x, y)
            canv.scale(xscale, yscale)
            canv.doForm(makerl(canv, img))
        else:
            canv.drawImage(img, x, y, self.img_width, self.img_height)
        canv.restoreState()

s = 0.7
swansea_logo = PdfImage(pagexobj(PdfReader("swanseaA.pdf").pages[0]), 130 * s, 81 * s)

def get_header(semester, styles, level=2, cymraeg=False):
    if cymraeg:
        title1 = "Adran Ffiseg • Dyddiadur Labordy"
        title2 = "Lefel {} • {}–{} BD{}"
    else:
        title1 = "Department of Physics • Lab Diary"
        title2 = "Level {} • {}–{} TB{}"

    contents = [[[swansea_logo],
                [Paragraph(title1, styles["Title"]),
                 Paragraph(title2.format(level, date.today().year,
                                         date.today().year + 1,
                                         semester),
                           styles["Title"])]]]
    table = Table(contents, [130, (210 - 15 - 25) * mm - 130])
    table_style = [('VALIGN', (0,0), (-1,-1), 'MIDDLE')]
    table.setStyle(table_style)
    return [table, Spacer(0, 5 * mm)]

def get_styles():
    pdfmetrics.registerFont(TTFont('Cosmos', 'CosmosBQ-Medium.ttf'))
    pdfmetrics.registerFont(TTFont('Futura', 'Futura-Book.ttf'))
    pdfmetrics.registerFont(TTFont('FuturaHeavy', 'Futura-Heavy.ttf'))
    pdfmetrics.registerFont(TTFont('AvenirNext', 'Avenir Next.ttc', subfontIndex=5))

    styles = getSampleStyleSheet()
    styles["Title"].textColor = swansea_blue
    styles["Title"].fontName = "Cosmos"
    styles["Heading1"].alignment = TA_CENTER
    styles["Heading1"].fontName = "Futura"#Heavy                                                                                                                                
    styles["Normal"].fontName = "Futura"
    styles["Normal"].fontSize = 11
    
    return styles

def build_document(students, dates, semester, filename, level=2):
    buf = io.BytesIO()
    
    output_doc = SimpleDocTemplate(
        buf,
        rightMargin = 30 * mm,
        leftmargin = 15 * mm,
        topMargin = 15 * mm,
        bottomMargin = 30 * mm,
        pagesize = A4,
        )
    
    styles = get_styles()

    Story = []
    english_header = get_header(semester, styles, level, False)
    cymraeg_header = get_header(semester, styles, level, True)

    for student in students:
        Story.extend(print_student(student, dates, semester, styles, 
                                   cymraeg_header if student.cymraeg else english_header))
        Story.append(PageBreak())
    del Story[-1]
    
    output_doc.build(Story)
    with open(filename, 'wb') as f:
        f.write(buf.getvalue())

def print_student(student, dates, semester, styles, header):
    Story = []
    Story.extend(header)

    barcode = code39.Standard39("{} {}".format(student.name, student.number), barWidth = 0.3 * mm)
    barcode.barHeight = 15 * mm
    barcode.hAlign = "CENTER"

    pair = "Pâr" if student.cymraeg else "Pair"
    Story.append(Paragraph("{} {}, {} {}".format(student.name, student.number, pair, student.pair_number),
                           styles["Heading1"]))
    Story.append(barcode)
    Story.append(Spacer(0, 5 * mm))
    
    if semester == 1:
        experiments = student.tb1_experiments
    elif semester == 2:
        experiments = student.tb2_experiments
    elif semester == "1+2":
        experiments = student.tb1_experiments + student.tb2_experiments
    else:
        raise InvalidArgumentException("Bad semester")

    if student.cymraeg:
        table_content = [["Dyddiad", "Rhif", "Teitl", "Cod", "Tudalen", "Marc", "Marcwr"]]
    else:
        table_content = [["Date", "Number", "Title", "Code", "Page", "Mark", "Marker"]]
    table_style = [('BACKGROUND', (0,0), (-1,0), medium_grey),
                   ('INNERGRID', (0,0), (-1,-1), 0.25, black),
                   ('BOX', (0,0), (-1,-1), 0.25, black),
                   ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                   ('FONTNAME', (0,0), (-1,-1), 'Futura'),
                   ('FONTSIZE', (0,0), (-1,-1), 11),
                   ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                   ('BOTTOMPADDING', (0,0), (-1,-1), 5)]
    for i, (day, experiment) in enumerate(zip(dates, experiments)):
        canonical_experiment = (all_experiments[experiment.acronym] 
                                if experiment.acronym != ""
                                else experiment)
        line = [day.isoformat(),
                canonical_experiment.number,
                Paragraph((canonical_experiment.teitl if student.cymraeg else canonical_experiment.title) + 
                ("" if canonical_experiment.writeup else "*"), styles["Normal"]),
                canonical_experiment.acronym,
                "", "", ""]
        table_content.append(line)
        if i % 2 == 1:
            table_style.append(('BACKGROUND', (0,i+1), (-1,i+1), light_grey))
    table = Table(table_content, colWidths=[None,None,75*mm,None,None,None], rowHeights=8*mm)
    table.setStyle(table_style)
    table.hAlign = 'CENTER'
    
    Story.append(table)

    Story.append(Paragraph("* Peidiwch ag ysgrifennu am yr arbrofion hyn" if student.cymraeg else
                           "* Do not write up these experiments", 
                           styles["Normal"]))
    
    return Story


if __name__ == "__main__":
    
    test_student = Student("360117", 
                           "Ed Bennett", 
                           [Experiment(201, "Numerical Analysis", "Analeg Niwmerical", "NA", writeup=False)], 
                           [Experiment("", "LabVIEW", "LabFIW", "LV", writeup=False)], 
                           0,
                           False)
    build_document([test_student, test_student], [date.today()], 1, "test.pdf")
    
