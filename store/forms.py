from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import gettext_lazy as _


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ('S', _('Банковская карта')),
        ('P', _('TStore Pay'))
    )

    shipping_address = forms.CharField()
    shipping_country = CountryField(
        blank_label='Выберите страну'
    ).formfield(
        required=True,
        widget=CountrySelectWidget(
            attrs={
                'class': 'custom-select d-block w-100',
            }
        )
    )
    shipping_zip = forms.CharField(
        label='Почтовый индекс',
        required=False
    )

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=PAYMENT_CHOICES,
        required=False
    )
    set_default_shipping = forms.BooleanField(required=False)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Промокод'),
        'aria-label': _('Recipient\'s username'),
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
