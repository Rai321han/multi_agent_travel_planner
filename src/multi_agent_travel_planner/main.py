#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from multi_agent_travel_planner.crew import MultiAgentTravelPlanner

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def print_token_usage(result):
    usage = result.token_usage or None
    print(result)
    # Some implementations might not populate every field
    if usage:
        total = usage.get("total_tokens") or usage.get("total") or 0
        prompt = usage.get("prompt_tokens") or usage.get("prompt") or 0
        completion = usage.get("completion_tokens") or usage.get("completion") or 0
        cached = usage.get("cached_prompt_tokens") or usage.get("cached_prompt") or 0
        successful = usage.get("successful_requests") or usage.get("successful") or 0

        print("TOKEN USAGE")
        print(f"  Total tokens       {total:,}")
        print(f"  Prompt tokens      {prompt:,}")
        print(f"  Completion tokens  {completion:,}")
        print(f"  Cached prompt      {cached:,}")
        print(f"  Successful reqs    {successful:,}")
        print()
    else:
        print("\nToken usage data not available.")


def get_user_inputs() -> dict:
    """Collect travel planning inputs from the user interactively."""
    print("\n" + "=" * 60)
    print("       AI Travel Planner Crew  ")
    print("=" * 60 + "\n")

    destination = input("Destination (e.g., Paris, France): ").strip()
    travel_dates = input("Travel Dates (e.g., 2025-08-01 to 2025-08-07): ").strip()
    budget = input("Total Budget in USD (e.g., 2000): ").strip()
    preferences = input(
        "Preferences (e.g., adventure, food, culture) [optional]: "
    ).strip()

    try:
        budget_val = float(budget.replace(",", ""))
    except ValueError:
        budget_val = 1000.0

    inputs = {
        "destination": destination,
        "travel_dates": travel_dates,
        "budget": budget_val,
        "preferences": preferences or "general sightseeing",
    }

    return inputs


def run():
    """
    Run the crew.
    """
    inputs = get_user_inputs()

    try:
        result = MultiAgentTravelPlanner().crew().kickoff(inputs=inputs)
        print_token_usage(result)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}
    try:
        MultiAgentTravelPlanner().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MultiAgentTravelPlanner().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}

    try:
        MultiAgentTravelPlanner().crew().test(
            n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "destination": trigger_payload.get("destination", "Paris"),
        "travel_dates": trigger_payload.get("travel_dates", "2026-02-26 to 2026-02-29"),
        "preferences": trigger_payload.get("preferences", "sightseeing, food, culture"),
        "budget": trigger_payload.get("budget", 3000),
    }

    try:
        result = MultiAgentTravelPlanner().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
