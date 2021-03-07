import decimal
import reportlab
from django.http import HttpResponse
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
from ventura import settings
from apps.sale.format_to_dates import utc_to_local
from apps.sale.number_to_letters import numero_a_moneda
from apps.sale.models import Order, Client
import io
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


def print_ticket_order_sales(request, pk=None):  # Boleto de viaje boleta / factura

    _wt = 3.25 * inch - 8 * 0.05 * inch
    # _wt = 3.14 * inch - 8 * 0.05 * inch

    order_obj = Order.objects.get(pk=int(pk))
    client_id = order_obj.client.id
    client_obj = Client.objects.get(id=client_id)
    client_name = ""
    client_document = ""
    client_name = ""
    client_address = ""

    tbh_business_name_address = 'COMERCIALIZADORA DE PRODUCTOS NACIONALES E INTERNACIONALES DON PEPITO S.A.C.\nAV. MARISCAL CASTILLA NUMERO 327 URB. SIMON BOLIVAR AREQUIPA - AREQUIPA - MIRAFLORES\n RUC: 20601927820'

    date = order_obj.update_at
    _format_time = datetime.now().strftime('%H:%M:%S')
    _format_date = date.strftime("%d/%m/%Y")

    tbn_document = 'ORDEN DE VENTA'

    client_type = client_obj.type_document
    client_name = client_obj.full_names
    client_document = client_obj.document
    if client_type == '06':
        client_address = client_obj.address
    line = '---------------------------------------------------------'

    I = Image(logo)
    I.drawHeight = 2.35 * inch / 2.9
    I.drawWidth = 3.4 * inch / 2.9

    style_table = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('BOTTOMPADDING', (0, 0), (-1, -1), -2),  # all columns
        ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'LEFT'),  # second column
        ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
    ]
    colwiths_table = [_wt * 23 / 100, _wt * 77 / 100]

    if client_type == '06':
        p0 = Paragraph(client_name, styles["Justify"])
        p1 = Paragraph(client_address, styles["Justify"])
        ana_c1 = Table(
            [('RUC: ', client_document)] +
            [('RAZÓN SOCIAL: ', p0)] +
            [('DIRECCIÓN: ', p1)] +
            [('ATENDIDO POR: ', order_obj.user.username.upper())] +
            [('FECHA: ', _format_date + '  HORA: ' + _format_time)],
            colWidths=colwiths_table)
    elif client_type != '06':
        p0 = Paragraph(client_name, styles["Left"])
        ana_c1 = Table(
            [('N° DOCUMENTO: ', client_document)] +
            [('SR(A): ', p0)] +
            [('ATENDIDO POR: ', order_obj.user.username.upper())] +
            [('FECHA: ', _format_date + '  HORA: ' + _format_time)],
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
        ('ALIGNMENT', (4, 0), (4, -1), 'RIGHT'),
    ]

    ana_header = Table(
        [('PRODUCTO', 'CANT', 'UND', 'PRECIO UND', 'IMPORTE')],
        colWidths=[_wt * 40 / 100, _wt * 10 / 100, _wt * 10 / 100, _wt * 20 / 100, _wt * 20 / 100]
    )
    ana_header.setStyle(TableStyle(my_style_header))

    my_style_table_detail = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square'),
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # first column
        ('ALIGNMENT', (1, 0), (1, -1), 'CENTER'),  # second column
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGNMENT', (2, 0), (2, -1), 'CENTER'),  # third column
        ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),
        ('RIGHTPADDING', (3, 0), (3, -1), 0),
        ('ALIGNMENT', (4, 0), (4, -1), 'RIGHT'),
        ('RIGHTPADDING', (4, 0), (4, -1), 0),
    ]
    _rows = []
    total = 0
    for d in order_obj.orderdetail_set.all():
        P0 = Paragraph(d.product.names.upper(), styles["Justify"])
        _rows.append((P0, str(decimal.Decimal(round(d.quantity, 0))), d.unit.name, str(round(d.price_unit, 2)),
                      str(decimal.Decimal(round(d.quantity * d.price_unit, 2)))))
        base_total = d.quantity * d.price_unit
        total = total + base_total
    ana_c_detail = Table(_rows,
                         colWidths=[_wt * 40 / 100, _wt * 10 / 100, _wt * 10 / 100, _wt * 20 / 100, _wt * 20 / 100])
    ana_c_detail.setStyle(TableStyle(my_style_table_detail))

    my_style_total = [
        ('FONTNAME', (0, 0), (-1, -1), 'Square-Bold'),  # all columns
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
        ('BOTTOMPADDING', (0, 0), (-1, -1), -6),  # all columns
        ('RIGHTPADDING', (2, 0), (2, -1), 0),  # third column
        ('ALIGNMENT', (2, 0), (2, -1), 'RIGHT'),  # third column
        ('RIGHTPADDING', (3, 0), (3, -1), 0.3),  # four column
        ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # four column
        ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
        ('FONTNAME', (0, 2), (-1, 2), 'Square-Bold'),  # third row
        ('FONTSIZE', (0, 2), (-1, 2), 10),  # third row
    ]

    ana_total = Table(
        [('TOTAL', '', 'S/.  ', str(round(total, 2)))],
        colWidths=[_wt * 60 / 100, _wt * 10 / 100, _wt * 10 / 100, _wt * 20 / 100]
    )
    ana_total.setStyle(TableStyle(my_style_total))

    footer = 'SON: ' + numero_a_moneda(order_obj.total)
    counter = order_obj.orderdetail_set.count()
    my_style_table6 = [
        # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
        ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
        ('SPAN', (0, 0), (1, 0)),  # first row
    ]

    datatable = 'https://www.italoventuraflores.com'
    ana_c9 = Table([(qr_code(datatable), '')], colWidths=[_wt * 99 / 100, _wt * 1 / 100])
    ana_c9.setStyle(TableStyle(my_style_table6))

    _dictionary = []
    _dictionary.append(I)
    _dictionary.append(Spacer(1, 5))
    _dictionary.append(Paragraph(tbh_business_name_address.replace("\n", "<br />"), styles["Center"]))
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(Paragraph(tbn_document, styles["Center_Regular"]))
    _dictionary.append(Spacer(1, 3))
    _dictionary.append(ana_c1)
    _dictionary.append(Paragraph(line, styles["Center2"]))
    _dictionary.append(Spacer(1, 3))
    _dictionary.append(Paragraph('DETALLE DE PRODUCTOS', styles["Center_Regular"]))
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
        Paragraph("***COMPROBANTE INTERNO NO TRIBUTARIO***".replace('***', '"'), styles["Center2"]))
    _dictionary.append(ana_c9)
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
                            pagesize=(3.14961 * inch, 7.0 * inch + (inch * 0.13 * counter)),
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


def qr_code(table):
    # generate and rescale QR
    qr_code = qr.QrCodeWidget(table)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = Drawing(
        3.5 * cm, 3.5 * cm, transform=[3.5 * cm / width, 0, 0, 3.5 * cm / height, 0, 0])
    drawing.add(qr_code)

    return drawing

# def print_ticket_order_sale(request, pk=None):  # Boleto de viaje boleta / factura
#     _wt = 3.14 * inch - 8 * 0.05 * inch
#
#     order_obj = Order.objects.get(pk=pk)
#     order_bill_obj = order_obj.orderbill
#     passenger_name = ""
#     passenger_document = ""
#     client_document = ""
#     client_name = ""
#     client_address = ""
#
#     tbh_business_name_address = 'TURISMO MENDIVIL S.R.L\n CALLE JAVIER P. DE CUELLAR B-3 INT 105\n TERM. TERRESTRE S/N INT. E1-E / \nURB. ARTURO IBAÑEZ HUNTER AREQUIPA\n RUC: 20442736759'
#
#     date = order_obj.programming_seat.programming.departure_date
#     _format_time = order_obj.programming_seat.programming.get_turn_display()
#     _format_date = date.strftime("%d/%m/%Y")
#
#     if order_bill_obj.type == '1':
#         tbn_document = 'FACTURA ELECTRÓNICA'
#         passenger_set = order_obj.client
#         company_set = order_obj.orderaction_set.filter(type='E')
#         if passenger_set:
#             passenger_name = passenger_set.names
#             passenger_document = passenger_set.clienttype_set.first().document_number
#         if company_set:
#             client_document = company_set.first().client.clienttype_set.first().document_number
#             client_name = company_set.first().client.names
#             client_address = company_set.first().client.clientaddress_set.first().address
#     elif order_bill_obj.type == '2':
#         tbn_document = 'BOLETA DE VENTA ELECTRÓNICA'
#         passenger_name = order_obj.client.names
#         passenger_document = order_obj.client.clienttype_set.first().document_number
#         client_name = passenger_name
#         client_document = passenger_document
#     line = '-------------------------------------------------------'
#
#     I = Image(logo)
#     I.drawHeight = 1.95 * inch / 2.9
#     I.drawWidth = 7.4 * inch / 2.9
#
#     style_table = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -2),  # all columns
#         ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#         ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),  # second column
#         ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
#     ]
#     colwiths_table = [_wt * 30 / 100, _wt * 70 / 100]
#
#     if order_bill_obj.type == '2':
#         p0 = Paragraph(client_name, styles["Right"])
#         ana_c1 = Table(
#             [('CLIENTE: N DOC ', client_document)] +
#             [('SR(A): ', p0)] +
#             [('ATENDIDO POR: ', order_obj.user.username.upper() + " " + order_obj.subsidiary.name)],
#             colWidths=colwiths_table)
#     elif order_bill_obj.type == '1':
#         p0 = Paragraph(client_name, styles["Justify"])
#         p1 = Paragraph(client_address, styles["Justify"])
#         ana_c1 = Table(
#             [('RUC ', client_document)] +
#             [('RAZÓN SOCIAL: ', p0)] +
#             [('DIRECCIÓN: ', p1)] +
#             [('ATENDIDO POR: ', order_obj.user.username.upper() + " " + order_obj.subsidiary.name)],
#             colWidths=colwiths_table)
#
#     ana_c1.setStyle(TableStyle(style_table))
#
#     style_table = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -2),  # all columns
#         ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#         ('FONTNAME', (0, 0), (0, -1), 'Ticketing'),  # first column
#         ('LEFTPADDING', (2, 0), (2, -1), 2),  # third column
#         ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # fourth column
#         ('FONTSIZE', (3, 0), (3, -1), 12),  # fourth column
#         ('FONTNAME', (3, 0), (3, -1), 'Ticketing'),  # fifth row [col 1:2]
#
#         ('FONTSIZE', (2, 3), (2, 4), 12),  # third column
#
#         ('ALIGNMENT', (1, 2), (1, 4), 'LEFT'),  # second column [row 3:5]
#         ('FONTNAME', (2, 3), (2, 4), 'Ticketing'),  # third column [row 4:5]
#         ('RIGHTPADDING', (3, 3), (3, 4), 0.5),  # fourth column [row 4:5]
#         ('FONTNAME', (0, 4), (1, 4), 'Square-Bold'),  # fifth row [col 1:2]
#         ('FONTSIZE', (0, 4), (1, 4), 12),  # fifth row [col 1:2]
#         ('LEFTPADDING', (1, 0), (1, -1), 0.5),  # second column
#         ('SPAN', (1, 0), (3, 0)),  # first row
#         ('SPAN', (0, 1), (1, 1)),  # second row
#         ('SPAN', (2, 1), (3, 1)),  # second row
#     ]
#     p10 = Paragraph('SR(A): ' + passenger_document + ' - ' + passenger_name, styles["Justify"])
#     colwiths_table = [_wt * 25 / 100, _wt * 25 / 100, _wt * 25 / 100, _wt * 25 / 100]
#     ana_c2 = Table(
#         [('PASAJERO:', p10, '', '')] +
#         [('AGENCIA DE EMBARQUE:', '', order_obj.subsidiary.name, '')] +
#         [('ORIG:', order_obj.subsidiary.short_name, '', '')] +
#         [('DEST:', order_obj.destiny.name, 'FECHA:', str(_format_date))] +
#         [('ASIENTO:', order_obj.programming_seat.plan_detail.name, 'HORA', str(_format_time))],
#         colWidths=colwiths_table)
#     ana_c2.setStyle(TableStyle(style_table))
#
#     my_style_table3 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.pink),  # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
#         ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -6),  # all columns
#         ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
#         ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),  # second column
#     ]
#     colwiths_table = [_wt * 80 / 100, _wt * 20 / 100]
#     ana_c6 = Table([('DESCRIPCIÓN', 'TOTAL')], colWidths=colwiths_table)
#     ana_c6.setStyle(TableStyle(my_style_table3))
#
#     sub_total = 0
#     total = 0
#     igv_total = 0
#
#     P0 = Paragraph(
#         'SER TRANSPORTE RUTA ' + order_obj.subsidiary.short_name + ' - ' + order_obj.destiny.name + '<br/> ASIENTO ' + order_obj.programming_seat.plan_detail.name + '.',
#         styles["Justify"])
#
#     base_total = 1 * 45
#     base_amount = base_total / 1.1800
#     igv = base_total - base_amount
#     sub_total = sub_total + base_amount
#     total = total + base_total
#     igv_total = igv_total + igv
#
#     my_style_table4 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.pink),   # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#         ('RIGHTPADDING', (1, 0), (1, -1), 0.5),  # second column
#         ('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'),  # second column
#     ]
#     ana_c7 = Table([(P0, 'S/ ' + str(decimal.Decimal(round(order_obj.total, 2))))],
#                    colWidths=[_wt * 80 / 100, _wt * 20 / 100])
#     ana_c7.setStyle(TableStyle(my_style_table4))
#
#     my_style_table5 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),  # all columns
#
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.pink),   # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 8),  # all columns
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -6),  # all columns
#         ('RIGHTPADDING', (2, 0), (2, -1), 0),  # third column
#         ('ALIGNMENT', (2, 0), (2, -1), 'RIGHT'),  # third column
#         ('RIGHTPADDING', (3, 0), (3, -1), 0.3),  # four column
#         ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # four column
#         ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#         ('FONTNAME', (0, 2), (-1, 2), 'Square-Bold'),  # third row
#         ('FONTSIZE', (0, 2), (-1, 2), 10),  # third row
#     ]
#
#     ana_c8 = Table(
#         [('OP. NO GRAVADA', '', 'S/', str(decimal.Decimal(round(order_obj.total, 2))))] +
#         [('I.G.V.  (18.00)', '', 'S/', '0.00')] +
#         [('TOTAL', '', 'S/', str(decimal.Decimal(round(order_obj.total, 2))))],
#         colWidths=[_wt * 60 / 100, _wt * 10 / 100, _wt * 10 / 100, _wt * 20 / 100]
#     )
#     ana_c8.setStyle(TableStyle(my_style_table5))
#     footer = 'SON: ' + numero_a_moneda(order_obj.total)
#
#     my_style_table6 = [
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
#         ('SPAN', (0, 0), (1, 0)),  # first row
#     ]
#
#     datatable = order_bill_obj.code_qr
#     ana_c9 = Table([(qr_code(datatable), '')], colWidths=[_wt * 99 / 100, _wt * 1 / 100])
#     ana_c9.setStyle(TableStyle(my_style_table6))
#
#     _dictionary = []
#     _dictionary.append(I)
#     _dictionary.append(Spacer(1, 5))
#     _dictionary.append(Paragraph(tbh_business_name_address.replace("\n", "<br />"), styles["Center"]))
#     _dictionary.append(Paragraph(line, styles["Center2"]))
#     _dictionary.append(Paragraph(tbn_document, styles["Center_Regular"]))
#     _dictionary.append(
#         Paragraph(order_bill_obj.serial + ' - ' + str(order_bill_obj.n_receipt).zfill(6), styles["Center_Bold"]))
#     _dictionary.append(Spacer(1, 3))
#     _dictionary.append(ana_c1)
#
#     _dictionary.append(Paragraph(line, styles["Center2"]))
#
#     _dictionary.append(Spacer(1, 6))
#
#     _dictionary.append(Paragraph('DATOS DE VIAJE ', styles["Center_Regular"]))
#     _dictionary.append(Spacer(1, 3))
#     _dictionary.append(ana_c2)
#     _dictionary.append(Spacer(1, 3))
#     _dictionary.append(Paragraph(line, styles["Center2"]))
#     _dictionary.append(ana_c6)
#     _dictionary.append(Paragraph(line, styles["Center2"]))
#     _dictionary.append(ana_c7)
#     _dictionary.append(Paragraph(line, styles["Center2"]))
#     _dictionary.append(ana_c8)
#     _dictionary.append(Paragraph(line, styles["Center2"]))
#     _dictionary.append(Paragraph(footer, styles["Center"]))
#     _dictionary.append(Paragraph(line, styles["Center2"]))
#     _dictionary.append(
#         Paragraph("***CONSERVAR SU COMPROBANTE ANTE CUALQUIER EVENTUALIDAD***".replace('***', '"'), styles["Center2"]))
#     _dictionary.append(ana_c9)
#     _dictionary.append(Paragraph("DE LAS CONDICIONES PARA EL SERVICIO DE TRANSPORTE: "
#                                  "1. EL BOLETO DE VIAJE ES PERSONAL, TRANSFERIBLE Y/O PO5TERGABLE."
#                                  "2. EL PASAJERO SE PRESENTARÁ 30 MIN ANTES DE LA HORA DE VIAJE, DEBIENDO PRESENTAR SU BOLETO DE VIAJE Y DNI."
#                                  "3. LOS MENORES DE EDAD VIAJAN CON SUS PADRES O EN SU DEFECTO DEBEN PRESENTAR PERMISO NOTARIAL DE SUS PADRES, MAYORES DE 5 AÑOS PAGAN SU PASAJE. "
#                                  "4. EN CASO DE ACCIDENTES EL PASAJERO VIAJA  ASEGURADO CON SOAT DE LA COMPANIA RIMAC SEGUROS "
#                                  "5. EL PASAJEROTIENE DERECHO ATRANSPORTAR 20 KILOS DE EQUIPAJE, SOLO ARTICULOS DE USO PERSONAL (NO CARGA).  EL EXCESO SERÁ ADMITIDO CUANDO LA CAPACIDAD DEL BUS LO PERMITA, PREVIO PAGO DE LA TARIFA."
#                                  "6. LA EMPRESA NO SE RESPONSABILIZA POR FALLAS AJENAS AL MISMO SERVICIO DE TRANSPORTE (WIFI, TOMACORRIENTES, PANTALLAS, AUDIO Y OTRAS SIMILARES) PUES ESTOS SERVICIOS SON OFRECIDOS EN CALIDAD DE CORTESIA. "
#                                  "7. LAS DEVOLUCIONES DE BOLETOS PAGADOS CON VISA SE EFECTUARÁ SEGÚN LOS PLAZOS, PROCEDIMIENTOS Y CANALES ESTABLECIDOS POR VISA, EN NINGUN CASO SE EFECTUARÁ DEVOLUCIÓN EN EFECTIVO.",
#                                  styles["Center3"]))
#     _dictionary.append(Spacer(1, 2))
#     _dictionary.append(Paragraph(line, styles["Center2"]))
#     _dictionary.append(Spacer(1, 2))
#     _dictionary.append(Paragraph(
#         "¡Gracias por viajar en MENDIVIL!",
#         styles["Center2"]))
#     buff = io.BytesIO()
#
#     ml = 0.05 * inch
#     mr = 0.055 * inch
#     ms = 0.039 * inch
#     mi = 0.039 * inch
#
#     doc = SimpleDocTemplate(buff,
#                             pagesize=(3.14961 * inch, 11.6 * inch),
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title='TICKET'
#                             )
#     doc.build(_dictionary)
#     # doc.build(elements)
#     # doc.build(Story)
#
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="CPE[{}].pdf"'.format(
#         order_obj.serial + '-' + order_obj.correlative_sale)
#
#     response.write(buff.getvalue())
#
#     buff.close()
#     return response


# def print_bill_order_commodity(request, pk=None):  # Boleta / Factura Encomienda
#     _wt = 3.14 * inch - 8 * 0.05 * inch
#
#     order_obj = Order.objects.get(pk=pk)
#     order_bill_obj = order_obj.orderbill
#     client_document = ""
#     client_name = ""
#     client_address = ""
#
#     order_action_sender_obj = OrderAction.objects.get(order=order_obj, type='R')
#     order_action_addressee_obj = OrderAction.objects.get(order=order_obj, type='D')
#
#     tbh_business_name_address = 'TURISMO MENDIVIL S.R.L\n CALLE JAVIER P. DE CUELLAR B-3 INT 105\n TERM. TERRESTRE S/N INT. E1-E / \nURB. ARTURO IBAÑEZ HUNTER AREQUIPA\n RUC: 20442736759'
#     if order_bill_obj.type == '1':
#         tbn_document = 'FACTURA ELECTRÓNICA'
#         client_set = order_obj.client
#         company_set = order_obj.orderaction_set.filter(type='R')
#         if company_set:
#             client_document = company_set.first().client.clienttype_set.first().document_number
#             client_name = company_set.first().client.names
#             client_address = company_set.first().client.clientaddress_set.first().address
#     elif order_bill_obj.type == '2':
#         tbn_document = 'BOLETA DE VENTA ELECTRÓNICA'
#         passenger_name = order_action_sender_obj.client.names
#         passenger_document = order_action_sender_obj.client.clienttype_set.first().document_number
#         client_name = passenger_name
#         client_document = passenger_document
#
#     line = '-------------------------------------------------------'
#     name_document = tbn_document
#     data_title = 'DATOS DE ENVIO'
#     serie = 'SERIE: ' + order_obj.serial
#     colwiths_table = [3.2 / 2.2 * inch, 3.2 / 2.2 * inch]
#     correlative = order_obj.correlative_sale
#
#     I = Image(logo)
#     I.drawHeight = 1.95 * inch / 2.9
#     I.drawWidth = 7.4 * inch / 2.9
#     # date = order_obj.create_at.date()
#     # date_hour = order_obj.create_at.time()
#     # _formatdate = date.strftime("%d/%m/%Y")
#     # _formattime = date_hour.strftime("%I:%M:%S %p")
#     date = order_obj.create_at.date()
#     _date_convert_zone = utc_to_local(order_obj.create_at)
#     date_hour = _date_convert_zone.time()
#     _formatdate = date.strftime("%d/%m/%Y")
#     _formattime = date_hour.strftime("%I:%M:%S %p")
#
#     td_date = ('FECHA DE EMISIÓN: ' + str(_formatdate), 'HORA EMISIÓN: ' + str(_formattime))
#     td_user = ('ATENDIDO POR: ' + order_obj.user.worker_set.last().employee.full_name(), order_obj.subsidiary.name)
#     ana_c1 = Table([td_date] + [td_user], colWidths=colwiths_table)
#     my_style_table = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         # ('ALIGN', (0, 0), (0, -1), 'CENTER'),
#         # ('FONTNAME', (0, 1), (0, -1), 'Newgot'),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -6),
#         ('ALIGNMENT', (1, 1), (1, 1), 'RIGHT'),
#         ('ALIGNMENT', (1, 0), (1, 0), 'RIGHT'),
#         # ('TOPPADDING', (0, 0), (-1, -1), 1),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         # ('LINEBELOW', (0, 0), (-1, 0), 1, colors.darkblue),
#         # ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
#     ]
#     my_style_table2_1 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('ALIGN', (0, 0), (0, -1), 'LEFT'),
#         # ('FONTNAME', (0, 1), (0, -1), 'Newgot'),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
#         ('LEFTPADDING', (0, 0), (0, -1), 0.3),  # first column
#         ('LEFTPADDING', (1, 0), (1, -1), 0.3),  # second column
#         ('VALIGN', (1, 0), (1, -1), 'TOP'),  # second column
#         # ('ALIGNMENT', (0, 1), (1, -1), 'LEFT'),
#         # ('ALIGNMENT', (1, 0), (1, 0), 'LEFT'),
#         # ('TOPPADDING', (0, 0), (-1, -1), 1),
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#         # ('LINEBELOW', (0, 0), (-1, 0), 1, colors.darkblue),
#         # ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
#     ]
#     my_style_table2_2 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('ALIGN', (0, 0), (0, -1), 'LEFT'),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -2),
#         ('TOPPADDING', (0, 1), (-1, -1), 2),
#         ('LEFTPADDING', (0, 0), (0, -1), 0.3),  # first column
#         ('LEFTPADDING', (1, 0), (1, -1), 0.3),  # second column
#         ('RIGHTPADDING', (1, 1), (1, 1), 0.3),  # second column
#         ('VALIGN', (1, 0), (1, -1), 'TOP'),  # second column
#         ('ALIGNMENT', (1, 1), (1, 1), 'RIGHT'),  # second column second row
#         ('VALIGN', (0, 0), (0, -1), 'TOP'),
#     ]
#     my_style_table2 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#         ('FONTNAME', (1, 3), (1, 3), 'Square-Bold'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -6),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#     ]
#     my_style_table3 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('ALIGNMENT', (2, 0), (2, -1), 'CENTER'),  # third column
#         ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -6),
#         ('TOPPADDING', (0, 0), (-1, -1), -1),
#         ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # four column
#         ('RIGHTPADDING', (3, 0), (3, -1), 0.5),  # four column
#     ]
#     my_style_table4 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
#         ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#         ('ALIGNMENT', (1, 0), (1, -1), 'CENTER'),  # second column
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('ALIGNMENT', (2, 0), (2, -1), 'CENTER'),  # third column
#         ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # four column
#         ('RIGHTPADDING', (3, 0), (3, -1), 0.5),  # four column
#     ]
#     my_style_table5 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Square'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('RIGHTPADDING', (2, 0), (2, -1), 0),  # third column
#         ('ALIGNMENT', (2, 0), (2, -1), 'RIGHT'),  # third column
#         ('RIGHTPADDING', (3, 0), (3, -1), 0.3),  # four column
#         ('ALIGNMENT', (3, 0), (3, -1), 'RIGHT'),  # four column
#         ('LEFTPADDING', (0, 0), (0, -1), 0.5),  # first column
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -6),
#     ]
#     my_style_table6 = [
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.blue),   # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),  # first column
#         ('SPAN', (0, 0), (1, 0)),  # first row
#     ]
#     ana_c1.setStyle(TableStyle(my_style_table))
#
#     client_document_type = str(order_action_sender_obj.client.clienttype_set.first().document_type.short_description)
#
#     if order_bill_obj.type == '1':
#
#         p1cn = Paragraph(order_action_sender_obj.client.names, styles["Justify"])
#         td_client2 = ('CLIENTE: ', p1cn)
#         # td_client = ('CLIENTE: ', str(order_action_sender_obj.client.names))
#         td_client_nro_documento = (client_document_type + ': ', str(order_action_sender_obj.client.clienttype_set.first().document_number))
#         p1c = Paragraph(client_address, styles["Justify"])
#         ana_c2 = Table([td_client2] + [td_client_nro_documento], colWidths=[_wt * 20 / 100, _wt * 80 / 100])
#         ana_c2.setStyle(TableStyle(my_style_table2_1))
#         ana_c2_1 = Table([('DIRECCION :', p1c)], colWidths=[_wt * 20 / 100, _wt * 80 / 100])
#         ana_c2_1.setStyle(TableStyle(my_style_table2_1))
#
#     elif order_bill_obj.type == '2':
#
#         p1cn = Paragraph(order_action_sender_obj.client.names, styles["Justify"])
#         td_client2 = ('CLIENTE: ', p1cn)
#         # td_client = ('CLIENTE: ', str(order_action_sender_obj.client.names))
#         td_client_nro_documento = (client_document_type + ': ', str(order_action_sender_obj.client.clienttype_set.first().document_number))
#         p1c = Paragraph(client_address, styles["Justify"])
#         ana_c2 = Table([td_client2] + [td_client_nro_documento], colWidths=[_wt * 20 / 100, _wt * 80 / 100])
#         ana_c2.setStyle(TableStyle(my_style_table2_1))
#         ana_c2_1 = Table([('DIRECCION :', p1c)], colWidths=[_wt * 20 / 100, _wt * 80 / 100])
#         ana_c2_1.setStyle(TableStyle(my_style_table2_1))
#
#     if order_action_sender_obj.client.phone:
#         p1r = Paragraph(str(order_action_sender_obj.client.names), styles["Justify"])
#         # td_sender = ('REMITENTE: ' + str(order_action_sender_obj.client.names), '')
#         td_sender = ('REMITENTE: ', p1r)
#         td_sender_document = (client_document_type + ': ' + str(order_action_sender_obj.client.clienttype_set.first().document_number),
#                               'TELEFONO: ' + str(order_action_sender_obj.client.phone))
#         ana_c3 = Table([td_sender] + [td_sender_document], colWidths=[_wt * 19 / 100, _wt * 81 / 100])
#         ana_c3.setStyle(TableStyle(my_style_table2_2))
#
#     else:
#         p1r = Paragraph(str(order_action_sender_obj.client.names), styles["Justify"])
#         # td_sender = ('REMITENTE: ' + str(order_action_sender_obj.client.names), '')
#         td_sender = ('REMITENTE: ', p1r)
#         td_sender_document = (client_document_type + ': ' + str(order_action_sender_obj.client.clienttype_set.first().document_number), '')
#         ana_c3 = Table([td_sender] + [td_sender_document], colWidths=[_wt * 19 / 100, _wt * 81 / 100])
#         ana_c3.setStyle(TableStyle(my_style_table2_2))
#
#     document_addressee = str(order_action_addressee_obj.client.clienttype_set.first().document_type.short_description)
#
#     if order_action_addressee_obj.client.names == 'CLIENTE REMITENTE':
#         td_addressee = ('DESTINATARIO: ' + str(order_obj.addressee_name), '')
#         td_addressee_nro_documento = (document_addressee + ': ' + '', '')
#         ana_c4 = Table([td_addressee] + [td_addressee_nro_documento], colWidths=colwiths_table)
#         ana_c4.setStyle(TableStyle(my_style_table))
#
#     else:
#         td_addressee = ('DESTINATARIO: ' + str(order_action_addressee_obj.client.names), '')
#         td_addressee_nro_documento = (
#             document_addressee + ': ' + str(order_action_addressee_obj.client.clienttype_set.first().document_number), '')
#         ana_c4 = Table([td_addressee] + [td_addressee_nro_documento], colWidths=colwiths_table)
#         ana_c4.setStyle(TableStyle(my_style_table))
#
#     td_type = ('TIPO', ': ENCOMIENDA')
#     td_origin = ('ORIGEN', ': ' + str(order_obj.orderroute_set.filter(type='O').first().subsidiary.short_name))
#     td_destiny = ('DESTINO', ': ' + str(order_obj.orderroute_set.filter(type='D').first().subsidiary.short_name))
#     td_way_to_pay = ('COND. PAGO', ': ' + str(order_obj.get_way_to_pay_display()))
#     td_service = ('SERVICIO', ': RECOGE EN OFICINA')
#     ana_c5 = Table([td_type] + [td_origin] + [td_destiny] + [td_way_to_pay] + [td_service],
#                    colWidths=[3.2 / 4.2 * inch, 3.2 / 1.5 * inch])
#     ana_c5.setStyle(TableStyle(my_style_table2))
#
#     td_description = ('DESCRIPCIÓN', 'U.M.', 'CANT.', 'TOTAL')
#     ana_c6 = Table([td_description], colWidths=[_wt * 60 / 100, _wt * 15 / 100, _wt * 10 / 100, _wt * 15 / 100])
#     ana_c6.setStyle(TableStyle(my_style_table3))
#
#     sub_total = 0
#     total = 0
#     igv_total = 0
#     _rows = []
#     _counter = order_obj.orderdetail_set.count()
#     for d in order_obj.orderdetail_set.all():
#         P0 = Paragraph(d.description.upper(), styles["Justify"])
#         _rows.append((P0, d.unit.description, str(decimal.Decimal(round(d.quantity))), str(d.amount)))
#         base_total = d.quantity * d.price_unit
#         base_amount = base_total / decimal.Decimal(1.1800)
#         igv = base_total - base_amount
#         sub_total = sub_total + base_amount
#         total = total + base_total
#         igv_total = igv_total + igv
#
#     ana_c7 = Table(_rows, colWidths=[_wt * 60 / 100, _wt * 15 / 100, _wt * 10 / 100, _wt * 15 / 100])
#
#     ana_c7.setStyle(TableStyle(my_style_table4))
#
#     td_gravada = ('OP.  GRAVADA', '', 'S/', str(decimal.Decimal(round(sub_total, 2))))
#     td_inafecta = ('OP.  INAFECTA', '', 'S/', '0.00')
#     td_exonerada = ('OP.  EXONERADA', '', 'S/', '0.00')
#     td_descuento = ('DESCUENTO', '', 'S/', '0.00')
#     td_igv = ('I.G.V.  (18.00)', '', 'S/', str(decimal.Decimal(round(igv_total, 2))))
#     td_importe_total = ('IMPORTE TOTAL', '', 'S/', str(decimal.Decimal(round(total, 2))))
#
#     ana_c8 = Table([td_gravada] + [td_inafecta] + [td_exonerada] + [td_descuento] + [td_igv] + [td_importe_total],
#                    colWidths=[_wt * 60 / 100, _wt * 10 / 100, _wt * 17 / 100, _wt * 13 / 100])
#     ana_c8.setStyle(TableStyle(my_style_table5))
#
#     datatable = order_bill_obj.code_qr
#     ana_c9 = Table([(qr_code(datatable), '')], colWidths=[_wt * 99 / 100, _wt * 1 / 100])
#     ana_c9.setStyle(TableStyle(my_style_table6))
#
#     footer = 'SON: ' + numero_a_moneda(total)
#     footer2 = 'ACEPTO LOS TÉRMINOS Y CONDICIONES DEL CONTRATO DE TRANSPORTE PUBLICADOS EN LA EMPRESA'
#
#     buff = io.BytesIO()
#
#     ml = 0.05 * inch
#     mr = 0.055 * inch
#     ms = 0.039 * inch
#     mi = 0.039 * inch
#
#     doc = SimpleDocTemplate(buff,
#                             pagesize=(3.14961 * inch, (11.6 * inch + (_counter * 0.13 * inch))),
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title='Encomienda Mendivil'
#                             )
#     dictionary = []
#     dictionary.append(I)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(Paragraph(tbh_business_name_address.replace("\n", "<br />"), styles["Center"]))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Paragraph(name_document, styles["Center_Regular"]))
#     dictionary.append(Paragraph(serie + ' - ' + correlative, styles["Center_Bold"]))
#     dictionary.append(Spacer(1, 3))
#     dictionary.append(ana_c1)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(ana_c2)
#     dictionary.append(ana_c2_1)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(data_title, styles["Center"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(ana_c3)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(ana_c4)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(ana_c5)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(ana_c6)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(ana_c7)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(ana_c8)
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(footer, styles["Center"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(footer2, styles["Center"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(ana_c9)
#     dictionary.append(Paragraph(
#         "CONDICIONES PARA EL SERVICIO DE ENCOMIENDAS: "
#         "1.	LA EMPRESA NO TRANSPORTA DINERO, VALORES Y JOYAS, ANIMALES VIVOS, SUSTANCIAS Y/O MATERIALES RESTRINGIDOS O PROHIBIDOS POR SENASA, DIGESA, SUNAT, EL CLIENTE ASUMIRÁ LA TOTAL RESPONSABILIDAD POR DAÑOS Y PERJUICIOS QUE SE OCASIONAN AL ESTADO, TERCEROS Y A LA EMPRESA. "
#         "2.	EN CASO DE PERDIDA, EXTRAVIO O SUSTRACCION, DETERIORO O DESTRUCCION ENTREGA ERRONEA DE UNA ENCOMIENDA A EXCEPCIÓN DEL PREVISTO EN EL NUMERAL ANTLRIOR, LA EMPRESA INDEMNIZARA AL CLIENTE DE ACUERDO A LA RESOLUCIÓN DIRECTORAL Nº OO1-2006-MTC/19. "
#         "3. EL PLAZO DE ENTREGA DE ENCOMIENDAS DE DESTINOS (AGFNCIAS DE LA EMPRESA ES DE 72 HORAS MAXIMO. "
#         "4. Si LA ENCOMIENDA NO ES RECLAMADA EN 30 DIAS. LA EMPRESA APLICARA LO ESTABLECIDO EN LA R.M. Nº 572-2008. MTC.",
#         styles["Center3"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(line, styles["Center2"]))
#     dictionary.append(Spacer(1, 2))
#     dictionary.append(Paragraph(
#         "¡Gracias por enviar en MENDIVIL!",
#         styles["Center2"]))
#
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="Encomienda_[{}].pdf"'.format(
#         order_obj.serial + '-' + order_obj.correlative_sale)
#     doc.build(dictionary)
#     # doc.build(elements)
#     # doc.build(Story)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#

# def print_manifest_passengers(request, pk=None):  # Manifiesto de Pasajeros
#     _legal = (8.5 * inch, 14 * inch)
#
#     ml = 0.75 * inch
#     mr = 0.75 * inch
#     ms = 0.75 * inch
#     mi = 1.0 * inch
#
#     _bts = 8.5 * inch - 0.5 * inch - 0.5 * inch
#
#     programming_obj = Programming.objects.get(id=pk)
#
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff,
#                             pagesize=(8.5 * inch, 14 * inch),
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title='Manifiesto de pasajeros'
#                             )
#     response = HttpResponse(content_type='application/pdf')
#
#     style_table = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),  # all columns
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),      # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('TOPPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('LEFTPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -2),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#
#         ('SPAN', (0, 0), (3, 0)),  # first row
#         ('ALIGNMENT', (0, 0), (3, 0), 'LEFT'),  # first row
#
#         ('SPAN', (4, 0), (4, 0)),  # first row
#         ('ALIGNMENT', (4, 0), (4, 0), 'RIGHT'),  # first row
#
#         ('SPAN', (0, 1), (3, 1)),  # second row
#         ('ALIGNMENT', (0, 1), (2, 1), 'LEFT'),  # second row
#         ('ALIGNMENT', (4, 1), (4, 1), 'RIGHT'),  # second row
#
#         # ('SPAN', (3, 1), (4, 1)),  # second row
#
#         # ('SPAN', (4, 1), (5, 1)),  # second row
#         ('SPAN', (7, 1), (9, 1)),  # second row
#         ('SPAN', (1, 2), (2, 2)),  # third row
#         ('ALIGNMENT', (1, 2), (2, 2), 'RIGHT'),  # third row
#         ('SPAN', (4, 2), (5, 2)),  # third row
#         ('ALIGNMENT', (4, 2), (5, 2), 'CENTER'),  # third row
#         ('SPAN', (7, 2), (9, 2)),  # third row
#         ('SPAN', (1, 3), (2, 3)),  # fourth row
#         ('ALIGNMENT', (1, 3), (2, 3), 'RIGHT'),  # fourth row
#         ('TOPPADDING', (1, 3), (2, 3), -4),  # fourth row
#
#         ('SPAN', (4, 3), (5, 3)),  # fourth row
#         ('ALIGNMENT', (4, 3), (5, 3), 'CENTER'),  # fourth row
#         ('TOPPADDING', (4, 3), (5, 3), -4),  # fourth row
#
#         ('SPAN', (7, 3), (9, 3)),  # fourth row
#         ('SPAN', (1, 4), (2, 4)),  # fifth row
#         ('ALIGNMENT', (1, 4), (2, 4), 'RIGHT'),  # fifth row
#         ('ALIGNMENT', (6, 4), (6, 4), 'RIGHT'),  # fifth row
#         ('ALIGNMENT', (9, 4), (9, 4), 'RIGHT'),  # fifth row
#     ]
#
#     col_widths = [
#         _bts * 5 / 100,  # destiny
#         _bts * 10 / 100,
#         _bts * 5 / 100,  # origin
#         _bts * 10 / 100,
#
#         _bts * 20 / 100,  # passengers
#         _bts * 5 / 100,
#
#         _bts * 10 / 100,  # date
#         _bts * 10 / 100,
#         _bts * 10 / 100,
#         _bts * 15 / 100
#     ]
#
#     col_heights = [
#         1 * inch / 8,
#         1 * inch / 4,
#         1 * inch / 4,
#         1 * inch / 4,
#         1 * inch / 8,
#     ]
#
#     _pilot = programming_obj.get_pilot()
#     _copilot = programming_obj.get_copilot()
#
#     _n_license_pilot = _pilot.n_license
#     _n_license_copilot = ''
#     _copilot_full_name = ''
#     if _copilot:
#         _copilot_full_name = _copilot.full_name()
#         _n_license_copilot = _copilot.n_license
#
#     _truck = programming_obj.truck
#     _hour = programming_obj.get_turn_display()
#     _date = str(programming_obj.departure_date.strftime("%d/%m/%y"))
#     programming_seat_set = programming_obj.programmingseat_set.filter(status='4')  # sold
#
#     p0 = Paragraph(programming_obj.path.get_first_point().short_name, styles["Justify-Dotcirful"])
#     p1 = Paragraph(programming_obj.path.get_last_point().short_name, styles["Justify-Dotcirful"])
#     p2 = Paragraph('Nº PASAJEROS EN LA RUTA', styles["Justify"])
#
#     ana_c1 = Table(
#         [(_pilot.full_name(), '', '', '', _n_license_pilot, '', '', '', '', '')] +
#         [(_copilot_full_name, '', '', '', _n_license_copilot, '', '', '', '', '')] +
#         [('', _truck.truck_model.truck_brand.name, '', '', _truck.license_plate, '', '', '', '', '')] +
#         [('', _truck.certificate, '', '', _truck.nro_passengers, '', '', '', '', '')] +
#         [('', p1, '', '', p0, '', programming_seat_set.count(), '', _date, _hour[0:8])], colWidths=col_widths,
#         rowHeights=col_heights)
#     ana_c1.setStyle(TableStyle(style_table))
#
#     _rows = []
#
#     for ps in programming_obj.programmingseat_set.filter(status='4'):
#         order_obj = Order.objects.filter(programming_seat=ps).last()
#         client_obj = order_obj.client
#         client_type_obj = client_obj.clienttype_set.get(document_type_id__in=['01', '04', '07'])
#         _birthday = 0
#         _short_name = ''
#         if order_obj.subsidiary.short_name:
#             _short_name = order_obj.subsidiary.short_name
#         if client_obj.birthday:
#             _birthday = calculate_age(client_obj.birthday)
#         _rows.append((
#             order_obj.serial[1:4],
#             order_obj.correlative_sale,
#             client_obj.names,
#             '',
#             ps.plan_detail.name,
#             client_type_obj.document_type.id,
#             client_type_obj.document_number,
#             _birthday,
#             # client_obj.nationality,
#             _short_name,
#             order_obj.destiny.name,
#             order_obj.total,
#         ))
#
#     style_table = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),  # all columns
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('TOPPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('LEFTPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -2),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#
#         ('ALIGNMENT', (0, 0), (0, -1), 'RIGHT'),  # first column
#         ('ALIGNMENT', (1, 0), (1, -1), 'CENTER'),  # second column
#         ('ALIGNMENT', (7, 0), (7, -1), 'CENTER'),  # eighth column
#         ('ALIGNMENT', (10, 0), (10, -1), 'RIGHT'),  # eleventh column
#     ]
#     _bts2 = 8.5 * inch - 1.0 * inch
#     col_widths = [
#         _bts2 * 8 / 100,  # serial
#         _bts2 * 10 / 100,  # correlative
#         _bts2 * 32 / 100,  # names
#
#         _bts2 * 8 / 100,  # void
#
#         _bts2 * 3 / 100,  # seat
#         _bts2 * 3 / 100,  # document type
#
#         _bts2 * 9 / 100,  # document number
#         _bts2 * 5 / 100,  # age
#
#         _bts2 * 9 / 100,
#         _bts2 * 9 / 100,
#         _bts2 * 5 / 100,
#
#     ]
#
#     ana_c2 = Table(_rows, colWidths=col_widths)
#
#     ana_c2.setStyle(TableStyle(style_table))
#
#     _dictionary = []
#     _dictionary.append(Spacer(1, 43))
#     _dictionary.append(ana_c1)
#     _dictionary.append(Spacer(1, 25))
#     _dictionary.append(ana_c2)
#
#     doc.build(_dictionary)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#

# def print_mock_up_passengers(request, pk=None):
#     _a4 = (8.3 * inch, 11.7 * inch)
#
#     ml = 0.25 * inch
#     mr = 0.25 * inch
#     ms = 0.25 * inch
#     mi = 0.25 * inch
#
#     _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
#
#     programming_obj = Programming.objects.get(id=pk)
#
#     plan_obj = programming_obj.truck.plan
#
#     rows = plan_obj.rows
#     cols = plan_obj.columns
#
#     first_floor_set = plan_obj.plandetail_set.filter(position='I')
#     second_floor_set = plan_obj.plandetail_set.filter(position='S')
#     _data_first_floor = []
#     _first_floor_style = []
#     _data_second_floor = []
#     _second_floor_style = []
#     x_style = 1
#     x2_style = 1
#     for x in range(1, rows + 1):
#         _row_first_floor = []
#         _row_second_floor = []
#         _count_void_first_floor = 0
#         _count_void_second_floor = 0
#         for y in range(1, cols + 1):
#             search_first_floor_seat = first_floor_set.filter(row=x, column=y)
#             search_second_floor_seat = second_floor_set.filter(row=x, column=y)
#
#             if search_first_floor_seat:
#                 _row_first_floor.append(search_first_floor_seat.last().name)
#                 _first_floor_style.append(('BOX', (y - 1, x_style - 1), (y - 1, x_style - 1), 1, colors.gray))
#                 _first_floor_style.append(('FONTNAME', (y - 1, x_style - 1), (y - 1, x_style - 1), 'Dotcirful-Regular'))
#                 _first_floor_style.append(('TOPPADDING', (y - 1, x_style - 1), (y - 1, x_style - 1), 0))
#                 _first_floor_style.append(('LEFTPADDING', (y - 1, x_style - 1), (y - 1, x_style - 1), 0))
#                 _first_floor_style.append(('VALIGN', (y - 1, x_style - 1), (y - 1, x_style - 1), 'TOP'))
#             else:
#                 _row_first_floor.append('')
#                 _count_void_first_floor = _count_void_first_floor + 1
#             if search_second_floor_seat:
#                 _row_second_floor.append(search_second_floor_seat.last().name)
#                 _second_floor_style.append(('BOX', (y - 1, x2_style - 1), (y - 1, x2_style - 1), 1, colors.gray))
#                 _second_floor_style.append(
#                     ('FONTNAME', (y - 1, x2_style - 1), (y - 1, x2_style - 1), 'Dotcirful-Regular'))
#                 _second_floor_style.append(('TOPPADDING', (y - 1, x2_style - 1), (y - 1, x2_style - 1), 0))
#                 _second_floor_style.append(('LEFTPADDING', (y - 1, x2_style - 1), (y - 1, x2_style - 1), 0))
#                 _second_floor_style.append(('VALIGN', (y - 1, x2_style - 1), (y - 1, x2_style - 1), 'TOP'))
#             else:
#                 _row_second_floor.append('')
#                 _count_void_second_floor = _count_void_second_floor + 1
#         if _count_void_first_floor != cols:
#             _data_first_floor.append(_row_first_floor)
#             x_style = x_style + 1
#
#         if _count_void_second_floor != cols:
#             _data_second_floor.append(_row_second_floor)
#             x2_style = x2_style + 1
#
#     # _first_floor_style.append(('BOX', (0, 0), (-1, -1), 1, colors.gray))
#     square_width = 0.87 * inch
#     square_height = 0.63 * inch
#     first_floor = Table(_data_first_floor, colWidths=cols * [square_width], rowHeights=(x_style - 1) * [square_height])
#     first_floor.setStyle(TableStyle(_first_floor_style))
#
#     # _second_floor_style.append(('BOX', (0, 0), (-1, -1), 1, colors.gray))
#     second_floor = Table(_data_second_floor, colWidths=cols * [square_width],
#                          rowHeights=(x2_style - 1) * [square_height])
#     second_floor.setStyle(TableStyle(_second_floor_style))
#
#     p0 = Paragraph('TURISMO MENDIVIL S.R.L CROQUIS DE CONTROL DE VIAJE', styles["Justify-Dotcirful"])
#     p1 = Paragraph(programming_obj.path.get_first_point().short_name, styles["Justify-Dotcirful"])
#     p2 = Paragraph(programming_obj.path.get_last_point().short_name, styles["Justify-Dotcirful"])
#     _pilot = programming_obj.get_pilot()
#     _n_license = _pilot.n_license
#     _truck = programming_obj.truck
#     _hour = programming_obj.get_turn_display()
#     _date = str(programming_obj.departure_date.strftime("%d/%m/%y"))
#
#     labeled = [
#         [p0, '', '', ''],
#         ['BUS: ', _truck.license_plate, 'HORARIO:', _hour[0:8]],
#         ['ORIGEN:', p1, '', ''],
#         ['DESTINO:', p2, '', ''],
#         ['PILOTO:', _pilot.full_name(), '', ''],
#         ['COPILOTO:', '', '', ''],
#         ['FECHA:', _date, '', ''],
#     ]
#     t_labeled = Table(labeled)
#     t_labeled.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),  # all columns
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),      # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('TOPPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('LEFTPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -2),  # all columns
#         ('SPAN', (0, 0), (3, 0)),  # first row
#         ('SPAN', (1, 2), (3, 2)),  # third row
#         ('SPAN', (1, 3), (3, 3)),  # fourth row
#         ('SPAN', (1, 4), (3, 4)),  # fifth row
#         ('SPAN', (1, 5), (3, 5)),  # sixth row
#
#     ]))
#     bus = [
#         [t_labeled, second_floor],
#         ['', ''],
#         ['', first_floor],
#         ['DESPACHADO POR:...................', '']
#     ]
#     t = Table(bus)
#
#     t.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),  # all columns
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),      # all columns
#         ('FONTSIZE', (0, 0), (-1, -1), 10),  # all columns
#         ('TOPPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('LEFTPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # all columns
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -2),  # all columns
#
#         ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (1, 0), (-1, -1), 'MIDDLE'),
#         ('VALIGN', (0, 0), (0, 0), 'TOP'),
#         ('SPAN', (0, 0), (0, 1)),  # first and second row
#     ]))
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff,
#                             pagesize=(8.3 * inch, 11.7 * inch),
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title='Croquis de pasajeros'
#                             )
#     response = HttpResponse(content_type='application/pdf')
#
#     _dictionary = []
#     _dictionary.append(t)
#
#     doc.build(_dictionary)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#
#
# def print_manifest_comidity(request, pk=None):  # Manifiesto de Encomiendas
#     _a4 = (8.3 * inch, 11.7 * inch)
#
#     ml = 0.25 * inch
#     mr = 0.25 * inch
#     ms = 0.25 * inch
#     mi = 0.25 * inch
#
#     _bts = 8.3 * inch - 0.25 * inch - 0.25 * inch
#
#     manifest_obj = Manifest.objects.get(id=pk)
#     orders_programmings_set = OrderProgramming.objects.filter(manifest=manifest_obj)
#     programming_obj = orders_programmings_set.first().programming
#
#     I = Image(logo)
#     I.drawHeight = 2.00 * inch / 2.9
#     I.drawWidth = 5.4 * inch / 2.9
#
#     tbh_business_name_address = 'TURISMO MENDIVIL S.R.L <br/> CALLE JAVIER P. DE CUELLAR B-3 INT 105 TERM. TERRESTRE S/N INT. E1-E / URB. ARTURO IBAÑEZ HUNTER AREQUIPA <br/> RUC: 20442736759'
#     ph = Paragraph(tbh_business_name_address, styles["Center-Dotcirful"])
#     tbn_name_document = 'MANIFIESTO DE ENCOMIENDAS'
#
#     p0 = Paragraph('MANIFIESTO DE CARGA', styles["CenterTitle-Dotcirful"])
#
#     _tbl_small = [
#         [p0, ''],
#         ['SERIE:', manifest_obj.serial],
#         ['CORRELATIVO:', manifest_obj.correlative],
#     ]
#
#     ana_c_1 = Table(_tbl_small)
#
#     _tbl_header = [
#         [I, ph, ana_c_1],
#     ]
#
#     ana_c = Table(_tbl_header)
#
#     # date = manifest_obj.create_at.date()
#     _date_convert_zone = utc_to_local(manifest_obj.created_at)
#     date_hour = _date_convert_zone.time()
#     # date = datetime.now()
#     _formatdate = _date_convert_zone.strftime("%d/%m/%Y")
#
#     td_date = ('FECHA: ', _formatdate, 'TURNO: ', programming_obj.get_turn_display())
#     td_data_drive = ('PILOTO: ', str(programming_obj.setemployee_set.first().employee.full_name()), 'COPILOTO: ',
#                      str(programming_obj.setemployee_set.last().employee.full_name()))
#     td_data_vehicle = (
#         'PLACA: ', str(programming_obj.truck.license_plate), 'TIPO: ',
#         str(programming_obj.truck.get_drive_type_display()))
#     td_route = ('ORIGEN: ', str(programming_obj.path.get_first_point().short_name), 'DESTINO: ',
#                 str(programming_obj.path.get_last_point().short_name))
#
#     colwiths_table = [_bts * 10 / 100, _bts * 30 / 100, _bts * 10 / 100, _bts * 50 / 100]
#     ana_c1 = Table([td_date] + [td_data_drive] + [td_data_vehicle] + [td_route], colWidths=colwiths_table)
#
#     td_title = (
#         '#', 'SERIE', 'NRO.', 'CANT.', 'UND.', 'PESO', 'DESCRIPCIÓN', 'DESTINATARIO', 'DESTINO', 'COND. PAGO', 'MONTO')
#     colwiths_table_title = [_bts * 3 / 100,
#                             _bts * 4 / 100,
#                             _bts * 4 / 100,
#                             _bts * 4 / 100,
#                             _bts * 6 / 100,
#                             _bts * 4 / 100,
#                             _bts * 25 / 100,
#                             _bts * 20 / 100,
#                             _bts * 14 / 100,
#                             _bts * 9 / 100,
#                             _bts * 7 / 100]
#     # ana_c2 = Table([td_title], colWidths=colwiths_table_title)
#     detail_style = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
#         ('FONTNAME', (0, 0), (-1, 0), 'Dotcirful-Regular'),
#         ('FONTNAME', (0, 0), (0, -1), 'Dotcirful-Regular'),
#         ('FONTSIZE', (0, 0), (0, -1), 10),
#         ('FONTSIZE', (0, 0), (-1, 0), 9)
#     ]
#     _rows = []
#     _rows.append(td_title)
#     _counter = 1
#     _c2 = 1
#     y = 8
#     cont_counted = 0
#     cont_destination_payment = 0
#     serial_row = ''
#     name_addreess = ''
#     for op in orders_programmings_set:
#         order_obj = op.order
#         for d in order_obj.orderdetail_set.all():
#             number_details = order_obj.orderdetail_set.all().count()
#             if order_obj and OrderBill.objects.filter(order=order_obj).count() > 0:
#                 serial_row = order_obj.orderbill.serial
#             else:
#                 serial_row = 'G' + order_obj.serial[-3:]
#             if order_obj.orderaction_set.filter(type='D').last().client.names.upper() == 'CLIENTE REMITENTE':
#                 name_addreess = order_obj.addressee_name.upper()
#             else:
#                 name_addreess = order_obj.orderaction_set.filter(type='D').last().client.names.upper()
#             _rows.append((_c2,
#                           serial_row,
#                           str(order_obj.correlative_sale[-4:]),
#                           str(decimal.Decimal(round(d.quantity))),
#                           d.unit.description,
#                           str(decimal.Decimal(round(d.weight))) + ' KG',
#                           Paragraph(d.description.upper(), styles["Justify-Dotcirful"]),
#                           Paragraph(name_addreess, styles["Justify-Dotcirful"]),
#                           # order_obj.orderprogramming.programming.path.get_last_point().short_name,
#                           order_obj.orderroute_set.filter(type='D').last().subsidiary.short_name,
#                           order_obj.get_way_to_pay_display(),
#                           'S/. ' + str(decimal.Decimal(round(order_obj.total, 2)))))
#             if number_details > 1:
#                 detail_style.append(('SPAN', (y - 1, _counter), (y - 1, _counter + number_details - 1)))
#                 detail_style.append(('SPAN', (y - 1 + 1, _counter), (y - 1 + 1, _counter + number_details - 1)))
#                 detail_style.append(('SPAN', (y - 1 + 2, _counter), (y - 1 + 2, _counter + number_details - 1)))
#                 detail_style.append(('SPAN', (y - 1 + 3, _counter), (y - 1 + 3, _counter + number_details - 1)))
#                 detail_style.append(('SPAN', (y - 1 - 7, _counter), (y - 1 - 7, _counter + number_details - 1)))
#                 detail_style.append(('SPAN', (y - 1 - 6, _counter), (y - 1 - 6, _counter + number_details - 1)))
#                 detail_style.append(('SPAN', (y - 1 - 5, _counter), (y - 1 - 5, _counter + number_details - 1)))
#                 _counter = _counter + 1
#             if order_obj.way_to_pay == 'C':
#                 cont_counted = cont_counted + order_obj.total
#             elif order_obj.way_to_pay == 'D':
#                 cont_destination_payment = cont_destination_payment + order_obj.total
#             if number_details > 1:
#                 _counter = _counter - 1
#         _c2 = _c2 + 1
#
#     ana_c3 = Table(_rows, colWidths=colwiths_table_title)
#
#     colwiths_table_totals = [_bts * 80 / 100, _bts * 10 / 100, _bts * 10 / 100]
#     p4 = Paragraph('TOTALES ENCOMIENDAS', styles["CenterTitle-Dotcirful"])
#     _tbl_totals = [
#         ['', p4, ''],
#         ['', 'TOTAL PAGO CONTADO:', 'S/. ' + str(decimal.Decimal(round(cont_counted, 2)))],
#         ['', 'TOTAL PAGO DESTINO:', 'S/. ' + str(decimal.Decimal(round(cont_destination_payment, 2)))],
#     ]
#     ana_c4 = Table(_tbl_totals, colWidths=colwiths_table_totals)
#
#     my_style_table = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('ALIGN', (0, 0), (0, -1), 'CENTER'),
#         # ('FONTNAME', (0, 1), (0, -1), 'Newgot'),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('FONTNAME', (0, 0), (0, -1), 'Dotcirful-Regular'),
#         ('FONTNAME', (2, 0), (2, -1), 'Dotcirful-Regular'),
#         # ('BOTTOMPADDING', (0, 0), (-1, -1), -6),
#         # ('ALIGNMENT', (1, 1), (1, 1), 'RIGHT'),
#         # ('ALIGNMENT', (1, 0), (1, 0), 'RIGHT'),
#         # ('TOPPADDING', (0, 0), (-1, -1), 1),
#         # ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         # ('LINEBELOW', (0, 0), (-1, 0), 1, colors.darkblue),
#         # ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
#     ]
#     ana_c1.setStyle(TableStyle(my_style_table))
#
#     my_style_table_header_1 = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('SPAN', (0, 0), (1, 0)),
#         ('VALIGN', (0, 0), (0, -1), 'MIDDLE')  # first column
#
#     ]
#     ana_c_1.setStyle(TableStyle(my_style_table_header_1))
#
#     my_style_table_header = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('VALIGN', (1, 0), (1, -1), 'MIDDLE')  # first column
#
#     ]
#     ana_c.setStyle(TableStyle(my_style_table_header))
#
#     my_style_table_totals = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('VALIGN', (1, 0), (1, -1), 'MIDDLE'),  # first column
#         ('SPAN', (1, 0), (2, 0)),  # first row
#         ('ALIGNMENT', (1, 0), (2, -1), 'RIGHT'),  # second column
#     ]
#     ana_c4.setStyle(TableStyle(my_style_table_totals))
#
#     ana_c3.setStyle(TableStyle(detail_style))
#
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff,
#                             pagesize=(8.3 * inch, 11.7 * inch),
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title='Manifiesto de Encomiendas'
#                             )
#     dictionary = []
#     dictionary.append(ana_c)
#     dictionary.append(Spacer(1, 5))
#     # dictionary.append(Paragraph(tbh_business_name_address.replace("\n", "<br />"), styles["Left"]))
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(Paragraph(tbn_name_document, styles["CenterTitle-Dotcirful"]))
#     dictionary.append(Spacer(20, 20))
#     dictionary.append(ana_c1)
#     dictionary.append(Spacer(10, 10))
#     # dictionary.append(ana_c2)
#     dictionary.append(ana_c3)
#     dictionary.append(Spacer(10, 10))
#     dictionary.append(ana_c4)
#
#     response = HttpResponse(content_type='application/pdf')
#     doc.build(dictionary)
#
#     response['Content-Disposition'] = 'attachment; filename="Manifiesto-Encomienda_[{}].pdf"'.format(manifest_obj.id)
#     # doc.build(elements)
#     # doc.build(Story)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#
#
# def print_guide_comidity(request, pk=None):  # Guia Remision Transportista
#     _a5 = (5.8 * inch, 8.3 * inch)
#
#     ml = 0.25 * inch
#     mr = 0.25 * inch
#     ms = 0.25 * inch
#     mi = 0.25 * inch
#
#     _bts = 5.8 * inch - 0.25 * inch - 0.25 * inch
#     # _bts2 = 8.3 * inch - 0.25 * inch - 0.25 * inch
#     colwiths_table = [_bts * 10 / 100, _bts * 30 / 100, _bts * 10 / 100, _bts * 50 / 100]
#     orders_programmings_obj = OrderProgramming.objects.filter(order_id=pk)
#     programming_obj = orders_programmings_obj.first().programming
#     order_obj = orders_programmings_obj.first().order
#     date = datetime.now()
#     _formatdate = date.strftime("%d/%m/%Y")
#
#     td_dates_1 = _formatdate
#     td_dates_2 = _formatdate
#     td_serial_guide = orders_programmings_obj.first().guide_serial + ' - '
#     td_nro_guide = orders_programmings_obj.first().guide_code
#
#     _tbl_header = [
#         ['', td_serial_guide, td_nro_guide],
#         ['', td_dates_1, td_dates_2],
#
#     ]
#     ana_c = Table(_tbl_header, colWidths=[_bts * 10 / 100, _bts * 35 / 100, _bts * 55 / 100],
#                   rowHeights=[_bts * 10 / 100, _bts * 10 / 100])
#
#     my_style_table_header = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('LEFTPADDING', (2, 0), (2, 0), 180),
#         ('LEFTPADDING', (1, 0), (1, 0), 291),
#         ('BOTTOMPADDING', (0, 0), (3, 0), -20),
#         # ('BACKGROUND',  (0, 0), (3, 0), colors.pink)
#         # ('VALIGN', (1, 0), (1, -1), 'MIDDLE')  # first column
#     ]
#     ana_c.setStyle(TableStyle(my_style_table_header))
#
#     td_subsidiary_origin = order_obj.orderroute_set.filter(type='O').last().subsidiary.address
#     td_subsidiary_destiny = order_obj.orderroute_set.filter(type='D').last().subsidiary.address
#
#     _tbl_subsidiarys = [
#         ['', '', td_subsidiary_origin],
#         ['', '', td_subsidiary_destiny],
#     ]
#     ana_c1 = Table(_tbl_subsidiarys, colWidths=[_bts * 10 / 100, _bts * 5 / 100, _bts * 85 / 100])
#
#     my_style_table_subsidiary = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('TOPPADDING', (0, 0), (3, 0), -6),  # first row
#         ('TOPPADDING', (0, 1), (3, 1), 2),  # second row
#         # ('BACKGROUND',  (0, 1), (3, 1), colors.pink),
#     ]
#     ana_c1.setStyle(TableStyle(my_style_table_subsidiary))
#
#     td_client_sender = order_obj.orderaction_set.filter(type='R').last().client.names.upper()
#     td_client_addreesse = order_obj.orderaction_set.filter(type='D').last().client.names.upper()
#     td_client_sender_type_document = order_obj.orderaction_set.filter(
#         type='R').last().client.clienttype_set.first().document_type.short_description + ':'
#     td_client_sender_document = order_obj.orderaction_set.filter(
#         type='R').last().client.clienttype_set.first().document_number
#     td_client_addreesse_type_document = order_obj.orderaction_set.filter(
#         type='D').last().client.clienttype_set.first().document_type.short_description + ':'
#     td_client_addreesse_document = order_obj.orderaction_set.filter(
#         type='D').last().client.clienttype_set.first().document_number
#
#     _tbl_clients = [
#         ['', '', td_client_sender] + [td_client_sender_type_document] + [td_client_sender_document],
#         ['', '', td_client_addreesse] + [td_client_addreesse_type_document] + [td_client_addreesse_document],
#     ]
#     ana_c2 = Table(_tbl_clients,
#                    colWidths=[_bts * 5 / 100, _bts * 4 / 100, _bts * 79 / 100, _bts * 5 / 100, _bts * 7 / 100])
#
#     my_style_table_client = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 8),
#         ('FONTSIZE', (3, 0), (4, -1), 6),
#         ('LEFTPADDING', (3, 0), (3, -1), 21),
#         ('LEFTPADDING', (4, 0), (4, -1), 12),
#         ('TOPPADDING', (0, 0), (4, 0), -1),  # first row
#         ('TOPPADDING', (0, 1), (4, 1), 3),  # second row
#     ]
#     ana_c2.setStyle(TableStyle(my_style_table_client))
#
#     colwiths_table_title = [_bts * 10 / 100,
#                             _bts * 65 / 100,
#                             _bts * 9 / 100,
#                             _bts * 9 / 100,
#                             _bts * 7 / 100]
#
#     _rows = []
#     _counter = 1
#     _c2 = 1
#     for op in orders_programmings_obj:
#         order_obj = op.order
#         for d in order_obj.orderdetail_set.all():
#             number_details = order_obj.orderdetail_set.all().count()
#             _rows.append((_c2,
#                           Paragraph(d.description.upper(), styles["Justify-Dotcirful-table"]),
#                           d.unit.description,
#                           str(decimal.Decimal(round(d.quantity))),
#                           str(decimal.Decimal(round(d.weight))) + ' KG'))
#             _c2 = _c2 + 1
#
#     ana_c3 = Table(_rows, colWidths=colwiths_table_title)
#
#     detail_style = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 7),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('ALIGNMENT', (4, 0), (4, -1), 'RIGHT'),  # four column
#         ('RIGHTPADDING', (4, 0), (4, -1), -4),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -5),  # all columns
#         # ('BACKGROUND', (4, 0), (4, -1), colors.lightgrey),
#         ('FONTNAME', (0, 0), (-1, 0), 'Dotcirful-Regular'),
#         ('FONTNAME', (0, 0), (0, -1), 'Dotcirful-Regular'),
#         ('FONTSIZE', (0, 0), (0, -1), 7),
#         ('FONTSIZE', (0, 0), (-1, 0), 7)
#     ]
#     ana_c3.setStyle(TableStyle(detail_style))
#
#     td_truck = programming_obj.truck.truck_model.truck_brand.name
#     td_plate = programming_obj.truck.license_plate
#     td_certificate = programming_obj.truck.certificate
#     td_license_nro = programming_obj.get_pilot().n_license
#
#     _tbl_truck_data = [
#         ['', td_truck],
#         ['', td_plate],
#         ['', ''],
#         ['', td_certificate],
#         ['', td_license_nro]
#     ]
#     ana_c4 = Table(_tbl_truck_data, colWidths=[_bts * 23 / 100, _bts * 77 / 100])
#
#     my_style_table_truck_data = [
#         ('FONTNAME', (0, 0), (-1, -1), 'Dotcirful-Regular'),
#         # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ('FONTSIZE', (0, 0), (-1, -1), 6),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), -5),  # all columns
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # all columns
#         ('TOPPADDING', (0, 0), (1, 0), -1),  # first row
#         ('TOPPADDING', (0, 1), (2, 1), 3),  # second row
#         ('TOPPADDING', (0, 2), (2, 2), -1),  # third row
#         ('BOTTOMPADDING', (0, 3), (3, 3), -10),  # fourth row
#         ('BOTTOMPADDING', (0, 4), (4, 4), -14),  # fourth row
#     ]
#     ana_c4.setStyle(TableStyle(my_style_table_truck_data))
#
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff,
#                             pagesize=A5,
#                             rightMargin=mr,
#                             leftMargin=ml,
#                             topMargin=ms,
#                             bottomMargin=mi,
#                             title='Manifiesto de Encomiendas'
#                             )
#     dictionary = []
#     dictionary.append(ana_c)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(ana_c1)
#     dictionary.append(Spacer(1, 5))
#     dictionary.append(ana_c2)
#     dictionary.append(Spacer(4, 10))
#     dictionary.append(ana_c3)
#     dictionary.append(Spacer(54, 54))
#     dictionary.append(ana_c4)
#
#     response = HttpResponse(content_type='application/pdf')
#     doc.build(dictionary)
#     response['Content-Disposition'] = 'attachment; filename="GuiaRemisionTransportista_[{}].pdf"'.format(
#         orders_programmings_obj.first().order.id)
#     # doc.build(elements)
#     # doc.build(Story)
#     response.write(buff.getvalue())
#     buff.close()
#     return response
#
#
