import argparse
from typing import Any, Dict, List

from openai import OpenAI

from src.supabase_client import supabase
from src.config import OPENAI_API_KEY


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


def build_context_text(
    resource: Dict[str, Any],
    attributes: List[Dict[str, Any]],
) -> str:
    """
    Build a plain-text context description of the resource and its attributes
    to send to the LLM.
    """
    lines: List[str] = []

    lines.append(
        f"Resource: {resource['provider']}.{resource['resource_name']} "
        f"(version {resource['version']})"
    )
    lines.append(f"Documentation URL: {resource['doc_url']}")
    lines.append("")
    lines.append("Attributes:")

    if not attributes:
        lines.append("  (no attributes found)")
        return "\n".join(lines)

    for attr in attributes:
        name = attr["attribute_name"]
        required = attr.get("required")
        required_label = "required" if required else "optional"
        attr_type = attr.get("attr_type") or "unknown"
        version_added = attr.get("version_added") or "n/a"
        version_removed = attr.get("version_removed") or ""
        description = attr.get("description") or ""

        lines.append(f"- {name}")
        lines.append(f"  Type: {attr_type}")
        lines.append(f"  Required: {required_label}")
        lines.append(f"  Since: {version_added}")
        if version_removed:
            lines.append(f"  Removed in: {version_removed}")
        lines.append("  Description:")
        lines.append(f"    {description}")
        lines.append("")

    return "\n".join(lines)


def call_llm_explanation(
    context_text: str,
    resource_name: str,
    version: str,
    language: str = "en",
    model: str = "gpt-4o-mini",
) -> str:
    """
    Call the LLM to generate a human-friendly explanation of the resource
    and its attributes based on the provided context_text.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Set it in your .env file to use LLM features."
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    if language.lower().startswith("de"):
        language_text = "German"
    else:
        language_text = "English"

    system_prompt = (
        "You are an expert Terraform assistant specializing in the hashicorp/azurerm "
        "provider. You receive structured documentation about a specific resource "
        "and its attributes for a given provider version.\n\n"
        "Your job is to explain the resource and its attributes clearly and accurately, "
        "without inventing attributes or versions that are not in the provided context. "
        "If something is not present in the context, say that you don't have that "
        "information.\n\n"
        "Focus on:\n"
        "- listing all attributes with short, clear explanations\n"
        "- highlighting whether they are required or optional\n"
        "- mentioning from which version they are available if given\n"
        "- referencing the provided documentation URL.\n"
    )

    user_prompt = (
        f"Explain the Terraform resource '{resource_name}' for provider version "
        f"'{version}' in {language_text}.\n\n"
        "Use the following documentation as your only source of truth:\n\n"
        f"{context_text}\n\n"
        "Do not invent additional attributes or options. If you are unsure about "
        "something because it is not in the context, say so explicitly."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content or ""


def generate_resource_explanation(
    resource_name: str,
    version: str,
    language: str = "en",
    model: str = "gpt-4o-mini",
) -> str:
    """
    High-level function that:
    - fetches the resource and its attributes from Supabase,
    - builds the context,
    - calls the LLM,
    - and returns the explanation text.
    """
    resource = fetch_resource(resource_name, version)
    attributes = fetch_attributes(resource["id"])
    context_text = build_context_text(resource, attributes)

    explanation = call_llm_explanation(
        context_text=context_text,
        resource_name=resource_name,
        version=version,
        language=language,
        model=model,
    )
    return explanation


def main() -> None:
    """
    CLI entry point: allows calling this script from the command line.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Fetch a Terraform resource and its attributes from Supabase and ask "
            "an LLM to explain them."
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
    parser.add_argument(
        "--language",
        default="en",
        help="Language of the explanation, e.g. 'en' or 'de' (default: en)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI chat model name (default: gpt-4o-mini)",
    )

    args = parser.parse_args()

    try:
        explanation = generate_resource_explanation(
            resource_name=args.resource,
            version=args.version,
            language=args.language,
            model=args.model,
        )
    except Exception as e:
        print(f"❌ Failed to generate explanation: {e}")
        return

    print("\n================ LLM Explanation ================\n")
    print(explanation)
    print("\n=================================================\n")


if __name__ == "__main__":
    main()
