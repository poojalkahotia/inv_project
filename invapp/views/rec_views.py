from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from invapp.models import RecMaster,HeadParty
from django.db.models import Max
import json
from django.contrib import messages
from datetime import date
from decimal import Decimal
from django.utils import timezone

def rec(request):
    entryno = request.GET.get('entryno')
    receipt = None
    today_date = date.today().strftime('%Y-%m-%d')

    if entryno:
        receipt = get_object_or_404(RecMaster, entryno=entryno)

    # ✅ Prepare party list with total_balance (model-based)
    parties_with_balance = [{
        "partyname": party.partyname,
        "total_balance": float(party.total_balance)
    } for party in HeadParty.objects.all().order_by('partyname')]

    if request.method == "POST":
        entrydate = request.POST.get('entrydate')
        partyname = request.POST.get('partyname')
        amount = request.POST.get('amount')
        remark = request.POST.get('remark')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "Invalid amount entered.")
            return render(request, "invapp/rec.html", {
                "receipt": receipt,
                "parties": parties_with_balance,
                "today_date": today_date,
                "next_entryno": receipt.entryno if receipt else '',
            })

        if receipt:
            # ✅ Update existing
            receipt.entrydate = entrydate
            receipt.partyname = partyname
            receipt.amount = amount
            receipt.remark = remark
            receipt.save()
            messages.success(request, "Receipt updated successfully!")
        else:
            # ✅ Create new
            latest_receipt = RecMaster.objects.order_by('-entryno').first()
            next_entryno = (getattr(latest_receipt, 'entryno', 0) + 1)
            RecMaster.objects.create(
                entryno=next_entryno,
                entrydate=entrydate,
                partyname=partyname,
                amount=amount,
                remark=remark,
            )
            messages.success(request, "Receipt entry saved successfully!")
        return redirect('recdata')

    # 🔹 For GET - determine next entry number
    if not receipt:
        latest_receipt = RecMaster.objects.order_by('-entryno').first()
        next_entryno = (getattr(latest_receipt, 'entryno', 0) + 1)
    else:
        next_entryno = receipt.entryno

    return render(request, 'invapp/rec.html', {
        'receipt': receipt,
        'parties': parties_with_balance,
        'next_entryno': next_entryno,
        'today_date': today_date
    })

    
def recdata(request):
    receipts = RecMaster.objects.all().order_by('-entryno')  # Order by latest entry
    return render(request, "invapp/recdata.html", {"receipts": receipts})

def update_rec(request, entryno):
    receipt = get_object_or_404(RecMaster, entryno=entryno)
    parties = HeadParty.objects.all().order_by("partyname")
    today_date = date.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        receipt.entrydate = request.POST.get("entrydate")
        receipt.partyname = request.POST.get("partyname")
        receipt.amount = request.POST.get("amount")
        receipt.remark = request.POST.get("remark")
        receipt.save()
        messages.success(request, "Receipt updated successfully!")
        return redirect("recdata")

    return render(
        request,
        "invapp/rec.html",  # ✅ Corrected path
        {
            "receipt": receipt,
            "parties": parties,
            "today_date": today_date,
        },
    )

def delete_rec(request, entryno):
    receipt = get_object_or_404(RecMaster, entryno=entryno)
    receipt.delete()
    messages.success(request, "Receipt entry deleted successfully!")
    return redirect('recdata')

def rec_list(request):
    receipts = RecMaster.objects.all().order_by('-entryno')  # Order by latest entry
    return render(request, "recdata.html", {"receipts": receipts})
