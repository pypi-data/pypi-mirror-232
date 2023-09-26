from connio.base.version import Version


class InstanceResource(object):
    def __init__(self, version):
        """
        :param Version version:
        """
        self._version: Version = version
        """ :type: Version """

