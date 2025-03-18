from django.contrib.auth.backends import BaseBackend
from typing import Any
from django.contrib.auth.models import User

from api.models import Seller

class EmailBackend(BaseBackend):

    def authenticate(self, request, username = None, password = None):


        try:

            user = Seller.objects.get(email = username)

            print(user)

            if user.check_password(password):

                return user
            
            else:

                return None
            
        except:

            return None
    
    def get_user(self, user_id):
        
        try:
            return Seller.objects.get(pk = user_id)
        
        except Seller.DoesNotExist:
            return None
        


