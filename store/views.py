from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (DetailView,
                                  ListView,
                                  View)

from store.forms import (CheckoutForm,
                         CouponForm,
                         RefundForm)
from store.models import (Address,
                          Category,
                          Coupon,
                          Item,
                          OrderItem,
                          Order,
                          Refund)


def get_categories():
    return Category.objects.all()


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    items = Item.objects.filter(category=category)

    context = {
        'category': category,
        'items': items,
    }
    return render(request, 'category_products.html', context)


def products(request):
    query = request.GET.get('q')
    items = Item.objects.all().filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ) if query else Item.objects.all()

    context = {
        'items': items,
        'query': query
    }
    return render(request, 'products.html', context)


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.info(request, _('У вас нет активного заказа'))
            return redirect('store:checkout')

        form = CheckoutForm()
        default_shipping_address = Address.objects.filter(
            user=request.user,
            default=True
        ).first()

        context = {
            'form': form,
            'couponform': CouponForm(),
            'order': order,
            'default_shipping_address': default_shipping_address,
            'DISPLAY_COUPON_FORM': True
        }
        return render(request, 'checkout.html', context)

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST)
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.warning(request, 'У вас нет активного заказа')
            return redirect('store:order-summary')

        if form.is_valid():
            payment_option = form.cleaned_data.get('payment_option')
            order.payment_option = payment_option

            shipping_address = Address(
                user=request.user,
                street_address=form.cleaned_data.get('shipping_address'),
                country=form.cleaned_data.get('shipping_country'),
                zip=form.cleaned_data.get('shipping_zip'),
            )
            shipping_address.save()
            order.shipping_address = shipping_address
            order.ordered = True
            order.save()

            messages.success(request, 'Ваш заказ успешно создан!')
            return redirect('/')

        messages.info(request, 'Пожалуйста, заполните обязательные поля')
        return redirect('store:checkout')


class HomeView(ListView):
    model = Item
    paginate_by = settings.PAGE_SIZE
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(
                user=self.request.user,
                ordered=False
            )
        except ObjectDoesNotExist:
            messages.warning(self.request, 'У вас нет активного заказа')
            return redirect('/')

        context = {'object': order}
        return render(self.request, 'order_summary.html', context)


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False).first()

    if order_qs:
        if order_qs.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Количество товаров обновлено.")
        else:
            order_qs.items.add(order_item)
            messages.info(request, "Товар добавлен в корзину.")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Товар добавлен в корзину.")

    return redirect("store:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False).first()

    if order_qs and order_qs.items.filter(item__slug=item.slug).exists():
        order_item = OrderItem.objects.get(item=item, user=request.user, ordered=False)
        order_item.delete()
        messages.info(request, 'Товар удален из корзины.')

    return redirect('store:order-summary')


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False).first()

    if order_qs and order_qs.items.filter(item__slug=item.slug).exists():
        order_item = OrderItem.objects.get(item=item, user=request.user, ordered=False)
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
            messages.info(request, 'Количество товаров обновлено.')
        else:
            order_item.delete()
            messages.info(request, 'Товар удален из корзины.')

    return redirect('store:order-summary')


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        messages.info(
            request,
            'Купон не существует'
        )
        return None
    return coupon


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            order = Order.objects.get(user=self.request.user, ordered=False)
            coupon = get_coupon(self.request, code)
            if coupon:
                order.coupon = coupon
                order.save()
                messages.success(
                    self.request,
                    'Купон успешно применён'
                )
                return redirect('store:checkout')

        return redirect('store:checkout')


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)

                if order.refund_requested or order.refund_granted:
                    messages.warning(self.request, 'Этот заказ уже обработан.')
                else:
                    order.refund_requested = True
                    order.save()

                    refund = Refund(order=order, reason=message, email=email)
                    refund.save()

                    messages.success(self.request, 'Ваш запрос получен.')
                return redirect('store:request-refund')

            except ObjectDoesNotExist:
                messages.error(self.request, 'Этот заказ не существует.')
        return redirect('store:request-refund')
