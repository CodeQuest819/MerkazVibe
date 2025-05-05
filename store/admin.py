from django import forms
from django.contrib import admin
from .models import TopDeal, Product, Category, Slider, Page, Notification, Cart, CartItem, Order, OrderItem, Profile

admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Notification)
admin.site.register(Profile)
admin.site.register(Slider)

@admin.register(TopDeal)
class TopDealAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

class ProductAdminForm(forms.ModelForm):
    new_category = forms.CharField(required=False)

    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'image', 'zip_file', 'quantity', 'category')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'price', 'quantity', 'category', 'created_at')
    fields = ('name', 'description', 'price', 'image', 'zip_file', 'quantity', 'category', 'new_category')
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('new_category'):
            category, created = Category.objects.get_or_create(
                name=form.cleaned_data['new_category']
            )
            obj.category = category
        super().save_model(request, obj, form, change)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    list_filter = ('is_active',)