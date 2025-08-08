from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from invapp.forms import SaleMasterForm, SaleDetailsForm
from invapp.models import SaleMaster, SaleDetails, HeadParty, HeadItem
from django.db.models import Max

import json
from django.contrib import messages
from datetime import date
from decimal import Decimal
from django.utils import timezone
from invapp.forms import amount_to_words

def sale_form(request, invno=None):
    sale = None
    sale_items_json = "[]"
    today_date = date.today().strftime("%Y-%m-%d")

    party_name = party_add1 = party_add2 = party_city = party_mobile = party_email = ""

    if invno:
        sale = get_object_or_404(SaleMaster, invno=invno)
        sale_items = SaleDetails.objects.filter(salemaster=sale)

        items_data = [
            {
                "name": item.itemname,
                "rate": float(item.itemrate),
                "qty": float(item.itemqty),
                "amt": float(item.itemamt),
            }
            for item in sale_items
        ]
        sale_items_json = json.dumps(items_data)

        if sale.invdate:
            today_date = sale.invdate.strftime("%Y-%m-%d")

        try:
            party = HeadParty.objects.get(partyname=sale.partyname)
            party_name = party.partyname
            party_add1 = party.add1
            party_add2 = party.add2
            party_city = party.city
            party_mobile = party.mobile
            party_email = party.email
        except HeadParty.DoesNotExist:
            pass

    next_invno = SaleMaster.objects.aggregate(Max("invno"))['invno__max']
    next_invno = (next_invno + 1) if next_invno else 8001

    parties_with_balance = [
        {
            "partyname": party.partyname,
            "add1": party.add1,
            "add2": party.add2,
            "city": party.city,
            "mobileno": party.mobile,
            "emailid": party.email,
            "total_balance": float(party.total_balance),
        }
        for party in HeadParty.objects.all().order_by("partyname")
    ]

    context = {
        "sale": sale,
        "sale_items_json": sale_items_json,
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

    return render(request, "invapp/sale.html", context)

def save_sale(request):
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

        sale = SaleMaster.objects.create(
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
            SaleDetails.objects.create(
                salemaster=sale,
                itemname=item["name"],
                itemrate=item["rate"],
                itemqty=item["qty"],
                itemamt=item["amt"]
            )

        messages.success(request, "Sale entry saved successfully!")
        return redirect("saledata")

    return redirect("sale_form_new")

def update_sale(request, invno):
    sale = get_object_or_404(SaleMaster, invno=invno)

    if request.method == "POST":
        sale.invdate = request.POST.get("invdate")
        sale.partyname = request.POST.get("partyname")
        sale.add1 = request.POST.get("add1", "")
        sale.add2 = request.POST.get("add2", "")
        sale.city = request.POST.get("city", "")
        sale.mobileno = request.POST.get("mobileno", "")
        sale.email = request.POST.get("emailid", "")
        otherno = request.POST.get("otherno")
        sale.otherno = int(otherno) if otherno and otherno.isdigit() else 0
        sale.remark = request.POST.get("remark", "")
        sale.amount = float(request.POST.get("amount", 0))
        sale.netamt = float(request.POST.get("netamt", 0))
        sale.amtinwords = request.POST.get("amtinwords", "")

        items_json = request.POST.get("items_json")
        items = json.loads(items_json) if items_json else []

        SaleDetails.objects.filter(salemaster=sale).delete()

        for item in items:
            SaleDetails.objects.create(
                salemaster=sale,
                itemname=item["name"],
                itemrate=item["rate"],
                itemqty=item["qty"],
                itemamt=item["amt"]
            )

        sale.save()

        messages.success(request, "Sale entry updated successfully!")
        return redirect("saledata")

    return redirect("sale_form_update", invno=invno)

def sale_data_view(request):
    sales = SaleMaster.objects.all().order_by("-invno")
    items = HeadItem.objects.all()
    parties = HeadParty.objects.all()

    return render(request, "invapp/saledata.html", {
        "sales": sales,
        "items": items,
        "parties": parties,
        "today_date": timezone.now().date(),
    })

def delete_sale(request, invno):
    sale = get_object_or_404(SaleMaster, invno=invno)
    sale.delete()
    messages.success(request, "Sale entry deleted successfully!")
    return redirect("saledata")
