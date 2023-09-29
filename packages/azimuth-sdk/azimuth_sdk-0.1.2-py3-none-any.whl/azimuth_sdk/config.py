import logging
import os

import yaml

from . import auth, client, exceptions


logger = logging.getLogger(__name__)


class Configuration:
    """
    Class for an Azimuth client configuration.
    """
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def async_client(self, **kwargs):
        """
        Returns a new asynchronous client using the configuration.
        """
        logger.debug("creating async client")
        merged = self._kwargs.copy()
        merged.update(kwargs)
        return client.AsyncClient(**merged)

    def sync_client(self, **kwargs):
        """
        Returns a new synchronous client using the configuration.
        """
        logger.debug("creating sync client")
        merged = self._kwargs.copy()
        merged.update(kwargs)
        return client.SyncClient(**merged)
    
    @classmethod
    def create(
        cls,
        base_url,
        *,
        auth_data,
        authenticator = None,
        authenticator_type = None,
        **kwargs
    ):
        """
        Returns a new Azimuth client configuration with the specified auth.
        """
        return cls(
            base_url = base_url,
            auth = auth.Auth(
                base_url,
                authenticator = authenticator,
                authenticator_type = authenticator_type,
                auth_data = auth_data
            ),
            **kwargs
        )
    
    @classmethod
    def from_openstack_clouds_file(
        cls,
        base_url,
        path,
        cloud = "openstack",
        *,
        default_tenancy_id = None,
        **kwargs
    ):
        """
        Returns a new Azimuth client configuration populated from an openstack cloud-config.
        """
        logger.debug(f"loading openstack config for cloud '{cloud}' from {path}")
        with open(path) as fh:
            cloud_config = yaml.safe_load(fh)["clouds"][cloud]
        auth_type = cloud_config.get("auth_type", "v3password")
        auth = cloud_config["auth"]
        if auth_type == "v3password":
            authenticator_type = "openstack_password"
            auth_data = {
                "username": auth["username"],
                "password": auth["password"],
            }
        elif auth_type == "v3applicationcredential":
            authenticator_type = "openstack_application_credential"
            auth_data = {
                "application_credential_id": auth["application_credential_id"],
                "application_credential_secret": auth["application_credential_secret"],
            }
        else:
            raise exceptions.SDKError(f"unsupported openstack auth type '{auth_type}'")
        logger.debug(f"using authenticator type '{authenticator_type}'")
        return cls.create(
            base_url,
            authenticator_type = authenticator_type,
            auth_data = auth_data,
            default_tenancy_id = default_tenancy_id or auth.get("project_id"),
            **kwargs
        )

    @classmethod
    def from_environment(cls, base_url, **kwargs):
        """
        Returns a new Azimuth client configuration populated from the environment.
        """
        # We support the same environment variables as the openstack CLI
        os_cloud = os.environ.get("OS_CLOUD")
        if os_cloud:
            logger.debug("detected openstack environment variables")
            # Use the first file from the standard locations that exists
            for path in [
                os.environ.get("OS_CLIENT_CONFIG_FILE"),
                os.path.join(os.getcwd(), "clouds.yaml"),
                os.path.expanduser("~/.config/openstack/clouds.yaml"),
                "/etc/openstack/clouds.yaml",
            ]:
                if path:
                    if os.path.exists(path):
                        return cls.from_openstack_clouds_file(
                            base_url,
                            path,
                            os_cloud,
                            **kwargs
                        )
                    else:
                        logger.warn(f"file {path} does not exist")
            else:
                raise exceptions.SDKError("no openstack config file in standard locations")
        else:
            raise exceptions.SDKError("no suitable authentication found in environment")
