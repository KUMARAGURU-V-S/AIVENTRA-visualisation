"""
ForensiX CDR Analyzer — AI Agent with Gemini Tool Calling
Uses Google Gemini API to plan and execute forensic analysis via tool calling.
"""

import json
import pandas as pd
from google import genai
from google.genai import types
from tools import TOOL_REGISTRY


# Define tool declarations for Gemini
TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="detect_high_frequency_callers",
        description="Detect phone numbers with abnormally high total call counts. Identifies potential stalking or obsessive calling patterns. Use this to find numbers making an unusual volume of calls.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"threshold_percentile": types.Schema(type=types.Type.NUMBER, description="Percentile threshold (default 95)")},
        ),
    ),
    types.FunctionDeclaration(
        name="analyze_time_distribution",
        description="Analyze call distribution across day/evening/night periods. Flags numbers with unusually high night-time activity which is suspicious.",
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="detect_anomalous_charges",
        description="Find statistically anomalous call charges using z-score analysis. Detects potential fraud or premium-rate abuse.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"z_threshold": types.Schema(type=types.Type.NUMBER, description="Z-score threshold (default 2.5)")},
        ),
    ),
    types.FunctionDeclaration(
        name="find_suspicious_international",
        description="Flag numbers with unusually high international call activity. Detects potential cross-border criminal communications.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"intl_call_threshold": types.Schema(type=types.Type.INTEGER, description="Minimum intl calls to flag (default 8)")},
        ),
    ),
    types.FunctionDeclaration(
        name="cluster_behavior_patterns",
        description="Group phone numbers into behavioral clusters using K-Means machine learning. Identifies outlier groups with suspicious behavior patterns.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"n_clusters": types.Schema(type=types.Type.INTEGER, description="Number of clusters (default 5)")},
        ),
    ),
    types.FunctionDeclaration(
        name="detect_burner_phones",
        description="Detect short-lived accounts with high call activity — classic burner phone pattern used by criminals to avoid detection.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"max_account_length": types.Schema(type=types.Type.INTEGER, description="Max account age in days to flag (default 40)")},
        ),
    ),
    types.FunctionDeclaration(
        name="correlation_analysis",
        description="Analyze correlations between all call features to discover hidden relationships and patterns in the evidence data.",
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="generate_suspect_timeline",
        description="Generate a detailed activity profile and radar chart for a specific suspect phone number.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"phone_number": types.Schema(type=types.Type.STRING, description="Phone number to profile (optional, defaults to most active)")},
        ),
    ),
]


SYSTEM_PROMPT = """You are ForensiX Agent — an expert digital forensics AI analyst specializing in Call Detail Record (CDR) analysis for criminal investigations.

You have access to a CDR dataset with phone call records. Your mission is to analyze this evidence systematically to identify:
1. Suspicious phone numbers and their behavioral patterns
2. Anomalous activity that could indicate criminal behavior
3. Potential burner phones used to evade detection
4. Unusual timing patterns (excessive night calls)
5. International call anomalies (cross-border criminal communications)
6. Hidden correlations in the data

APPROACH:
- Start by explaining your analysis plan to the investigator
- Call tools strategically, one at a time
- After each tool result, interpret the findings forensically
- Cross-reference findings between tools
- End with a comprehensive forensic summary with key suspects

Be thorough, professional, and present findings as forensic evidence."""


def execute_tool(tool_name: str, args: dict, df: pd.DataFrame) -> dict:
    """Execute a registered tool and return its results."""
    if tool_name not in TOOL_REGISTRY:
        return {"summary": f"Unknown tool: {tool_name}", "data": [], "chart": None}

    fn = TOOL_REGISTRY[tool_name]["fn"]
    # Filter args to only those the function accepts
    import inspect
    valid_params = inspect.signature(fn).parameters
    filtered_args = {k: v for k, v in args.items() if k in valid_params and k != "df"}
    return fn(df, **filtered_args)


def run_agent(api_key: str, df: pd.DataFrame, user_query: str, on_step=None):
    """
    Run the forensic analysis agent.

    Args:
        api_key: Gemini API key
        df: CDR DataFrame
        user_query: The investigator's analysis request
        on_step: Callback function(step_type, content, chart=None) for live UI updates

    Returns:
        List of all steps taken by the agent
    """
    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash"

    tools = types.Tool(function_declarations=TOOL_DECLARATIONS)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[tools],
        temperature=0.3,
    )

    # Build context about the dataset
    dataset_info = (
        f"Dataset: {len(df)} phone records with columns: {', '.join(df.columns.tolist())}. "
        f"Phone numbers: {df['Phone Number'].nunique()} unique. "
        f"Account lengths range: {df['Account Length'].min()}-{df['Account Length'].max()} days. "
        f"Churn rate: {(df['Churn'].astype(str).str.upper() == 'TRUE').mean():.1%}."
    )

    messages = [
        types.Content(role="user", parts=[
            types.Part.from_text(text=f"INVESTIGATOR REQUEST: {user_query}\n\nDATASET INFO: {dataset_info}\n\nPlan your analysis approach, then execute your tools to analyze the evidence. After all analysis, provide a comprehensive forensic report.")
        ])
    ]

    steps = []
    max_iterations = 15

    for iteration in range(max_iterations):
        response = client.models.generate_content(
            model=model,
            contents=messages,
            config=config,
        )

        candidate = response.candidates[0]
        parts = candidate.content.parts

        # Check for text responses
        text_parts = [p.text for p in parts if p.text]
        if text_parts:
            text = "\n".join(text_parts)
            step = {"type": "thought", "content": text}
            steps.append(step)
            if on_step:
                on_step("thought", text)

        # Check for function calls
        fn_calls = [p.function_call for p in parts if p.function_call]

        if not fn_calls:
            # Agent is done — no more tool calls
            break

        # Add the assistant's response to conversation
        messages.append(candidate.content)

        # Execute each function call
        fn_response_parts = []
        for fc in fn_calls:
            tool_name = fc.name
            tool_args = dict(fc.args) if fc.args else {}
            icon = TOOL_REGISTRY.get(tool_name, {}).get("icon", "🔧")

            step_info = {"type": "tool_call", "tool": tool_name, "args": tool_args, "icon": icon}
            steps.append(step_info)
            if on_step:
                on_step("tool_call", f"{icon} Calling `{tool_name}`({json.dumps(tool_args)})")

            # Execute the tool
            try:
                result = execute_tool(tool_name, tool_args, df)
                summary = result["summary"]
                chart = result.get("chart")
                data_preview = str(result.get("data", []))[:500]

                step_result = {"type": "tool_result", "tool": tool_name, "summary": summary, "chart": chart, "icon": icon}
                steps.append(step_result)
                if on_step:
                    on_step("tool_result", summary, chart)

                fn_response_parts.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"summary": summary, "data_sample": data_preview},
                    )
                )
            except Exception as e:
                error_msg = f"Tool error: {str(e)}"
                steps.append({"type": "error", "tool": tool_name, "content": error_msg})
                if on_step:
                    on_step("error", error_msg)
                fn_response_parts.append(
                    types.Part.from_function_response(name=tool_name, response={"error": error_msg})
                )

        # Send tool results back to the model
        messages.append(types.Content(role="user", parts=fn_response_parts))

    return steps
