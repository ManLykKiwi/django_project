from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm

class PastQuestions(models.Model): #creating a table for flashcard decks in main db
    question = models.CharField(max_length = 20)
    answer = models.CharField(max_length = 20)
    subject = models.CharField(max_length = 10)
    difficulty = models.CharField(max_length = 2)
    examboard = models.CharField(max_length = 10)
    topic = models.CharField(max_length = 20)
    timereq = models.CharField(max_length = 20)
    marks = models.CharField(max_length = 20)


class Deck(models.Model): #creating a table for flashcard decks in main db
     #topic and description allow users to name their decks as needed
     topic = models.CharField(max_length = 20)
     description = models.CharField(max_length = 20)
     user = models.ForeignKey(User, on_delete = models.CASCADE)
     
     
    

class Flashcard(models.Model): #creates a table for Flashcards in the main db.
    question = models.CharField(max_length= 20)
    answer = models.CharField(max_length = 20)
    user = models.ForeignKey(User, on_delete = models.CASCADE) #Custom Flashcards for specific Users
    deck = models.ForeignKey(Deck, on_delete = models.CASCADE)

    #SM-2 Variables
    successfulRepetitions = models.PositiveIntegerField(default = 0) 
    interval = models.PositiveIntegerField(default = 0)
    ef = models.FloatField(default = 2.5) #should never drop below 1.3
    nextReview = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.question
           
    
    def reviewingFlashcards(self, receivedGrade):
        """
            (SM-2) updating flashcard attributes in relation to review times based on user input
        """
    
        mappingGrades = {"B": 1, "G": 2, "E": 3, "P": 4}
        receivedGrade = mappingGrades.get(receivedGrade)    #converting string input into integer
        
        if receivedGrade == 1:           
            self.successfulRepetitions = 0 
            self.interval = 1
        else:
            self.successfulRepetitions+=1 

            if receivedGrade == 2:
                self.interval = 2 
            
            elif receivedGrade == 3:
                self.interval = 3

            else:
            
                #Calculating the next interval at which the flashcard should be shown to the user, making sure that it does not drop below 1.
                self.interval = round(self.interval * self.ef)
                if self.interval < 1:
                    self.interval = 1 

            #Calculating a new easiness factor for a particular Flashcard based on the user's response
            self.ef = (self.ef + (0.1 - (5 - receivedGrade) * (0.08 + (5 - receivedGrade) * 0.02))) 
            if self.ef < 1.3: #ensuring easiness factor does not drop below 1.3 during calculations 
                self.ef = 1.3 


        #Setting up the next review date for a particular Flashcard
        currentDate = timezone.now()
        self.nextReview = currentDate + timedelta(minutes = self.interval)
        self.save() 


    #Method used to output Flashcard details to User
    #REMOVE IF NOT NEEDED
    def displayingDetails(self):
        print(f"Flashcard: {self.question}, Next Review: {self.nextReview}")





            






        





        



