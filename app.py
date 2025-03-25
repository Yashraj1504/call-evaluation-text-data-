import streamlit as st
from langchain_groq import ChatGroq
import json

# Initialize LLM model
GROQ_API_KEY = "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"
llm = ChatGroq(
    model="Llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=GROQ_API_KEY
)

# Streamlit Interface
st.title("Call Evaluation Analysis App")
conversation = st.text_area("Paste the call conversation here:")

criteria = [
    "Opening and Preparation",
    "Call Closing",
    "Temp Check",
    "Disposition",
    "Product Knowledge",
    "Attitude",
    "Voice",
    "Mute/Hold",
    "Sales Pitch",
    "Understanding the Customer Issue",
    "Giving the Correct Resolution"
]

# Persistent results
if 'results' not in st.session_state:
    st.session_state['results'] = {}

# Identify Client and Agent
if st.button("Identify Client and Agent"):
    messages = [
        ("system", "You are an AI that identifies speakers in a conversation as either 'Client' or 'Agent'.\n"
                    "Classify each speaker as either 'Client' or 'Agent' based on their role in the conversation.\n"
                    "Respond in the following JSON format:\n"
                    "{\n"
                    '  "classification": {\n'
                    '    "speaker_0": "Client",\n'
                    '    "speaker_1": "Agent"\n'
                    '  }\n'
                    "}"),
        ("human", conversation)
    ]
    response = llm.invoke(messages)

    # Extract classification and replace speakers in conversation
    try:
        classification = json.loads(response.content)['classification']
        updated_conversation = conversation.replace("speaker_0", classification['speaker_0'])
        updated_conversation = updated_conversation.replace("speaker_1", classification['speaker_1'])
        st.session_state['updated_conversation'] = updated_conversation
        st.markdown("### Identified Speakers")
        st.json(classification)
    except Exception as e:
        st.error("Failed to classify speakers or update conversation format.")

# Show Updated Conversation Button
# if 'updated_conversation' in st.session_state:
#     if st.button("Show Updated Conversation"):
#         st.markdown("### Updated Conversation")
#         st.text_area("Updated Conversation", st.session_state['updated_conversation'], height=300)

# Individual Buttons for Each Criterion
for item in criteria:
    if st.button(f"Analyze {item}"):
        conversation_input = st.session_state.get('updated_conversation', conversation)
        messages = [
            ("system", f"""
            Analyze the provided conversation based on the criterion: {item}.  
            Provide the response in the following concise format:  

            **{item}**  
            - **Evaluation:** [Brief evaluation highlighting key points]  
            - **Example from Call:** [Short, relevant quote or reference from the conversation]    
            """),
            ("human", conversation_input)
        ]

        ai_response = llm.invoke(messages)
        st.session_state['results'][item] = ai_response.content

# Display Results
for item, result in st.session_state['results'].items():
    st.markdown(f"### {item}")
    st.write(result)
    st.markdown("---")
