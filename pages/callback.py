import streamlit as st
import asyncio
from services.docusign_service import DocuSignClient

def callback_page():
    st.title("DocuSign Authentication")
    
    # Handle callback
    if 'code' in st.query_params:
        code = st.query_params['code']
        
        with st.spinner("Authenticating with DocuSign..."):
            # Exchange code for token
            client = DocuSignClient()
            token_data = asyncio.run(client.get_token(code))
            
            if token_data and 'access_token' in token_data:
                # Store complete token data and client in session state
                st.session_state.docusign_token = token_data
                client.access_token = token_data['access_token']
                st.session_state.docusign_client = client
                st.session_state.docusign_authenticated = True
                
                # Get and store account ID
                account_id = asyncio.run(client.get_account_id())
                if account_id:
                    st.session_state.docusign_account_id = account_id
                
                st.success("Successfully authenticated with DocuSign!")
                st.markdown("""
                    <meta http-equiv="refresh" content="2;url=/" />
                    Redirecting back to main page...
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.error("Authentication failed")
                if st.button("Try Again"):
                    st.query_params.clear()
                    st.rerun()
    else:
        st.error("No authentication code found")
        if st.button("Return to Home"):
            st.query_params.clear()
            st.rerun()

if __name__ == "__main__":
    callback_page() 