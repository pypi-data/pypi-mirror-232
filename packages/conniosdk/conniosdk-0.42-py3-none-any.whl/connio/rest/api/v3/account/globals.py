from connio.base import values
from connio.base.instance_context import InstanceContext


HTTP_POST = "POST"
HTTP_GET = "GET"
HTTP_PUT = "PUT"


class GlobalContext(InstanceContext):
    def __init__(self, version, account_id):
        """
        Initialize the GlobalContext

        :param Version version: Version that contains the resource
        :param account_id: The account_id

        :returns: connio.rest.api.v3.account.global.GlobalContext
        :rtype: connio.rest.api.v3.account.global.GlobalContext
        """
        super(GlobalContext, self).__init__(version)

        # Path Solution
        self._solution = {'account_id': account_id, }
        self._uri = '/accounts/{account_id}/objectmodel/globals'.format(**self._solution)

    def get(self) -> str:
        """
        Get globals
        """
        params = values.of({})

        response = self._version.request(
            HTTP_GET,
            self._uri,
            params=params
        )

        return eval(response.text)

    def update(self, globals_string: str):
        """
        Update globals
        """
        self._version.update(
            HTTP_PUT,
            uri=self._uri,
            data=globals_string.encode(),
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Connio.Api.V3.GlobalContext>'