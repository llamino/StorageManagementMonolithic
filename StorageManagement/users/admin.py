from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, Address
from .models import CustomLogEntry

@admin.register(CustomLogEntry)
class CustomLogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    search_fields = ('object_repr', 'change_message')
# Define an Inline for Address
class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    fields = ('province', 'city', 'street', 'alley', 'house_number')


# Define a custom UserAdmin
class UserAdmin(BaseUserAdmin):
    # Fields to be displayed in the admin list view
    list_display = ('email', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'phone_number')
    ordering = ('email',)

    # Fields in detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('phone_number',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'create_date', 'update_date')}),
    )

    # Fields displayed when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # def has_delete_permission(self, request, obj=None):
    #     return True  # اجازه حذف را فعال می‌کند

    # Readonly fields
    readonly_fields = ('create_date', 'update_date')

    # Add AddressInline to UserAdmin
    inlines = [AddressInline]

# Register the custom User model
admin.site.register(User, UserAdmin)

# Register the Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name')
    search_fields = ('user__email', 'first_name', 'last_name')
    ordering = ('user__email',)


# Register the Address model (Optional: for direct access in admin panel)
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'province', 'city', 'street', 'alley', 'house_number')
    search_fields = ('user__email', 'province', 'city', 'street')
    ordering = ('user__email',)
    verbose_name_plural = 'addresses'
