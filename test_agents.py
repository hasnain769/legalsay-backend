import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
from app.core.logger import logging

# Load env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Import Agents
from backend.agent import root_agent, ContractAnalysisOutput
from backend.classifier import ClassifierAgent, ClassifierOutput
from backend.specialists import (
    GeneralParserAgent, NDAParserAgent, SOWParserAgent, RiskAgent,
    GeneralParserOutput, NDAParserOutput, SOWParserOutput, RiskAgentOutput
)
from main import run_agent
import json

async def run_test(filename, jurisdiction):
    print(f"\n\n{'='*50}")
    print(f"TESTING: {filename} ({jurisdiction})")
    print(f"{'='*50}")
    
    # Load Contract
    try:
        with open(f"test_data/{filename}", "r") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    print(f"Contract Loaded. Length: {len(text)} chars.")

    # 1. Classify
    print("\n1. CLASSIFYING...")
    classifier = ClassifierAgent()
    classification = await run_agent(classifier, text[:2000], ClassifierOutput)
    print(f"Result: {classification}")
    
    contract_type = "Other"
    if isinstance(classification, dict):
        contract_type = classification.get("contract_type", "Other")
    elif hasattr(classification, 'contract_type'):
        contract_type = classification.contract_type
        
    # 2. Specialist
    print(f"\n2. RUNNING SPECIALIST ({contract_type})...")
    specialist = GeneralParserAgent()
    specialist_model = GeneralParserOutput
    if contract_type == "NDA":
        specialist = NDAParserAgent()
        specialist_model = NDAParserOutput
    elif contract_type == "SOW" or contract_type == "Freelance Agreement":
        specialist = SOWParserAgent()
        specialist_model = SOWParserOutput
        
    specialist_result = await run_agent(specialist, text, specialist_model)
    print(f"Result: {specialist_result}")

    # 3. Risk Agent
    print("\n3. RUNNING RISK AGENT...")
    risk_agent = RiskAgent()
    risk_prompt = f"Jurisdiction: {jurisdiction}\n\nContract Text:\n{text}"
    risk_result = await run_agent(risk_agent, risk_prompt, RiskAgentOutput)
    print(f"Result: {json.dumps(risk_result, indent=2) if isinstance(risk_result, dict) else risk_result}")

    # 4. Synthesizer
    print("\n4. SYNTHESIZING...")
    synthesizer = root_agent
    synthesis_input = {
        "contract_type": contract_type,
        "specialist_findings": specialist_result,
        "risk_findings": risk_result,
        "jurisdiction": jurisdiction,
        "original_text_snippet": text[:2000] 
    }
    final_analysis = await run_agent(synthesizer, json.dumps(synthesis_input), ContractAnalysisOutput)
    print(f"\nFINAL ANALYSIS:\n{json.dumps(final_analysis, indent=2) if isinstance(final_analysis, dict) else final_analysis}")

async def test_baseline():
    tests = [
        ("risky_contract.txt", "California"),
        ("nda_ny.txt", "New York"),
        ("employment_ca.txt", "California"),
        ("saas_delaware.txt", "Delaware")
    ]
    
    for filename, jurisdiction in tests:
        await run_test(filename, jurisdiction)

if __name__ == "__main__":
    asyncio.run(test_baseline())
