from django.db import models
from artd_customer.models import Customer
from artd_product.models import Product
from artd_partner.models import Partner
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


ADDRESS_TYPE = (
    ("billing", _("Billing")),
    ("shipping", _("Shipping")),
)


class OrderBaseModel(models.Model):
    created_at = models.DateTimeField(
        _("Created at"),
        help_text=_("Date time on which the object was created."),
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        help_text=_("Date time on which the object was last updated."),
        auto_now=True,
        editable=False,
    )
    status = models.BooleanField(
        _("Status"),
        help_text=_("Status of the object."),
        default=True,
    )

    class Meta:
        abstract = True


class OrderDeliveryMethod(OrderBaseModel):
    """Model definition for Order Delivery Method."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Partner"),
        on_delete=models.CASCADE,
    )
    delivery_method_code = models.CharField(
        _("Delivery method code"),
        help_text=_("Delivery method code"),
        max_length=100,
        unique=True,
    )
    delivery_method_description = models.CharField(
        _("Delivery method description"),
        help_text=_("Delivery method description"),
        max_length=250,
    )
    json_data = models.JSONField(
        _("JSON data"),
        help_text=_("JSON data"),
        null=True,
        blank=True,
    )

    class Meta:
        """Meta definition for Order Delivery Method."""

        verbose_name = "Order Delivery Method"
        verbose_name_plural = "Order Delivery Methods"

    def __str__(self):
        """Unicode representation of Order Delivery Method."""
        return f"{self.delivery_method_code}"


class OrderStatus(OrderBaseModel):
    """Model definition for OrderStatus."""

    status_code = models.CharField(
        _("Order status code"),
        help_text=_("Order status code"),
        max_length=100,
        unique=True,
    )
    status_description = models.CharField(
        _("Order status description"),
        help_text=_("Order status description"),
        max_length=250,
    )

    class Meta:
        """Meta definition for OrderStatus."""

        verbose_name = _("Order Status")
        verbose_name_plural = _("Order Statuses")

    def __str__(self):
        """Unicode representation of OrderStatus."""
        return self.status_code


class Order(OrderBaseModel):
    """Model definition for Order."""

    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        help_text=_("Partner"),
        on_delete=models.CASCADE,
    )
    increment_id = models.PositiveBigIntegerField(
        _("Increment ID"),
        help_text=_("Increment ID"),
    )
    customer = models.ForeignKey(
        Customer,
        verbose_name=_("Customer"),
        help_text=_("Customer"),
        on_delete=models.CASCADE,
    )
    order_status = models.ForeignKey(
        OrderStatus,
        verbose_name=_("Order status"),
        help_text=_("Order status"),
        on_delete=models.CASCADE,
        default=1,
    )
    payment_code = models.CharField(
        _("Payment code"),
        help_text=_("Payment code"),
        max_length=100,
    )
    delivery_method = models.ForeignKey(
        OrderDeliveryMethod,
        verbose_name=_("Delivery method"),
        help_text=_("Delivery method"),
        on_delete=models.CASCADE,
    )
    coupon_code = models.CharField(
        _("Coupon code"),
        help_text=_("Coupon code"),
        max_length=100,
        null=True,
        blank=True,
    )
    discount_amount = models.DecimalField(
        _("Base discount amount"),
        help_text=_("Base discount amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    grand_total = models.DecimalField(
        _("Base grand total"),
        help_text=_("Base grand total"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    shipping_amount = models.DecimalField(
        _("Base shipping amount"),
        help_text=_("Base shipping amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    subtotal = models.DecimalField(
        _("Base subtotal"),
        help_text=_("Base subtotal"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    tax_amount = models.DecimalField(
        _("Base tax amount"),
        help_text=_("Base tax amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    total_paid = models.DecimalField(
        _("Base total paid"),
        help_text=_("Base total paid"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    weight = models.DecimalField(
        _("Weight"),
        help_text=_("Weight"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    comment = models.TextField(
        _("Comment"),
        help_text=_("Comment"),
        null=True,
        blank=True,
    )
    json_data = models.JSONField(
        _("JSON data"),
        help_text=_("JSON data"),
        null=True,
        blank=True,
    )

    class Meta:
        """Meta definition for Order."""

        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        """Unicode representation of Order."""
        return self.increment_id


class OrderProduct(OrderBaseModel):
    """Model definition for Order Product."""

    order = models.ForeignKey(
        Order,
        verbose_name=_("Order"),
        help_text=_("Order"),
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        help_text=_("Product"),
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        _("Quantity"),
        help_text=_("Quantity"),
        default=1,
    )
    base_amount = models.DecimalField(
        _("Base amount"),
        help_text=_("Base amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    base_discount_amount = models.DecimalField(
        _("Base discount amount"),
        help_text=_("Base discount amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    base_tax_amount = models.DecimalField(
        _("Base tax amount"),
        help_text=_("Base tax amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    base_total = models.DecimalField(
        _("Base total"),
        help_text=_("Base total"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    amount = models.DecimalField(
        _("Amount"),
        help_text=_("Amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    discount_amount = models.DecimalField(
        _("Discount amount"),
        help_text=_("Discount amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    tax_amount = models.DecimalField(
        _("Tax amount"),
        help_text=_("Tax amount"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    total = models.DecimalField(
        _("Total"),
        help_text=_("Total"),
        default=0.00,
        max_digits=20,
        decimal_places=2,
    )
    json_data = models.JSONField(
        _("JSON data"),
        help_text=_("JSON data"),
        null=True,
        blank=True,
    )

    class Meta:
        """Meta definition for Order Product."""

        verbose_name = "Order Product"
        verbose_name_plural = "Order Products"

    def __str__(self):
        """Unicode representation of Order Product."""
        return self.product.name


class OrderStatusHistory(OrderBaseModel):
    """Model definition for Order Status History."""

    order_status = models.ForeignKey(
        OrderStatus,
        verbose_name=_("Order status"),
        help_text=_("Order status"),
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        verbose_name=_("Order"),
        help_text=_("Order"),
        on_delete=models.CASCADE,
    )
    comment = models.TextField(
        _("Comment"),
        help_text=_("Comment"),
        null=True,
        blank=True,
    )

    class Meta:
        """Meta definition for Order Status History."""

        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status Histories"

    def __str__(self):
        """Unicode representation of Order Status History."""
        return str(self.order.increment_id)


class OrderPaymentHistory(OrderBaseModel):
    """Model definition for Order Payment History."""

    order = models.ForeignKey(
        Order,
        verbose_name=_("Order"),
        help_text=_("Order"),
        on_delete=models.CASCADE,
    )
    payment_code = models.CharField(
        _("Payment code"),
        help_text=_("Payment code"),
        max_length=100,
    )
    json_data = models.JSONField(
        _("JSON data"),
        help_text=_("JSON data"),
        null=True,
        blank=True,
    )

    class Meta:
        """Meta definition for Order Payment History."""

        verbose_name = "Order Payment History"
        verbose_name_plural = "Order Payment Histories"

    def __str__(self):
        """Unicode representation of Order Payment History."""
        return self.id


class OrderAdress(OrderBaseModel):
    """Model definition for Order Adress."""

    order = models.ForeignKey(
        Order,
        verbose_name=_("Order"),
        help_text=_("Order"),
        on_delete=models.CASCADE,
    )
    address_type = models.CharField(
        _("Address type"),
        help_text=_("Address type"),
        max_length=100,
        choices=ADDRESS_TYPE,
    )
    city = models.CharField(
        _("City"),
        help_text=_("City"),
        max_length=100,
    )
    address = models.CharField(
        _("Address"),
        help_text=_("Address"),
        max_length=250,
    )
    phone = models.CharField(
        _("Phone"),
        help_text=_("Phone"),
        max_length=100,
    )
    firstname = models.CharField(
        _("Firstname"),
        help_text=_("Firstname"),
        max_length=250,
        blank=True,
        null=True,
    )
    lastname = models.CharField(
        _("Lastname"),
        help_text=_("Lastname"),
        max_length=250,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        _("Email"),
        help_text=_("Email"),
        max_length=250,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta definition for Order Adress."""

        verbose_name = "Order Adress"
        verbose_name_plural = "Order Adresses"

    def __str__(self):
        """Unicode representation of Order Adress."""
        return f"{self.order.increment_id} ({self.address_type})"


@receiver(post_save, sender=Order)
def createfirst_status_history(sender, instance, created, **kwargs):
    if created:
        OrderStatusHistory.objects.create(
            order_status=instance.order_status,
            order=instance,
            comment="Order created",
        )
