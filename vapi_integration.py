import os
import json
import threading
import time
import re
from typing import Dict, Any, Optional

import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import uvicorn
from jinja2 import Template

# =========================
# ENV VARS (set these)
# =========================
VAPI_API_KEY        = os.getenv("6aae2ead-2aef-4c92-b025-49dbbb6b55ff")       # from Vapi
#VAPI_ASSISTANT_ID   = os.getenv("VAPI_ASSISTANT_ID", "")  # optional (you can omit and send inline assistant)
#TO_NUMBER           = os.getenv("TO_NUMBER", "")          # e.g., +1XXXXXXXXXX
#PUBLIC_URL          = os.getenv("PUBLIC_URL", "")         # your webhook base, e.g., https://xyz.ngrok.io

# Optional defaults
TEAM_NAME_DEFAULT   = os.getenv("TEAM_NAME_DEFAULT", "SF Giants")
PURCHASE_LINK_FALLBACK = os.getenv("PURCHASE_LINK_FALLBACK", "https://tickets.example.com/giants/single-game")

# =========================
# VARIABLE PROMPT TEMPLATES
# (You can edit these; they are rendered at call time)
# =========================
SYSTEM_TEMPLATE = Template("""
You are a professional sports ticket sales representative making outbound calls to fans who have prior history with the team.
Always simulate the flow of a live phone conversation.

Start with a warm, professional introduction.

Use MCP/CRM data naturally if present:
- Fan: {{ fan_name or "there" }}
- Prior connection: {{ prior_context or "previous engagement with the team" }}
- Favorite player: {{ favorite_player or "N/A" }}

Focus on selling **single-game tickets** (spotlight: {{ spotlight_game or "upcoming home game" }}) in a friendly, confident tone — persuasive, never begging.

Keep responses short and conversational, like real phone dialogue.
Handle objections with simple reassurance and concrete options (date alternatives, value sections, transparent pricing).

Always move toward the close and provide a clear purchase link **in-call** before hanging up:
{{ purchase_link or fallback_link }}

Success criteria (binary): the call is only successful if you (1) greet professionally, (2) pitch single-game tickets, and (3) provide the purchase link before ending.

Stay fully in character as a phone sales rep.
""".strip())

FIRST_MESSAGE_TEMPLATE = Template("""
Hi {{ fan_name or "there" }}, this is {{ rep_name or "Fangio" }} from the {{ team_name or team_default }} ticket office.
I saw you {{ prior_context or "connected with us before" }}, and I’ve got great single-game options for {{ spotlight_game or "our next home game" }}.
Do you have a quick minute?
""".strip())

# =========================
# RUNTIME STATE (very light)
# =========================
CALL_STATE: Dict[str, Dict[str, Any]] = {}  # keyed by vapi call id (or provided event id)

# =========================
# FASTAPI APP (for Vapi webhooks)
# =========================
app = FastAPI()

def extract_link(text: str) -> bool:
    return bool(re.search(r"https?://\S+", text or ""))

@app.post("/vapi/events")
async def vapi_events(req: Request):
    """
    Generic Vapi webhook. Logs transcripts/summaries and computes binary success.
    Expecting events like:
      - call.updated / call.ended
      - transcript.updated
      - analysis.summary (if configured)
    """
    body = await req.json()
    event = body.get("type") or body.get("event") or "unknown"
    data  = body.get("data", {})
    call_id = data.get("id") or data.get("callId") or body.get("callId") or "unknown"

    st = CALL_STATE.setdefault(call_id, {"transcript": "", "link_sent": False, "summary": ""})

    # Some Vapi setups send running transcript or message chunks:
    transcript = data.get("transcript") or body.get("transcript") or ""
    if transcript:
        st["transcript"] = transcript
        if extract_link(transcript):
            st["link_sent"] = True

    # If assistant messages are included
    messages = data.get("messages") or []
    for m in messages:
        if isinstance(m, dict):
            content = m.get("content") or ""
            if extract_link(content):
                st["link_sent"] = True

    # Optional analysis summary payload
    summary = data.get("summary") or body.get("summary")
    if summary:
        st["summary"] = summary

    # On end, print summary + binary success
    if event in ("call.ended", "ended", "call.completed"):
        transcript_text = st["transcript"]
        success = bool(st["link_sent"]) and ("ticket" in transcript_text.lower() or "single-game" in transcript_text.lower())
        print("\n===== CALL ENDED =====")
        print(f"Call ID: {call_id}")
        print("Summary:", st.get("summary") or "(no summary provided)")
        print("Binary Success (link sent?):", "SUCCESS" if success else "FAIL")
        print("======================\n")

    return JSONResponse({"ok": True})

# =========================
# VAPI HELPER
# =========================
def vapi_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json",
    }

def build_inline_assistant(system_prompt: str, first_message: str) -> Dict[str, Any]:
    """
    Minimal inline Vapi assistant config. Adjust as needed for your account:
      - model
      - voice
      - transcriber
      - analysis/success eval (if you enable in Vapi)
    """
    return {
        "name": "SF Marketer (Inline)",
        "model": {
            "provider": "openai",
            "model": "gpt-4o-mini-realtime-preview-2024-12-17",  # Vapi realtime-capable model tag
            "temperature": 0.6,
            "maxOutputTokens": 50
        },
        "voice": {
            "provider": "openai",
            "model": "tts-1-hd",
            "voice": "ash"
        },
        "firstMessageMode": "assistant",   # assistant speaks first
        "firstMessage": first_message,
        "systemPrompt": system_prompt,
        # Optional: send events to our webhook
        "serverUrl": f"{PUBLIC_URL}/vapi/events",
        # Transcriber (Vapi handles this internally, configure to your plan)
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en"
        },
        # Basic barge-in/latency controls (tune later)
        "stopSpeakingPlan": {
            "numWords": 4,
            "voiceSeconds": 0.3,
            "backoffSeconds": 3
        },
        # End message (Vapi will speak this when your logic ends the call)
        "endCallMessage": "Goodbye."
    }

def start_vapi_call(
    to_number: str,
    system_prompt: str,
    first_message: str,
    assistant_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Triggers an outbound call in Vapi.
    If assistant_id is provided, uses that assistant; otherwise sends inline assistant config.
    """
    url = "https://api.vapi.ai/call"  # Vapi's create-call endpoint (name may vary; use your workspace docs)

    payload: Dict[str, Any] = {
        "phoneNumber": to_number,
        "assistant": {"assistantId": assistant_id} if assistant_id else build_inline_assistant(system_prompt, first_message),
        # If your Vapi workspace wants a top-level serverUrl for events:
        "serverUrl": f"{PUBLIC_URL}/vapi/events"
    }

    r = requests.post(url, headers=vapi_headers(), data=json.dumps(payload), timeout=20)
    r.raise_for_status()
    return r.json()

# =========================
# MCP SERVER
# =========================
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("vapi-ticket-sales-rep")

@mcp.tool()
def ping(ctx: Context) -> str:          # ← rename '_' to 'ctx'
    "Health check."
    return "pong"

@mcp.tool()
def start_call(ctx: Context, variables_json: str = "{}") -> str:  # name is fine
    ...


@mcp.tool()
def ping(_: Context) -> str:
    "Health check."
    return "pong"

@mcp.tool()
def start_call(ctx: Context, variables_json: str = "{}") -> str:
    """
    Render variable prompts and start a Vapi call.
    Pass a JSON string for variables_json, e.g.:
    {
      "fan_name": "Sarah Kim",
      "rep_name": "Fangio",
      "team_name": "SF Giants",
      "prior_context": "were at our rivalry game last season",
      "spotlight_game": "Saturday vs. Dodgers",
      "favorite_player": "#22 Lewis",
      "purchase_link": "https://tickets.example.com/sg/abc123"
    }
    """
    try:
        variables = json.loads(variables_json or "{}")
    except Exception as e:
        return f"Invalid JSON for variables_json: {e}"

    # Provide defaults and fallback link
    variables.setdefault("team_name", TEAM_NAME_DEFAULT)
    variables.setdefault("team_default", TEAM_NAME_DEFAULT)
    variables.setdefault("fallback_link", PURCHASE_LINK_FALLBACK)

    # Render prompts
    system_prompt = SYSTEM_TEMPLATE.render(**variables)
    first_message = FIRST_MESSAGE_TEMPLATE.render(**variables)

    # Trigger Vapi call
    resp = start_vapi_call(
        to_number=TO_NUMBER,
        system_prompt=system_prompt,
        first_message=first_message,
        assistant_id=VAPI_ASSISTANT_ID or None
    )
    call_id = resp.get("id") or resp.get("callId") or "unknown"
    CALL_STATE[call_id] = {"transcript": "", "link_sent": False, "summary": ""}

    return f"Dialing {TO_NUMBER}. Vapi call id: {call_id}"

def start_http():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

def main():
    # sanity
    for k in ["VAPI_API_KEY", "TO_NUMBER", "PUBLIC_URL"]:
        if not globals()[k]:
            raise RuntimeError(f"Missing env var: {k}")

    # start webhook server
    t = threading.Thread(target=start_http, daemon=True)
    t.start()
    time.sleep(0.8)

    # Run MCP (stdio)
    mcp.run()

if __name__ == "__main__":
    main()
