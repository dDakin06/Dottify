from decimal import Decimal
from datetime import date
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from dateutil.relativedelta import relativedelta  
from django.db.models import Max 
from django.contrib.auth.models import User

def validate_increments(value: Decimal):
    if value % Decimal("0.5") != 0:
        raise models.ValidationError("Stars must be a multiple of 0.5.")
    
def validate_release_date(value: date):
    if value is None:
        return
    max_future = date.today() + relativedelta(months=+6)
    if value > max_future:
        raise models.ValidationError("The release dat for unreleased albums can only be 6 months later than the date.")
class DottifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=800,blank=False)

album_formats = (
    ("SNGL", "Single"),
    ("RMST", "Remaster"),
    ("DLUX", "Deluxe Edition"), 
    ("COMP", "Compilation"),
    ("LIVE", "Live Recording"),
)
class Album(models.Model):


    cover_image = models.ImageField(
        blank=True,
        null=True,
        default="default_cover.jpg",  
        help_text="Optional cover art; uses a default image if not provided.",
    )
    title = models.CharField(max_length=800,blank=False)
    artist_name = models.CharField(max_length=800,blank=False)
    retail_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("999.99"))],blank=False,
    )
    artist_account = models.ForeignKey(DottifyUser, on_delete=models.SET_NULL, blank=True, null=True)
    release_date = models.DateField(validators=[validate_release_date])
    slug = models.SlugField(blank=True, editable=False, null = True)
    format = models.CharField(
        max_length=4,
        choices=album_formats,
        blank=True,
        null=True,
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "artist_name", "format"],
                name="unique_Album_Title",
            )
        ]
    

    def save(self, *args, **kwargs):
        
        self.slug = slugify(self.title or "")
        super().save(*args, **kwargs)

class Song(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE) #might need to add fuctionality to access all songs from an album here 
    length = models.PositiveIntegerField(validators=[MinValueValidator(10)],blank=False)
    title = models.CharField(max_length=800)
    position = models.PositiveIntegerField(null=True, blank=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["album", "title"],
                name="unique_Song",
            ),
           
            models.UniqueConstraint(
                fields=["album", "position"],
                name="unique_position_per_album",
            )
        ]

    def save(self, *args, **kwargs):
       if self.position is None and self._state.adding:
            last = (
                Song.objects.filter(album_id=self.album_id)
                .aggregate(m=Max("position"))["m"]
                or 0
            )
            self.position = last + 1
       super().save(*args, **kwargs)


   
visibility_choices = (
    (0, "Hidden"),
    (1, "Unlisted"),
    (2, "Public"),
)   

class Playlist(models.Model):
    name = models.CharField(max_length=800,blank=False)
    created_at = models.DateTimeField()
    songs = models.ManyToManyField(Song)
    visibility_level = models.IntegerField(choices=visibility_choices, default=0)
    owner = models.ForeignKey(DottifyUser, on_delete=models.CASCADE)


class Rating(models.Model):
    stars = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("5.0")), validate_increments])

class Comment(models.Model):
    comment_text = models.CharField(max_length=800)