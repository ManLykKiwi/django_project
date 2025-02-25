from django.urls import path 
from . import views

urlpatterns = [
    path('home/', views.home, name="home"),
    path('logout/', views.userLogout, name="logout"),
    path('register/', views.register, name="register"),
    path('decks/', views.listingDecks, name="listingDecks"),
    path('questionfinder/', views.questionFinder, name = "questionFinder"),
    path('attemptQuestion/', views.attemptingQuestion, name = "attemptingQuestion"),
    path('decks/create/', views.newDeck, name = "newDeck"),
    path('decks/<int:deck_id>/', views.insideOfDeck, name = "insideCurrentDeck"),
    path('api/gettingQuestions/', views.retreivingQuestions, name ="getQ"), 
    path('test/', views.test, name="test"),
    path('decks/createCard/<int:deck_id>', views.newFlashcard, name = "newFlashcard"),
    path('deletingcard/<int:flashcard_id>', views.deletingFlashcard, name = "deletingFlashcard"),
    path('decks/editCard/<int:flashcard_id>', views.updateFlashcard, name = "editingFlashcard"),
    path('decks/deleteDeck/<int:deck_id>', views.deletingDeck, name = "deletingDeck"),
]

