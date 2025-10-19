Dottify

A simple Django app for managing albums, songs, playlists, user profiles, ratings, and comments. Built for COM2042 lab Sheet A with validation rules and unit tests.

Features

Albums with cover image, title, artist name, optional format, retail price, release date, and slug computed from title

Songs that belong to albums with auto assigned immutable track positions

Playlists with visibility levels and automatic creation timestamp

DottifyUser profile model that wraps Django’s User

Ratings with half star increments from 0.0 to 5.0

Comments with message text

Test suite for provided cases and extra edge cases

Tech stack

Python 3.13

Django

SQLite for local development

Pytest or Django test runner
