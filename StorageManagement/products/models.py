# products/models.py
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from django.db import models



class Size(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    image = models.ImageField(upload_to='products/', null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    avg_score = models.FloatField(null=True, blank=True, default=0)
    categories = models.ManyToManyField(Category, related_name='products')
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductProperty(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, related_name='properties', null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, related_name='properties', null=True, blank=True)
    buy_price = models.FloatField(null=True, blank=True)
    sell_price = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    can_sale = models.BooleanField(default=True)
    total_stock = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f'{self.product.name} properties'

    class Meta:
        unique_together = ('product', 'size', 'color')


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='comments', null=True, blank=True)
    title = models.CharField(max_length=100)
    text = models.TextField(null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProductRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    rating_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-rating_date']

    def __str__(self):
        return f'{self.user} - {self.product} - {self.rating}'

    def clean(self):
        if self.rating is not None and (self.rating > 5 or self.rating < 0):
            raise ValidationError('Rating must be between 0 and 5.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

