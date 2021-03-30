from api_yamdb.settings import NOREPLY_YAMDB_EMAIL
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, views, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import TitleFilter
from .models import Category, Comment, Genre, Review, Title, User
from .permissions import IsAdminOrReadOnly, IsModerator, IsOwner
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleGetSerializer, TitlePostUpdateSerializer,
                          UserSerializer)
from .validators import email_is_valid


def send_email(to_email, code):
    subject = 'Obtaining confirmation code'
    text_content = f'Your confirmation code is {code}.'
    to = to_email

    mail.send_mail(
        subject, text_content,
        NOREPLY_YAMDB_EMAIL, [to],
        fail_silently=False
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    email = request.data.get('email')
    if email is None:
        message = 'Email is required'
    else:
        if email_is_valid(email):
            user = get_object_or_404(User, email=email)
            code = default_token_generator.make_token(user)
            send_email(email, code)
            user.confirmation_code = code
            message = email
            user.save()
        else:
            message = 'Valid email is required'
    return Response({'email': message})          
 


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=username',]
    lookup_field = 'username'


    @action(methods=['PATCH', 'GET'], detail=False,
            permission_classes = [IsAuthenticated | IsAdminUser],
            url_path = 'me', url_name = 'update_user_profile')
    def update_user_profile(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.data)           




class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name',]
    lookup_field = 'slug'





class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name',]
    lookup_field = 'slug'




class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title__id=title_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        queryset = Comment.objects.filter(
            review__id=self.kwargs.get('review_id')
        )
        return queryset


    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'partial_update':
            permission_classes = [IsOwner]
        elif self.action == 'destroy':            
            permission_classes = [IsModerator | IsAdminUser]
        return [permission() for permission in permission_classes]            





class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitlePostUpdateSerializer




class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user,
                        title=title
                        )

        avg_rating = Review.objects.filter(title=title).aggregate(Avg('score'))
        title.rating = avg_rating['score__avg']
        title.save(update_fields=['rating'])


    def perform_update(self, serializer):
        serializer.save()    
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        avg_rating = Review.objects.filter(title=title).aggregate(Avg('score'))
        title.rating = avg_rating['score__avg']
        title.save(update_fields=['rating'])        


    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.review.all()


    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'partial_update':
            permission_classes = [IsOwner]
        elif self.action == 'destroy':            
            permission_classes = [IsModerator | IsAdminUser]
        return [permission() for permission in permission_classes]      
