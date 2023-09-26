from utilities.choices import ChoiceSet


#
# Clusters
#

class DeviceClusterStatusChoices(ChoiceSet):
    key = 'DeviceCluster.status'

    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_MAINTENANCE = 'decommissioning'
    STATUS_OFFLINE = 'offline'

    CHOICES = [
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_STAGING, 'Staging', 'blue'),
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_MAINTENANCE, 'Decommissioning', 'yellow'),
        (STATUS_OFFLINE, 'Offline', 'red'),
    ]
