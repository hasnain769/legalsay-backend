import pytest
import asyncio
from backend.classifier import ClassifierAgent, ContractType, ClassifierOutput
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os

# Mock environment for testing
os.environ["GOOGLE_API_KEY"] = "test_key" # This won't actually work for real calls, but we need it set.
# Ideally we'd mock the LLM response, but for this environment we might rely on the real one if keys are set in the env.
# If keys are not set, this test will fail. Assuming the user has keys set in their environment.

@pytest.mark.asyncio
async def test_classifier_irrelevant():
    agent = ClassifierAgent()
    
    # Text that is clearly irrelevant
    irrelevant_text = "Here is a recipe for chocolate cake. Mix flour, sugar, and eggs. Bake at 350 degrees."
    
    runner = Runner(agent=agent, app_name="test_app", session_service=InMemorySessionService())
    session_id = "test_session_irrelevant"
    await runner.session_service.create_session(app_name="test_app", user_id="test_user", session_id=session_id)
    
    content = types.Content(role='user', parts=[types.Part(text=irrelevant_text)])
    events = runner.run(user_id="test_user", session_id=session_id, new_message=content)
    
    final_text = ""
    for event in events:
        if event.is_final_response() and event.content:
            final_text = event.content.parts[0].text.strip()
            break
            
    print(f"Agent Response: {final_text}")
    
    # We expect the agent to return a JSON with "Irrelevant"
    assert "Irrelevant" in final_text
