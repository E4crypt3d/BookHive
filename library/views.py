from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
import re
from library.models import Book, Category, Student, Borrowing, LibrarySetting
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import date
# Create your views here.


def home(request):
    if request.htmx:
        # Get the search query from the request
        roll_no = request.GET.get('search', '')
        department = request.GET.get('department', '')
        search = f"T/BS-{department}/{department}-{roll_no}".upper()

        # Validate the search query
        if roll_no == '' or department == '':
            return HttpResponse('')

        # Validate the student ID
        if re.match(r'^T/BS-[A-Z]+/[A-Z]+-[1-9]\d?$', search):
            # Get the borrowings for the student
            borrows = Borrowing.objects.select_related(
                'student', 'book').filter(Q(student__roll_no=search) & Q(returned=False))
            if borrows.exists():
                # Render the partial template with the borrowings
                context = {'borrows': borrows}
                return render(request, 'partials/partial_home.html', context)
            else:
                # Return a message if the student is not found
                return HttpResponse('''
                    <div role="alert" class="alert alert-error !text-center">
                        Student not found. Please make sure the student ID is correct and the student has borrowed a book before. </div>
                ''')
        else:
            # Return a message if the student ID is invalid
            return HttpResponse('''
                <div class="alert alert-warning !text-center" role="alert">
                    Invalid student ID.
                </div>
            ''')
    else:
        # Return the full home page html template if the request is not from htmx
        return render(request, 'home.html')


def catalog(request):
    if request.method == 'POST':
        try:
            # Extract and validate POST data
            title = request.POST.get('bookTitle', '').strip()
            isbn = request.POST.get('bookISBN', '').strip()
            student_id = request.POST.get('studentId', '').strip().upper()
            name = request.POST.get('nameId', '').strip()
            department = request.POST.get('departmentId', '').strip()
            borrow_date = request.POST.get('borrowDate')
            return_date = request.POST.get('returnDate')
            regex = r'^T/BS-[A-Z]+/[A-Z]+-[1-9]\d?$'

            # Validate student ID
            if not re.match(regex, student_id):
                messages.error(request, 'Invalid student roll number format.')
                return render(request, 'catalog.html')

            # Validate that book and student details exist
            book = Book.objects.filter(
                Q(isbn_13=isbn) | Q(isbn_10=isbn)).first()
            if not book:
                messages.error(
                    request, 'Book not found with the provided ISBN.')
                return render(request, 'catalog.html')

            # Create or get the student
            student, created = Student.objects.get_or_create(
                name=name, department=department, roll_no=student_id)

            # Create borrowing entry
            borrow = Borrowing.objects.create(
                student=student, book=book, issue_date=borrow_date, due_date=return_date)

            # Update book stock
            if borrow:
                book.stock -= 1
                # Only update the stock field
                book.save(update_fields=['stock'])

                # Success: Redirect to success page with the borrow details
                return redirect(reverse('success_borrowed', kwargs={'borrow_id': borrow.id}))

        except Exception as e:
            messages.error(
                request, 'An unexpected error occurred. Please try again.')
            return render(request, 'catalog.html')

    else:
        try:
            # Get all books and categories
            all_books = Book.objects.all()
            categories = Category.objects.all()

            # Paginate books
            page_number = request.GET.get('page', 1)
            paginator = Paginator(all_books, 6)  # Paginate 6 books per page
            books = paginator.get_page(page_number)

            # Context for the template
            context = {'books': books, 'categories': categories}

            # HTMX support for partial rendering
            if request.htmx:
                return render(request, 'partials/partial_catalog.html', context)
            return render(request, 'catalog.html', context)

        except Exception as e:
            # Handle any errors during GET

            messages.error(
                request, 'Error loading the catalog. Please try again later.')
            return render(request, 'catalog.html')


def filter_by_category(request):
    # Get the selected category from the request
    category_id = request.GET.get("category", None)
    search = request.GET.get("search", None)

    # Filter books based on the selected category
    if category_id:
        books = Book.objects.filter(
            categories__id=category_id)
    # Filter books by search query
    elif search:
        books = Book.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(isbn_13__icontains=search) |
            Q(isbn_10__icontains=search))
    else:
        # If no category is selected, show all books
        books = Book.objects.all()

    context = {
        'books': books}

    # Render the partial template for HTMX request
    return render(request, 'partials/partial_catalog.html', context)


def borrowing(request, id=None):
    if id:
        borrows = Borrowing.objects.select_related('student', 'book').filter(
            student__id=id
        )
        if not borrows.exists():
            context = {'borrows': borrows,
                       'returned_borrows': borrows.filter(returned=True)[:5],
                       'current_borrows': borrows.filter(returned=False), }
            print(borrows)
        else:
            borrows = Borrowing.objects.select_related('student', 'book').all()
            context = {'borrows': borrows,
                       'returned_borrows': borrows.filter(returned=True)[:5],
                       'current_borrows': borrows.filter(returned=False),
                       'overdue_borrows': borrows.filter(
                           returned=False, due_date__lt=date.today())}
    return render(request, 'borrowing.html', context)


def success_borrowed(request, borrow_id):
    borrow = Borrowing.objects.select_related(
        'student', 'book').get(id=int(borrow_id))
    return render(request, 'success_borrowed.html', {'borrow': borrow})


def return_book(request, borrow_id):
    if request.htmx:
        # Get the borrowing object from the database
        borrow = Borrowing.objects.select_related(
            'book').get(id=int(borrow_id))

        # Increase the stock of the book by 1
        borrow.book.stock += 1

        # Set the returned flag to True
        borrow.returned = True

        # Save the changes
        borrow.save()

        # Get all borrowing objects from the database
        borrows = Borrowing.objects.select_related('student', 'book').all()

        # Create a context dictionary with the borrowing objects
        context = {'borrows': borrows,
                   'returned_borrows': borrows.filter(returned=True),
                   'current_borrows': borrows.filter(returned=False),
                   'overdue_borrows': borrows.filter(
                       returned=False, due_date__lt=date.today())}

        # Render the partial template for HTMX request
        return render(request, 'partials/partial_borrowing.html', context)
