from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions

from .serializers import AuthTokenSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def obtain_auth_token(request):
    if request.user.is_authenticated:
        return Response("User is already authenticated")
    serializer = AuthTokenSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    #  token, created = Token.objects.get_or_create(user=user)
    try:
        token = user.auth_token.key
        return Response({'token': token})
    except Token.DoesNotExist:
        return Response(data={"error": "This user does not have a token."}, status=status.HTTP_401_UNAUTHORIZED)
