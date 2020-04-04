from django.core.management import BaseCommand

from netbox_vcenter.background_tasks import get_virtual_machines
from netbox_vcenter.models import ClusterVCenter


class Command(BaseCommand):
    help = "Update the cache of vCenter information"

    def handle(self, verbosity, *args, **kwargs):
        for vcenter in ClusterVCenter.objects.all():
            if verbosity >= 1:
                self.stdout.write(f"Scheduling cache update for {vcenter.cluster.name}")
            get_virtual_machines.delay(vcenter=vcenter, force=True)
