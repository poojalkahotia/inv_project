# invapp/views/item_views.py
from django.shortcuts import render, get_object_or_404, redirect
from invapp.forms import ItemForm
from invapp.models import HeadItem
from django.contrib import messages


def item_view(request, pk=None):
    instance = None
    if pk:
        instance = get_object_or_404(HeadItem, pk=pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            if pk:
                messages.success(request, "✅ Item updated successfully!")
            else:
                messages.success(request, "✅ Item added successfully!")
            return redirect('item')
    else:
        form = ItemForm(instance=instance)

    items = HeadItem.objects.all()
    return render(request, 'invapp/item.html', {
        'form': form,
        'items': items,
        'editing': pk is not None,
        'editing_id': pk
    })

def item_delete(request, pk):
    item = get_object_or_404(HeadItem, pk=pk)
    item.delete()
    messages.success(request, "Item deleted successfully!")
    return redirect('item')