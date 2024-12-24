from rest_framework import serializers
from .models import User, Profile, Address
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'phone_number': {'required': True},
        }

    def validate(self, data):
        """Ensure password and confirm_password match."""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def validate_email(self, value):
        """Ensure email uniqueness and validity."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        """Validate phone number format (e.g., must be numeric and 11 digits)."""
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits long.")
        return value

    def create(self, validated_data):
        # Remove confirm_password from validated_data
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'is_active', 'profile', 'created_date', 'updated_date']
        read_only_fields = ['is_active', 'created_date', 'updated_date']

    def update(self, instance, validated_data):
        # استخراج داده‌های پروفایل
        profile_data = validated_data.pop('profile', None)

        # به‌روزرسانی مدل User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # به‌روزرسانی مدل Profile
        if profile_data:
            profile, created = Profile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


