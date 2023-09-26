from bpkio_api.models import Tenant
from bpkio_cli.commands.template_crud import create_resource_group


def add_tenants_commands():
    return create_resource_group(
        "tenant",
        resource_class=Tenant,
        endpoint_path=["tenants"],
        aliases=["tnt", "tenants"],
        default_fields=["id", "name", "email", "state"],
    )
