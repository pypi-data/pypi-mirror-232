from rest_framework import serializers

from dcim.api.nested_serializers import (
    NestedDeviceSerializer, NestedSiteSerializer,
)

from netbox.api.fields import ChoiceField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from netbox_cluster.choices import *
from netbox_cluster.models import DeviceCluster, DeviceClusterGroup, DeviceClusterType
from .nested_serializers import *


#
# DeviceClusters
#

class DeviceClusterTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='clusters-api:clustertype-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceClusterType
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'cluster_count',
        ]


class DeviceClusterGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='clusters-api:clustergroup-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceClusterGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'cluster_count',
        ]


class DeviceClusterSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='clusters-api:cluster-detail')
    type = NestedDeviceClusterTypeSerializer()
    group = NestedDeviceClusterGroupSerializer(required=False, allow_null=True, default=None)
    status = ChoiceField(choices=DeviceClusterStatusChoices, required=False)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer(required=False, allow_null=True, default=None)
    devices = NestedDeviceSerializer(required=False, allow_null=True)
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceCluster
        fields = [
            'id', 'url', 'display', 'name', 'type', 'group', 'status', 'tenant', 'site', 'tags', 'created', 'last_updated', 'device_count',
        ]
