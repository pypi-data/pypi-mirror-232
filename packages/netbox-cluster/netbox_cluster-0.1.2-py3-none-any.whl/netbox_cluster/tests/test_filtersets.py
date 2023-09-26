from django.test import TestCase

from dcim.models import Device, DeviceRole, Platform, Region, Site, SiteGroup
from ipam.models import IPAddress, VRF
from tenancy.models import Tenant, TenantGroup
from utilities.testing import ChangeLoggedFilterSetTests, create_test_device
from netbox_cluster.choices import *
from netbox_cluster.filtersets import *
from netbox_cluster.models import DeviceCluster, DeviceClusterGroup, DeviceClusterType


class ClusterTypeTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DeviceClusterType.objects.all()
    filterset = DeviceClusterTypeFilterSet

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            DeviceClusterType(name='Cluster Type 1', slug='cluster-type-1', description='A'),
            DeviceClusterType(name='Cluster Type 2', slug='cluster-type-2', description='B'),
            DeviceClusterType(name='Cluster Type 3', slug='cluster-type-3', description='C'),
        )
        DeviceClusterType.objects.bulk_create(cluster_types)

    def test_name(self):
        params = {'name': ['Cluster Type 1', 'Cluster Type 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['cluster-type-1', 'cluster-type-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ClusterGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DeviceClusterGroup.objects.all()
    filterset = DeviceClusterGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        cluster_groups = (
            DeviceClusterGroup(name='Cluster Group 1', slug='cluster-group-1', description='A'),
            DeviceClusterGroup(name='Cluster Group 2', slug='cluster-group-2', description='B'),
            DeviceClusterGroup(name='Cluster Group 3', slug='cluster-group-3', description='C'),
        )
        DeviceClusterGroup.objects.bulk_create(cluster_groups)

    def test_name(self):
        params = {'name': ['Cluster Group 1', 'Cluster Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['cluster-group-1', 'cluster-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ClusterTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DeviceCluster.objects.all()
    filterset = DeviceClusterFilterSet

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            DeviceClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            DeviceClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            DeviceClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        DeviceClusterType.objects.bulk_create(cluster_types)

        cluster_groups = (
            DeviceClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            DeviceClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            DeviceClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        )
        DeviceClusterGroup.objects.bulk_create(cluster_groups)

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
            Region(name='Test Region 3', slug='test-region-3'),
        )
        for r in regions:
            r.save()

        site_groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for site_group in site_groups:
            site_group.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0], group=site_groups[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1], group=site_groups[1]),
            Site(name='Test Site 3', slug='test-site-3', region=regions[2], group=site_groups[2]),
        )
        Site.objects.bulk_create(sites)

        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        clusters = (
            DeviceCluster(name='Cluster 1', type=cluster_types[0], group=cluster_groups[0], status=DeviceClusterStatusChoices.STATUS_PLANNED, site=sites[0], tenant=tenants[0]),
            DeviceCluster(name='Cluster 2', type=cluster_types[1], group=cluster_groups[1], status=DeviceClusterStatusChoices.STATUS_STAGING, site=sites[1], tenant=tenants[1]),
            DeviceCluster(name='Cluster 3', type=cluster_types[2], group=cluster_groups[2], status=DeviceClusterStatusChoices.STATUS_ACTIVE, site=sites[2], tenant=tenants[2]),
        )
        DeviceCluster.objects.bulk_create(clusters)

    def test_name(self):
        params = {'name': ['Cluster 1', 'Cluster 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = DeviceClusterGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [DeviceClusterStatusChoices.STATUS_PLANNED, DeviceClusterStatusChoices.STATUS_STAGING]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        types = DeviceClusterType.objects.all()[:2]
        params = {'type_id': [types[0].pk, types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'type': [types[0].slug, types[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
