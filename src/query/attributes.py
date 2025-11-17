import argparse
from typing import Any, Dict, List

from src.supabase_client import supabase


def fetch_resource(resource_name: str, version: str) -> Dict[str, Any]:
    """
    Fetch a single resource row from the database by resource_name and version.
    """
    try:
        response = (
            supabase
            .table("resource")
            .select("*")
            .eq("resource_name", resource_name)
            .eq("version", version)
            .execute()
        )
    except Exception as e:
        raise RuntimeError(f"Supabase query for resource failed: {e}") from e

    if not response.data:
        raise RuntimeError(
            f"No resource found for name={resource_name!r}, version={version!r}."
        )

    return response.data[0]


def fetch_attributes(resource_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all attributes for a given resource_id.
    """
    try:
        response = (
            supabase
            .table("attribute")
            .select("*")
            .eq("resource_id", resource_id)
            .order("attribute_name")
            .execute()
        )
    except Exception as e:
        raise RuntimeError(f"Supabase query for attributes failed: {e}") from e

    return response.data or []


def print_attributes(
    resource: Dict[str, Any],
    attributes: List[Dict[str, Any]],
) -> None:
    """
    Pretty-print the resource and its attributes to the console.
    """
    print()
    print(
        f"Resource: {resource['provider']}.{resource['resource_name']} "
        f"(version {resource['version']})"
    )
    print(f"Doc URL: {resource['doc_url']}")
    print("-" * 80)

    if not attributes:
        print("No attributes found.")
        return

    for attr in attributes:
        required = attr.get("required")
        required_label = "required" if required else "optional"
        attr_type = attr.get("attr_type") or "unknown"
        version_added = attr.get("version_added") or "n/a"
        version_removed = attr.get("version_removed") or ""
        description = attr.get("description") or ""

        print(f"Attribute: {attr['attribute_name']}")
        print(f"  Type:        {attr_type}")
        print(f"  Required?:   {required_label}")
        print(f"  Since:       {version_added}")
        if version_removed:
            print(f"  Removed in:  {version_removed}")
        print("  Description:")
        print(f"    {description}")
        print("-" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch and display all attributes for a Terraform resource from Supabase."
        )
    )
    parser.add_argument(
        "--resource",
        required=True,
        help="Resource name, e.g. azurerm_storage_account",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Provider version, e.g. 4.52.0",
    )

    args = parser.parse_args()
    resource_name: str = args.resource
    version: str = args.version

    try:
        resource = fetch_resource(resource_name, version)
        attributes = fetch_attributes(resource["id"])
    except RuntimeError as e:
        print(f"❌ {e}")
        return

    print_attributes(resource, attributes)


if __name__ == "__main__":
    main()
