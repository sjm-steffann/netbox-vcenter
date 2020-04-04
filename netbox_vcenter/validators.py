from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _


class HostnameValidator(RegexValidator):
    regex = '^(' + URLValidator.host_re + ')$'
    message = _('Enter a valid hostname.')


class HostnameAddressValidator(RegexValidator):
    regex = '^(' + URLValidator.ipv4_re + '|' + URLValidator.ipv6_re + '|' + URLValidator.host_re + ')$'
    message = _('Enter a valid hostname or IP address.')
