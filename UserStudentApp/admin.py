from django.contrib import admin
from .models import Student, CustomUser, Course, UserImage
from django.contrib.auth.admin import UserAdmin

UserAdmin.fieldsets += ('Personal info', {'fields': ['contact_num', 'age', 'profile_pic']}),


class AdminUser(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin')
    search_fields = ('email', 'username')
    filter_horizontal = ()
    list_filter = ()
    fieldset = ()
    readonly_fields = ["date_joined", "last_login", 'is_staff']


admin.site.register(CustomUser, AdminUser)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(UserImage)
