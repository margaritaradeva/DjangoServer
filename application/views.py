from django.http import HttpResponse
from django.db import IntegrityError
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import Throttled, ValidationError, NotFound
from django.db.utils import OperationalError
from collections import defaultdict
import datetime
from datetime import timedelta
from django.utils import timezone
import logging

from .models import CustomUser, get_user_by_email, UserActivity
from .serializers import CustomUserSerializer, UserActivitySerializer

# Setup logging
logger = logging.getLogger("application")
logger.debug("This is a debug message")


def home_view(request):
    """
    Simple home view, created to test urls.
    """
    return HttpResponse("Welcome to the home page!")


class SignUp(APIView):
    """
    API view for user registration. Handles user creation with JWT token generation.
    This endpoint expects data for creating a new user account-first and last name, email, password.
    It validates the data, creates a user, and generates JWT tokens for authentication

    Methods:
        post: Receives user data, validates, creates the user and returns JWT tokens.
    I
    """

    def post(self, request):
        """
        Handle POST requests  to register a new user.

        Args:
            request (HttpsRequest): The request object cointaining the user credentials data

        Returns:
            Response: A django rest response object with the newly created user data and tokens or error message

        This method:
            -Takes user data from the request
            -Validates the data using the CustomUserSerializer
            -If the validation fails it returns an http 400 bad request
            -If validation passes it saves the user in the database
            -creates a refresh and access token using django rest
            -returns a response with the user details and tokens if successful
            -handles already existing users - http 409 conflict
            -additionally it checks for any other validation errors (in the serializer)

        """
        serializer = CustomUserSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                refresh_token = RefreshToken.for_user(user)
                access_token = refresh_token.access_token

                data = {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "refresh": str(refresh_token),
                    "access": str(access_token),
                }
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"detail": "Password does not meet the complexity requirements"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except DRFValidationError as e:
            return Response(e.detail, status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            # Handle the unique constraint error
            return Response(
                {"detail": "A user with that email already exists."},
                status=status.HTTP_409_CONFLICT,
            )


class SignIn(APIView):
    """
    API view for authentication. This view handles the login process, verifies user credentials,
    and provides JWT tokens.
    """

    def post(self, request):
        """
        Authenticate a user based on email and password and return jwt access and refresh tokens

        Args:
            request (HttpRequest): The request object contaiing the user's credentials

        Returns:
                Response: a django rest response object with jwt tokens and user fata if authentication is successful, otherwise raises Authentication failed exception
        """
        try:
            email = request.data["email"]
            password = request.data["password"]

            user = get_user_by_email(email=email)
            # Invalid credentials for both cases bc we dont wanna tell an attacker which one is wrong
            if user is None:
                raise exceptions.AuthenticationFailed("Invalid credentials")
            if not user.check_password(raw_password=password):
                raise exceptions.AuthenticationFailed("Invalid credentials")
            # Generate access and refresh tokens from JWT

            refresh_token = RefreshToken.for_user(user)
            access = refresh_token.access_token
            response = Response()
            serializer = CustomUserSerializer(user)
            response.data = {
                "refresh": str(refresh_token),
                "access": str(access),
                "user": serializer.data,
            }
            response.status_code = status.HTTP_200_OK
            return response
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Reuthenticate(APIView):
    """
    API view for reauthenticating users, used in the frontend application to confirm user credentials when requesting to reset parent PIN
    """

    def post(self, request):
        """
        Reauthenticate a user to verify their credentials while still logged in

        Args:
            request (HttpRequest): The request object contaiing the user's credentials

        Returns:
                Response: a django rest response object with http 200 ok status if user reauthentication is successful and a raised exception otherwise

        """
        try:
            email = request.data["email"]
            password = request.data["password"]
            user = get_user_by_email(email=email)

            if user is None or not user.check_password(raw_password=password):
                raise exceptions.AuthenticationFailed("Invalid credentials")
            if not user.check_password(raw_password=password):
                raise exceptions.AuthenticationFailed("Invalid credentials")

            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class isSignedIn(APIView):
    """
    API view to check if the current user session is valid and to return user's details. This view
    ensures that the user is authenticated via jwt tokens

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """

        Responds with the serizlized data of the authenticated user. The user is taken directly from request.user
        which is guaranteed to be authenticated due to  the isAuthenticated permission

        Args:
            request (HttpResponse): the request object automatically populated with the user by the authentication classes

        Returns:
            Response: django rest response object containing the user's info and a raiased exception otherwise
        """
        try:
            user = request.user
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class update_total_brush_time(APIView):
    """
    API View for updating the total brushing time of the authenticated user. This view increments
    the user's total brushing time based on the input provided in the request

    Methods:
        post: Updates the total rushing time for the authenticated user

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Increment the user's tota brush time y the amount specified in the request.

        Args:
            request (HttpRequest): The request oject containing 'added_time'-the number of seconds
            to add to the totaal brush time.

        Returns:
            Response: A Djanfo rest Framework Response oject with the updated user data or an error message.

        Note:
        -User's last_active_date is updated whenever added_time is updated

        """
        added_time = request.data.get("added_time", None)
        user = request.user

        if added_time is not None:
            serializer = CustomUserSerializer(
                user,
                data={"total_brush_time": user.total_brush_time + int(added_time)},
                partial=True,
            )
            try:
                user.total_brush_time += int(added_time)
                user.last_active_date = datetime.date.today()
                user.save()
                serializer = CustomUserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"detail": "added_time parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateStreak(APIView):
    """
    API View for updating the streak of a user based on their last active date. This view ensures that
    consecutive day logins are accurately tracked and the streak is updated appropriately.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
         Updates' the user's streak based on the last active date.

         Args:
            request (HttpRequest): the request object contaiing user data.

         Returns:
            Response: a django rest framework resonse object with the updated user data or error message

        Logic:
            - The method retrieves the user from the session.
            - It calculates whether the new login is consecutive to the last login date.
            - If the difference between the last active date and today's date is exactly one day,
            it increments the current streak.
            - If the difference is more than one day, it resets the streak to 1.
            - Finally, it updates the user's max streak and returns the serialized user data.

        """
        user = request.user
        try:
            today = datetime.date.today()
            
            # logger.debug(f"Updating streak for user: {user.email}, Last active date: {user.last_active_date}, Today: {today}")
            if user.last_active_date is not None and user.current_streak !=0:
                 if today - user.last_active_date == timedelta(days=1):
                     # 1 day so we up the streak
                     user.current_streak += 1
                     user.total_brushes_days +=1
                    
                 elif today - user.last_active_date > timedelta(days=1):
                     # longer than 1 day so reset the streak
                     user.current_streak  = 1
                     user.total_brushes_days +=1
            else:
                user.current_streak = 1
                user.total_brushes_days +=1

            

            if user.current_streak > user.max_streak:
                user.max_streak = user.current_streak
            user.last_active_date = today
            # user.save()
            # logger.debug(f"After update - Current streak: {user.current_streak}, Is PIN set: {user.is_pin_set}")
            
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e: 
            print(e) 
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST) 


class SetCharterName(APIView):
    """
    API view for setting or updating the character name of an authenticated user's profile.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Updates the character name for the authenticated user.

        Args:
            request (HttpRequest): The request object that contains the new character name in the 'new_name' key.

        Returns:
            Response: A Django REST Framework Response object with HTTP 200 OK if the update is successful, or
                      HTTP 400 Bad Request with error details if the update fails.

        Process:
        - Retrieves the 'new_name' from the request data.
        - If 'new_name' is provided, updates the user's character name and sets 'is_char_name_set' to True if it wasn't already.
        - Saves the user's updated information to the database.
        - Returns HTTP 200 OK on successful update or an error response if an exception occurs.
        """
        try:
            new_name = request.data.get("new_name")
            user = request.user
            user.character_name = new_name
            if user.is_char_name_set is False:
                user.is_char_name_set = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)


class UpdateActivity(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    """
    API view for updating user's daily activities and their streaks. The streak is determined based
    on whether the activity is performed consecutively in the morning or evening sessions. Activities
    are classified into morning (before 12:00 PM) and evening (after 12:00 PM) to track separate streaks.
    """

    def post(self, request):
        """
        Receives a POST request update users' activity streaks. It differentiates
        between morning and evening activities to maintain separate streaks for each.

        Returns:
            Response: A Response object from Django REST Framework containing the updated user data if successful,
                      or an error message with appropriate HTTP status code if an error occurs.
        """
        # Retrieve the user from the request
        user = request.user
        updated_streak = False
        today = datetime.date.today()
        if user is None: 
            return Response({'detail':'User not found'}, status=status.HTTP_404_NOT_FOUND)
        time_now = timezone.now()
        try:
            if time_now.hour < 12:
                # Morning activity
                if user.last_active_morning is not None and user.streak_morning !=0:
                    if time_now.date() - user.last_active_morning.date() == timedelta(days=1):
                        user.streak_morning += 1
                        updated_streak = True
                    elif time_now.date() - user.last_active_morning.date() > timedelta(days=1):
                        user.streak_morning = 1
                        updated_streak = True
                else: 
                    user.streak_morning = 1
                    updated_streak = True
                user.last_active_morning = time_now
                user.total_brushes_morning += 1
                user.total_brushes += 1
                user.percentage_morning = user.total_brushes_morning/user.total_brushes_days

                if user.streak_morning > user.max_streak_morning:
                    user.max_streak_morning = user.streak_morning

            else:
                if user.last_active_evening is not None and user.streak_evening !=0:
                    if time_now.date() - user.last_active_evening.date() == timedelta(days=1):
                        user.streak_evening += 1
                        updated_streak = True
                    elif time_now.date() - user.last_active_evening.date() > timedelta(days=1):
                        user.streak_evening = 1
                        updated_streak = True
                else: user.streak_evening = 1
                updated_streak = True
                user.last_active_evening = time_now
                user.total_brushes_evening += 1
                user.total_brushes += 1
                user.percentage_evening = user.total_brushes_evening/user.total_brushes_days
                if user.streak_evening > user.max_streak_evening:
                    user.max_streak_evening = user.streak_evening

            if updated_streak == True:
                time_now = timezone.now()
                
                
                if time_now.hour<12:
                    type='morning'
                else:
                    type='evening'

                
                new_activity = UserActivity(
                    user=user,
                    activity_date=today,
                    activity_time= time_now,
                    activity_type=type
                )
                new_activity.save()
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail':str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateLevel(APIView):
    """
    API view to increment a user's level based on a specified value.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Receives an integer to update the user's level and applies the update to the user's profile.

        Args:
            request (HttpRequest): The request object containing the amount to increase the user's level.

        Returns:
            Response: A Django REST Framework Response object with the updated user data or an error message.
        """
        update_level_by = request.data.get("update_level_by", None)
        user = request.user
        if update_level_by is not None:
            serializer = CustomUserSerializer(
                user,
                data={"current_level": user.current_level + int(update_level_by)},
                partial=True,
            )
        try:
            user.current_level += int(update_level_by)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateLevelXP(APIView):
    """
    API view to update the user's current experience points.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Receives an integer to update the user's current XP and applies the update to the user's profile.

        Args:
            request (HttpRequest): The request object containing the amount to update the user's XP.

        Returns:
            Response: A Django REST Framework Response object with the updated user data or an error message.
        """
        update_current_xp = request.data.get("current_level_xp", None)
        user = request.user
        if update_current_xp is not None:
            serializer = CustomUserSerializer(
                user, data={"current_level_xp": int(update_current_xp)}, partial=True
            )
        try:
            user.current_level_xp = int(update_current_xp)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {"detail": 'Invalid "current_level_xp" value. It must be an integer.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MiniShopPhoto(APIView):
    """
    API view for updating the user's profile image ID.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Updates the image ID for a user's profile based on the provided image ID.

        Args:
            request (HttpRequest): The request object containing the new image ID and user.

        Returns:
            Response: A DRF Response object with the updated user data or an error message.
        """
        update_image_id = request.data.get("image_id", None)
        user = request.user
        if update_image_id is not None:
            serializer = CustomUserSerializer(
                user, data={"image_id": int(update_image_id)}, partial=True
            )
        try:
            user.image_id = int(update_image_id)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {"detail": "Invalid image ID. It must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateLevelMaxXP(APIView):
    """
    API view for updating the maximum XP level for a user.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Updates the maximum level XP for a user based on the provided value.

        Args:
            request (HttpRequest): The request object containing the new maximum XP level and user.

        Returns:
            Response: A DRF Response object with the updated user data or an error message.
        """
        update_current_level_max = request.data.get("current_level_max_xp", None)
        user = request.user

        if update_current_level_max is not None:
            serializer = CustomUserSerializer(
                user,
                data={"current_level_max_xp": int(update_current_level_max)},
                partial=True,
            )

        try:
            user.current_level_max_xp = int(update_current_level_max)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {"detail": "Invalid XP value. It must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(e)  # For debugging purposes
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SignOut(APIView):
    """
    API view to handle user logout by invalidating the provided JWT refresh token.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Receives a POST request with a refresh token and attempts to blacklist it to log the user out.

        Args:
            request (HttpRequest): The request object containing the 'refresh' token.

        Returns:
            Response: A Django REST Framework Response object indicating the logout status.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            if token is None:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
            resp = Response()
            resp.data = {"message": "user logged out"}

            return Response(status=status.HTTP_200_OK)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class DeleteUser(APIView):
    """
    API view to delete the currently authenticated user's account.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetParentPin(APIView):
    """
    API view to set or update a parent PIN for the currently authenticated user.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Sets or updates a 6-digit parent PIN for the user.

        Args:
            request (HttpRequest): The request object containing the parent PIN.

        Returns:
            Response: A Django REST Framework Response object with a success message or an error message.
        """
        user = request.user
        pin = request.data.get("parent_pin")
        if not pin or not pin.isdigit() or len(pin) != 6:
            return Response(
                {"error": "The PIN mist be exactly 6 digits"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.parent_pin = pin
        user.is_pin_set = True
        user.save()
        return Response(
            {"message": "Parent PIN was set successfully."}, status=status.HTTP_200_OK
        )


class CheckParentPIN(APIView):
    """
    API view to check if the provided parent PIN matches the one stored for the authenticated user.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Validates the provided PIN against the user's stored parent PIN.
        """
        user = request.user
        input_pin = request.data.get("parent_pin")

        if user.parent_pin == input_pin:
            return Response(
                {"message": "The PIN is correct"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "The PIN is incorrect"}, status=status.HTTP_400_BAD_REQUEST
            )


class CheckIfPinIsSet(APIView):
    """
    API view to check if the authenticated user has a parent PIN set.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Checks if the current user has a parent PIN set and returns the status.
        """
        user = request.user
        return Response({"is_pin_set": user.is_pin_set}, status=status.HTTP_200_OK)


class UserActivities(APIView):
    """
    API view to retrieve and summarize the user's activities by day, indicating whether activities occurred
    in the morning, evening, or both.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        activities = UserActivity.objects.filter(user=user).values('activity_date', 'activity_type')

        grouped = defaultdict(set)
        for activity in activities:
            grouped[activity['activity_date']].add(activity['activity_type'])
        activity_pairs = []

        for date, type in grouped.items():
            if 'morning' in type and 'evening' in type:
                activity_pairs.append({'activity_date': date, 'activity_type': 'both'})
            else:
                activity_type = 'morning' if 'morning' in type else 'evening'
                activity_pairs.append({'activity_date': date, 'activity_type': activity_type})


        return Response(activity_pairs, status=status.HTTP_200_OK)
