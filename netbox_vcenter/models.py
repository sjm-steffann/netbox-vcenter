from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox_vcenter.validators import HostnameAddressValidator
from virtualization.models import Cluster


class ClusterVCenter(models.Model):
    cluster = models.OneToOneField(
        to=Cluster,
        on_delete=models.CASCADE,
        related_name='vcenter',
    )
    server = models.CharField(
        verbose_name=_('vCenter Server'),
        max_length=64,
        validators=[HostnameAddressValidator()],
    )
    validate_certificate = models.BooleanField(
        verbose_name=_('validate certificate'),
        default=True,
    )
    username = models.CharField(
        verbose_name=_('username'),
        max_length=64,
    )
    password = models.CharField(
        verbose_name=_('password'),
        max_length=64,
    )

    class Meta:
        verbose_name = _('vCenter configuration')
        verbose_name_plural = _('vCenter configurations')

    def __str__(self):
        return self.cluster.name

    def get_absolute_url(self):
        return self.cluster.get_absolute_url()
