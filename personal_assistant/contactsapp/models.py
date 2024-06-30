from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Group(models.Model):
    name_en = models.CharField(max_length=100, verbose_name=_('Group Name (English)'))
    name_uk = models.CharField(max_length=100, verbose_name=_('Group Name (Ukrainian)'))
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['creator', 'name_en'], name='group_of_creator_en'),
                       models.UniqueConstraint(fields=['creator', 'name_uk'], name='group_of_creator_uk')]
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.name_en

    def get_name(self, language):
        if language == 'uk':
            return self.name_uk
        return self.name_en


class Contact(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, verbose_name='Name', null=False)
    phone = models.CharField(max_length=12, verbose_name='Phone', blank=True)
    email = models.EmailField(max_length=30, verbose_name='Email', blank=True)
    address = models.CharField(max_length=100, verbose_name='Address', blank=True)
    birthday = models.DateField(default=None, verbose_name='Birthday', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, verbose_name='Group', null=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True, verbose_name='Creation time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['creator', 'name'], name='contact_of_creator')]
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return f"{self.name}: {self.phone}."
