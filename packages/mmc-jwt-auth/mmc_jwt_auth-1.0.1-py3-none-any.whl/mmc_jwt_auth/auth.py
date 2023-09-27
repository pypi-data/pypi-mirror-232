from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Authenticate the token using the parent class
        user = super().authenticate(request)

        if user is not None:
            # Extract user data from the token payload
            user_data = user[1].get('user_data')

            # Attach user data to the request for use in views
            request.user_data = user_data

        return user
