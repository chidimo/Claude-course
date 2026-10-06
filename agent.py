import logging
import os

import anthropic
from dotenv import load_dotenv

from tools import tools

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("agent.log")],
    force=True,
    datefmt="[%Y-%m-%d %H:%M:%S]",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MAX_ITERATIONS = 10
MODEL = os.getenv("ANTHROPIC_MODEL")
API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not MODEL or not API_KEY:
    raise ValueError(
        "ANTHROPIC_MODEL and ANTHROPIC_API_KEY environment variables must be set."
    )

client = anthropic.Anthropic(api_key=API_KEY)


def run_tool(name, input_data):
    if name == "calculator":
        try:
            return str(eval(input_data.get("expression")))
        except Exception as e:
            logger.error(f"Error running tool {name} with input {input_data}: {e}")
            return str(e)
    if name == "web_search":
        return "The population of Nigeria is approximately 223 million."

    return f"Unknown tool {name}"


def main(prompt):
    messages = [{"role": "user", "content": prompt}]
    logger.info(f"Starting main loop with messages: {messages}")
    for i in range(MAX_ITERATIONS):
        logger.info(f"Iteration {i + 1}: starting")
        response = client.messages.create(
            model=MODEL, max_tokens=1024, tools=tools, messages=messages
        )
        message_content = response.content
        logger.info(f"response={message_content}")

        if response.stop_reason == "end_turn":
            logger.info(f"stop_reason={response.stop_reason}")
            for block in message_content:
                if block.type == "text":
                    return block.text

        if response.stop_reason == "tool_use":
            logger.info(f"Tool use block: request={message_content}")
            app = {"role": "assistant", "content": message_content}

            tool_results = []

            for block in message_content:
                logger.info(
                    f"  {block.type}: {getattr(block, 'text', None) or getattr(block, 'input', None)}"
                )
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )
            messages.append(app)
            messages.append({"role": "user", "content": tool_results})

        else:
            logger.info(f"Unexpected stop_reason: {response.stop_reason}")

        logger.info("\n--------------------\n")

    logger.info("Finished all iterations.")


print(main("Search for the population of Nigeria, then calculate 3% of it."))
