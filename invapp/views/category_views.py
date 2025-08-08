# invapp/views/category_views.py
from django.shortcuts import render, redirect, get_object_or_404
from invapp.forms import CategoryForm
from invapp.models import HeadCategory
from django.contrib import messages

def category_view(request):
    selected_category = None
    categories = HeadCategory.objects.all()
    form = CategoryForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        category_name = request.POST.get('category')

        if category_name:
            try:
                selected_category = HeadCategory.objects.get(category=category_name)
            except HeadCategory.DoesNotExist:
                selected_category = None

        if action == 'save':
            form = CategoryForm(request.POST, instance=selected_category)
            if form.is_valid():
                form.save()
                messages.success(request, "Category saved successfully!")
                return redirect('category')  # refresh to clear form

        elif action == 'delete' and selected_category:
            selected_category.delete()
            messages.success(request, "Category deleted successfully!")
            return redirect('category')

    return render(request, 'invapp/category.html', {
        'form': form,
        'categories': categories,
    })

