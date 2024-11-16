from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('borrowing/', views.borrowing, name='borrowing'),
    path('borrowing/<int:id>', views.borrowing, name='borrowing'),
    path('filter/', views.filter_by_category, name='filter'),
    path('success_borrowed/<int:borrow_id>/',
         views.success_borrowed, name='success_borrowed'),
    path('return_book/<int:borrow_id>/',
         views.return_book, name='return_book'),

]
