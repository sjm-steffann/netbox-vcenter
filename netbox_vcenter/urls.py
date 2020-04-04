from django.urls import path

from .views import (ClusterVCenterDeleteView, ClusterVCenterEditView, TestView, VirtualMachineRefresh,
                    VirtualMachineUpdate)

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('clusters/<int:cluster_id>/edit/', ClusterVCenterEditView.as_view(), name='cluster_vcenter_edit'),
    path('clusters/<int:cluster_id>/delete/', ClusterVCenterDeleteView.as_view(), name='cluster_vcenter_delete'),
    path('virtualhosts/<int:virtualmachine_id>/update/<field>/', VirtualMachineUpdate.as_view(),
         name='virtualmachine_update'),
    path('virtualhosts/<int:virtualmachine_id>/refresh/', VirtualMachineRefresh.as_view(),
         name='virtualmachine_refresh'),
]
