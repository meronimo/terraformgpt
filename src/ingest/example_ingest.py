from src.supabase_client import supabase
from src.models import ResourceInput, AttributeInput


def ingest_resource(resource: ResourceInput) -> None:
    """
    Insert a single resource and its attributes into the database.
    """
    # 1. Insert the resource row
    try:
        result = (
            supabase
            .table("resource")
            .insert({
                "provider": resource.provider,
                "resource_name": resource.resource_name,
                "version": resource.version,
                "doc_url": resource.doc_url,
            })
            .execute()
        )
    except Exception as e:
        print("❌ Error inserting resource:", e)
        return

    if not result.data:
        print("❌ Resource insert returned no data.")
        return

    inserted_resource = result.data[0]
    resource_id = inserted_resource["id"]

    # 2. Prepare attribute rows
    attributes_to_insert = [
        {
            "resource_id": resource_id,
            "attribute_name": a.attribute_name,
            "description": a.description,
            "required": a.required,
            "attr_type": a.attr_type,
            "version_added": a.version_added or resource.version,
            "version_removed": a.version_removed,
            "doc_anchor": a.doc_anchor,
        }
        for a in resource.attributes
    ]

    # 3. Insert attributes
    try:
        attr_result = (
            supabase
            .table("attribute")
            .insert(attributes_to_insert)
            .execute()
        )
    except Exception as e:
        print("❌ Error inserting attributes:", e)
        return

    if not attr_result.data:
        print("⚠️ Attributes insert returned no data (but may still have succeeded).")
    else:
        print(
            f"✅ Inserted {len(attributes_to_insert)} attributes for "
            f"resource '{resource.resource_name}' version '{resource.version}'."
        )


def main() -> None:
    """
    Example: ingest a single azurerm_storage_account resource with a few attributes.
    Replace this later with real scraped data.
    """
    example = ResourceInput(
        provider="azurerm",
        resource_name="azurerm_storage_account",
        version="4.52.0",
        doc_url=(
            "https://registry.terraform.io/providers/"
            "hashicorp/azurerm/4.52.0/docs/resources/storage_account"
        ),
        attributes=[
            AttributeInput(
                attribute_name="name",
                description="The name of the storage account.",
                required=True,
                attr_type="string",
                version_added="4.0.0",
                doc_anchor="#name",
            ),
            AttributeInput(
                attribute_name="resource_group_name",
                description=(
                    "The name of the resource group in which to "
                    "create the storage account."
                ),
                required=True,
                attr_type="string",
                version_added="4.0.0",
                doc_anchor="#resource_group_name",
            ),
        ],
    )

    ingest_resource(example)


if __name__ == "__main__":
    main()
