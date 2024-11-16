import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from library.models import Book, Category
import random


class Command(BaseCommand):
    help = 'Fetch book data from API and store it in the database'

    def handle(self, *args, **options):
        # Example API URL
        subjects = [
            "Quantum Mechanics",
            "Renaissance Art",
            "Organic Chemistry",
            "Ancient Civilizations",
            "Machine Learning",
            "Philosophy of Mind",
            "Climate Change",
            "Modern Architecture",
            "Classical Literature",
            "Artificial Intelligence Ethics",
            "Neuroscience",
            "Astronomy",
            "Ethical Hacking",
            "Cognitive Psychology",
            "World War II History",
            "Digital Marketing",
            "Biotechnology",
            "Astrophysics",
            "Cultural Anthropology",
            "Environmental Science",
            "Linguistics",
            "Game Theory",
            "Sustainable Development",
            "Feminist Theory",
            "Robotics",
            "Data Visualization",
            "Classical Music Theory",
            "Urban Planning",
            "Cybersecurity",
            "Sports Psychology",
            "Visual Communication",
            "Social Media Trends",
            "Film Studies",
            "Mythology",
            "Microeconomics",
            "Global Health",
            "Political Theory",
            "Fashion Design",
            "Cryptocurrency",
            "Philosophy of Science",
            "Rural Sociology",
            "Marine Biology",
            "Theology",
            "Behavioral Economics",
            "Genetics",
            "History of Philosophy",
            "Artificial Neural Networks",
            "Creative Writing",
            "Virtual Reality Technologies",
            "Folklore Studies",
            "Public Health"
        ]

        for subject in subjects:
            try:
                stock = random.randint(1, 100)
                api_url = f'https://www.googleapis.com/books/v1/volumes?q={
                    subject}'
                response = requests.get(api_url)

                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(
                        'Failed to fetch data from API'))
                    return

                data = response.json()
                items = data.get('items', [])

                for item in items:
                    volume_info = item['volumeInfo']
                    title = volume_info.get('title')
                    author = volume_info.get('authors', [])[
                        0] if volume_info.get('authors') else 'Unknown'
                    publisher = volume_info.get('publisher', 'Unknown')
                    published_date_str = volume_info.get('publishedDate', None)

                    # Handle date formatting
                    published_date = None
                    if published_date_str:
                        if len(published_date_str) == 7:  # Format "YYYY-MM"
                            published_date_str += '-01'  # Append day
                        published_date = parse_date(published_date_str)

                    description = volume_info.get('description', '')

                    # Safely get ISBN identifiers
                    industry_identifiers = volume_info.get(
                        'industryIdentifiers', [])
                    isbn_10 = ''
                    isbn_13 = ''
                    for identifier in industry_identifiers:
                        if identifier.get('type') == 'ISBN_10':
                            isbn_10 = identifier.get('identifier', '')
                        elif identifier.get('type') == 'ISBN_13':
                            isbn_13 = identifier.get('identifier', '')

                    page_count = volume_info.get('pageCount', 0)
                    language = volume_info.get('language', 'en')
                    maturity_rating = volume_info.get(
                        'maturityRating', 'NOT_MATURE')
                    thumbnail = volume_info.get(
                        'imageLinks', {}).get('thumbnail', '')

                    # Create or get book instance
                    book, created = Book.objects.update_or_create(
                        isbn_10=isbn_10,
                        defaults={
                            'title': title,
                            'author': author,
                            'publisher': publisher,
                            'published_date': published_date,
                            'description': description,
                            'isbn_13': isbn_13,
                            'page_count': page_count,
                            'language': language,
                            'maturity_rating': maturity_rating,
                            'thumbnail': thumbnail,
                            'stock': stock
                        }
                    )

                    # Handle categories (tags)
                    categories = volume_info.get('categories', [])
                    for category_name in categories:
                        category, _ = Category.objects.get_or_create(
                            name=category_name)
                        book.categories.add(category)

                    self.stdout.write(self.style.SUCCESS(
                        f'Book "{title}" processed.'))

                self.stdout.write(self.style.SUCCESS(
                    'All books have been fetched and stored.'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Failed to fetch data from API: {e}'))
                continue
