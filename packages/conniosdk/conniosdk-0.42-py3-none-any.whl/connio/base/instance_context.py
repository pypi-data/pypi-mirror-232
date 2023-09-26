from connio.base.version import Version


class InstanceContext(object):
    def __init__(self, version):
        """
        :param Version version:
        """
        self._version: Version = version
        """ :type: Version """

