# invapp/forms.py

from django import forms
from .models import HeadCompanyinfo,HeadParty,HeadCategory,HeadCompany,HeadItem,PurDetails,PurMaster,SaleMaster,SaleDetails
from num2words import num2words

class CompanyinfoForm(forms.ModelForm):
    class Meta:
        model = HeadCompanyinfo
        fields = '__all__'
        widgets = {
            'companyname': forms.TextInput(attrs={'class': 'form-control'}),
            'add1': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'add2': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'otherno': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'term1': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'term2': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PartyForm(forms.ModelForm):
    class Meta:
        model = HeadParty
        fields = '__all__'
        widgets = {
            'partyname': forms.TextInput(attrs={'class': 'form-control',}),
            'add1': forms.TextInput(attrs={'class': 'form-control'}),
            'add2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'otherno': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'openingdebit': forms.NumberInput(attrs={'class': 'form-control'}),
            'openingcredit': forms.NumberInput(attrs={'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        super(PartyForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].label = field.capitalize()

      # 👇 Disable 'partyname' if it's edit mode (instance exists)
        if self.instance and self.instance.pk:
            self.fields['partyname'].disabled = True


class CategoryForm(forms.ModelForm):
    class Meta:
        model = HeadCategory
        fields = '__all__'
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = HeadCompany
        fields = '__all__'
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
class ItemForm(forms.ModelForm):
    class Meta:
        model = HeadItem
        fields = '__all__'
        widgets = {
            'itemname': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'op_st': forms.NumberInput(attrs={'class': 'form-control'}),
            'pur_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'reorder': forms.NumberInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].label = field.replace('_', ' ').title()
        
         # 👇 Disable 'partyname' if it's edit mode (instance exists)
        if self.instance and self.instance.pk:
            self.fields['itemname'].disabled = True

class PurMasterForm(forms.ModelForm):
    # Dropdown for partyname from HeadParty
    partyname = forms.ModelChoiceField(
        queryset=HeadParty.objects.all().order_by('partyname'),
        empty_label="Select Party",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PurMaster
        fields = [
            'invno', 'invdate', 'partyname',
            'add1', 'add2', 'city', 'state',
            'mobileno', 'otherno', 'email',
            'amount', 'adjustment', 'netamt',
            'amtinwords', 'remark'
        ]
        widgets = {
            'invno': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'invdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'add1': forms.TextInput(attrs={'class': 'form-control'}),
            'add2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'mobileno': forms.NumberInput(attrs={'class': 'form-control'}),
            'otherno': forms.NumberInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'adjustment': forms.NumberInput(attrs={'class': 'form-control'}),
            'netamt': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'amtinwords': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

def amount_to_words(amount):
        amount = float(amount)
        words = num2words(amount, lang="en_IN")
        return f"{words.title()} Rupees Only"    

def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('netamt') or 0
        try:
            if amount > 0:
                words = amount_to_words(amount)
                cleaned_data['amtinwords'] = words
            else:
                cleaned_data['amtinwords'] = ""
        except:
            cleaned_data['amtinwords'] = ""
        return cleaned_data

    
class PurDetailsForm(forms.ModelForm):
    # Dropdown for itemname from HeadItem
    itemname = forms.ModelChoiceField(
        queryset=HeadItem.objects.all().order_by('itemname'),
        empty_label="Select Item",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PurDetails
        fields = ['itemname', 'itemrate', 'itemqty', 'itemamt']
        widgets = {
            'qty': forms.NumberInput(attrs={
                'class': 'form-control',
                'oninput': 'calculateAmount()'
            }),
            'rate': forms.NumberInput(attrs={
                'class': 'form-control'
                
            }),
            'itemamt': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
        }

class SaleMasterForm(forms.ModelForm):
    # Dropdown for partyname from HeadParty
    partyname = forms.ModelChoiceField(
        queryset=HeadParty.objects.all().order_by('partyname'),
        empty_label="Select Party",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = SaleMaster
        fields = [
            'invno', 'invdate', 'partyname',
            'add1', 'add2', 'city', 'state',
            'mobileno', 'otherno', 'email',
            'amount', 'adjustment', 'netamt',
            'amtinwords', 'remark'
        ]
        widgets = {
            'invno': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'invdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'add1': forms.TextInput(attrs={'class': 'form-control'}),
            'add2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'mobileno': forms.NumberInput(attrs={'class': 'form-control'}),
            'otherno': forms.NumberInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'adjustment': forms.NumberInput(attrs={'class': 'form-control'}),
            'netamt': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'amtinwords': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class SaleDetailsForm(forms.ModelForm):
    itemname = forms.ModelChoiceField(
        queryset=HeadItem.objects.all().order_by('itemname'),
        empty_label="Select Item",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = SaleDetails
        fields = ['itemname', 'itemrate', 'itemqty', 'itemamt']
        widgets = {
            'itemqty': forms.NumberInput(attrs={
                'class': 'form-control',
                'oninput': 'calculateAmount()'
            }),
            'itemrate': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'itemamt': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
        }
        