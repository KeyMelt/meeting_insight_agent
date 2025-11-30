import streamlit as st
import os
from dotenv import load_dotenv
from agent import MeetingAgent

load_dotenv()

st.set_page_config(page_title="Meeting Insight Agent", layout="wide")

st.title("🤖 Meeting Insight Agent")
st.markdown("### Enterprise Agent for Action Item Extraction")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Try to load API key from environment
    env_api_key = os.getenv("GOOGLE_API_KEY")
    
    if env_api_key:
        st.success("API Key loaded from environment ✅")
        api_key = env_api_key
    else:
        api_key = st.text_input("Enter Google Gemini API Key", type="password")
        st.info("Get your API key from [Google AI Studio](https://aistudio.google.com/)")

if not api_key:
    st.warning("Please enter your API Key in the sidebar to proceed.")
    st.stop()

# Initialize Agent
if "agent" not in st.session_state:
    st.session_state.agent = MeetingAgent(api_key)

# Main Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Meeting Transcript")
    transcript = st.text_area("Paste your meeting transcript here:", height=400, placeholder="Speaker A: ...")
    
    analyze_btn = st.button("Analyze Transcript", type="primary")

if analyze_btn and transcript:
    with st.spinner("Analyzing transcript..."):
        try:
            analysis = st.session_state.agent.analyze_transcript(transcript)
            st.session_state.analysis = analysis
            st.success("Analysis Complete!")
        except Exception as e:
            st.error(f"Error during analysis: {e}")

# Display Results
if "analysis" in st.session_state:
    analysis = st.session_state.analysis
    
    with col2:
        st.subheader("📊 Insights")
        
        st.markdown("#### Summary")
        st.write(analysis.get("summary", "No summary available."))
        
        st.markdown("#### Decisions")
        for decision in analysis.get("decisions", []):
            st.success(f"✅ {decision}")
            
        st.markdown("#### Action Items")
        action_items = analysis.get("action_items", [])
        
        if not action_items:
            st.info("No action items found.")
        
        # Form to review and execute actions
        with st.form("actions_form"):
            selected_actions = []
            updated_emails = {} # Store user-provided emails
            
            for i, item in enumerate(action_items):
                st.markdown(f"**{i+1}. {item.get('description')}**")
                
                # Check for unknown email if type is 'email'
                if item.get('type') == 'email':
                    assignee = item.get('assignee')
                    # We need to check if this assignee resolves to an email
                    from employees import get_email_for_name
                    resolved_email = get_email_for_name(assignee)
                    
                    if not resolved_email:
                        st.warning(f"⚠️ Email for '{assignee}' not found.")
                        user_email = st.text_input(f"Enter email for {assignee}:", key=f"email_{i}")
                        if user_email:
                            updated_emails[i] = user_email
                            st.caption(f"Using: {user_email}")
                    else:
                        st.caption(f"Assignee: {assignee} ({resolved_email}) | Type: {item.get('type')}")
                else:
                    st.caption(f"Assignee: {item.get('assignee')} | Type: {item.get('type')}")
                
                # Checkbox to select for execution
                if st.checkbox(f"Execute this action ({item.get('type')})", key=f"action_{i}"):
                    # Inject the user-provided email into the item details if needed
                    if i in updated_emails:
                        item['details']['to'] = updated_emails[i]
                    selected_actions.append(item)
                
                st.divider()
            
            execute_btn = st.form_submit_button("Execute Selected Actions")
            
            if execute_btn:
                if selected_actions:
                    with st.spinner("Executing actions..."):
                        results = st.session_state.agent.execute_actions(selected_actions)
                        for res in results:
                            st.toast(res)
                        st.success(f"Executed {len(selected_actions)} actions.")
                else:
                    st.warning("No actions selected.")

    # Debug View (Observability)
    with st.expander("🔍 View Raw Analysis (Observability Log)"):
        st.json(analysis)

    # View Mock Tool State
    st.divider()
    st.subheader("🛠️ Mock Tool State (Simulation)")
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        st.markdown("**Sent Emails**")
        st.json(st.session_state.agent.email_service.get_sent_emails())
        
    with t_col2:
        st.markdown("**Created Tickets**")
        st.json(st.session_state.agent.ticket_service.get_tickets())
