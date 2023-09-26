from django.urls import reverse
from rest_framework import status

from utilities.testing import APITestCase, APIViewTestCases
from netbox_cluster.choices import *
from netbox_cluster.models import DeviceCluster, DeviceClusterGroup, DeviceClusterType

class AppTest(APITestCase):

    def test_root(self):

        url = reverse('clusters-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class DeviceClusterTypeTest(APIViewTestCases.APIViewTestCase):
    model = DeviceClusterType
    brief_fields = ['cluster_count', 'display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Cluster Type 4',
            'slug': 'cluster-type-4',
        },
        {
            'name': 'Cluster Type 5',
            'slug': 'cluster-type-5',
        },
        {
            'name': 'Cluster Type 6',
            'slug': 'cluster-type-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            DeviceClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            DeviceClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            DeviceClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        DeviceClusterType.objects.bulk_create(cluster_types)


class DeviceClusterGroupTest(APIViewTestCases.APIViewTestCase):
    model = DeviceClusterGroup
    brief_fields = ['cluster_count', 'display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Cluster Group 4',
            'slug': 'cluster-type-4',
        },
        {
            'name': 'Cluster Group 5',
            'slug': 'cluster-type-5',
        },
        {
            'name': 'Cluster Group 6',
            'slug': 'cluster-type-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        cluster_Groups = (
            DeviceClusterGroup(name='Cluster Group 1', slug='cluster-type-1'),
            DeviceClusterGroup(name='Cluster Group 2', slug='cluster-type-2'),
            DeviceClusterGroup(name='Cluster Group 3', slug='cluster-type-3'),
        )
        DeviceClusterGroup.objects.bulk_create(cluster_Groups)


class DeviceClusterTest(APIViewTestCases.APIViewTestCase):
    model = DeviceCluster
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'status': 'offline',
        'comments': 'New comment',
    }

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            DeviceClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            DeviceClusterType(name='Cluster Type 2', slug='cluster-type-2'),
        )
        DeviceClusterType.objects.bulk_create(cluster_types)

        cluster_groups = (
            DeviceClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            DeviceClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
        )
        DeviceClusterGroup.objects.bulk_create(cluster_groups)

        clusters = (
            DeviceCluster(name='Cluster 1', type=cluster_types[0], group=cluster_groups[0], status=DeviceClusterStatusChoices.STATUS_PLANNED),
            DeviceCluster(name='Cluster 2', type=cluster_types[0], group=cluster_groups[0], status=DeviceClusterStatusChoices.STATUS_PLANNED),
            DeviceCluster(name='Cluster 3', type=cluster_types[0], group=cluster_groups[0], status=DeviceClusterStatusChoices.STATUS_PLANNED),
        )
        DeviceCluster.objects.bulk_create(clusters)

        cls.create_data = [
            {
                'name': 'Cluster 4',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
                'status': DeviceClusterStatusChoices.STATUS_STAGING,
            },
            {
                'name': 'Cluster 5',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
                'status': DeviceClusterStatusChoices.STATUS_STAGING,
            },
            {
                'name': 'Cluster 6',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
                'status': DeviceClusterStatusChoices.STATUS_STAGING,
            },
        ]
