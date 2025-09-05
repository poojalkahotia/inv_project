from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum

class HeadCompanyinfo(models.Model):
    companyname = models.CharField(max_length=100, primary_key=True)
    add1 = models.TextField(blank=True)
    add2 = models.TextField(blank=True)
    city = models.TextField(blank=True)
    state = models.TextField(blank=True)
    mobile = models.TextField(blank=True)
    otherno = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    remark = models.TextField(blank=True)
    term1 = models.TextField(blank=True)
    term2 = models.TextField(blank=True)

    def __str__(self):
        return self.companyname



class HeadParty(models.Model):
    partyname = models.CharField(max_length=100, primary_key=True)
    add1 = models.CharField(max_length=200, blank=True)
    add2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    otherno = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    remark = models.TextField(blank=True)
    openingdebit = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    openingcredit = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    def __str__(self):
        return self.partyname

    @property
    def total_balance(self):
        sales_total = SaleMaster.objects.filter(partyname=self.partyname).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        purchase_total = PurMaster.objects.filter(partyname=self.partyname).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        receipt_total = RecMaster.objects.filter(partyname=self.partyname).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        payment_total = PayMaster.objects.filter(partyname=self.partyname).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

        opening_debit = Decimal(self.openingdebit or 0)
        opening_credit = Decimal(self.openingcredit or 0)

        return purchase_total - sales_total + receipt_total - payment_total - opening_debit + opening_credit
    

class HeadCategory(models.Model):
    category = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.category

class HeadCompany(models.Model):
    company = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.company

class HeadItem(models.Model):
    itemname = models.CharField(max_length=100, primary_key=True)
    company = models.ForeignKey('HeadCompany', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('HeadCategory', on_delete=models.SET_NULL, null=True)
    op_st = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Op. St.', default=0)
    pur_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Pur Rate', default=0)
    sale_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Sale Rate', default=0)
    reorder = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Reorder', default=0)
    remark = models.TextField(blank=True)

    def __str__(self):
        return self.itemname

class PurMaster(models.Model):
    invno = models.AutoField(primary_key=True)  # Unique invoice number
    invdate = models.DateField()
    partyname = models.CharField(max_length=255)
    add1 = models.CharField(max_length=255, blank=True, null=True)
    add2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    mobileno = models.BigIntegerField(default=0)
    otherno = models.BigIntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 👈 Already present
    netamt = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    amtinwords = models.CharField(max_length=255, blank=True, null=True)# 👈 Already present
    remark = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"Invoice {self.invno} - {self.partyname}"

class PurDetails(models.Model):
    purmaster = models.ForeignKey('PurMaster', on_delete=models.CASCADE)
    itemname = models.CharField(max_length=100) 
    itemqty = models.IntegerField()
    itemrate = models.DecimalField(max_digits=10, decimal_places=2)
    itemamt = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.itemname} - {self.qty}"

class SaleMaster(models.Model):
    invno = models.AutoField(primary_key=True)  # Unique invoice number
    invdate = models.DateField()
    partyname = models.CharField(max_length=255)
    add1 = models.CharField(max_length=255, blank=True, null=True)
    add2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    mobileno = models.BigIntegerField(default=0)
    otherno = models.BigIntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    netamt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amtinwords = models.CharField(max_length=255, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Sale Invoice {self.invno} - {self.partyname}"


class SaleDetails(models.Model):
    salemaster = models.ForeignKey('SaleMaster', on_delete=models.CASCADE)
    itemname = models.CharField(max_length=100)
    itemqty = models.IntegerField()
    itemrate = models.DecimalField(max_digits=10, decimal_places=2)
    itemamt = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.itemname} - {self.itemqty}"


class RecMaster(models.Model):
    entryno = models.AutoField(primary_key=True)
    entrydate = models.DateField()
    partyname = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remark = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.entryno} - {self.partyname}"


class PayMaster(models.Model):
    entryno = models.AutoField(primary_key=True)
    entrydate = models.DateField()
    partyname = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remark = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.entryno} - {self.partyname}"
  