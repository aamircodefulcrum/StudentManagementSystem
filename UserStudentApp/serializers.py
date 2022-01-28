from rest_framework import serializers
from .models import Student, CustomUser, Course, Image


class UserSerializer(serializers.HyperlinkedModelSerializer):
    students = serializers.HyperlinkedRelatedField(many = True, view_name = 'student-detail', read_only = True)

    class Meta:
        model  = CustomUser
        fields = ['id', 'url', 'username', 'email', 'contact_num', 'age', 'students', 'profile_pic', 'images']


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source = 'owner.name')

    class Meta:
        model  = Student
        fields = ['id', 'url', 'owner', 'name', 'age', 'city', 'is_activated', 'courses']


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    students = serializers.HyperlinkedIdentityField(many = True, view_name = 'student-detail', read_only = True)

    class Meta:
        model  = Course
        fields = ['id', 'url', 'name', 'students']


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model  = Image
        fields = ['id', 'other_pics', 'images'] 