from django import forms
from django.utils.translation import gettext_lazy as _

from netbox_vcenter.models import ClusterVCenter
from utilities.forms import BootstrapMixin


class ClusterVCenterEditForm(BootstrapMixin, forms.ModelForm):
    new_password = forms.CharField(
        max_length=64,
        label='Password',
        widget=forms.PasswordInput(),
        help_text=_('This password is stored unencrypted in the database. '
                    'Use a read-only account with limited privileges!'),
    )

    class Meta:
        model = ClusterVCenter
        fields = ['server', 'validate_certificate', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.password:
            # Hack the password field and make it non-required
            self.fields['new_password'].required = False
            self.fields['new_password'].widget.is_required = False
            if 'required' in self.fields['new_password'].widget.attrs:
                del self.fields['new_password'].widget.attrs['required']
            self.fields['new_password'].widget.attrs['placeholder'] = 'current password hidden'

    def _post_clean(self):
        # Update the password if it is provided
        if self.cleaned_data['new_password']:
            self.instance.password = self.cleaned_data['new_password']

        return super()._post_clean()
