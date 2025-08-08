# invapp/views/party_views.py

from django.shortcuts import render, get_object_or_404, redirect
from invapp.forms import PartyForm
from invapp.models import HeadParty
from django.contrib import messages

def party_view(request, pk=None):
    instance = None
    if pk:
        instance = get_object_or_404(HeadParty, pk=pk)

    if request.method == 'POST':
        form = PartyForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            if pk:
                messages.success(request, '✅ Party updated successfully!')
            else:
                messages.success(request, '✅ Party added successfully!')
            return redirect('party')  # back to form list
    else:
        form = PartyForm(instance=instance)

    parties = HeadParty.objects.all()
    return render(request, 'invapp/party.html', {
        'form': form,
        'parties': parties,
        'editing': pk is not None,
        'editing_id': pk
    })


def party_delete(request, pk):
    party = get_object_or_404(HeadParty, pk=pk)
    party.delete()
    messages.success(request, "Party deleted successfully!")
    return redirect('party')
