from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import Album, Song, Playlist, DottifyUser, Rating

class SheetAExtras(TestCase):
    def test_album_slug_computed_and_updates(self):
        a = Album(title="Greatest hits", artist_name="X", release_date="2024-01-01", retail_price="0.00")
        a.full_clean(); a.save()
        self.assertEqual(a.slug, "greatest-hits")
        # change title -> slug updates on save
        a.title = "Even Greater Hits"
        a.full_clean(); a.save()
        self.assertEqual(a.slug, "even-greater-hits")

    def test_album_unique_title_artist_format(self):
        Album.objects.create(title="T", artist_name="A", format="SNGL", release_date="2024-01-01", retail_price="1.00")
        dup = Album(title="T", artist_name="A", format="SNGL", release_date="2024-01-01", retail_price="1.00")
        with self.assertRaises(ValidationError):
            dup.full_clean()

    def test_album_release_date_limit_inclusive(self):
        max_future = date.today() + timedelta(days=6*30)
        ok = Album(title="OK", artist_name="A", release_date=max_future, retail_price="0.00")
        ok.full_clean()  # should not raise

        bad = Album(title="BAD", artist_name="A", release_date=max_future + timedelta(days=1), retail_price="0.00")
        with self.assertRaises(ValidationError):
            bad.full_clean()

    def test_artist_account_optional_and_set_null(self):
        u = User.objects.create_user("u1")
        du = DottifyUser.objects.create(user=u, display_name="Stage")
        a = Album.objects.create(title="T", artist_name="A", release_date="2024-01-01", retail_price="1.00", artist_account=du)
        du.delete()  # should not delete album; FK should become NULL
        a.refresh_from_db()
        self.assertIsNone(a.artist_account)

    def test_song_position_auto_and_immutable(self):
        a = Album.objects.create(title="T", artist_name="A", release_date="2024-01-01", retail_price="1.00")
        s1 = Song.objects.create(title="S1", album=a, length=60)
        s2 = Song.objects.create(title="S2", album=a, length=60)
        self.assertEqual(s1.position, 1)
        self.assertEqual(s2.position, 2)
        # try to change s1.position
        old = s1.position
        s1.position = 99
        s1.save()
        s1.refresh_from_db()
        self.assertEqual(s1.position, old)  # stays unchanged

    def test_song_unique_constraints(self):
        a = Album.objects.create(title="T", artist_name="A", release_date="2024-01-01", retail_price="1.00")
        Song.objects.create(title="SAME", album=a, length=60)
        dup_title = Song(title="SAME", album=a, length=61)
        with self.assertRaises(ValidationError):
            dup_title.full_clean()

    def test_playlist_created_at_and_visibility_default(self):
        u = User.objects.create_user("u1")
        du = DottifyUser.objects.create(user=u, display_name="Stage")
        p = Playlist.objects.create(name="P", owner=du)  # created_at auto, visibility default 0
        self.assertIsNotNone(p.created_at)
        self.assertEqual(p.visibility_level, 0)

    def test_rating_half_steps_and_bounds(self):
        ok = Rating(stars=Decimal("4.5")); ok.full_clean()
        edge = Rating(stars=Decimal("0.0")); edge.full_clean()
        top = Rating(stars=Decimal("5.0")); top.full_clean()

        bad_step = Rating(stars=Decimal("4.4"))
        with self.assertRaises(ValidationError):
            bad_step.full_clean()
        too_high = Rating(stars=Decimal("5.5"))
        with self.assertRaises(ValidationError):
            too_high.full_clean()
