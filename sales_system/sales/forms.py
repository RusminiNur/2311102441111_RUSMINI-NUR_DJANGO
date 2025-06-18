from django import forms
from .models import Member, Supplier, Product, Sale, Purchase

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'supplier', 'price', 'stock']

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['member', 'product', 'quantity']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product', 'supplier', 'quantity', 'purchase_price']