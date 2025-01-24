import streamlit as st
from services.docusign_service import DocuSignService

def callback_page():
    st.title("DocuSign Authentication")
    
    # Handle callback
    query_params = st.query_params
    if 'code' in query_params:
        docusign = DocuSignService()
        code = query_params['code'][0]
        state = query_params.get('state', [None])[0]
        
        if docusign.authenticate_with_code(code, state):
            st.session_state.docusign_authenticated = True
            st.session_state.access_token = docusign.access_token
            st.success("Successfully authenticated!")
            
            # Redirect back to main page
            st.markdown("""
                <meta http-equiv="refresh" content="1;url=/" />
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