import streamlit as st

from src.llm.explain_resource import generate_resource_explanation


def main() -> None:
    st.set_page_config(page_title="Terraform LLM Assistant", layout="wide")

    st.title("Terraform LLM Assistant")
    st.caption("Explain Terraform azurerm resources for specific provider versions.")

    with st.sidebar:
        st.header("Configuration")
        resource_name = st.text_input(
            "Resource name",
            value="azurerm_storage_account",
            help="Terraform resource name, e.g. azurerm_storage_account",
        )
        version = st.text_input(
            "Provider version",
            value="4.52.0",
            help="Provider version, e.g. 4.52.0",
        )
        language = st.selectbox(
            "Explanation language",
            options=["en", "de"],
            index=0,
        )
        model = st.text_input(
            "OpenAI model",
            value="gpt-4o-mini",
            help="Name of the OpenAI chat model to use.",
        )

        explain_button = st.button("Explain resource")

    if explain_button:
        if not resource_name or not version:
            st.error("Please provide both a resource name and a version.")
            return

        with st.spinner("Generating explanation using LLM..."):
            try:
                explanation = generate_resource_explanation(
                    resource_name=resource_name,
                    version=version,
                    language=language,
                    model=model,
                )
            except Exception as e:
                st.error(f"Failed to generate explanation: {e}")
                return

        st.subheader("LLM Explanation")
        st.markdown(explanation)


if __name__ == "__main__":
    main()
