from django.shortcuts import render, redirect
from django.contrib import messages
from invapp.models import HeadCompany,HeadItem
from invapp.forms import CompanyForm
from django.db.models import ProtectedError

def company_view(request):
    form = CompanyForm()
    companies = HeadCompany.objects.all()

    if request.method == 'POST':
        form = CompanyForm(request.POST)

        if request.POST.get('action') == 'save':
            if form.is_valid():
                form.save()
                messages.success(request, "Company saved successfully!")
                return redirect('company')

        elif request.POST.get('action') == 'delete':
            name = request.POST.get('company')
            try:
                obj = HeadCompany.objects.get(company=name)

                # Check if company is used in any item
                if HeadItem.objects.filter(company=obj).exists():
                    messages.warning(request, "Cannot delete: Company is used in items.")
                else:
                    obj.delete()
                    messages.success(request, "Company deleted successfully!")

                return redirect('company')

            except HeadCompany.DoesNotExist:
                messages.error(request, "Company not found!")

    return render(request, 'invapp/company.html', {
        'form': form,
        'companies': companies
    })
