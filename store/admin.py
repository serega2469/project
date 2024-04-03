from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from store.models import (Address,
                          Category,
                          Coupon,
                          Item,
                          Order,
                          OrderItem,
                          OrderStatus,
                          Refund,
                          Tag)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'ordered',
                    'get_shipping_address',
                    'coupon')
    list_display_links = ('user',)
    list_filter = ('ordered',
                   'status')
    search_fields = ('user__username',
                     'ref_code')

    def get_shipping_address(self, obj):
        if obj.shipping_address:
            return (f'{obj.shipping_address.street_address}, '
                    f'{obj.shipping_address.country}, '
                    f'{obj.shipping_address.zip}')
        return 'No address provided'

    get_shipping_address.short_description = _('Shipping Address')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'street_address',
                    'country',
                    'zip',
                    'default')
    list_filter = ('default',
                   'country')
    search_fields = ('user',
                     'street_address',
                     'zip')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'price',
                    'discount_price',
                    'category',
                    'get_tags',
                    'slug')
    list_filter = ('category', 'label')
    search_fields = ('title', 'category__name', 'label__title')
    actions = ['create_new_item']

    def get_tags(self, obj):
        return ', '.join([tag.title for tag in obj.label.all()])

    get_tags.short_description = 'Tags'

    def create_new_item(modeladmin, request, queryset):

        try:
            for item in queryset:
                item.pk = None
                item.slug += '_copy'
                item.save()
        except Exception as e:
            raise ValidationError(f'"The slug {item.slug} already exists"')

    create_new_item.short_description = 'Create a copy of selected object'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'ordered',
        'item',
        'quantity',
        'get_total_item_price',
        'get_total_discount_item_price',
        'get_amount_saved',
        'get_final_price'
    )

    list_filter = ('ordered',)
    actions = ['mark_as_ordered']

    def mark_as_ordered(modeladmin, request, queryset):
        queryset.update(ordered=True)

    mark_as_ordered.short_description = 'Mark as ordered'


admin.site.register(OrderStatus)
admin.site.register(Coupon)
admin.site.register(Refund)
