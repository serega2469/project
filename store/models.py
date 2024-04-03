from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from store.validators import validate_min_value

User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Title')
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name=_('SLUG')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Tag(models.Model):
    title = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Title')
    )
    color = models.CharField(
        max_length=7,
        verbose_name=_('Color'),
        help_text=_('Hex color code, e.g., #ABC123 or #DDD')
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name=_('SLUG')
    )

    class Meta:
        ordering = ('title',)
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.title


class Item(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name=_('Title')
    )
    discount_price = models.FloatField(
        verbose_name=_('Discount price'),
        validators=[validate_min_value],
        null=True,
        blank=True,
    )
    price = models.FloatField(
        verbose_name=_('Price'),
        validators=[validate_min_value]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Category')
    )
    label = models.ManyToManyField(
        Tag,
        verbose_name=_('Tags')
    )
    slug = models.SlugField(
        unique=True,
        max_length=255,
        verbose_name=_('SLUG')
    )
    description = models.TextField(
        verbose_name=_('Description')
    )
    image = models.ImageField(
        upload_to='images/items/',
        verbose_name=_('Image')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created date')
    )

    def get_absolute_url(self):
        return reverse("store:product",
                       kwargs={'slug': self.slug}
                       )

    def get_add_to_cart_url(self):
        return reverse(
            "store:add-to-cart",
            kwargs={'slug': self.slug}
        )

    def get_remove_from_cart_url(self):
        return reverse(
            "store:remove-from-cart",
            kwargs={'slug': self.slug}
        )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    def __str__(self):
        return self.title


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User')
    )
    street_address = models.CharField(
        max_length=100,
        verbose_name=_('Street address')
    )
    country = CountryField(
        multiple=False,
        verbose_name=_('Country')
    )
    zip = models.CharField(
        max_length=100,
        verbose_name=_('Zip code')
    )

    default = models.BooleanField(
        default=False,
        verbose_name=_('Default')
    )

    class Meta:
        ordering = ('country',)
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        return self.user.username


class OrderStatus(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_('Status Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Status Description')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('Order Status')
        verbose_name_plural = _('Order Statuses')

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User')
    )
    ordered = models.BooleanField(
        default=True,
        verbose_name=_('Ordered')
    )
    item = models.ForeignKey(
        Item,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('Product')
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Quantity')
    )

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return (self.get_total_item_price()
                - self.get_total_discount_item_price())

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    class Meta:
        ordering = ('item',)
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')

    def __str__(self):
        return f"{self.quantity} - {self.item.title}"


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User')
    )
    ref_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Refund code')
    )
    items = models.ManyToManyField(
        OrderItem,
        verbose_name=_('Products')
    )
    start_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Start date')
    )
    ordered_date = models.DateTimeField(
        verbose_name=_('Ordered date')
    )
    ordered = models.BooleanField(
        default=False,
        verbose_name=_('Ordered')
    )
    shipping_address = models.ForeignKey(
        'Address',
        related_name='shipping_address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Shipping Address')
    )

    # payment = models.ForeignKey(
    #     'Payment',
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    #     verbose_name=_('Payment')
    # )
    coupon = models.ForeignKey(
        'Coupon',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('Coupon')
    )
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        related_name='status',
        blank=True,
        null=True,
        verbose_name=_('Order Status')
    )

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    class Meta:
        ordering = ('-ordered_date',)
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('User')
    )
    amount = models.FloatField(
        verbose_name=_('Amount'),
        validators=[validate_min_value]
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(
        max_length=15,
        verbose_name=_('Promo Code')
    )
    amount = models.FloatField(
        verbose_name=_('Discount amount'),
        validators=[validate_min_value]
    )

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_('Order')
    )
    reason = models.TextField(
        verbose_name=_('Reason')
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name=_('Accepted')
    )
    email = models.EmailField(
        verbose_name=_('E-mail')
    )

    def __str__(self):
        return f"{self.pk}"
