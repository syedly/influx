from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
# Create your models here.

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("email is required!")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user
    
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        #return self._create_user(email, password, **extra_fields)
        return self._create_user(
            email=email,
            name=extra_fields.get('name'),
            f_name=extra_fields.get('f_name'),
            l_name=extra_fields.get('l_name'),
            phone_num=extra_fields.get('phone_num'),
            profile_img=extra_fields.get('profile_img'),
            password=password,
            **extra_fields
        )
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True, unique=True, default='')
    name = models.CharField(max_length=50, null= False)
    f_name = models.CharField(max_length=50, null= False)
    l_name = models.CharField(max_length=50, null= False)
    phone_num = models.CharField(max_length=11, null= False)
    profile_img = models.ImageField(upload_to='myapp/images', blank=True, null=True)
    bio = models.CharField(max_length=50, default="hey there!")
    private_account = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.name


class Post(models.Model):
    post = models.ImageField(upload_to='posts')
    caption = models.CharField(max_length=250 ,blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(User, blank=True, related_name='liked_post')

    def __str__(self):
        return self.user.name
    
class Report(models.Model):
    email = models.EmailField()
    title = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name
    
class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.from_user.name} - {self.to_user.name}'
    
class Messages(models.Model):
    sender = models.ForeignKey(User, related_name='sender_messages', on_delete=models.CASCADE)
    recipient  = models.ForeignKey(User, related_name='recipient_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.name} - {self.recipient.name}'