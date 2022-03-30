from rest_framework import serializers
from .models import Student, CustomUser, Course, UserImage


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserImage
        fields = ['image']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    students = serializers.HyperlinkedRelatedField(many=True, view_name='student-detail', read_only=True)
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'contact_num', 'age', 'students', 'profile_pic', 'images']


class CourseNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name']


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    assigned_courses = CourseNameSerializer(many=True, source='courses', read_only=True)
    courses = serializers.PrimaryKeyRelatedField(many=True, write_only=True,
                                                 queryset=Course.objects.all())

    class Meta:
        model = Student
        fields = ['id', 'owner', 'name', 'age', 'city', 'is_activated', 'assigned_courses', 'profile_pic', 'courses']

    def create(self, validated_data):
        courses = validated_data.pop("courses", None)
        student = Student.objects.create(**validated_data)
        if courses:
            for course in courses:
                course.students.add(student)
        return student


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    students = serializers.HyperlinkedIdentityField(many=True, view_name='student-detail')

    class Meta:
        model = Course
        fields = ['id', 'name', 'students']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
