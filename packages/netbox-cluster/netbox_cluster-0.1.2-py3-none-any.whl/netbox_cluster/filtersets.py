import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from dcim.models import Device, Region, Site, SiteGroup
from netbox.filtersets import OrganizationalModelFilterSet, NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import TreeNodeMultipleChoiceFilter
from .choices import *
from .models import DeviceCluster, DeviceClusterGroup, DeviceClusterType

__all__ = (
    'DeviceClusterFilterSet',
    'DeviceClusterGroupFilterSet',
    'DeviceClusterTypeFilterSet',
)


class DeviceClusterTypeFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = DeviceClusterType
        fields = ['id', 'name', 'slug', 'description']


class DeviceClusterGroupFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = DeviceClusterGroup
        fields = ['id', 'name', 'slug', 'description']


class DeviceClusterFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceClusterGroup.objects.all(),
        label=_('Parent group (ID)'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=DeviceClusterGroup.objects.all(),
        to_field_name='slug',
        label=_('Parent group (slug)'),
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceClusterType.objects.all(),
        label=_('luster type (ID)'),
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=DeviceClusterType.objects.all(),
        to_field_name='slug',
        label=_('Cluster type (slug)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=DeviceClusterStatusChoices,
        null_value=None
    )
    devices = TreeNodeMultipleChoiceFilter(
        queryset=Device.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    class Meta:
        model = DeviceCluster
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )
