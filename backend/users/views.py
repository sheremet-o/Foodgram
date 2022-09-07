from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from foodgram.pagination import FoodgramPaginator
from .models import CustomUser, Subscription
from .serializers import SubscriptionSerializer


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated, ])
def subscribe_to(request, pk):
    user = get_object_or_404(CustomUser, username=request.user.username)
    author = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        if user.id == author.id:
            context = {'errors': 'Нельзя подписаться на себя'}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        try:
            Subscription.objects.create(user=user, author=author)
        except IntegrityError:
            context = {'errors': 'Вы уже подписаны на этого автора'}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        subscribed_to = CustomUser.objects.all().filter(username=author)
        serializer = SubscriptionSerializer(
            subscribed_to,
            context={'request': request},
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        try:
            subscription = Subscription.objects.get(user=user, author=author)
        except ObjectDoesNotExist:
            content = {'errors': 'Вы не подписаны на этого автора'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return HttpResponse('Вы отменили подписку на этого автора',
                            status=status.HTTP_204_NO_CONTENT)


class SubscriptionListView(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = FoodgramPaginator
    filter_backends = (filters.SearchFilter,)
    permission_classes = (permissions.IsAuthenticated,)
    search_fields = ('^following__user',)

    def get_queryset(self):
        user = self.request.user
        new_queryset = CustomUser.objects.filter(following__user=user)
        return new_queryset
