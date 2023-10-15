from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}'

    class Meta:
        unique_together = ['subscriber', 'author']
