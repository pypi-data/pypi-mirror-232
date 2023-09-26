from rest_framework.routers import APIRootView

from dcim.models import Device
from extras.api.mixins import ConfigContextQuerySetMixin
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.utils import count_related
from netbox_cluster import filtersets
from netbox_cluster.models import DeviceCluster, DeviceClusterGroup, DeviceClusterType
from . import serializers


class NetboxClusterRootView(APIRootView):
    """
    Device Clusters API root view
    """
    def get_view_name(self):
        return 'Clusters'

#
# Clusters
#

class DeviceClusterTypeViewSet(NetBoxModelViewSet):
    queryset = DeviceClusterType.objects.annotate(
        cluster_count=count_related(DeviceCluster, 'type')
    ).prefetch_related('tags')
    serializer_class = serializers.DeviceClusterTypeSerializer
    filterset_class = filtersets.DeviceClusterTypeFilterSet


class DeviceClusterGroupViewSet(NetBoxModelViewSet):
    queryset = DeviceClusterGroup.objects.annotate(
        cluster_count=count_related(DeviceCluster, 'group')
    ).prefetch_related('tags')
    serializer_class = serializers.DeviceClusterGroupSerializer
    filterset_class = filtersets.DeviceClusterGroupFilterSet


class DeviceClusterViewSet(NetBoxModelViewSet):
    queryset = DeviceCluster.objects.prefetch_related(
        'type', 'group', 'tenant', 'site', 'tags'
    ).annotate(
        device_count=count_related(Device, 'cluster'),
    )
    serializer_class = serializers.DeviceClusterSerializer
    filterset_class = filtersets.DeviceClusterFilterSet

