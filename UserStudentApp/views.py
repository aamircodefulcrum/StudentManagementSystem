from .models import Student, CustomUser, Course, UserImage
from .serializers import (StudentSerializer, UserSerializer, CourseSerializer, ImageSerializer,
                          ChangePasswordSerializer, PasswordResetConfirmSerializer,
                          PasswordResetSerializer)
from django.contrib.auth import authenticate
from rest_framework import permissions, viewsets, status, generics
from .permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        request_user = self.request.user
        name = self.request.query_params.get('name')
        
        if request_user.is_superuser:
            queryset = CustomUser.objects.all()
            if name:
                queryset = CustomUser.objects.filter(username=name)
        else:
            queryset = CustomUser.objects.filter(email=request_user)

        return queryset
  

class StudentViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]
    serializer_class = StudentSerializer

    def get_queryset(self, *args, **kwargs):
        request_user = self.request.user
        if request_user.is_superuser:
            names = self.request.query_params.getlist('name')
            is_activated = self.request.query_params.get('is_activated')
            if names:
                queryset = Student.objects.filter(Q(name__in=names) | Q(owner__username__in=names))
            elif is_activated:
                queryset = Student.objects.filter(is_activated=is_activated)
            else:
                queryset = Student.objects.all()
        else:
            queryset = Student.objects.filter(owner=request_user) 
            name = self.request.query_params.get('name')
            age = self.request.query_params.get('age')
            is_activated = self.request.query_params.get('is_activated')
            if name:
                queryset = queryset.filter(name=name)
            elif age:
                queryset = queryset.filter(age=age)
            elif is_activated:
                queryset = queryset.filter(is_activated=is_activated)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_activated:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        request_user = self.request.user
        data = request.data
        instance = self.get_object()
        if request_user.is_superuser:
            instance = self.get_object()
            instance.name = data.get("name", instance.name)
            instance.age = data.get("age", instance.age)
            instance.city = data.get("city", instance.city)      
            instance.is_activated = False if data.get('is_activated') is None or data.get('is_activated') == 0 \
                                             or data.get('is_activated') == "0" else True
            instance.save()
            return Response({'status': "Content Modified"}, status=status.HTTP_200_OK)
        else:  
            is_active = instance.is_activated 
            if is_active:
                return Response({'status': "Forbidden Request"}, status=status.HTTP_403_FORBIDDEN)
            else:
                instance.name = data.get("name", instance.name)
                instance.age = data.get("age", instance.age)
                instance.city = data.get("city", instance.city)
                instance.is_activated = bool(data.get('is_activated', instance.is_activated))
                instance.save()
                return Response({'status': "Content Modified"}, status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = UserImage.objects.filter(user__email=self.request.user)
        return queryset


class LoginView(generics.GenericAPIView):
    def post(self, request):
        data = request.data
        email = data['username']
        password = data["password"]
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                if user.is_blocked:
                    return Response({
                        'Message': 'Your account has been blocked because your password has been expired.'\
                        'An email has been sent to your account please check it.'
                        })
                else:
                    user = authenticate(email=email, password=password)
                    return Response({'token': user.auth_token.key})
            else:
                return Response({'Message': 'Incorrect Password Entered'})
        except CustomUser.DoesNotExist as e:
            return Response({'Message': "Email does not exists."})


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data.get('new_password') == serializer.data.get('confirm_password'):
                self.object.set_password(serializer.data.get("new_password"))

                self.object.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully.',
                }
            else:
                response = {
                    'status': 'unsuccessful',
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'New password does not match.',
                }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.CreateAPIView):
    serializer_class = PasswordResetSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.data.get('email')
            try:
                user = CustomUser.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                subject = 'Password Reset Notification'
                link = 'localhost:8000/reset/' + uid + '/' + token
                message = "Use the following link to change your password.\n"+link
                send_mail(subject, message, 'admin@django.com', ['itsrealboy1@gmail.com'])
                return Response({'Message': 'Email has been sent to your account please check it.'})
            except CustomUser.DoesNotExist as e:
                return Response({'Message': 'Email Does not exists.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'Message': 'Invalid Data Entered'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.UpdateAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if serializer.data.get('new_password') == serializer.data.get('confirm_password'):
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully.',
                }
            else:
                response = {
                    'status': 'unsuccessful',
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Confirm password does not match.',
                }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
