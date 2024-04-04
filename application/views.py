from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import status, permissions
from django.http import HttpResponse
from .serializers import CustomUserSerializer, UserActivitySerializer
from django.db import IntegrityError
from datetime import timedelta
import datetime
from rest_framework.exceptions import ValidationError as DRFValidationError
#from rest_framework_simplejwt.token_blacklist import OutstandingToken, BlacklistedToken
from .managers import CustomUserManager
from .models import CustomUser, get_user_by_email, UserActivity
from django.utils import timezone
import logging

logger = logging.getLogger('application') 
logger.debug('This is a debug message')

def home_view(request):
    return HttpResponse("Welcome to the home page!")


class SignUp(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()

                refresh_token = RefreshToken.for_user(user)
                access_token = refresh_token.access_token

                data = {
                    'id':user.id,
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'email':user.email,
                    'refresh': str(refresh_token),
                    'access': str(access_token),
                }
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail':'Password does not meet the complexity requirements'},status=status.HTTP_403_FORBIDDEN)
        except DRFValidationError as e:
            return Response(e.detail, status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            # Handle the unique constraint error
            return Response({'detail': 'A user with that email already exists.'}, status=status.HTTP_409_CONFLICT)

class SignIn(APIView):
    def post(self, request):
        # not gonna return a dataclass object bc i want to
        # authenticate a user and store that session
        # inside a cookie
        email = request.data["email"]
        password = request.data["password"]

        user = get_user_by_email(email=email)
        # INvalid credentials for both cases bc we dont wanna tell an attacker which one is wrong
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
            'refresh': str(refresh_token),
            'access': str(access),
            'user': serializer.data
        }
        response.status_code = status.HTTP_200_OK
        return response
        # JWT token
class Reuthenticate(APIView):
    def post(self,request):
        email = request.data['email']
        password = request.data['password']
        user = get_user_by_email(email=email)

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid credentials")
        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid credentials")
        
        return Response(status=status.HTTP_200_OK)


class isSignedIn(APIView):
        # can only be used if the user is authenticated
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email")
        user = get_user_by_email(email=email)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class update_total_brush_time(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        added_time =request.data.get("added_time", None)
        email = request.data["email"]
        user = get_user_by_email(email=email)
       

        if added_time is not None:
            serializer = CustomUserSerializer(user, data={'total_brush_time':user.total_brush_time + int(added_time)}, partial=True)
            try:
                user.total_brush_time += int(added_time)
                user.last_active_date = datetime.date.today()
                # yesterday = datetime.datetime(2024, 4, 3)
                # yesterday_date = yesterday.date()
                # user.last_active_date = yesterday_date
                user.save()
                serializer = CustomUserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
class UpdateStreak(APIView):

    def post(self, request):
         email = request.data["email"]
         user = get_user_by_email(email=email)
         updated_streak = False
         try:
            today = datetime.date.today()
            # logger.debug(f"Updating streak for user: {user.email}, Last active date: {user.last_active_date}, Today: {today}")
            if user.last_active_date is not None and user.current_streak !=0:
                 if today - user.last_active_date == timedelta(days=1):
                     # 1 day so we up the streak
                     user.current_streak += 1
                     updated_streak=True
                    
                 elif today - user.last_active_date > timedelta(days=1):
                     # longer than 1 day so reset the streak
                     user.current_streak  = 1
                     updated_streak=True
            else:
                user.current_streak = 1
                updated_streak=True

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


class UpdateActivity(APIView):

    def post(sewlf, request):
        email = request.data.get("email")
        user = get_user_by_email(email=email)

        if user is None: 
            return Response({'detail':'User not found'}, status=status.HTTP_404_NOT_FOUND)
        time_now = timezone.now()
        try:
            if time_now.hour < 12:
                # Morning activity
                if user.last_active_morning is not None and user.streak_morning !=0:
                    if time_now.date() - user.last_active_morning.date() == timedelta(days=1):
                        user.streak_morning += 1
                    elif time_now.date() - user.last_active_morning.date() > timedelta(days=1):
                        user.streak_morning = 1
                else: 
                    user.streak_morning = 1
                user.last_active_morning = time_now
                user.total_brushes_morning += 1
                user.total_brushes += 1
                user.percentage_morning = user.total_brushes_morning/user.total_brushes
                if user.streak_morning > user.max_streak_morning:
                    user.max_streak_morning = user.streak_morning

            else:
                if user.last_active_evening is not None and user.streak_evening !=0:
                    if time_now.date() - user.last_active_evening.date() == timedelta(days=1):
                        user.streak_evening += 1
                    elif time_now.date() - user.last_active_evening.date() > timedelta(days=1):
                        user.streak_evening = 1
                else: user.streak_evening = 1
                user.last_active_evening = time_now
                user.total_brushes_evening += 1
                user.total_brushes += 1
                user.percentage_evening = user.total_brushes_evening/user.total_brushes
                if user.streak_evening > user.max_streak_evening:
                    user.max_streak_evening = user.streak_evening

            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail':str(e)}, status=status.HTTP_400_BAD_REQUEST)




class UpdateLevel(APIView):

    def post(self,request):
        update_level_by = request.data.get("update_level_by", None)
        email = request.data["email"]
        user = get_user_by_email(email=email)
        if update_level_by is not None:
            serializer = CustomUserSerializer(user, data={'current_level':user.current_level + int(update_level_by)}, partial=True)
        try:
            user.current_level += int(update_level_by)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class UpdateLevelXP(APIView):
    def post(self, request):
        update_current_xp = request.data.get("current_level_xp", None)
        email = request.data["email"]
        user = get_user_by_email(email=email)
        if update_current_xp is not None:
            serializer = CustomUserSerializer(user, data={'current_level_xp':int(update_current_xp)}, partial=True)
        try:
            user.current_level_xp = int(update_current_xp)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class MiniShopPhoto(APIView):
    def post(self, request):
        update_image_id = request.data.get('image_id', None)
        email = request.data["email"]
        user = get_user_by_email(email=email)
        if update_image_id is not None:
            serializer = CustomUserSerializer(user, data={'image_id': int(update_image_id)}, partial=True)
        try: 
            user.image_id = int(update_image_id)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
   

class UpdateLevelMaxXP(APIView):
    def post(self, request):
        update_current_level_max = request.data.get("current_level_max_xp", None)
        email = request.data["email"]
        user = get_user_by_email(email=email)

        if update_current_level_max is not None:
            serializer = CustomUserSerializer(user, data={'current_level_max_xp':int(update_current_level_max)}, partial=True)

        try:
            user.current_level_max_xp = int(update_current_level_max)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'detail':str(e)},status=status.HTTP_400_BAD_REQUEST)
        

class SignOut(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            if token is None:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            # token_delete = OutstandingToken.objects.get(token=token) 
            # token_delete.black()
            resp = Response()
            resp.data = {"message":"user logged out"}
           
            return Response(status=status.HTTP_200_OK)
        except KeyError:
         return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            print(e) 
            return Response(status=status.HTTP_400_BAD_REQUEST) 
        

class DeleteUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        # email = request.data["email"]

        # user = get_user_by_email(email=email)

        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SetParentPin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user=request.user
        pin = request.data.get("parent_pin")
        if not pin or not pin.isdigit() or len(pin) != 6:
            return Response({"error":"The PIN mist be exactly 6 digits"},status=status.HTTP_400_BAD_REQUEST)
        user.parent_pin = pin
        user.is_pin_set = True
        user.save()
        return Response({"message":"Parent PIN was set successfully."}, status=status.HTTP_200_OK)
    
class Statistics(APIView):
    def post(self, request):
        update_current_streak_by = request.data.get("update_current_streak_by", None)
        update_max_streak_by = request.data.get("update_max_streak_by", None)
        update_total_brushes_by = request.data.get("update_total_brushes_by", None)
        email = request.data["email"]
        user = get_user_by_email(email=email)
       
        try:
            user.current_streak += int(update_current_streak_by)
            user.max_streak += int(update_max_streak_by)
            user.total_brushes += int(update_total_brushes_by)
            user.save()
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CheckParentPIN(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user=request.user
        input_pin = request.data.get("parent_pin")

        if user.parent_pin == input_pin:
            return Response({"message":"The PIN is correct"},status=status.HTTP_200_OK)
        else:
            return Response({"message":"The PIN is incorrect"},status=status.HTTP_400_BAD_REQUEST)
        

class CheckIfPinIsSet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user=request.user
        return Response({"is_pin_set": user.is_pin_set}, status=status.HTTP_200_OK)
    

class UserActivities(APIView):

    def post(self,request):
        email = request.data["email"]
        user = get_user_by_email(email=email)
        activities = UserActivity.objects.filter(user=user)
        serializer = UserActivitySerializer(activities, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)