import json
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from plan_creator_bundle.plan_creator.state.agent_state import AgentState
from langchain_openai import ChatOpenAI

from plan_creator_bundle.tools.tools import (
    retriever_indicators_tool,
)
from plan_creator_bundle.plan_creator.models import MerIndicatorList

import logging

logger = logging.getLogger(__name__)

from plan_creator_bundle.plan_creator.prompts.agent_7_prompt import (
    agent_7_system_prompt,
    agent_7_user_prompt,
)

# Create the agents
model = ChatOpenAI(model="gpt-4o", temperature=0.0, seed=42)

# model = ChatOpenAI(model="o3-mini", temperature=None)

# Define tools for the agent
tools = [retriever_indicators_tool]

# - sub-actions
# 4. Review the sub-actions for implementing the climate action that you are provided with.
system_prompt_agent_7 = SystemMessage(agent_7_system_prompt)


def build_custom_agent_7():
    """Wrap create_react_agent to store final output in AgentState."""

    # The chain returned by create_react_agent
    react_chain = create_react_agent(
        model, tools, prompt=system_prompt_agent_7, response_format=MerIndicatorList
    )

    def custom_agent_7(state: AgentState) -> AgentState:
        logger.info("Agent 7 start...")

        result_state = react_chain.invoke(
            {
                "messages": HumanMessage(
                    agent_7_user_prompt.format(
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
        agent_output_structured: MerIndicatorList = result_state["structured_response"]
        result_state["response_agent_7"] = agent_output_structured

        logger.info("Agent 7 done\n")
        return AgentState(**result_state)

    return custom_agent_7
