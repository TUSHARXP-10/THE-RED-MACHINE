import streamlit as st
import pandas as pd
import json
from datetime import datetime

PROMPT_LOG_FILE = 'prompt_log.json'

def load_prompts():
    try:
        with open(PROMPT_LOG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_prompts(prompts):
    with open(PROMPT_LOG_FILE, 'w') as f:
        json.dump(prompts, f, indent=4)

def log_prompt(prompt_text, strategy_id=None, pnl=None, version=1.0):
    prompts = load_prompts()
    new_prompt = {
        'id': len(prompts) + 1,
        'timestamp': datetime.now().isoformat(),
        'prompt_text': prompt_text,
        'strategy_id': strategy_id,
        'pnl': pnl,
        'version': version,
        'status': 'active' # e.g., active, retired, experimental
    }
    prompts.append(new_prompt)
    save_prompts(prompts)
    return new_prompt

def update_prompt_performance(prompt_id, pnl):
    prompts = load_prompts()
    for prompt in prompts:
        if prompt['id'] == prompt_id:
            prompt['pnl'] = pnl
            break
    save_prompts(prompts)

def get_prompt_by_id(prompt_id):
    prompts = load_prompts()
    for prompt in prompts:
        if prompt['id'] == prompt_id:
            return prompt
    return None

def prompt_tracking_dashboard():
    st.header("AI Prompt Tracking System")

    prompts = load_prompts()
    df = pd.DataFrame(prompts)

    if not df.empty:
        st.subheader("Logged Prompts")
        st.dataframe(df)

        st.subheader("Mutate High-Performing Prompts")
        prompt_ids = df['id'].tolist()
        selected_prompt_id = st.selectbox("Select Prompt ID to Mutate", prompt_ids)

        if selected_prompt_id:
            selected_prompt = get_prompt_by_id(selected_prompt_id)
            if selected_prompt:
                st.write(f"Current Prompt Text: {selected_prompt['prompt_text']}")
                new_prompt_text = st.text_area("New Prompt Text", value=selected_prompt['prompt_text'], height=150)
                new_version = st.number_input("New Version", value=selected_prompt['version'] + 0.1, step=0.1)
                new_status = st.selectbox("New Status", ['active', 'retired', 'experimental'], index=['active', 'retired', 'experimental'].index(selected_prompt['status']))

                if st.button("Update Prompt"):
                    for i, prompt in enumerate(prompts):
                        if prompt['id'] == selected_prompt_id:
                            prompts[i]['prompt_text'] = new_prompt_text
                            prompts[i]['version'] = new_version
                            prompts[i]['status'] = new_status
                            prompts[i]['timestamp'] = datetime.now().isoformat() # Update timestamp on mutation
                            break
                    save_prompts(prompts)
                    st.success("Prompt updated successfully!")
                    st.rerun()
            else:
                st.warning("Selected prompt not found.")
    else:
        st.info("No prompts logged yet.")

    st.subheader("Log New Prompt")
    with st.form("new_prompt_form"):
        new_prompt_text_input = st.text_area("Prompt Text", height=100)
        new_prompt_strategy_id = st.text_input("Strategy ID (optional)")
        new_prompt_pnl = st.number_input("PnL (optional)", format="%.2f")
        submitted = st.form_submit_button("Log Prompt")
        if submitted:
            logged_prompt = log_prompt(new_prompt_text_input, new_prompt_strategy_id, new_prompt_pnl)
            st.success(f"Prompt logged with ID: {logged_prompt['id']}")
            st.rerun()

if __name__ == '__main__':
    prompt_tracking_dashboard()