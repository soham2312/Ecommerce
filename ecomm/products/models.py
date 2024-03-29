from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
# Create your models here.

class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True,blank=True)
    category_image = models.ImageField(upload_to="categories")

    def save(self,*args,**kwargs):
        self.slug = slugify(self.category_name)
        super(Category,self).save(*args,**kwargs)

    def __str__(self):
        return self.category_name
    
class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price= models.IntegerField(default=0)

    def __str__(self):
        return self.color_name

    
class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price= models.IntegerField(default=0)

    def __str__(self):
        return self.size_name

class Product(BaseModel):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True,blank=True)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name="products")
    product_description = models.TextField()
    color = models.ManyToManyField(ColorVariant,blank=True)
    size = models.ManyToManyField(SizeVariant,blank=True)

    def save(self,*args,**kwargs):
        self.slug = slugify(self.product_name)
        super(Product,self).save(*args,**kwargs)
 
    def __str__(self):
        return self.product_name
    
    def get_product_price_by_size(self,size):
        return self.price + self.size.get(size_name=size).price 
 
class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to="product")
    is_featured = models.BooleanField(default=False)

class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=100)
    discount = models.IntegerField()
    is_expired = models.BooleanField(default=False)
    minimum_amount = models.IntegerField(default=500)

    def __str__(self):
        return self.coupon_code
