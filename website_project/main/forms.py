from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm    #Prebuilt django-forms
from django.contrib.auth.models import User      #Importing user 'settings' e.g. Authentication, Permission and Details
from . models import Deck, Flashcard
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError

class rForm(UserCreationForm):
    #Adding attributes that are not found in the UserCreationForm class. 
    email = forms.EmailField(required=True)
    classnumber = forms.IntegerField(required=True)
    username = forms.CharField(required=True, validators=[MinLengthValidator(5, message = "Username must be ⩾ 5 Characters")])

    class Meta:
        model = User    
        fields = ["username", "email", "classnumber", "password1", "password2"] #specifying the fields that are going to be displayed to the user 


    
    def clean_classnumber(self):
        """
        -used to add an extra validation to the class number, it should be a number and only 4 digits
        -clean() methods allows us to retrieve data that has been submitted into a form
        """

        grabbingClassnumber = self.cleaned_data.get("classnumber") #retrieving class number from submitted form 
        
        if len(str(grabbingClassnumber)) !=4:
            raise ValidationError("Class number should have 4 digits")


    def clean_password1(self):
        """
        used to add an extra validation to the password, it should contain atleast one special character 
        """

        grabbingPass = self.cleaned_data.get("password1") #retrieving password number from submitted form
        requiredCharSet = "!@#$%^&*(),.?\":{}|<>"

        for specialChar in grabbingPass:
            if specialChar in requiredCharSet:
                print("Password meets requirements!")
                return grabbingPass

        raise ValidationError("Please ensure password contains atleast one special character!")
        
    



class deckForm(ModelForm):
    """
    form that allows users to create new decks
    """

    class Meta:
        model = Deck
        fields = ['topic', 'description']

class flashcardForm(ModelForm):
    """
    form that allows users to create flashcards
    """
    class Meta:
        model = Flashcard
        fields = ['question','answer']