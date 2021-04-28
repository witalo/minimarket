import decimal
from http import HTTPStatus

import reportlab
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import landscape, A5, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Spacer, Image
from reportlab.platypus import Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.rl_settings import defaultPageSize

from apps.hrm.models import Employee
from ventura import settings
from apps.accounting.models import Payments, Casing
from apps.sale.number_to_letters import numero_a_moneda
from django.contrib.auth.models import User
from django.db.models import Min, Max, Sum, Count, Q
import io
from .zone import utc_to_local
import datetime
from datetime import datetime

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT, leading=8, fontName='Square', fontSize=8))
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, leading=8, fontName='Square', fontSize=8))
styles.add(ParagraphStyle(name='Justify-Dotcirful', alignment=TA_JUSTIFY, leading=12, fontName='Dotcirful-Regular',
                          fontSize=10))
styles.add(
    ParagraphStyle(name='Justify-Dotcirful-table', alignment=TA_JUSTIFY, leading=12, fontName='Dotcirful-Regular',
                   fontSize=7))
styles.add(ParagraphStyle(name='Justify_Bold', alignment=TA_JUSTIFY, leading=8, fontName='Square-Bold', fontSize=8))
styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, leading=8, fontName='Square', fontSize=8))
styles.add(
    ParagraphStyle(name='Center-Dotcirful', alignment=TA_CENTER, leading=12, fontName='Dotcirful-Regular', fontSize=10))
styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT, leading=8, fontName='Square', fontSize=8))
styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, leading=8, fontName='Square-Bold', fontSize=8))
styles.add(ParagraphStyle(name='CenterTitle-Dotcirful', alignment=TA_CENTER, leading=12, fontName='Dotcirful-Regular',
                          fontSize=10))
styles.add(ParagraphStyle(name='CenterTitle2', alignment=TA_CENTER, leading=8, fontName='Square-Bold', fontSize=12))
styles.add(ParagraphStyle(name='Center_Regular', alignment=TA_CENTER, leading=8, fontName='Ticketing', fontSize=10))
styles.add(ParagraphStyle(name='Center_Bold', alignment=TA_CENTER,
                          leading=8, fontName='Square-Bold', fontSize=12, spaceBefore=6, spaceAfter=6))
styles.add(ParagraphStyle(name='Center2', alignment=TA_CENTER, leading=8, fontName='Ticketing', fontSize=8))
styles.add(ParagraphStyle(name='Center3', alignment=TA_JUSTIFY, leading=8, fontName='Ticketing', fontSize=7))
style = styles["Normal"]

reportlab.rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
pdfmetrics.registerFont(TTFont('Square', 'square-721-condensed-bt.ttf'))
pdfmetrics.registerFont(TTFont('Square-Bold', 'sqr721bc.ttf'))
pdfmetrics.registerFont(TTFont('Newgot', 'newgotbc.ttf'))
pdfmetrics.registerFont(TTFont('Ticketing', 'ticketing.regular.ttf'))
pdfmetrics.registerFont(TTFont('Lucida-Console', 'lucida-console.ttf'))
pdfmetrics.registerFont(TTFont('Square-Dot', 'square_dot_digital-7.ttf'))
pdfmetrics.registerFont(TTFont('Serif-Dot', 'serif_dot_digital-7.ttf'))
pdfmetrics.registerFont(TTFont('Enhanced-Dot-Digital', 'enhanced-dot-digital-7.regular.ttf'))
pdfmetrics.registerFont(TTFont('Merchant-Copy-Wide', 'MerchantCopyWide.ttf'))
pdfmetrics.registerFont(TTFont('Dot-Digital', 'dot_digital-7.ttf'))
pdfmetrics.registerFont(TTFont('Raleway-Dots-Regular', 'RalewayDotsRegular.ttf'))
pdfmetrics.registerFont(TTFont('Ordre-Depart', 'Ordre-de-Depart.ttf'))
pdfmetrics.registerFont(TTFont('Dotcirful-Regular', 'DotcirfulRegular.otf'))
pdfmetrics.registerFont(TTFont('Nationfd', 'Nationfd.ttf'))
pdfmetrics.registerFont(TTFont('Kg-Primary-Dots', 'KgPrimaryDots-Pl0E.ttf'))
pdfmetrics.registerFont(TTFont('Dot-line', 'Dotline-LA7g.ttf'))
pdfmetrics.registerFont(TTFont('Dot-line-Light', 'DotlineLight-XXeo.ttf'))
pdfmetrics.registerFont(TTFont('Jd-Lcd-Rounded', 'JdLcdRoundedRegular-vXwE.ttf'))

logo = "static/img/logo1.jpg"


def print_ticket_closing_cash(request, pk=None):  # ticket de cierre de caja

    _wt = 3.25 * inch - 8 * 0.05 * inch
    # _wt = 3.14 * inch - 8 * 0.05 * inch

    payment_obj = Payments.objects.get(pk=int(pk))
    user_id = payment_obj.user.id
    user_obj = User.objects.get(id=user_id)

    tbh_business_name_address = 'COMERCIALIZADORA DE PRODUCTOS NACIONALES E INTERNACIONALES DON PEPITO S.A.C.\nAV. MARISCAL CASTILLA NUMERO 327 URB. SIMON BOLIVAR AREQUIPA - AREQUIPA - MIRAFLORES\n RUC: 20601927820'

    date = utc_to_local(payment_obj.create_at)
    _format_time = date.strftime('%H:%M:%S')
    _format_date = date.strftime("%d/%m/%Y")

    title = 'CIERRE DE CAJA'
    line = '---------------------------------------------------------'

    I = Image(logo)
    I.drawHeight = 2.35 * inch / 2.9
    I.drawWidth = 3.4 * inch / 2.9

    style_table = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('BOTTOMPADDING', (0, 0), (-1, -1), -1),  # all columns
        ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
        ('ALIGNMENT', (0, 0), (1, -1), 'LEFT'),  # second column
        ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
    ]
    colwiths_table = [_wt * 40 / 100, _wt * 60 / 100]
    employee_obj = Employee.objects.get(user=user_obj)

    if user_obj is not None:
        p0 = Paragraph(employee_obj.document_number, styles["Justify"])
        p1 = Paragraph(employee_obj.full_name(), styles["Justify"])
        p2 = Paragraph(employee_obj.get_occupation_display(), styles["Justify"])
        ana_c1 = Table(
            [('Documento: ', p0)] +
            [('Responsable: ', p1)] +
            [('Cargo: ', p2)] +
            [('Fecha: ', _format_date + '  Hora: ' + _format_time)],
            colWidths=colwiths_table)

    ana_c1.setStyle(TableStyle(style_table))

    my_style_header = [
        ('FONTNAME', (0, 0), (-1, -1), 'Ticketing'),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # all columns
        ('BOTTOMPADDING', (0, 0), (-1, -1), -6),  # all columns
        ('RIGHTPADDING', (3, 0), (3, -1), 0),  # four column
        ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # four column
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # first column
        ('FONTNAME', (0, 2), (-1, 2), 'Ticketing'),  # third row
        ('FONTSIZE', (0, 2), (-1, 2), 9),  # third row

        ('LEFTPADDING', (2, 0), (2, -1), 5),
        ('ALIGNMENT', (2, 0), (2, -1), 'CENTER'),

        ('LEFTPADDING', (1, 0), (1, -1), 0),
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),

        ('RIGHTPADDING', (4, 0), (4, -1), 0),
        ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),
    ]

    ana_header = Table(
        [('OPERACION', 'MONTO')],
        colWidths=[_wt * 75 / 100, _wt * 25 / 100]
    )
    ana_header.setStyle(TableStyle(my_style_header))

    my_style_table_detail = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),  # second column
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # ('ALIGNMENT', (2, 0), (2, -1), 'CENTER'),  # third column
        # ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),
        # ('RIGHTPADDING', (3, 0), (3, -1), 0),
        # ('ALIGNMENT', (4, 0), (4, -1), 'RIGHT'),
        # ('RIGHTPADDING', (4, 0), (4, -1), 0),
    ]
    _rows = []
    subsidiary_obj = payment_obj.subsidiary
    casing_obj = payment_obj.casing
    d1 = Paragraph('APERTURA DE CAJA', styles["Justify"])
    payment_aperture_obj = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                   type_payment='E', type='A').last()
    _rows.append((d1, str(decimal.Decimal(round(payment_aperture_obj.amount, 2)))))
    d2 = Paragraph('TOTAL VENTA EN EFECTIVO', styles["Justify"])
    payment_total_cash = Payments.objects.filter(casing=casing_obj, subsidiary=subsidiary_obj,
                                                 type_payment='E', type='I',
                                                 create_at__gte=payment_aperture_obj.create_at).aggregate(
        Sum('amount'))
    if payment_total_cash is not None:
        total_cash = payment_total_cash['amount__sum']
    else:
        total_cash = 0
    _rows.append((d2, str(decimal.Decimal(round(total_cash, 2)))))
    d3 = Paragraph('TOTAL VENTA EN DEPOSITO', styles["Justify"])
    payment_total_deposit = Payments.objects.filter(user=user_obj, subsidiary=subsidiary_obj,
                                                    type_payment='D', type='I',
                                                    create_at__gte=payment_aperture_obj.create_at).aggregate(
        Sum('amount'))
    if payment_total_deposit is not None:
        total_deposit = payment_total_deposit['amount__sum']
    else:
        total_deposit = 0
    _rows.append((d3, str(decimal.Decimal(round(total_deposit, 2)))))

    ana_c_detail = Table(_rows,
                         colWidths=[_wt * 60 / 100, _wt * 40 / 100])
    ana_c_detail.setStyle(TableStyle(my_style_table_detail))

    my_style_total = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square-Bold'),  # all columns
        #('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # all columns
        ('ALIGNMENT', (1, 0), (3, -1), 'RIGHT'),  # four column
        ('LEFTPADDING', (0, 0), (-1, -1), 0),  # first column
        ('FONTNAME', (0, 2), (-1, 2), 'Square-Bold'),  # third row
        ('FONTSIZE', (0, 2), (-1, 2), 10),  # third row
        ('RIGHTPADDING', (0, 0), (-1, -1), 0.9),  # four column
    ]

    ana_total = Table(
        [('TOTAL', '', 'S/.  ', str(round(total_cash, 2)))],
        colWidths=[_wt * 50 / 100, _wt * 15 / 100, _wt * 10 / 100, _wt * 25 / 100]
    )
    ana_total.setStyle(TableStyle(my_style_total))

    footer = 'SON: ' + numero_a_moneda(total_cash)
    my_style_table6 = [
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
        ('SPAN', (0, 0), (1, 0)),  # first row
    ]

    datatable = 'Visitanos en https://www.venturaflores.com'
    # ana_c9 = Table([(qr_code(datatable), '')], colWidths=[_wt * 99 / 100, _wt * 1 / 100])
    # ana_c9.setStyle(TableStyle(my_style_table6))

    _dictionary = []
    _dictionary.append(I)
    _dictionary.append(Spacer(1, 5))
    _dictionary.append(Paragraph(tbh_business_name_address.replace("\n", "<br />"), styles["Center"]))
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(Paragraph(title, styles["Center_Regular"]))
    _dictionary.append(Spacer(1, 3))
    _dictionary.append(ana_c1)
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(Spacer(1, 3))
    _dictionary.append(Paragraph('RESUMEN DEL CIERRE DE CAJA', styles["Center_Regular"]))
    _dictionary.append(Spacer(1, 3))
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(ana_header)
    _dictionary.append(Spacer(1, 2))
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(ana_c_detail)  # "ana_c2"
    _dictionary.append(Spacer(1, 3))
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(ana_total)
    _dictionary.append(Spacer(1, 3))
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(Paragraph(footer, styles["Center"]))
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(
        Paragraph("***COMPROBANTE DEL CIERRE DE CAJA***".replace('***', '"'), styles["Center2"]))
    # _dictionary.append(ana_c9)
    _dictionary.append(Paragraph("DESARROLLADO POR IVANET",
                                 styles["Center2"]))
    _dictionary.append(Spacer(1, 2))
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(Spacer(1, 2))
    _dictionary.append(Paragraph(
        "www.ivanet.com",
        styles["Center2"]))
    buff = io.BytesIO()

    ml = 0.05 * inch
    mr = 0.055 * inch
    ms = 0.039 * inch
    mi = 0.039 * inch

    doc = SimpleDocTemplate(buff,
                            pagesize=(3.14961 * inch, 6.6 * inch),
                            rightMargin=mr,
                            leftMargin=ml,
                            topMargin=ms,
                            bottomMargin=mi,
                            title='TICKET'
                            )
    doc.build(_dictionary)
    # doc.build(elements)
    # doc.build(Story)

    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'inline; filename="somefilename.pdf"'
    # response['Content-Disposition'] = 'attachment; filename="ORDEN[{}].pdf"'.format(
    #     str(order_obj.subsidiary_store.subsidiary.serial) + '-' + str(order_obj.id))

    response.write(buff.getvalue())
    buff.close()
    return response
