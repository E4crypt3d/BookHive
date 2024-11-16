from django.contrib import admin

from .models import Book, Category, Borrowing, Student, LibrarySetting

# Register your models here.


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_date", 'categories_str')
    search_fields = ('title', 'author', 'isbn_13', 'isbn_10')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ("book", "student", 'student__roll_no',
                    "issue_date", 'due_date', "return_date")
    search_fields = ('book__title', 'student__name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "roll_no")
    search_fields = ('name', 'department', 'roll_no', 'book__title')


@admin.register(LibrarySetting)
class LibrarySettingAdmin(admin.ModelAdmin):
    list_display = ("overdue_fee_per_day",)
