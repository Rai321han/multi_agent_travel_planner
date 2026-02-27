# Why Multi-Agent?
A single LLM prompt handling research, budgeting, scheduling, and validation simultaneously produces shallow, error-prone output. Errors in one area silently corrupt everything else with no checkpoint to catch them.
Multi-agent separates concerns — each agent has one job, its own tools, and its own iteration budget. The budget agent doesn't re-research attractions; the itinerary agent doesn't recalculate prices. If one agent fails, the validation agent catches it before it reaches the final output. Focused agents also consistently outperform a single generalist prompt on complex, multi-step tasks.

# What If Serper Returns Incorrect Data?
Serper returns Google Search results, which can include outdated prices, closed venues, or SEO-optimized pages with misleading information. Agents trust whatever Serper returns. So, there's no cross-referencing or source verification built in.
The validation_agent only checks math and logic against already-collected data, so bad source data passes through unchallenged. All specific claims (prices, hours, restaurant names), should be manually verified before booking anything.


# What If the Budget Is Unrealistic?
Over-budget scenarios are handled through PASS/WARNING/FAIL flags in budget_task and ±10% variance checks in validation_task. Under-budget scenarios are handled poorly, if $500 is entered for 7 nights in Tokyo, agents either produce an unlivable plan or return a FAIL with no actionable fix.
There's also no pre-flight sanity check. The user only finds out their budget is unrealistic after all 16 LLM requests have already run. A simple minimum-cost estimate before kickoff would save time and API costs.


# Hallucination Risks
Travel planning is high-risk for hallucinations because outputs look specific and authoritative. The most likely failure points are fabricated attraction details, invented price ranges when Serper returns poor results, non-existent restaurants, and plausible-but-wrong transport times.
destination_researcher and budget_planner both have max_iter=2, so each gets one retry on bad searches which is better than one attempt, but if both fail, the agent falls back on LLaMA's parametric memory, which is unreliable for current local prices and business details. "Do NOT make up information" in the task prompt is a nudge, not a guarantee.


# Token Usage
25,344 total tokens across 16 requests, with an 85%/15% prompt-to-completion ratio. Agents are spending most tokens re-reading prior task outputs rather than generating new content — a sign of context bloat.
MAX_TOKEN=2500 is likely causing output truncation, which forces downstream agents to reason around incomplete context, inflating their prompts further. Raising it to 4000–6000 and having the research task output a compact structured summary instead of full Markdown would reduce this significantly.


# Scalability
The pipeline is sequential by design, takes 16 API round-trips, each waiting on the previous. On Groq this is fast, but the core dependency chain (budget needs research, itinerary needs both) cannot be parallelized.
The more immediate problem is file collision. All outputs write to a shared output/ directory with no run-level namespacing. Two simultaneous runs overwrite each other's files, and the merge hook assembles a silently corrupted mixed-run document. Any multi-user deployment needs session-namespaced outputs and a concurrency-aware merge strategy.