#!/bin/env python

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

logo_width_in_file = 191.87
logo_height_in_file = 54.84
logo_width = 150
s = logo_width / logo_width_in_file
logo_height = logo_height_in_file * s

swansea_logo = PdfImage(pagexobj(PdfReader("swansea.pdf").pages[0]), logo_width, logo_height)


def get_styles():
    pdfmetrics.registerFont(TTFont('Cosmos', 'Cosmos-Light.ttf'))
    pdfmetrics.registerFont(TTFont('Futura', 'Futura-Book.ttf'))
    pdfmetrics.registerFont(TTFont('FuturaHeavy', 'Futura-Heavy.ttf'))
    pdfmetrics.registerFont(TTFont('AvenirNext', 'Avenir Next.ttc', subfontIndex=5))

    styles = getSampleStyleSheet()
    styles["Title"].textColor = swansea_blue
    styles["Title"].fontName = "Cosmos"
    styles["Heading1"].alignment = TA_CENTER
    styles["Heading1"].fontName = "Futura"#Heavy
    styles["Heading2"].textColor = swansea_blue
    styles["Heading2"].fontName = "Cosmos"
    styles["Normal"].fontName = "Futura"
    styles["Normal"].fontSize = 11
    
    return styles

