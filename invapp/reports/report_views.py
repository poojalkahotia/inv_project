from django.shortcuts import render
from invapp.models import PurMaster,HeadParty,HeadItem,SaleMaster,RecMaster,PayMaster,SaleDetails,PurDetails
from invapp.reports.party_report import get_party_report
from datetime import datetime
from django.db.models import Sum
from datetime import date 
from decimal import Decimal
from django.http import HttpResponse
from invapp.utils.pdf_utils import PartyBalancePDF,ItemBalancePDF,PartyStatementPDF,PurchaseReportPDF,SaleReportPDF,ReceiptReportPDF,PaymentReportPDF
from invapp.reports.pdf_reports import SaleReportPDF


def all_party_balance(request):
    party_objs = HeadParty.objects.all().order_by("partyname")

    party_balances = []
    for party in party_objs:
        purchases = PurMaster.objects.filter(partyname=party.partyname).aggregate(total=Sum("amount"))["total"] or 0
        sales = SaleMaster.objects.filter(partyname=party.partyname).aggregate(total=Sum("amount"))["total"] or 0
        receipts = RecMaster.objects.filter(partyname=party.partyname).aggregate(total=Sum("amount"))["total"] or 0
        payments = PayMaster.objects.filter(partyname=party.partyname).aggregate(total=Sum("amount"))["total"] or 0

        # New: Include opening balances
        opening_debit = party.openingdebit or 0
        opening_credit = party.openingcredit or 0

        total_balance = (
            Decimal(purchases) - Decimal(sales) +
            Decimal(receipts) - Decimal(payments) +
            Decimal(opening_debit) - Decimal(opening_credit)
        )

        party_balances.append({
            "partyname": party.partyname,
            "total_purchase": purchases,
            "total_sale": sales,
            "total_receipt": receipts,
            "total_payment": payments,
            "opening_debit": opening_debit,
            "opening_credit": opening_credit,
            "total_balance": total_balance,
        })

    context = {"party_balances": party_balances}
    return render(request, "reports/all_party_balance.html", context)

def all_party_balance_pdf(request):
    parties = HeadParty.objects.all().order_by("partyname")

    data = []
    for party in parties:
        purchases = PurMaster.objects.filter(partyname=party.partyname).aggregate(total=Sum("amount"))["total"] or 0
        sales = SaleMaster.objects.filter(partyname=party.partyname).aggregate(total=Sum("amount"))["total"] or 0
        receipts = RecMaster.objects.filter(partyname=party.partyname).aggregate(total=Sum("amount"))["total"] or 0
        payments = PayMaster.objects.filter(partyname=party.partyname).aggregate(total=Sum("amount"))["total"] or 0

        opening_debit = party.openingdebit or 0
        opening_credit = party.openingcredit or 0

        # Updated Balance Calculation
        balance = (
            Decimal(purchases) - Decimal(sales) +
            Decimal(receipts) - Decimal(payments) +
            Decimal(opening_debit) - Decimal(opening_credit)
        )

        data.append([
            party.partyname,
            str(opening_debit),
            str(opening_credit),
            str(purchases),
            str(sales),
            str(receipts),
            str(payments),
            str(balance)
        ])

    pdf = PartyBalancePDF()
    pdf.add_page()

    # Updated: 8 columns
    col_widths = [30, 18, 18, 22, 22, 22, 22, 22]
    headers = ["Party", "Opn Dr", "Opn Cr", "Purchase", "Sale", "Receipt", "Payment", "Balance"]

    pdf.add_table(data, col_widths, headers)

    pdf_data = bytes(pdf.output(dest="S"))
    return HttpResponse(pdf_data, content_type="application/pdf")

def party_master_report(request):
    parties = PurMaster.objects.values_list('partyname', flat=True).distinct()
    report_data = []
    from_date = None
    to_date = None

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        partyname = request.POST.get('partyname')

        report_data = get_party_report(from_date, to_date, partyname)

    context = {
        'parties': parties,
        'report_data': report_data,
        'from_date': from_date,
        'to_date': to_date
    }
    return render(request, 'reports/partymaster_report.html', context)

def party_st(request):
    parties = HeadParty.objects.all().order_by('partyname')
    selected_party = None
    combined_data = []
    total_balance = Decimal("0")

    if request.method == 'POST':
        partyname = request.POST.get('partyname')
        if partyname:
            try:
                selected_party = HeadParty.objects.get(partyname=partyname)

                # ✅ Opening Balance Entry
                opening_debit = selected_party.openingdebit or 0
                opening_credit = selected_party.openingcredit or 0

                combined_data.append({
                    'date': None,
                    'type': 'Opening Balance',
                    'ref': '',
                    'amount': Decimal(opening_debit) - Decimal(opening_credit),
                    'remarks': '',
                    'debit': Decimal(opening_debit),
                    'credit': Decimal(opening_credit),
                })

                # Sales
                sales = SaleMaster.objects.filter(partyname=partyname)
                for sale in sales:
                    amt = Decimal(sale.amount or 0)
                    combined_data.append({
                        'date': sale.invdate,
                        'type': 'Sale',
                        'ref': sale.invno,
                        'amount': amt,
                        'remarks': sale.remark,
                        'debit': amt,
                        'credit': Decimal("0"),
                    })

                # Purchases
                purchases = PurMaster.objects.filter(partyname=partyname)
                for purchase in purchases:
                    amt = Decimal(purchase.amount or 0)
                    combined_data.append({
                        'date': purchase.invdate,
                        'type': 'Purchase',
                        'ref': purchase.invno,
                        'amount': amt,
                        'remarks': purchase.remark,
                        'debit': Decimal("0"),
                        'credit': amt,
                    })

                # Receipts
                receipts = RecMaster.objects.filter(partyname=partyname)
                for receipt in receipts:
                    amt = Decimal(receipt.amount or 0)
                    combined_data.append({
                        'date': receipt.entrydate,
                        'type': 'Receipt',
                        'ref': receipt.entryno,
                        'amount': -amt,
                        'remarks': receipt.remark,
                        'debit': Decimal("0"),
                        'credit': amt,
                    })

                # Payments
                payments = PayMaster.objects.filter(partyname=partyname)
                for payment in payments:
                    amt = Decimal(payment.amount or 0)
                    combined_data.append({
                        'date': payment.entrydate,
                        'type': 'Payment',
                        'ref': payment.entryno,
                        'amount': -amt,
                        'remarks': payment.remark,
                        'debit': amt,
                        'credit': Decimal("0"),
                    })

                # Sort by date (put None date entries like Opening Balance first)
                combined_data.sort(key=lambda x: (x['date'] is not None, x['date']))

                # Total balance calculation
                total_balance = sum(entry['debit'] - entry['credit'] for entry in combined_data)

            except HeadParty.DoesNotExist:
                pass

    context = {
        'parties': parties,
        'selected_party': selected_party,
        'combined_data': combined_data,
        'total_balance': total_balance,
    }
    return render(request, 'reports/partyst.html', context)

def party_st_pdf(request, partyname):
    try:
        selected_party = HeadParty.objects.get(partyname=partyname)
    except HeadParty.DoesNotExist:
        return HttpResponse("Party not found", status=404)

    combined_data = []
    total_balance = Decimal("0")

    # Opening Balance
    opening_debit = selected_party.openingdebit or 0
    opening_credit = selected_party.openingcredit or 0

    combined_data.append({
        'date': None,
        'type': 'Opening Balance',
        'ref': '',
        'remarks': '',
        'debit': Decimal(opening_debit),
        'credit': Decimal(opening_credit),
    })

    # Sale
    for sale in SaleMaster.objects.filter(partyname=partyname):
        amt = Decimal(sale.amount or 0)
        combined_data.append({
            'date': sale.invdate,
            'type': 'Sale',
            'ref': sale.invno,
            'remarks': sale.remark,
            'debit': amt,
            'credit': Decimal("0"),
        })

    # Purchase
    for purchase in PurMaster.objects.filter(partyname=partyname):
        amt = Decimal(purchase.amount or 0)
        combined_data.append({
            'date': purchase.invdate,
            'type': 'Purchase',
            'ref': purchase.invno,
            'remarks': purchase.remark,
            'debit': Decimal("0"),
            'credit': amt,
        })

    # Receipt
    for rec in RecMaster.objects.filter(partyname=partyname):
        amt = Decimal(rec.amount or 0)
        combined_data.append({
            'date': rec.entrydate,
            'type': 'Receipt',
            'ref': rec.entryno,
            'remarks': rec.remark,
            'debit': Decimal("0"),
            'credit': amt,
        })

    # Payment
    for pay in PayMaster.objects.filter(partyname=partyname):
        amt = Decimal(pay.amount or 0)
        combined_data.append({
            'date': pay.entrydate,
            'type': 'Payment',
            'ref': pay.entryno,
            'remarks': pay.remark,
            'debit': amt,
            'credit': Decimal("0"),
        })

    # Sort data
    combined_data.sort(key=lambda x: (x['date'] is not None, x['date']))

    # Total Balance
    total_balance = sum(entry['debit'] - entry['credit'] for entry in combined_data)

    # Generate PDF
    pdf = PartyStatementPDF()
    pdf.add_page()
    pdf.render_statement(selected_party.partyname, combined_data, total_balance)
    pdf_output = bytes(pdf.output(dest="S"))

    return HttpResponse(pdf_output, content_type="application/pdf")




def all_item_balance(request):
    """सभी वस्तुओं का स्टॉक बैलेंस रिपोर्ट"""
    items = HeadItem.objects.all().order_by("itemname")

    item_balances = []
    for item in items:
        total_purchase = PurDetails.objects.filter(itemname=item.itemname).aggregate(total=Sum("itemqty"))["total"] or 0
        total_sale = SaleDetails.objects.filter(itemname=item.itemname).aggregate(total=Sum("itemqty"))["total"] or 0

        total_balance = item.op_st + total_purchase - total_sale  # Opening Stock + Purchases - Sales

        item_balances.append({
            "itemname": item.itemname,
            "opening_stock": item.op_st,
            "total_purchase": total_purchase,
            "total_sale": total_sale,
            "total_balance": total_balance,
        })

    context = {"item_balances": item_balances}
    return render(request, "reports/all_item_balance.html", context)

def all_item_balance_pdf(request):
    items = HeadItem.objects.all().order_by("itemname")

    data = []
    for item in items:
        total_purchase = (
            PurDetails.objects.filter(itemname=item.itemname)
            .aggregate(total=Sum("itemqty"))["total"] or 0
        )
        total_sale = (
            SaleDetails.objects.filter(itemname=item.itemname)
            .aggregate(total=Sum("itemqty"))["total"] or 0
        )
        total_balance = item.op_st + total_purchase - total_sale

        data.append([
            item.itemname,
            str(item.op_st),
            str(total_purchase),
            str(total_sale),
            str(total_balance)
        ])

    pdf = ItemBalancePDF()
    pdf.add_page()

    col_widths = [50, 30, 30, 30, 30]
    headers = ["Item Name", "Opening Stock", "Total Purchase", "Total Sale", "Total Balance"]

    pdf.add_table(data, col_widths, headers)

    pdf_data = bytes(pdf.output(dest="S"))
    return HttpResponse(pdf_data, content_type="application/pdf")



def item_st(request):
    items = HeadItem.objects.all()
    selected_item = None
    combined_data = []
    total_sold = 0
    total_purchased = 0
    closing_balance = 0

    if request.method == 'POST':
        itemname = request.POST.get('itemname')
        if itemname:
            try:
                selected_item = HeadItem.objects.get(itemname=itemname)
                
                # Fetch sales and purchases
                sales = SaleDetails.objects.filter(itemname=itemname)
                purchases = PurDetails.objects.filter(itemname=itemname)

                # Process sales
                for sale in sales:
                    combined_data.append({
                        'date': sale.salemaster.invdate,
                        'type': 'Sale',
                        'quantity': -sale.itemqty,
                        'rate': sale.itemrate,
                        'amount': -float(sale.itemamt)
                    })
                    total_sold += sale.itemqty

                # Process purchases
                for purchase in purchases:
                    combined_data.append({
                        'date': purchase.purmaster.invdate,
                        'type': 'Purchase',
                        'quantity': purchase.itemqty,
                        'rate': purchase.itemrate,
                        'amount': float(purchase.itemamt)
                    })
                    total_purchased += purchase.itemqty

                # Sort transactions by date
                combined_data.sort(key=lambda x: x['date'])

                # Calculate closing balance
                closing_balance = selected_item.op_st + total_purchased - total_sold

            except HeadItem.DoesNotExist:
                pass

    context = {
        'items': items,
        'selected_item': selected_item,
        'combined_data': combined_data,
        'total_sold': total_sold,
        'total_purchased': total_purchased,
        'closing_balance': closing_balance,
    }
    return render(request, 'reports/itemst.html', context)

def purmaster_report(request):
    # Default date range (current month)
    today = datetime.today()
    from_date = request.GET.get('from_date', today.replace(day=1).strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', today.strftime('%Y-%m-%d'))
    partyname = request.GET.get('partyname', '')

    # Filter purchase records
    filters = {'invdate__range': [from_date, to_date]}
    if partyname:
        filters['partyname'] = partyname

    purchases = PurMaster.objects.filter(**filters).order_by('-invdate')
    total_amount = sum(purchase.amount for purchase in purchases)

    # Get list of parties for dropdown
    parties = HeadParty.objects.values('partyname').distinct()

    context = {
        'purchases': purchases,
        'from_date': from_date,
        'to_date': to_date,
        'selected_party': partyname,
        'parties': parties,
        'total_amount': total_amount,
    }
    return render(request, 'reports/purchase_report.html', context)

def purchase_report_pdf(request):
    today = datetime.today()
    from_date = request.GET.get('from_date', today.replace(day=1).strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', today.strftime('%Y-%m-%d'))
    partyname = request.GET.get('partyname', '')

    filters = {'invdate__range': [from_date, to_date]}
    if partyname:
        filters['partyname'] = partyname

    purchases = PurMaster.objects.filter(**filters).order_by('-invdate')
    total_amount = sum(p.amount for p in purchases)

    # PDF
    pdf = PurchaseReportPDF()
    pdf.add_page()
    pdf.render_purchase_report(purchases, total_amount, from_date, to_date, partyname)

    pdf_output = bytes(pdf.output(dest="S"))

    return HttpResponse(pdf_output, content_type="application/pdf")


def salemaster_report(request):
    # Default date range (current month)
    today = datetime.today()
    from_date = request.GET.get('from_date', today.replace(day=1).strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', today.strftime('%Y-%m-%d'))
    partyname = request.GET.get('partyname', '')

    # Filter sale records
    filters = {'invdate__range': [from_date, to_date]}
    if partyname:
        filters['partyname'] = partyname

    sales = SaleMaster.objects.filter(**filters).order_by('-invdate')
    total_amount = sum(sale.amount for sale in sales)

    # Get list of parties for dropdown
    parties = HeadParty.objects.values('partyname').distinct()

    context = {
        'sales': sales,
        'from_date': from_date,
        'to_date': to_date,
        'selected_party': partyname,
        'parties': parties,
        'total_amount': total_amount,
    }
    return render(request, 'reports/salemaster_report.html', context)

def sale_pdf(request, invno):
    try:
        sale = SaleMaster.objects.get(invno=invno)
    except SaleMaster.DoesNotExist:
        return HttpResponse("⚠️ Sale not found", status=404)

    details = SaleDetails.objects.filter(salemaster=sale)
    if not details.exists():
        return HttpResponse("⚠️ No sale details found", status=404)

    pdf = SaleReportPDF(sale, details)
    pdf.add_page()
    pdf.sales_table()

    pdf_data = bytes(pdf.output(dest="S"))
    return HttpResponse(pdf_data, content_type="application/pdf")

def recmaster_report(request):
    # Default date range (current month)
    today = datetime.today()
    from_date = request.GET.get('from_date', today.replace(day=1).strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', today.strftime('%Y-%m-%d'))
    partyname = request.GET.get('partyname', '')

    # Filter receipt records
    filters = {'entrydate__range': [from_date, to_date]}
    if partyname:
        filters['partyname'] = partyname

    receipts = RecMaster.objects.filter(**filters).order_by('-entrydate')
    total_amount = sum(receipt.amount for receipt in receipts)

    # Get list of parties for dropdown
    parties = HeadParty.objects.values('partyname').distinct()

    context = {
        'receipts': receipts,
        'from_date': from_date,
        'to_date': to_date,
        'selected_party': partyname,
        'parties': parties,
        'total_amount': total_amount,
    }
    return render(request, 'reports/recmaster_report.html', context)

def receipt_report_pdf(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    partyname = request.GET.get("partyname", "")

    filters = {"entrydate__range": [from_date, to_date]}
    if partyname:
        filters["partyname"] = partyname

    receipts = RecMaster.objects.filter(**filters).order_by("entrydate")

    pdf = ReceiptReportPDF()
    pdf.add_page()
    pdf.receipts_table(receipts)

    pdf_data = bytes(pdf.output(dest="S"))
    return HttpResponse(pdf_data, content_type="application/pdf")



def paymaster_report(request):
    # Default date range (current month)
    today = datetime.today()
    from_date = request.GET.get('from_date', today.replace(day=1).strftime('%Y-%m-%d'))
    to_date = request.GET.get('to_date', today.strftime('%Y-%m-%d'))
    partyname = request.GET.get('partyname', '')

    # Filter payment records
    filters = {'entrydate__range': [from_date, to_date]}
    if partyname:
        filters['partyname'] = partyname

    payments = PayMaster.objects.filter(**filters).order_by('-entrydate')
    total_amount = sum(payment.amount for payment in payments)

    # Get list of parties for dropdown
    parties = HeadParty.objects.values('partyname').distinct()

    context = {
        'payments': payments,
        'from_date': from_date,
        'to_date': to_date,
        'selected_party': partyname,
        'parties': parties,
        'total_amount': total_amount,
    }
    return render(request, 'reports/paymaster_report.html', context)

def payment_report_pdf(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    partyname = request.GET.get("partyname", "")

    filters = {"entrydate__range": [from_date, to_date]}
    if partyname:
        filters["partyname"] = partyname

    payments = PayMaster.objects.filter(**filters).order_by("entrydate")

    pdf = PaymentReportPDF()
    pdf.add_page()
    pdf.payments_table(payments)

    pdf_data = bytes(pdf.output(dest="S"))
    return HttpResponse(pdf_data, content_type="application/pdf")


