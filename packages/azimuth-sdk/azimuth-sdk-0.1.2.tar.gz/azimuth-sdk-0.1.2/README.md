# azimuth-sdk

An SDK for interacting with [Azimuth](https://github.com/stackhpc/azimuth) resources using
[Python](https://www.python.org/).

Both synchronous use and asynchronous use, using the `async/await` syntax from
[asyncio](https://docs.python.org/3/library/asyncio.html), are supported.

## Installation

The Azimuth SDK can be installed from PyPI:

```sh
pip install azimuth-sdk
```

## Usage

To begin using the Azimuth SDK, you must first create a configuration object that defines how
to authenticate with Azimuth.

Currently, authentication with Azimuth uses [OpenStack](https://www.openstack.org/) credentials.
Azimuth supports two user-facing authentication methods:

  * Username + Password
  * [Keystone federation](https://docs.openstack.org/keystone/latest/admin/federation/introduction.html)

The Keystone federation flow requires a browser, so is not supported by the Azimuth SDK.

Azimuth also supports authenticating with an
[application credential](https://docs.openstack.org/keystone/latest/user/application_credentials.html).
This authentication method is usually hidden from browser-based users, but is available for use
by the SDK. **This is the recommended authentication method.**

The SDK `Configuration` object can be initialised either using known credentials or from a
[clouds.yaml file](https://docs.openstack.org/python-openstackclient/pike/configuration/index.html).
The Azimuth SDK respects the same `OS_CLOUD` and `OS_CLIENT_CONFIG_FILE` environment variables that
the [OpenStack CLI](https://docs.openstack.org/python-openstackclient/latest/) respects.

```python
from azimuth_sdk import Configuration


AZIMUTH_URL = "https://portal.azimuth.example.org"

# Initialise from variables
config = Configuration.create(
    AZIMUTH_URL,
    authenticator = "appcred",
    auth_data = {
        "application_credential_id": "<application credential id>",
        "application_credential_secret": "<application credential secret>",
    },
    # Optionally set a default tenancy
    default_tenancy_id = "<tenancy id>"
)

# Initialise from a specific clouds.yaml file
config = Configuration.from_openstack_clouds_file(
    AZIMUTH_URL,
    "/path/to/openstack/clouds.yaml"
)

# Initialise from environment variables
config = Configuration.from_environment(AZIMUTH_URL)
```

Once you have a `Configuration` object, it can be used to create either synchronous or
asynchronous clients with which you can interact with Azimuth, e.g. by listing the
available tenancies:

```python
# Synchronous client
with config.sync_client() as client:
    for tenancy in client.tenancies().list():
        print(tenancy.name)

# Asynchronous client
async with config.async_client() as client:
    async for tenancy in client.tenancies().list():
        print(tenancy.name)
```

> **WARNING**
>
> It is important that the client is used inside a `with` or `async with` block, for
> synchronous or asynchronous clients respectively, as this ensures that resources
> are set up and released as required.
>
> See Python's [contextlib](https://docs.python.org/3/library/contextlib.html) for more information.

You can then interact with resources for a tenancy. The following resources are available:

```python
# Interact with the images for a tenancy
client.images(tenancy_id = None)
# Interact with the sizes for a tenancy
client.sizes(tenancy_id = None)
# Interact with the volumes for a tenancy
client.volumes(tenancy_id = None)
# Interact with the external IPs for a tenancy
client.external_ips(tenancy_id = None)
# Interact with the machines for a tenancy
client.machines(tenancy_id = None)
# Interact with the CaaS cluster types for a tenancy
client.cluster_types(tenancy_id = None)
# Interact with the CaaS clusters for a tenancy
client.clusters(tenancy_id = None)
# Interact with the Kubernetes templates for a tenancy
client.kubernetes_cluster_templates(tenancy_id = None)
# Interact with the Kubernetes clusters for a tenancy
client.kubernetes_clusters(tenancy_id = None)
# Interact with the Kubernetes app templates for a tenancy
client.kubernetes_app_templates(tenancy_id = None)
# Interact with the Kubernetes apps for a tenancy
client.kubernetes_apps(tenancy_id = None)
```

For each of these methods, the `tenancy_id` is optional. If it is not given, a default
tenancy ID will be used, which is determined as follows:

  * Explicitly set when the `Configuration` is created
  * From `clouds.{cloud}.auth.project_id` in the `clouds.yaml`, if present
  * As the first available tenancy in the tenancy list (may not be deterministic)

The default tenancy for a client can also be changed using the `switch_tenancy` method:

```python
client.switch_tenancy(new_tenancy_id)
```

Each of these returns a `Resource` object, which can be interacted with as follows.

> **NOTE**
>
> The sync methods are available on resources produced by synchronous clients
> (i.e. created using `config.sync_client`), and the
> async methods on resources produced by asynchronous clients
> (i.e. created using `config.async_client`).

```python
# List instances
#   sync
for instance in resource.list():
    print(instance)
#   async
async for instance in resource.list():
    print(instance)

# Get the first instance from a list response
#   sync
instance = resource.first()
#   async
instance = await resource.first()

# Fetch an instance by ID
#   sync
instance = resource.fetch("<id>")
#   async
instance = await resource.fetch("<id>")

# Create a new instance
#   sync
instance = resource.create({"name": "my-instance", "<prop>": "<value>"})
#   async
instance = await resource.create({ "name": "my-instance", "<prop>": "<value>"})

# Replace an instance by ID (PUT request)
#   sync
instance = resource.replace("<id>", {"name": "my-instance", "<prop>": "<value>"})
#   async
instance = await resource.replace("<id>", {"name": "my-instance", "<prop>": "<value>"})

# Patch an instance by ID (PATCH request)
#   sync
instance = resource.patch("<id>", {"<prop>": "<value>"})
#   async
instance = await resource.patch("<id>", {"<prop>": "<value>"})

# Replace an instance by ID, or create it (using the same data) if it doesn't exist
#   sync
instance = resource.create_or_replace("<id>", {"name": "my-instance", "<prop>": "<value>"})
#   async
instance = await resource.create_or_replace("<id>", {"name": "my-instance", "<prop>": "<value>"})

# Patch an instance by ID, or create it (using the same data) if it doesn't exist
#   sync
instance = resource.create_or_patch("<id>", {"<prop>": "<value>"})
#   async
instance = await resource.create_or_patch("<id>", {"<prop>": "<value>"})

# Delete an instance by ID
#   sync
instance = resource.delete("<id>")
#   async
instance = await resource.delete("<id>")
```
