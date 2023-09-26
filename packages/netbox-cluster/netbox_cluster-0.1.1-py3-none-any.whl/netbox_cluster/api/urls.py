from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.NetboxClusterRootView

# Clusters
router.register('cluster-types', views.DeviceClusterTypeViewSet)
router.register('cluster-groups', views.DeviceClusterGroupViewSet)
router.register('clusters', views.DeviceClusterViewSet)

app_name = 'clusters-api'
urlpatterns = router.urls
