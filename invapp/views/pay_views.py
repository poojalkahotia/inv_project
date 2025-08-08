from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from invapp.models import PayMaster,HeadParty
from django.db.models import Max

import json
from django.contrib import messages
from datetime import date
from decimal import Decimal
from django.utils import timezone

def paydata(request):
    payments = PayMaster.objects.all().order_by("-entrydate")  # Retrieve all payments, latest first
    return render(request, "invapp/paydata.html", {"payments": payments})

def payment_view(request, entryno=None):
    payment = None
    today_date = date.today().strftime('%Y-%m-%d')

    if entryno:
        payment = get_object_or_404(PayMaster, entryno=entryno)

    # ✅ Use total_balance property from model
    parties_with_balance = [{
        "partyname": party.partyname,
        "total_balance": float(party.total_balance)
    } for party in HeadParty.objects.all().order_by('partyname')]

    if request.method == "POST":
        entrydate = request.POST.get("entrydate")
        partyname = request.POST.get("partyname")
        amount = request.POST.get("amount")
        remark = request.POST.get("remark")

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "Invalid amount entered.")
            return render(request, "invapp/pay.html", {
                "payment": payment,
                "parties": parties_with_balance,
                "today_date": today_date,
                "next_entryno": payment.entryno if payment else '',
            })

        if payment:
            # ✅ Update existing
            payment.entrydate = entrydate
            payment.partyname = partyname
            payment.amount = amount
            payment.remark = remark
            payment.save()
            messages.success(request, "Payment updated successfully!")
        else:
            # ✅ Create new
            latest_payment = PayMaster.objects.order_by('-entryno').first()
            next_entryno = (getattr(latest_payment, 'entryno', 0) + 1)
            PayMaster.objects.create(
                entryno=next_entryno,
                entrydate=entrydate,
                partyname=partyname,
                amount=amount,
                remark=remark,
            )
            messages.success(request, "New payment added successfully!")
        return redirect("paydata")

    # 🔹 For GET - assign next entry number
    if not payment:
        latest_payment = PayMaster.objects.order_by('-entryno').first()
        next_entryno = (getattr(latest_payment, 'entryno', 0) + 1)
    else:
        next_entryno = payment.entryno

    return render(request, 'invapp/pay.html', {
        'payment': payment,
        'parties': parties_with_balance,
        'next_entryno': next_entryno,
        'today_date': today_date
    })


    
def update_payment(request, entryno):
    payment = get_object_or_404(PayMaster, entryno=entryno)  # ✅ Get existing payment
    parties = HeadParty.objects.all().order_by("partyname")  # ✅ Fetch party list
    today_date = date.today().strftime("%Y-%m-%d")  # ✅ Get today's date

    if request.method == "POST":
        entrydate = request.POST.get("entrydate")
        partyname = request.POST.get("partyname")
        amount = request.POST.get("amount")
        remark = request.POST.get("remark")

        try:
            amount = float(amount)  # ✅ Ensure amount is a valid number
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return render(request, "pay.html", {
                "payment": payment, "parties": parties, "today_date": today_date
            })

        # ✅ Update payment details
        payment.entrydate = entrydate
        payment.partyname = partyname
        payment.amount = amount
        payment.remark = remark
        payment.save()

        messages.success(request, "Payment updated successfully!")
        return redirect("paydata")  # ✅ Redirect to payment list

    return render(request, "invapp/pay.html", {
        "payment": payment,
        "parties": parties,
        "today_date": today_date
    })

def pay_list(request):
    payments = PayMaster.objects.all().order_by('-entryno')  # Order by latest entry
    return render(request, "paydata.html", {"payments": payments})

def delete_payment(request, entryno):
    payment = get_object_or_404(PayMaster, entryno=entryno)
    payment.delete()
    messages.success(request, f'Payment {entryno} deleted successfully!')
    return redirect('paydata')  # Refresh `paydata.html`
