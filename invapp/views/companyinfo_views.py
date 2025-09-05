from django.shortcuts import render, redirect
from django.contrib import messages
from invapp.models import HeadCompanyinfo
from invapp.forms import CompanyinfoForm


def companyinfo_view(request):
    company = HeadCompanyinfo.objects.first()
    editing = request.GET.get("edit") == "true"

    if request.method == "POST":
        form = CompanyinfoForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            if company:
                messages.success(request, "✅ Company updated successfully!")
            else:
                messages.success(request, "✅ Company added successfully!")
            return redirect("companyinfo")   # Save ke baad info view pe redirect
    else:
        form = CompanyinfoForm(instance=company)

    return render(request, "invapp/companyinfo.html", {
        "form": form,
        "company": company,
        "editing": editing,
    })
