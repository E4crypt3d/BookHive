from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.core.exceptions import ObjectDoesNotExist


class User(AbstractUser):
    pass


class LibrarySetting(models.Model):
    overdue_fee_per_day = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.50)
    add_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Overdue Fee: {self.overdue_fee_per_day} per day"


class Student(models.Model):
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    roll_no = models.CharField(max_length=255, unique=True)
    add_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id and self.roll_no:
            self.roll_no = self.roll_no.upper()
        return super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    isbn_10 = models.CharField(
        max_length=10, unique=True, null=True, blank=True)
    isbn_13 = models.CharField(
        max_length=13, unique=True, null=True, blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=2, null=True, blank=True)
    maturity_rating = models.CharField(max_length=50, null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=True)
    preview_link = models.URLField(null=True, blank=True)
    info_link = models.URLField(null=True, blank=True)
    canonical_volume_link = models.URLField(null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)

    categories = models.ManyToManyField(Category, related_name='books')
    add_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['add_at']

    def __str__(self):
        return self.title

    def categories_str(self):
        return ", ".join([category.name for category in self.categories.all()])

    def get_absolute_url(self):
        return f"/book/{self.id}/"


class Borrowing(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    add_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-add_at']
        constraints = [
            models.UniqueConstraint(fields=['student', 'book', 'returned'], condition=models.Q(
                returned=False), name='unique_active_borrowing')
        ]

    def save(self, *args, **kwargs):
        if self.returned and not self.return_date:
            self.return_date = date.today()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.book.title}"

    @property
    def is_overdue(self):
        if not self.returned and date.today() > self.due_date:
            return True
        return False

    @property
    def remaining_days(self):
        if not self.returned and self.due_date:
            return max(0, (self.due_date - date.today()).days)
        return 0

    def calculate_fee(self):
        if self.is_overdue:
            overdue_days = max(0, (date.today() - self.due_date).days)
            return overdue_days * 50
        return 0
