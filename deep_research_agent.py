#!/usr/bin/env python3
"""
Interactive chat script with integrated tools for web search, content scraping, and package management.
"""

import argparse
import json
import logging
import os
import sys
import subprocess
from typing import Optional, List
from dataclasses import dataclass
import time

import openai

from tool_definitions import function_definitions
import tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    reasoning_tokens: Optional[int] = None

@dataclass
class ChatResponse:
    content: str
    token_usage: TokenUsage
    cost: float
    thinking_time: float = 0.0

def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """Calculate the cost of API usage based on model pricing.
    
    Args:
        prompt_tokens: Number of input tokens
        completion_tokens: Number of completion tokens
        model: Model name to determine pricing
    
    Returns:
        Total cost in USD
    """
    # Pricing per 1M tokens for different models
    MODEL_PRICING = {
        "o3-mini": {"input": 1.10, "output": 4.40},
        "o1": {"input": 15.0, "output": 60.0},
    }
    
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["o3-mini"])
    
    # Convert to millions and calculate
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    
    return input_cost + output_cost

def load_system_prompt(config_file: str = '.deep_research_rules') -> str:
    """
    Load system prompt from configuration file.

    Args:
        config_file: Path to the configuration file containing system prompt

    Returns:
        System prompt string
    """
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    today_prompt = f"""You are an AI staff helping to execute tasks using the tools at your hand. Today's date is {today}. Take this into consideration when you think about history and future."""
    
    try:
        if not os.path.exists(config_file):
            logger.warning(f"Config file {config_file} not found. Using default system prompt.")
            return today_prompt
        
        with open(config_file, 'r', encoding='utf-8') as f:
            custom_prompt = f.read().strip()
            return f"{custom_prompt}\n{today_prompt}"
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return f"""You are an AI staff helping to execute tasks using the tools at your hand. Today's date is {today}."""

def handle_function_call(tool_call: openai.types.chat.ChatCompletionMessageToolCall) -> Optional[str]:
    """
    Execute the function call from the assistant's message and return the result.

    Args:
        tool_call: Tool call object containing function details

    Returns:
        Function result string or None if no function call
    """
    if tool_call:
        func_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Handle terminal command execution
        if func_name == "execute_command":
            command = arguments.get("command")
            explanation = arguments.get("explanation")
            
            if not command:
                return "Error: No command provided"
            
            # Ask for user confirmation
            print(f"\nConfirm execution of command: {command}")
            print(f"Explanation: {explanation}")
            confirmation = input("[y/N]: ").strip().lower()
            
            if confirmation != 'y':
                return "Command execution cancelled by user."
            
            # Execute command
            try:
                print(f"\nExecuting command: {command}")
                # 修改命令执行方式
                env = os.environ.copy()
                env['SHELL'] = '/bin/bash'  # 确保使用 bash
                result = subprocess.run(
                    command,
                    shell=True,
                    executable='/bin/bash',  # 显式指定 shell
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False  # 不立即检查返回值
                )
                
                if result.returncode != 0:
                    return f"Command failed with exit code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                return f"Command executed successfully\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            except Exception as e:
                print(f"\nError executing command: {str(e)}")
                return f"Error executing command: {str(e)}"
        
        # Handle other functions
        elif func_name == "perform_search":
            return tools.perform_search(**arguments)
        elif func_name == "fetch_web_content":
            # 修改参数名称
            if 'url' in arguments:
                arguments['urls'] = [arguments.pop('url')]
            return tools.fetch_web_content(**arguments)
        elif func_name == "create_file":
            return tools.create_file(**arguments)
        else:
            return f"Unknown function: {func_name}"
    return None

def chat_loop(model: str, query: str, system_prompt: str) -> None:
    """
    Main chat loop function.
    """
    # 初始化 Azure OpenAI 客户端
    client = openai.AzureOpenAI(
        api_key="DuyZ0hHrPDcKN5FswiEyi43Reqqu2qLulqfQMglca8xDYA79URG3JQQJ99BAACYeBjFXJ3w3AAABACOGvlW6",
        api_version="2024-08-01-preview",
        azure_endpoint="https://ai-search-gpt4.openai.azure.com"
    )
    
    # Start a conversation
    conversation = []
    prompt = system_prompt + "\n\nUser's request:\n" + query
    print(f"\nTask:\n{prompt}")
    
    # Add initial prompt to conversation
    conversation.append({"role": "user", "content": prompt})
    
    # Initialize token tracking
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost = 0.0
    
    # Counter for non-tool responses
    non_tool_responses = 0
    
    # 创建输出文件
    output_file = "research_output.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Research Results: {query}\n\n")
    
    while True:
        try:
            # Start timer
            start_time = time.time()
            
            # Get assistant's response
            response = client.chat.completions.create(
                #deployment_id="gpt-4o",  # 使用 deployment_id 而不是 model
                messages=conversation,
                temperature=0.7,
                max_tokens=10000,
                stream=False,
                model="gpt-4o",  # 添加必需的 model 参数
                tools=function_definitions
            )
            
            # Calculate thinking time
            thinking_time = time.time() - start_time
            
            # Track token usage
            usage = response.usage
            token_usage = TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            )
            
            # Update totals
            total_prompt_tokens += token_usage.prompt_tokens
            total_completion_tokens += token_usage.completion_tokens
            step_cost = calculate_cost(token_usage.prompt_tokens, token_usage.completion_tokens, model)
            total_cost += step_cost
            
            # Log usage for this step
            logger.info(f"\nStep Token Usage:")
            logger.info(f"Input tokens: {token_usage.prompt_tokens}")
            logger.info(f"Output tokens: {token_usage.completion_tokens}")
            logger.info(f"Total tokens: {token_usage.total_tokens}")
            logger.info(f"Step cost: ${step_cost:.6f}")
            logger.info(f"Thinking time: {thinking_time:.2f}s")
            
            assistant_message = response.choices[0].message
            
            # 添加详细日志
            print("\nAPI Response Details:")
            print(f"Model: {model}")
            print(f"Response: {response}")
            print(f"Message: {assistant_message}")
            print(f"Content: {assistant_message.content}")
            print(f"Tool Calls: {assistant_message.tool_calls}")  # 修改这里
            
            # 修改检查逻辑：检查 tool_calls
            if not assistant_message.content and not assistant_message.tool_calls:
                print("\nError: Empty response from assistant")
                break
            
            # 修改工具调用的处理逻辑
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    # Parse and display the tool call details
                    func_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    print(f"\nAssistant: Using tool '{func_name}' with parameters:")
                    for key, value in arguments.items():
                        print(f"  - {key}: {value}")
                    
                    # Execute the tool
                    result = handle_function_call(tool_call)
                    print("\nTool output:")
                    if result and len(result) > 500:
                        print(f"{result[:500]}...\n[Output truncated, total length: {len(result)} chars]")
                    else:
                        print(result)
                    
                    # Add the function call and result to conversation
                    conversation.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": func_name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                        ]
                    })
                    # Include function result in the next user message
                    conversation.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tool_call.id,
                        "name": func_name
                    })
            
            else:
                # If it's a final response (no more tool calls needed)
                print("\nAssistant's Response:")
                print(assistant_message.content)
                conversation.append({"role": "assistant", "content": assistant_message.content})
                
                # Give user a chance to provide additional input
                print("\nWould you like to add any comments or provide additional input? (Press Enter to skip)")
                user_input = input("> ").strip()
                if user_input:
                    print("\nReceived your input. Sending request to assistant...")
                    conversation.append({"role": "user", "content": user_input})
                    continue
                else:
                    print("\nNo additional input received. Continuing with the conversation...")
                
                non_tool_responses += 1
                if non_tool_responses == 2:
                    # Print final token usage statistics
                    print("\nFinal Token Usage Statistics:")
                    print(f"Total input tokens: {total_prompt_tokens}")
                    print(f"Total output tokens: {total_completion_tokens}")
                    print(f"Total tokens: {total_prompt_tokens + total_completion_tokens}")
                    print(f"Total cost: ${total_cost:.6f}")
                    # End the conversation after second non-tool response
                    break
                elif non_tool_responses == 1:
                    # Prepare reflection prompt
                    reflection_prompt = "Do you think you have fully addressed the user's request? Please carefully consider if there are any missing aspects, e.g. are the facts backed by evidences? If the task is not completely resolved, please continue using the tools to complete it."
                    
                    # Add scratchpad content if it exists
                    try:
                        if os.path.exists('scratchpad.md'):
                            with open('scratchpad.md', 'r', encoding='utf-8') as f:
                                scratchpad_content = f.read()
                                reflection_prompt += f"\n\nHere is the current scratchpad content for your reference in determining task completion:\n\n{scratchpad_content}"
                                reflection_prompt += "\n\nHere is the user's request:\n\n" + query
                                reflection_prompt += "\n\nPlease first update the scratchpad to reflect the progress of the task. Then think about how to further improve the report, and execute the plan to improve the report."
                    except Exception as e:
                        logger.warning(f"Failed to read scratchpad.md: {e}")
                    
                    conversation.append({"role": "user", "content": reflection_prompt})
                    print("\nAsking assistant to reflect on task completion...")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Error details:", type(e).__name__)
            break

def main() -> None:
    """Main function to parse arguments and start the chat."""
    parser = argparse.ArgumentParser(
        description="Interactive chat with integrated tools for research and analysis."
    )
    parser.add_argument(
        "query",
        help="The research query or task to investigate"
    )
    parser.add_argument(
        "--model",
        default="o3-mini",
        help="OpenAI model to use (default: o3-mini)"
    )
    parser.add_argument(
        "--config",
        default=".deep_research_rules",
        help="Path to configuration file containing system prompt (default: .deep_research_rules)"
    )
    
    args = parser.parse_args()
    
    # Load system prompt
    system_prompt = load_system_prompt(args.config)
    
    # Start chat loop
    chat_loop(args.model, args.query, system_prompt)

if __name__ == "__main__":
    main()