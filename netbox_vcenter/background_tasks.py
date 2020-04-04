import hashlib
import logging
import time

from cacheops import CacheMiss, cache
from django.conf import settings
from django_rq import job
from pyVim import connect
from pyVmomi import vim

from netbox_vcenter.models import ClusterVCenter

logger = logging.getLogger('netbox_vcenter')


def get_vms(vcenter: ClusterVCenter):
    if not vcenter:
        return None

    logger.debug("Checking for VMs on {}".format(vcenter.server))
    try:
        cache_key = get_cache_key(vcenter)
        vms = cache.get(cache_key)
        if vms != 'FAILED':
            logger.debug("Found cached VMs on {}".format(vcenter.server))
            return vms
    except CacheMiss:
        # Get the VMs in the background worker, it will fill the cache
        logger.info("Initiating background task to retrieve VMs from {}".format(vcenter.server))
        get_virtual_machines.delay(vcenter=vcenter)

    return None


def get_objects_of_type(content, obj_type):
    view_mgr = content.viewManager.CreateContainerView(content.rootFolder,
                                                       [obj_type],
                                                       True)
    try:
        return [obj for obj in view_mgr.view]
    finally:
        view_mgr.Destroy()


def get_cache_key(vcenter: ClusterVCenter):
    raw_key = f'{vcenter.server}\t{vcenter.username}\t{vcenter.password}'
    key = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[-16]
    return key


@job
def get_virtual_machines(vcenter: ClusterVCenter, force=False):
    config = settings.PLUGINS_CONFIG['netbox_vcenter']
    vcenter_cache_key = get_cache_key(vcenter)

    # Check whether this server has failed recently and shouldn't be retried yet
    try:
        cached_data = cache.get(vcenter_cache_key)
        if not force and cached_data == 'FAILED':
            logger.info("Skipping vCenter update; server {} failed recently".format(vcenter.server))
            return

        if not force:
            logger.info("Skipping vCenter update; server {} already in cache".format(vcenter.server))
            return cached_data
    except CacheMiss:
        pass

    service_instance = None
    try:
        logger.debug("Fetching VMs from {}".format(vcenter.server))

        # Connect to the vCenter server
        if vcenter.validate_certificate:
            service_instance = connect.Connect(vcenter.server, user=vcenter.username, pwd=vcenter.password)
        else:
            service_instance = connect.ConnectNoSSL(vcenter.server, user=vcenter.username, pwd=vcenter.password)

        content = service_instance.RetrieveContent()

        vms = get_objects_of_type(content, vim.VirtualMachine)
        all_stats = {
            'timestamp': time.time(),
            'vms': {}
        }
        for vm in vms:
            vm_stats = {
                'power': None,
                'vcpus': None,
                'memory': None,
                'disk': None,
            }

            try:
                if vm.runtime.powerState:
                    vm_stats['powered_on'] = vm.runtime.powerState == 'poweredOn'
                if vm.config.hardware.numCPU:
                    vm_stats['vcpus'] = vm.config.hardware.numCPU
                if vm.config.hardware.memoryMB:
                    vm_stats['memory'] = vm.config.hardware.memoryMB

                disk_devices = [device for device in vm.config.hardware.device
                                if isinstance(device, vim.vm.device.VirtualDisk)]
                if disk_devices:
                    # Sum and convert from KB to GB
                    total_capacity = 0
                    for device in disk_devices:
                        total_capacity += device.capacityInKB
                    vm_stats['disk'] = round(total_capacity / 1048576)
            except Exception:
                logger.exception("Error while fetching virtual machine {} from {}".format(vm.name, vcenter.server))
                continue

            # Collect all stats for returning
            all_stats['vms'][vm.name] = vm_stats

        # Cache a list of all VMs
        cache.set(vcenter_cache_key, all_stats, config['CACHE_TIMEOUT'])

        return all_stats
    except Exception:
        # Set a cookie in the cache so we don't keep retrying
        logger.exception("Error while fetching virtual machines from {}. "
                         "Disabling checks for 5 minutes.".format(vcenter.server))
        cache.set(vcenter_cache_key, 'FAILED', config['CACHE_FAILURE_TIMEOUT'])
    finally:
        if service_instance:
            connect.Disconnect(service_instance)
