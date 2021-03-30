from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .serializers import EmailSerializer
from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet,
                    send_confirmation_code)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'titles/(?P<title_id>[^/.]+)/reviews', ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments',
    CommentViewSet, basename='comments'
)


urlpatterns = [
    path('', include(router.urls)),
    
    path('auth/token/', TokenObtainPairView.as_view(
                        serializer_class=EmailSerializer),
                        name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),                    
    path('auth/email/', send_confirmation_code),
        
]
