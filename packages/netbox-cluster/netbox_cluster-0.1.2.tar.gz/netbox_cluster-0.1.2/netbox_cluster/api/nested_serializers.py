from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from netbox_cluster.models import DeviceCluster, DeviceClusterGroup, DeviceClusterType

__all__ = [
    'NestedDeviceClusterGroupSerializer',
    'NestedDeviceClusterSerializer',
    'NestedDeviceClusterTypeSerializer',
]

#
# DeviceClusters
#


@extend_schema_serializer(
    exclude_fields=('cluster_count',),
)
class NestedDeviceClusterTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='clusters-api:clustertype-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceClusterType
        fields = ['id', 'url', 'display', 'name', 'slug', 'cluster_count']


@extend_schema_serializer(
    exclude_fields=('cluster_count',),
)
class NestedDeviceClusterGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='clusters-api:clustergroup-detail')
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceClusterGroup
        fields = ['id', 'url', 'display', 'name', 'slug', 'cluster_count']


@extend_schema_serializer()
class NestedDeviceClusterSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='clusters-api:cluster-detail')

    class Meta:
        model = DeviceCluster
        fields = ['id', 'url', 'display', 'name']
