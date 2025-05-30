# recommendation/models.py

from django.db import models
from products.models import Product

class AssociationRule(models.Model):
    support = models.FloatField(verbose_name="پشتیبانی")
    confidence = models.FloatField(verbose_name="اطمینان")
    lift = models.FloatField(verbose_name="لیفت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "قانون انجمنی"
        verbose_name_plural = "قوانین انجمنی"
        ordering = ['-lift']

    def __str__(self):
        return f"قانون {self.id} (اعتماد: {self.confidence:.2f})"

class RuleProduct(models.Model):
    rule = models.ForeignKey(
        AssociationRule,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="قانون انجمنی"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='rules'
    )
    is_antecedent = models.BooleanField(
        default=True,
        verbose_name="آیا مقدم است؟",
        help_text="اگر محصول بخش مقدم قانون باشد True، در غیر این صورت (نتیجه) False"
    )

    class Meta:
        verbose_name = "محصول قانون"
        verbose_name_plural = "محصولات قوانین"
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['is_antecedent']),
        ]

    def __str__(self):
        role = "مقدم" if self.is_antecedent else "نتیجه"
        return f"{self.product.name} ({role}) در قانون {self.rule.id}"