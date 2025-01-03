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
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    stock = models.IntegerField()
    score = models.IntegerField()
    categories = models.ManyToManyField(Category, related_name='products')

    def __str__(self):
        return self.name

class ProductProperty(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='properties')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='properties')
    price = models.FloatField()
    weight = models.FloatField()
    def __str__(self):
        return f'{self.product.name} properties'


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    def __str__(self):
        return self.title

class ProductRating(models.Model):
    user = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    pub_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.user} - {self.product} - {self.rating}'