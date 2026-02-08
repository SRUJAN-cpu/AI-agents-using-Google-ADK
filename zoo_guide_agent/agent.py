import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.llms import VertexAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

# --- Add a tool to get zoo animal data ---
def get_zoo_animal_data(tool_context: ToolContext, animal_name: str) -> str:
    """Retrieves specific data about animals currently at our zoo."""
    # Mock data for demonstration
    zoo_db = {
        "lion": "We have Simba (10 years old) and Nala (8 years old) at the 'African Savanna' exhibit.",
        "penguin": "We have 15 Gentoo penguins at the 'Polar Outpost'. Feeding time is 2:00 PM.",
        "elephant": "Our elephant, Jumbo, is 25 years old and lives in the 'Elephant Sanctuary'."
    }
    animal_key = animal_name.lower()
    return zoo_db.get(animal_key, f"We don't currently have {animal_name} at our zoo, but I can tell you general facts about them.")

# Greet user and save their prompt

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}

# Configuring the Wikipedia Tool
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

# 1. Researcher Agent
comprehensive_researcher = Agent(
    name="comprehensive_researcher",
    model=model_name,
    description="The primary researcher that can access both internal zoo data and external knowledge from Wikipedia.",
    instruction="""
    You are a helpful research assistant. Your goal is to fully answer the user's PROMPT.
    You have access to two tools:
    1. A tool for getting specific data about animals AT OUR ZOO (names, ages, locations).
    2. A tool for searching Wikipedia for general knowledge (facts, lifespan, diet, habitat).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one tool, use that tool.
    - If the prompt is complex and requires information from both the zoo's database AND Wikipedia,
      you MUST use both tools to gather all necessary information.
    - Synthesize the results from the tool(s) you use into preliminary data outputs.

    PROMPT:
    { PROMPT }
    """,
    tools=[
        wikipedia_tool,
        get_zoo_animal_data
    ],
    output_key="research_data" # A key to store the combined findings
)

# 2. Response Formatter Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all information into a friendly, readable response.",
    instruction="""
    You are the friendly voice of the Zoo Tour Guide. Your task is to take the
    RESEARCH_DATA and present it to the user in a complete and helpful answer.

    - First, present the specific information from the zoo (like names, ages, and where to find them).
    - Then, add the interesting general facts from the research.
    - If some information is missing, just present the information you have.
    - Be conversational and engaging.

    RESEARCH_DATA:
    { research_data }
    """
)

tour_guide_workflow = SequentialAgent(
    name="tour_guide_workflow",
    description="The main workflow for handling a user's request about an animal.",
    sub_agents=[
        comprehensive_researcher, # Step 1: Gather all data
        response_formatter,       # Step 2: Format the final response
    ]
)

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point for the Zoo Tour Guide.",
    instruction="""
    - Let the user know you will help them learn about the animals we have in the zoo.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    After using the tool, transfer control to the 'tour_guide_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[tour_guide_workflow]
)

# --- Run the agent as a web service ---
if __name__ == "__main__":
    # The ADK automatically picks up the PORT environment variable.
    # The default host is "0.0.0.0" which is required by Cloud Run.
    logging.info("Starting agent server...")
    root_agent.serve()
    logging.info("Agent server stopped.")