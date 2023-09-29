import logging

import httpx

from easykube import flow, rest

from . import exceptions


logger = logging.getLogger(__name__)


class Resource(rest.Resource):
    """
    Resource class for the Azimuth API.
    """
    def _prepare_path(self, id = None, params = None):
        # Make sure that paths have a trailing slash to avoid having to handle 301s
        path, params = super()._prepare_path(id, params)
        if not path.endswith("/"):
            path = path + "/"
        return path, params


class BaseClient:
    """
    Base class for sync and async clients.
    """
    def __init__(self, *, default_tenancy_id = None, **kwargs):
        # Add the JSON header to all requests by default
        kwargs.setdefault("headers", {}).setdefault("Content-Type", "application/json")
        # Set longer default timeouts as some responses take a little while
        kwargs.setdefault("timeout", httpx.Timeout(5.0, read = 30.0))
        # Follow redirects by default
        kwargs.setdefault("follow_redirects", True)
        super().__init__(**kwargs)
        self._default_tenancy_id = default_tenancy_id

    @flow.flow
    def raise_for_status(self, response):
        # Convert response errors into ApiErrors for better messages
        try:
            yield super().raise_for_status(response)
        except httpx.HTTPStatusError as source:
            raise exceptions.APIError(source)

    @flow.flow
    def _init(self):
        """
        Perform any asynchronous initialisation that is required.
        """
        if not self._default_tenancy_id:
            logger.debug("discovering default tenancy")
            # Use the first tenancy as the default tenancy
            default_tenancy = yield self.tenancies().first()
            if default_tenancy:
                self._default_tenancy_id = default_tenancy.id
        if self._default_tenancy_id:
            logger.debug(f"using {self._default_tenancy_id} as default tenancy")

    def switch_tenancy(self, tenancy_id):
        """
        Switch to the specified tenancy.
        """
        self._default_tenancy_id = tenancy_id

    def tenancies(self):
        """
        Returns a REST resource for interacting with tenancies.
        """
        logger.debug("creating resource for tenancies")
        return Resource(self, "tenancies", prefix = "/api")
    
    def _tenancy_resource(self, resource, tenancy_id = None):
        tenancy_id = tenancy_id or self._default_tenancy_id
        if not tenancy_id:
            raise exceptions.SDKError("unable to detect default tenancy")
        logger.debug(f"creating resource for {resource} in tenancy {tenancy_id}")
        return Resource(self, resource, prefix = f"/api/tenancies/{tenancy_id}")

    def images(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the images for a tenancy.
        """
        return self._tenancy_resource("images", tenancy_id)

    def sizes(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the sizes for a tenancy.
        """
        return self._tenancy_resource("sizes", tenancy_id)

    def volumes(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the volumes for a tenancy.
        """
        return self._tenancy_resource("volumes", tenancy_id)

    def external_ips(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the external IPs for a tenancy.
        """
        return self._tenancy_resource("external_ips", tenancy_id)

    def machines(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the machines for a tenancy.
        """
        return self._tenancy_resource("machines", tenancy_id)

    def cluster_types(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the CaaS cluster types for a tenancy.
        """
        return self._tenancy_resource("cluster_types", tenancy_id)
    
    def clusters(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the CaaS clusters for a tenancy.
        """
        return self._tenancy_resource("clusters", tenancy_id)

    def kubernetes_cluster_templates(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the Kubernetes cluster templates for a tenancy.
        """
        return self._tenancy_resource("kubernetes_cluster_templates", tenancy_id)

    def kubernetes_clusters(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the Kubernetes clusters for a tenancy.
        """
        return self._tenancy_resource("kubernetes_clusters", tenancy_id)

    def kubernetes_app_templates(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the Kubernetes app templates for a tenancy.
        """
        return self._tenancy_resource("kubernetes_app_templates", tenancy_id)

    def kubernetes_apps(self, tenancy_id = None):
        """
        Returns a REST resource for interacting with the Kubernetes apps for a tenancy.
        """
        return self._tenancy_resource("kubernetes_apps", tenancy_id)


class SyncClient(BaseClient, rest.SyncClient):
    """
    Sync client for the Azimuth API.
    """
    def __enter__(self):
        obj = super().__enter__()
        obj._init()
        return self


class AsyncClient(BaseClient, rest.AsyncClient):
    """
    Async client for the Azimuth API.
    """
    async def __aenter__(self):
        obj = await super().__aenter__()
        await obj._init()
        return self
