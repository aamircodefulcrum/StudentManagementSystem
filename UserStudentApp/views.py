from .models import Student, CustomUser, Course, UserImage
from .serializers import StudentSerializer, UserSerializer, CourseSerializer, ImageSerializer
from rest_framework import permissions, viewsets, status
from .permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from django.db.models import Q


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
            queryset = Student.objects.all()
            names = self.request.query_params.getlist('name')
            if names:
                queryset = Student.objects.filter(Q(name__in=names) | Q(owner__username__in=names))
        else:
            queryset = Student.objects.filter(owner=request_user)
            name = self.request.query_params.get('name')
            age = self.request.query_params.get('age')
            if name and age:
                queryset = queryset.filter(Q(name=name) & Q(age=age))
            elif name:
                queryset = queryset.filter(name=name)
            elif age:
                queryset = queryset.filter(age=age)
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


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = UserImage.objects.filter(user__email=self.request.user)
        return queryset
  