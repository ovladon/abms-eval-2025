import streamlit as st
import re
import binascii
from aspect_based_metadata_decoder import decode_aspect_based_metadata
from result_presenter import ResultPresenter
from content_speculation import ContentSpeculator

def main():
    st.title("Reader Application")
    st.write("Enter the aspect based metadata and the corresponding encryption key to decode the analysis results.")

    aspect_based_metadata = st.text_area("aspect based metadata").strip()
    encryption_key_hex = st.text_input("Encryption Key (hex)").strip()

    # Option to select output format
    output_format = st.selectbox("Select Output Format", options=['Human-readable', 'Machine-readable'])

    # Initialize session state variables if not already done
    if 'analysis_results' not in st.session_state:
        st.session_state['analysis_results'] = None

    if st.button("Decode aspect based metadata"):
        if not aspect_based_metadata or not encryption_key_hex:
            st.error("Please enter both the aspect based metadata and the encryption key.")
            return

        # Check that encryption_key_hex contains only hexadecimal characters
        if not re.fullmatch(r'[0-9a-fA-F]+', encryption_key_hex):
            st.error("Invalid encryption key format. Please ensure it is a valid hexadecimal string.")
            return

        try:
            # Remove any extraneous whitespace/newlines
            encryption_key_hex = encryption_key_hex.replace('\n', '').replace(' ', '')
            encryption_key = binascii.unhexlify(encryption_key_hex)
            analysis_wrapper = decode_aspect_based_metadata(aspect_based_metadata, encryption_key)
            if analysis_wrapper is None or 'analysis_results' not in analysis_wrapper:
                st.error("Failed to decode the aspect based metadata. Please check the aspect based metadata and encryption key.")
                return

            analysis_results = analysis_wrapper['analysis_results']
            st.session_state['analysis_results'] = analysis_results
            display_results(analysis_results, output_format)

        except (ValueError, binascii.Error):
            st.error("Invalid encryption key format. Please ensure it is a valid hexadecimal string.")
        except Exception as e:
            st.error(f"An error occurred during decoding: {str(e)}")

    elif st.session_state['analysis_results'] is not None:
        display_results(st.session_state['analysis_results'], output_format)
    else:
        st.write("Please enter the aspect based metadata and the encryption key.")

def display_results(analysis_results, output_format):
    presenter = ResultPresenter(analysis_results)
    presenter.present_in_streamlit()

    st.subheader("Content Speculation")
    speculator = ContentSpeculator(analysis_results)
    if output_format == 'Machine-readable':
        matched_categories = speculator.speculate_content(output_format='machine')
        st.write("**Inferred Content Categories (Machine-readable):**")
        if matched_categories:
            st.json(matched_categories)
        else:
            st.write("No inferred content categories could be determined from the analysis results.")

        matched_synergies = speculator.speculate_synergies(output_format='machine')
        st.write("**Inferred Synergies (Machine-readable):**")
        if matched_synergies:
            st.json(matched_synergies)
        else:
            st.write("No significant inferred synergies could be determined from the current analysis.")
    else:
        matched_categories = speculator.speculate_content(output_format='human')
        st.write("**Inferred Content Categories (Human-readable):**")
        if matched_categories:
            for category in matched_categories:
                st.write(f"**Inferred Content Category:** {category['name']}")
                st.write(f"**Description:** {category['human_description']}")
                st.write(f"**Related Keywords:** {', '.join(category['keywords'])}")
                st.write("**References:**")
                for ref in category.get('references', []):
                    st.write(f"- [{ref['reference']}]({ref['reference']}): {ref['reference_explanation']}")
                st.write(f"**Confidence Score:** {category['confidence_score']}")
                st.write("---")
        else:
            st.write("No inferred content categories could be determined from the analysis results.")

        matched_synergies = speculator.speculate_synergies(output_format='human')
        st.write("**Inferred Synergies (Human-readable):**")
        if matched_synergies:
            for synergy in matched_synergies:
                st.write(f"**Inferred Synergy:** {synergy['name']}")
                st.write(f"**Description:** {synergy['human_description']}")
                st.write(f"**Aspects Involved:** {', '.join(synergy['aspects_involved'])}")
                st.write("**References:**")
                for ref in synergy.get('references', []):
                    st.write(f"- [{ref['reference']}]({ref['reference']}): {ref['reference_explanation']}")
                st.write(f"**Confidence Score:** {synergy['confidence_score']}")
                st.write("---")
        else:
            st.write("No significant inferred synergies could be determined from the current analysis.")

if __name__ == "__main__":
    main()

