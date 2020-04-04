from datetime import datetime

from django.contrib.auth.context_processors import PermWrapper
from django.template.context_processors import csrf

from extras.plugins import PluginTemplateExtension
from netbox_vcenter.background_tasks import get_virtual_machines
from virtualization.models import VirtualMachine


# noinspection PyAbstractClass
class ClusterInfo(PluginTemplateExtension):
    model = 'virtualization.cluster'

    def left_page(self):
        """
        An info-box with edit button for the vCenter settings
        """
        return self.render('netbox_vcenter/cluster/vcenter_info.html', {
            'perms': PermWrapper(self.context['request'].user)
        })


# noinspection PyAbstractClass
class VirtualMachineInfo(PluginTemplateExtension):
    model = 'virtualization.virtualmachine'

    def buttons(self):
        context = {
            'perms': PermWrapper(self.context['request'].user),
        }
        context.update(csrf(self.context['request']))
        return self.render('netbox_vcenter/virtualmachine/vcenter_refresh.html', context)

    def right_page(self):
        """
        An info-box with information from vCenter
        """
        vm = self.context['object']  # type: VirtualMachine

        try:
            all_stats = get_virtual_machines(vm.cluster.vcenter)
            vcenter_timestamp = datetime.fromtimestamp(all_stats['timestamp'])
            vcenter_resources = all_stats['vms'][vm.name]
        except Exception:
            return ''

        context = {
            'perms': PermWrapper(self.context['request'].user),
            'vcenter_timestamp': vcenter_timestamp,
            'vcenter_resources': vcenter_resources,
        }
        context.update(csrf(self.context['request']))
        return self.render('netbox_vcenter/virtualmachine/vcenter_resources.html', context)


template_extensions = [ClusterInfo, VirtualMachineInfo]
