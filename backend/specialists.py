from google.adk.agents.llm_agent import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.genai import types
from google.genai.types import ThinkingConfig
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Schemas ---

class GeneralParserOutput(BaseModel):
    parties: List[str] = Field(description="List of parties involved in the contract.")
    effective_date: Optional[str] = Field(description="The effective date of the contract.")

class NDAParserOutput(BaseModel):
    term_duration: Optional[str] = Field(description="The duration of the confidentiality obligations.")
    confidential_info_definition: Optional[str] = Field(description="Summary of what is defined as confidential information.")

class SOWParserOutput(BaseModel):
    fees: Optional[str] = Field(description="The fee structure or total amount.")
    deliverables: List[str] = Field(description="List of deliverables or services to be provided.")

class RiskAgentOutput(BaseModel):
    red_flags: List[str] = Field(description="List of critical risks found.")
    yellow_flags: List[str] = Field(description="List of moderate risks found.")
    green_flags: List[str] = Field(description="List of positive clauses found.")

# --- Agents ---

class GeneralParserAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model='gemini-2.0-flash',
            name='general_parser',
            instruction="Extract the parties and effective date from the contract.",
            planner=BuiltInPlanner(thinking_config=ThinkingConfig(include_thoughts=True)),
            output_schema=GeneralParserOutput,
        )

class NDAParserAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model='gemini-2.0-flash',
            name='nda_parser',
            instruction="Extract the term duration and definition of confidential information from the NDA.",
            planner=BuiltInPlanner(thinking_config=ThinkingConfig(include_thoughts=True)),
            output_schema=NDAParserOutput,
        )

class SOWParserAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model='gemini-2.0-flash',
            name='sow_parser',
            instruction="Extract the fees and deliverables from the Freelance/Service Agreement.",
            planner=BuiltInPlanner(thinking_config=ThinkingConfig(include_thoughts=True)),
            output_schema=SOWParserOutput,
        )

class RiskAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model='gemini-2.0-flash',
            name='risk_agent',
            instruction="""You are a cynical, highly experienced senior partner at a top law firm.
            Your job is to protect your client (the Recipient/Service Provider usually, but be neutral if unclear) from dangerous terms.
            
            You will be provided with:
            1. The Contract Text.
            2. The Jurisdiction (Governing Law).
            
            If a Jurisdiction is provided, you MUST apply its specific statutes and case law.
            For example:
            - If 'California': Non-competes are generally void (B&P Code 16600).
            - If 'New York': Non-competes are enforceable if reasonable.
            
            IMPORTANT: You have access to Google Search. You MUST use it to verify and cite specific statutes or case law for the given Jurisdiction.
            - If you flag a risk, cite the law in this format: "Risk Description. [CITATION: Law/Statute]"
            - Do not hallucinate laws. If you are unsure, search first.
            
            identify:
            - RED FLAGS: Critical risks, deal-breakers, illegal clauses (in the given jurisdiction), or highly unusual terms. Cite the law.
            - YELLOW FLAGS: Moderate risks, vague terms, or things that need clarification.
            - GREEN FLAGS: Good, standard, or fair clauses that protect the user.
            - MISSING CLAUSES: Check for standard protections that are absent (e.g., "Missing Mutual Indemnification", "Missing Termination for Convenience"). Flag these as YELLOW or RED depending on severity.

            OUTPUT FORMAT:
            You MUST return a valid JSON object with the following structure:
            {
                "red_flags": ["risk 1 [CITATION: Code § X]", "risk 2"],
                "yellow_flags": ["risk 3", "Missing Clause: X"],
                "green_flags": ["good clause 1"]
            }
            Do not wrap in markdown code blocks.
            """,
            tools=[google_search],
        )
