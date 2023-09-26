from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from dcim.models import Device
from netbox.models import OrganizationalModel, PrimaryModel
from netbox_cluster.choices import *

__all__ = (
    'DeviceCluster',
    'DeviceClusterGroup',
    'DeviceClusterType',
)


class DeviceClusterType(OrganizationalModel):
    """
    A type of Cluster.
    """
    # def get_absolute_url(self):
    #     return reverse('device-cluster:clustertype', args=[self.pk])

class DeviceClusterGroup(OrganizationalModel):
    """
    An organizational group of Clusters.
    """

    # def get_absolute_url(self):
    #     return reverse('device-cluster:clustergroup', args=[self.pk])


class DeviceCluster(PrimaryModel):
    """
    A cluster of physical devices. Each Cluster may optionally be associated with one or more Devices.
    """
    name = models.CharField(
        max_length=100
    )
    type = models.ForeignKey(
        to=DeviceClusterType,
        on_delete=models.PROTECT,
        related_name='device_clusters'
    )
    group = models.ForeignKey(
        to=DeviceClusterGroup,
        on_delete=models.PROTECT,
        related_name='device_clusters',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=50,
        choices=DeviceClusterStatusChoices,
        default=DeviceClusterStatusChoices.STATUS_ACTIVE
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='device_clusters',
        blank=True,
        null=True
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='device_clusters',
        blank=True,
        null=True
    )
    devices = models.ManyToManyField(Device)
    clone_fields = (
        'type', 'group', 'status', 'tenant', 'site',
    )
    prerequisite_models = (
        'netbox_cluster.DeviceClusterType',
    )

    class Meta:
        ordering = ['name']
        constraints = (
            models.UniqueConstraint(
                fields=('group', 'name'),
                name='%(app_label)s_%(class)s_unique_group_name'
            ),
            models.UniqueConstraint(
                fields=('site', 'name'),
                name='%(app_label)s_%(class)s_unique_site_name'
            ),
        )

    def __str__(self):
        return self.name