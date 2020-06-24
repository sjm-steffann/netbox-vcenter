import logging
import time
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from rq.job import Job

from netbox_vcenter.background_tasks import refresh_virtual_machines
from netbox_vcenter.forms import ClusterVCenterEditForm
from netbox_vcenter.models import ClusterVCenter
from utilities.views import GetReturnURLMixin, ObjectDeleteView, ObjectEditView
from virtualization.models import Cluster, VirtualMachine

logger = logging.getLogger('netbox_vcenter')


class ClusterVCenterObjectMixin:
    def get_object(self, kwargs):
        if 'cluster_id' not in kwargs:
            raise Http404

        cluster = get_object_or_404(Cluster, pk=kwargs['cluster_id'])

        try:
            return ClusterVCenter.objects.get(cluster=cluster)
        except ClusterVCenter.DoesNotExist:
            return ClusterVCenter(cluster=cluster)


class ClusterVCenterEditView(PermissionRequiredMixin, ClusterVCenterObjectMixin, ObjectEditView):
    permission_required = 'change_clustervcenter'
    model = ClusterVCenter
    model_form = ClusterVCenterEditForm


class ClusterVCenterDeleteView(PermissionRequiredMixin, ClusterVCenterObjectMixin, ObjectDeleteView):
    permission_required = 'delete_clustervcenter'
    model = ClusterVCenter


class VirtualMachineRefresh(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'view_virtualmachine'

    def post(self, request, virtualmachine_id):
        config = settings.PLUGINS_CONFIG['netbox_vcenter']

        vm = get_object_or_404(VirtualMachine, pk=virtualmachine_id)
        vcenter = vm.cluster.vcenter

        logger.info("Forcing background task to retrieve VMs from {}".format(vcenter.server))
        job = refresh_virtual_machines.delay(vcenter=vcenter, force=True)  # type: Job

        delay = 0.2
        max_wait = config['REFRESH_WAIT']
        max_loops = max_wait / delay
        loops = 0
        while job.is_queued or job.is_started:
            if loops > max_loops:
                break

            time.sleep(delay)
            loops += 1

        return redirect(self.get_return_url(request, vm))


class VirtualMachineUpdate(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'change_virtualmachine'

    def post(self, request, virtualmachine_id, field):
        if field not in ['vcpus', 'memory', 'disk']:
            raise Http404

        if field not in request.POST:
            return HttpResponseBadRequest(f'No value provided for {field}')

        try:
            value = int(request.POST[field])
        except ValueError:
            return HttpResponseBadRequest(f'Value of {field} must be an integer')

        vm = get_object_or_404(VirtualMachine, pk=virtualmachine_id)
        setattr(vm, field, value)
        vm.save()

        messages.info(request, f"Updated {vm._meta.get_field(field).verbose_name} of {vm.name}")

        return redirect(self.get_return_url(request, vm))

# class CompareVCenterView(View):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         self.content = None
#         self._pgs_cache = {}
#
#     def get(self, request):
#         try:
#             self.content = service_instance.RetrieveContent()
#
#             output = ''
#             vms = self.get_objects_of_type(vim.VirtualMachine)
#             for vm in vms:
#                 output += f'VM {vm.name}\n'
#                 for dev in vm.config.hardware.device:
#                     if isinstance(dev, vim.vm.device.VirtualEthernetCard):
#                         vlan = self.get_nic_vlan(vm, dev)
#                         output += f'  NIC {dev.deviceInfo.label} [{dev.macAddress}] = {vlan}\n'
#
#             return HttpResponse(output, "text/plain")
#         finally:
#             connect.Disconnect(service_instance)
#
#     def get_objects_of_type(self, obj_type):
#         view_mgr = self.content.viewManager.CreateContainerView(self.content.rootFolder,
#                                                                 [obj_type],
#                                                                 True)
#         try:
#             return list(view_mgr.view)
#         finally:
#             view_mgr.Destroy()
