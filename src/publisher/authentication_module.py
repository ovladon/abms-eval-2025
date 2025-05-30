# Basic authentication
def check_password():
    """Simple password check for access control."""
    def password_entered():
        if st.session_state["password"] == "AaBbMmSs7":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # remove it once validated
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password", type="password", key="password", on_change=password_entered)
        st.stop()  # Halt app until password is provided
    elif not st.session_state["password_correct"]:
        st.error("Incorrect password")
        st.stop()

check_password()
