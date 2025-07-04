import json
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from plan_creator_bundle.plan_creator.state.agent_state import AgentState
from langchain_openai import ChatOpenAI
from plan_creator_bundle.plan_creator.models import SubactionList
from plan_creator_bundle.plan_creator.prompts.agent_2_prompt import (
    agent_2_system_prompt,
    agent_2_user_prompt,
)

import logging

logger = logging.getLogger(__name__)

from plan_creator_bundle.tools.tools import (
    retriever_sub_action_tool,
)

# Create the agents
model = ChatOpenAI(model="gpt-4o", temperature=0.0, seed=42)

# Define tools for the agent
tools = [retriever_sub_action_tool]


system_prompt_agent_2 = SystemMessage(agent_2_system_prompt)


def build_custom_agent_2():
    """Wrap create_react_agent to store final output in AgentState."""

    # The chain returned by create_react_agent
    react_chain = create_react_agent(
        model, tools, prompt=system_prompt_agent_2, response_format=SubactionList
    )

    def custom_agent_2(state: AgentState) -> AgentState:

        logger.info("Agent 2 start...")

        result_state = react_chain.invoke(
            {
                "messages": HumanMessage(
                    agent_2_user_prompt.format(
                        climate_action_data=json.dumps(
                            state["climate_action_data"], indent=2
                        ),
                        city_data=json.dumps(state["city_data"], indent=2),
                        response_agent_1=json.dumps(
                            state["response_agent_1"].model_dump(), indent=2
                        ),
                    )
                )
            }
        )

        # Extract the structured response from the result_state
        agent_output_structured: SubactionList = result_state["structured_response"]
        result_state["response_agent_2"] = agent_output_structured

        logger.info("Agent 2 done\n")
        return AgentState(**result_state)

    return custom_agent_2
