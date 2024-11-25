from django.db import models

# Create your models here.
from django.conf import settings


class Category(models.Model):
    """
    Categories for clothing items (e.g., Tops, Bottoms, Shoes, etc.)
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Color(models.Model):
    """
    Colors for clothing items
    """
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7)  # Format: #RRGGBB

    def __str__(self):
        return self.name


class Season(models.Model):
    """
    Seasons for clothing items (Spring, Summer, Fall, Winter)
    """
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class ClothingItem(models.Model):
    """
    Individual clothing items in a user's wardrobe
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clothing_items'
    )
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='items'
    )
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20)
    colors = models.ManyToManyField(Color, related_name='items')
    seasons = models.ManyToManyField(Season, related_name='items')
    image = models.ImageField(
        upload_to='clothing_items/',
        null=True, blank=True
    )
    purchase_date = models.DateField(null=True, blank=True)
    last_worn = models.DateField(null=True, blank=True)
    times_worn = models.PositiveIntegerField(default=0)
    favorite = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username}'s {self.name}"


class Outfit(models.Model):
    """
    Combinations of clothing items that make complete outfits
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='outfits'
    )
    name = models.CharField(max_length=100)
    items = models.ManyToManyField(ClothingItem, related_name='outfits')
    description = models.TextField(blank=True)
    seasons = models.ManyToManyField(Season, related_name='outfits')
    occasion = models.CharField(max_length=50, blank=True)
    favorite = models.BooleanField(default=False)
    times_worn = models.PositiveIntegerField(default=0)
    last_worn = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username}'s {self.name}"


class Tag(models.Model):
    """
    Custom tags for clothing items and outfits
    """
    name = models.CharField(max_length=50, unique=True)
    items = models.ManyToManyField(
        ClothingItem,
        related_name='tags',
        blank=True
    )
    outfits = models.ManyToManyField(Outfit, related_name='tags', blank=True)

    def __str__(self):
        return self.name
