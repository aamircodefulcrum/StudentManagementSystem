from django.db import models    
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('User must have an Email')
        if not username:
            raise ValueError('User must have an Username')
        user = self.model(
            email = self.normalize_email(email),
            username = username,
        )
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self,email,username,password):
        user = self.create_user(
            email    = self.normalize_email(email),
            username = username,
            password = password,
        )
        user.is_admin     = True
        user.is_active    = True
        user.is_superuser = True
        user.save(using = self._db)
        return user

def get_picture_path(self, filename):
    return f'profile_pics/{self.pk}/{"profile_img.jpg"}'

def get_other_pictures(self, filename):
    return f'other_pics/{self.pk}/{"pic_name.jpg"}'

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email        = models.EmailField(max_length = 32, unique = True)
    first_name   = models.CharField(max_length = 16, null = True)
    last_name    = models.CharField(max_length = 16, null = True)
    username     = models.CharField(max_length = 16, unique = True)
    contact_num  = models.CharField(verbose_name = 'Contact Number' , max_length = 11, null = True)
    age          = models.PositiveIntegerField(default = 15)
    date_joined  = models.DateTimeField(verbose_name = 'date joined', auto_now_add = True) 
    last_login   = models.DateTimeField(verbose_name = 'last login', auto_now = True) 
    is_admin     = models.BooleanField(default = False)
    is_active    = models.BooleanField(default = False)
    is_staff     = models.BooleanField(default = False)
    is_superuser = models.BooleanField(default = False)
    profile_pic  = models.ImageField(null= True, blank= True, upload_to= get_picture_path, default= "default.jpg") 


    objects = CustomManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
 
class Student(models.Model):
    name         = models.CharField(max_length = 20)
    age          = models.PositiveIntegerField(default = 5)
    city         = models.CharField(max_length = 50)
    is_activated = models.BooleanField(default = True)    
    owner        = models.ForeignKey('CustomUser', related_name= 'student', on_delete= models.CASCADE)

    def __str__(self):
        return self.name

class Course(models.Model):
    course_name = models.CharField(max_length= 16)
    students    = models.ManyToManyField(Student, related_name= 'courses')

    def __str__(self):
        return self.course_name

class Image(models.Model):
    other_pics = models.ImageField(null= True, blank= True, upload_to= get_other_pictures, default= "default.jpg")
    images     = models.ForeignKey(CustomUser, on_delete= models.CASCADE, related_name= 'images', null= True)

@receiver(post_save, sender= settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance= None, created= False, **kwargs):
    if created:
        Token.objects.create(user= instance)