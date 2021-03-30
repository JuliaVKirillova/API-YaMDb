from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')


    first_name = models.TextField(
            verbose_name = 'имя пользователя',
            null=True
        )
    last_name = models.TextField(
            verbose_name = 'фамилия пользователя',
            null=True
        )
    username = models.CharField(
            max_length=200,
            verbose_name = 'логин пользователя',
            unique=True,
            null=True
        )    
    email = models.EmailField(
            verbose_name = 'электронная почта',
            unique=True
        )
    bio = models.TextField(verbose_name='информация', null=True)
    role = models.CharField(
            max_length=10, 
            default=Role.USER,
            choices=Role.choices,
            verbose_name='роль пользователя'
        )
    confirmation_code = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return self.username    




""" Категории (типы) произведений """
class Category(models.Model):
    name = models.CharField(
            verbose_name = 'название категории',
            max_length=100,
            unique=True
            )
    slug = models.SlugField(null=True, unique=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name





""" Категории жанров """
class Genre(models.Model):
    name = models.CharField(
            max_length=100, 
            verbose_name = 'название категории'
        ) 
    slug = models.SlugField(null=True, unique=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name






""" Произведения, к которым пишут отзывы """
class Title(models.Model):
    name = models.CharField(
            max_length=100,
            verbose_name = 'название произведения')

    year = models.PositiveIntegerField(
        validators = [
            MinValueValidator(1800)
        ],
        verbose_name = 'год создания'
        )  
    description = models.TextField(
            null=True,
            verbose_name = 'описание'
        )  
    genre = models.ManyToManyField(
                Genre,
                related_name = 'titles',
                verbose_name='жанр'
                )
    category = models.ForeignKey(
                Category,
                related_name = 'titles',
                on_delete = models.SET_NULL,
                verbose_name='категория',
                null=True
                ) 
    rating = models.PositiveIntegerField(
        verbose_name = 'рейтинг',
        null=True
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name





""" Отзывы """
class Review(models.Model):
    text = models.TextField(verbose_name='отзыв')  
    author = models.ForeignKey(
                User, 
                on_delete=models.CASCADE,
                verbose_name='автор отзыва'
            )
    score = models.PositiveIntegerField(
            validators = [
                MinValueValidator(1),
                MaxValueValidator(10)
                ],
            verbose_name='оценка',
            )  
    title = models.ForeignKey(
            Title,
            on_delete=models.CASCADE,
            related_name = 'review',
            blank=True,
            null=True,
            verbose_name='произведение',
            )
    pub_date = models.DateTimeField(
            auto_now_add=True,
            verbose_name='дата публикации'
        )        

    class Meta:
        ordering = ['-pub_date']
        unique_together = ['title', 'author']

    def __str__(self):
        return self.text





""" Комментарии к отзывам """
class Comment(models.Model):
    text = models.TextField(verbose_name='текст комментария')
    author = models.ForeignKey(
            User, 
            on_delete=models.CASCADE,
            verbose_name = 'автор комментария'
            )
    review = models.ForeignKey(
            Review, 
            on_delete=models.CASCADE,
            related_name='comments',
            verbose_name='отзыв',
            null=True
            )
    pub_date = models.DateTimeField(
            auto_now_add=True,
            verbose_name='дата публикации'
        )

    class Meta:
        ordering = ['-pub_date']
    
    def __str__(self):
        return self.text

