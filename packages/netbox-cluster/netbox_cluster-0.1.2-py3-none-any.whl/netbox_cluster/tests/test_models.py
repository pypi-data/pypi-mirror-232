from django.core.exceptions import ValidationError
from django.test import TestCase

from circuits.models import *
from dcim.choices import *
from dcim.models import *
from tenancy.models import Tenant
from netbox_cluster.models import *


class DeviceClusterTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cluster_type = DeviceClusterType.objects.create(name='DeviceCluster Type 1', slug='cluster-type-1')
        DeviceCluster.objects.create(name='DeviceCluster 1', type=cluster_type)


    def test_node_duplicate_name_per_cluster(self):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        device_role = DeviceRole.objects.create(
            name='Device Role 1', slug='device-role-1', color='ff0000'
        )
        site_a = Site.objects.create(name='Site A', slug='site-a')
        location_a1 = Location(site=site_a, name='Location A1', slug='location-a1')
        location_a1.save()
        location_a2 = Location(site=site_a, parent=location_a1, name='Location A2', slug='location-a2')
        location_a2.save()

        device1 = Device.objects.create(
            site=site_a,
            location=location_a1,
            name='Device 1',
            device_type=device_type,
            device_role=device_role
        )
        device2 = Device.objects.create(
            site=site_a,
            location=location_a2,
            name='Device 2',
            device_type=device_type,
            device_role=device_role
        )
        test_cluster = DeviceCluster.objects.first()
        test_cluster.devices.add(device1)
        test_cluster.devices.add(device2)

        self.assertEqual(test_cluster.devices.count(), 2)
        self.assertEqual(test_cluster.devices.first().site, site_a)
        self.assertEqual(test_cluster.devices.first().location, location_a1)
        self.assertEqual(test_cluster.devices.first().device_role, device_role)