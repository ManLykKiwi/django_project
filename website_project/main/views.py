from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.urls import reverse
from django.http import HttpResponse
from . forms import rForm, deckForm, flashcardForm
from . models import Flashcard, Deck, PastQuestions, UserPreferences
from django.contrib.auth.decorators import login_required  
from django.contrib import messages
import random 
from django.core import serializers
from django.http import JsonResponse
import json
import os 
from django.conf import settings
from django.utils.translation import gettext as _, get_language

@login_required(login_url="/login") #telling decorator where to redirect us if we are not signed in. 
def home(request):
    """
    Returns the main page when a user first clicks on website link
    """

    return render(request, 'main/home.html')

def userLogout(request):
    """
    Handles user logouts by using login() method from inbuilt libraries - once complete they are 
    returned to the login page
    """
    #user is logged out and redirected to the logout HTML page
    logout(request)
    return render(request, 'registration/login.html') 

def register(request):
    """
    -a prebuilt form in forms.py is loaded onto the user page by passing the form variable as a template variable which can be used in the register template
    -if the user meets the requirements for the form, they are logged into the system and redirected to the home page
    """

    #allows users to create an account on the system, if this process is successful user is redirected to the home page
    if request.method == 'POST':
        form = rForm(request.POST)  #validating data 
        if form.is_valid():
            user = form.save() #saving the user
            login(request, user) 
            return redirect(reverse('home'))
    else:
        form = rForm()  #returning empty form if user does not pass required details
    return render(request, 'registration/register.html', {"form": form })   #passing custom form to register page



#@login_required(login_url="/login")
def newDeck(request):
    """
    -used to recieve input for decks by comparing it to a predefined deck form defined in forms.py
    -if its successful, it is saved in the database so they can access it
    -this custom form is passed to the deckcreation template as a template variable via a dict
    """


    #fetching the current deck user wants to access
    if request.method == 'POST':
        form = deckForm(request.POST)
        if form.is_valid():
            currentDeck = form.save(commit = False) #doing this allows the program to assign a particular user to the new deck
            currentDeck.user = request.user #ensuring that decks and users have a 1-1 relationship
            currentDeck.save()
            return redirect(reverse('listingDecks')) 
        
    else:
        form = deckForm()

    return render(request, 'main/subsystem/deckcreation.html', {'form': form})

def newFlashcard(request, deck_id):

    """
    -used to add a new flashcard into a particular deck
    -checks if flashcard exists already, if it does it is not stored in the system - if not it is stored in the database
    """


    #fetching the current deck user wants to access
    currentDeck = Deck.objects.get(id = deck_id)
    if request.method == "POST":
        form = flashcardForm(request.POST)
        if form.is_valid():

            currentCard = form.save(commit = False)
            #Fetching the data that the user has just input
            inputQuestion = form.cleaned_data.get('question') 
            inputAnswer = form.cleaned_data.get('answer')
            displayingDecks = Deck.objects.filter(user = request.user)
            
            searchingDB = Flashcard.objects.filter(question = inputQuestion, answer = inputAnswer).exists()  #querying database to see if card details already exists

            if searchingDB:
                messages.error(request, "Card already exists!")
                return render(request, 'main/subsystem/cardcreation.html')
            else:
                messages.success(request, "Card has been added!")
                currentCard.user = request.user #ensuring that flashcards and users have a 1-1 relationship 
                currentCard.deck = currentDeck 
                currentCard.save()
            
                return render(request, 'main/subsystem/decks.html', {"displayingDecks": displayingDecks}) 
    else:
        form = flashcardForm()
    
    return render(request, "main/subsystem/cardcreation.html", {'form': form})

#@login_required(login_url="/login")
def listingDecks(request):
    """
    -used to display all flashcard decks that belong to a particular user
    -stores this in a variable and passes it as a template variable so that it can be displayed in a HTML format. 
    """

    #listing all decks that have been created by a particular user

    displayingDecks = Deck.objects.filter(user = request.user)  #ONLY retrieves decks for a particular user
    loggedInUser = request.user  #Accessing User model object
    return render(request, "main/subsystem/decks.html", {"displayingDecks": displayingDecks, "user": loggedInUser})
    


def insideOfDeck(request, deck_id):
    """
    -used to retrieve all flashcards in a deck that has just been accessed by a user
    -pay special attention to lines 139-142, without this a 'NULL VALUE constraint' value would occur, especially without currentFlashcard as this would mean that 
    I am trying to display a value that doesn't exist in a HTML Template
    """
    #displays all the flashcards within a particular deck
    displayingDeck = get_object_or_404(Deck, id = deck_id) 
    loggedInUser = request.user
    displayingFlashcards = displayingDeck.flashcard_set.filter(user = request.user) #Using reverse relationships to access all flashcards within a particular deck to a particular user
    
    #selecting a flashcard if there are any
    if displayingFlashcards:  
        currentFlashcard = random.choice(displayingFlashcards)
    else:
        currentFlashcard = None

    if request.method == "POST":  
        receivedGrade = request.POST.get("Grade")
        currentFlashcard.reviewingFlashcards(receivedGrade) #passing flashcard so that new interval for repetition can be calculated

    #random quotes to present to user
    quotes = ['Keep Going!', 'You got this!', 'Self-discipline is key!', 'Fail, Learn, Grow ']
    choosingQuote = random.choice(quotes)
    

   

    return render(request, 'main/subsystem/indeck.html', {"displayingDecks": displayingDeck, 
                                                          "displayingFlashcards": displayingFlashcards, 
                                                          "currentFlashcard": currentFlashcard,
                                                          "randomQuote": choosingQuote})

def deletingFlashcard(request, flashcard_id):
    """
    Used to delete flashcards for a particular user
    """
    retrievingCard = Flashcard.objects.filter(id = flashcard_id).delete()
    return redirect(reverse('listingDecks'))

def updateFlashcard(request, flashcard_id):
    """
    used to retrieve data for an existing flashcard in the database, change its data and store it back in the database permanently
    """
    editCard = get_object_or_404(Flashcard, id = flashcard_id) #fetching the current flashcard from DB
    if request.method == "POST":
        form = flashcardForm(request.POST, instance = editCard) #returning an instance of the model form and inputting new data

        if form.is_valid():
            form.save()
            return redirect(reverse('listingDecks'))
        
    else:
        form = flashcardForm(instance = editCard) #if no changes are made, the old values are displayed 
    return render(request, 'main/subsystem/editcard.html', {"editFlashcard": editCard, "form": form})

def deletingDeck(request, deck_id):
    """
    similar to deleteFlashcard but deletes a flashcard deck instead
    """
    retrievingDeck = Deck.objects.filter(id = deck_id).delete()
    return redirect(reverse('listingDecks'))


def questionFinder(request):
    """
    returns the question finder HTML Template page to the user
    """
    return render(request, 'main/subsystem2/questionfinder.html')
    
def retreivingQuestions(request):
   """
   -Recives JSON object from questionfinder.html template
   -Uses this to extract required data from database and pass it back to the questionfinder.html template so that it can be displayed to the user
   """
   if request.method == "POST":
       requestDict = json.loads(request.body) #converting JSON object into python dict
       #retrieving inputs
       subjectInput = requestDict.get('subject')
       difficultyInput = requestDict.get('difficulty')
       examboardInput = requestDict.get('examboard')
       topicInput = requestDict.get('topic')
       requiredQuestions = PastQuestions.objects.filter(subject = subjectInput, difficulty = difficultyInput, examboard = examboardInput, topic = topicInput).values("id","question", "answer", "timereq", "marks", "difficulty")
       return JsonResponse(list(requiredQuestions), safe = False) #converting queryset into JSON serializable format 
       #filteredQuestions = subjectInput

            
def attemptingQuestion(request):
    """
    -works in tandem with retrievingQuestions, when a user wants to answer a question the details of the current question are fetched from the database
    -these are then sent to the HTML Template, i.e. attemptQuestion, in charge of handling the revealing of these extracted details
    """
    if request.method == "POST":
        fetchingID = request.POST.get("currentQuestionID") #grabbing question ID from form
        #fetching all required data for pastpaper questions 
        fetchingQuestion = PastQuestions.objects.get(id=fetchingID) 
        questionField = fetchingQuestion.question
        answerField = fetchingQuestion.answer
        marksField = fetchingQuestion.marks
        return render(request, 'main/subsystem2/attemptQuestion.html', {"question": questionField, "answer": answerField, "marks": marksField})
    














def test(request):
    return render(request, 'main/base.html')
