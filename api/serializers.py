from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['first_name', 'last_name', 'username',
                  'bio', 'role', 'email']
        model = User


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }   




class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=100)

    def validate(self, data):
        user = get_object_or_404(
            User, confirmation_code=data['confirmation_code'],
            email=data['email']
        )
        return get_tokens_for_user(user)    




class CategorySerializer(serializers.ModelSerializer):
    class Meta:    
        fields = ['name', 'slug',]
        lookup_field = 'slug'
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'slug',]
        lookup_field = 'slug'
        model = Genre 


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many = True,read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title 


class TitlePostUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
            slug_field = 'slug',
            queryset = Category.objects.all()
        )
    genre = serializers.SlugRelatedField(
            slug_field = 'slug',
            many = True,
            queryset = Genre.objects.all()
        )
    
    class Meta:
        fields = [
                    'id', 'name', 'year', 'description',
                    'genre', 'category', 'rating'
                ]
        model = Title 
    



class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
            slug_field = 'username', 
            read_only=True
        )

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review


    def validate(self, data):
        super().validate(data)

        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = (
            self.context['request'].parser_context['kwargs']['title_id']
        )
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                'You have already submitted your review'
            ) 
        return data     


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
            slug_field='username',
            read_only=True
        )

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date']
        model = Comment                
