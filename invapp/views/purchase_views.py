from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from invapp.forms import PurMasterForm, PurDetailsForm
from invapp.models import PurMaster, PurDetails, HeadParty, HeadItem
from django.db.models import Max

import json
from django.db import transaction
from django.contrib import messages
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from invapp.forms import amount_to_words

def purchase_form(request, invno=None):
    purchase = None
    purchase_items_json = "[]"
    today_date = date.today().strftime("%Y-%m-%d")

    # default party info
    party_name = party_add1 = party_add2 = party_city = party_mobile = party_email = ""

    if invno:
        purchase = get_object_or_404(PurMaster, invno=invno)
        purchase_items = PurDetails.objects.filter(purmaster=purchase)

        # Prepare item JSON for JavaScript use
        items_data = [
            {
                "name": item.itemname,
                "rate": float(item.itemrate),
                "qty": float(item.itemqty),
                "amt": float(item.itemamt),
            }
            for item in purchase_items
        ]
        purchase_items_json = json.dumps(items_data)

        # Set date if available
        if purchase.invdate:
            today_date = purchase.invdate.strftime("%Y-%m-%d")

        # Set default party info from HeadParty
        try:
            party = HeadParty.objects.get(partyname=purchase.partyname)
            party_name = party.partyname
            party_add1 = party.add1
            party_add2 = party.add2
            party_city = party.city
            party_mobile = party.mobile
            party_email = party.email
        except HeadParty.DoesNotExist:
            pass

    # Next invoice number suggestion
    next_invno = PurMaster.objects.aggregate(Max("invno"))["invno__max"]
    next_invno = (next_invno + 1) if next_invno else 7010

    # List of parties with balance and contact info
    parties_with_balance = [
        {
            "partyname": party.partyname,
            "add1": party.add1,
            "add2": party.add2,
            "city": party.city,
            "mobileno": party.mobile,  # 🔁 corrected: was party.mobile
            "emailid": party.email,    # 🔁 corrected: was party.email
            "total_balance": float(party.total_balance),
        }
        for party in HeadParty.objects.all().order_by("partyname")
    ]

    context = {
        "purchase": purchase,
        "purchase_items_json": purchase_items_json,
        "next_invno": next_invno,
        "today_date": today_date,
        "items": HeadItem.objects.all().order_by("itemname"),
        "parties": parties_with_balance,
        "party_name": party_name,
        "party_add1": party_add1,
        "party_add2": party_add2,
        "party_city": party_city,
        "party_mobile": party_mobile,
        "party_email": party_email,
    }

    return render(request, "invapp/purchase.html", context)


def save_purchase(request):
    if request.method == "POST":
        invdate = request.POST.get("invdate")
        partyname = request.POST.get("partyname")
        remark = request.POST.get("remark", "")
        amount = float(request.POST.get("amount", 0))
        netamt = float(request.POST.get("netamt", 0))

        add1 = request.POST.get("add1", "")
        add2 = request.POST.get("add2", "")
        city = request.POST.get("city", "")
        mobileno = request.POST.get("mobileno", "")
        emailid = request.POST.get("emailid", "")
        otherno = request.POST.get("otherno")
        otherno = int(otherno) if otherno and otherno.isdigit() else 0

        amtinwords = request.POST.get("amtinwords", "")

        items_json = request.POST.get("items_json")
        items = json.loads(items_json) if items_json else []

        # 🔹 Create PurMaster Entry
        purchase = PurMaster.objects.create(
            invdate=invdate,
            partyname=partyname,
            add1=add1,
            add2=add2,
            city=city,
            mobileno=mobileno,
            email=emailid,
            otherno=otherno,
            remark=remark,
            amount=amount,
            netamt=netamt,
            amtinwords=amtinwords,
        )

        for item in items:
            PurDetails.objects.create(
                purmaster=purchase,
                itemname=item["name"],
                itemrate=item["rate"],
                itemqty=item["qty"],
                itemamt=item["amt"]
            )

        messages.success(request, "Purchase entry saved successfully!")
        return redirect("purchasedata")

    return redirect("purchase_form_new")

def update_purchase(request, invno):
    purchase = get_object_or_404(PurMaster, invno=invno)

    if request.method == "POST":
        purchase.invdate = request.POST.get("invdate")
        purchase.partyname = request.POST.get("partyname")
        purchase.add1 = request.POST.get("add1", "")
        purchase.add2 = request.POST.get("add2", "")
        purchase.city = request.POST.get("city", "")
        purchase.mobileno = request.POST.get("mobileno", "")
        purchase.email = request.POST.get("emailid", "")
        otherno = request.POST.get("otherno")
        purchase.otherno = int(otherno) if otherno and otherno.isdigit() else 0
        purchase.remark = request.POST.get("remark", "")

        # amount & netamt
        purchase.amount = float(request.POST.get("amount", 0))
        purchase.netamt = float(request.POST.get("netamt", 0))

        # amount in words
        purchase.amtinwords = request.POST.get("amtinwords", "")

        # update item details
        items_json = request.POST.get("items_json")
        items = json.loads(items_json) if items_json else []

        # delete old items
        PurDetails.objects.filter(purmaster=purchase).delete()

        # add new items
        for item in items:
            PurDetails.objects.create(
                purmaster=purchase,
                itemname=item["name"],
                itemrate=item["rate"],
                itemqty=item["qty"],
                itemamt=item["amt"]
            )

        purchase.save()

        messages.success(request, "Purchase entry updated successfully!")
        return redirect("purchasedata")

    return redirect("purchase_form_update", invno=invno)


def purchase_data_view(request):
    purchases = PurMaster.objects.all().order_by("-invno")
    items = HeadItem.objects.all()  # ✅ Fetch items
    parties = HeadParty.objects.all()  # ✅ Fetch party data

    return render(request, "invapp/purchasedata.html", {
        "purchases": purchases,
        "items": items,  # ✅ Pass items to template
        "parties": parties,  # ✅ Pass parties to template
        "today_date": timezone.now().date(),  # ✅ Pass today's date
    })

def delete_purchase(request, invno):
    purchase = get_object_or_404(PurMaster, invno=invno)
    purchase.delete()
    messages.success(request, "Purchase entry deleted successfully!")
    return redirect("purchasedata")

def num_to_words(request):
    try:
        num = Decimal(request.GET.get('num', '0')).quantize(Decimal('0.01'))
        if num > 0:
            words = amount_to_words(num)
            return JsonResponse({'words': words})
        else:
            return JsonResponse({'words': ''})
    except:
        return JsonResponse({'words': ''})
