"""PreToolUse write gate: outbound email and Drive writes always ask the CIO first.

The system prompt says this too, but prose can be skipped; a hook cannot.
"""
import json
import sys

event = json.load(sys.stdin)
tool = event.get("tool_name", "")
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": f"ThorInvest write gate: '{tool}' leaves the CIO office. "
                                    "Confirm recipient/location and that compliance_precheck passed.",
    }
}))
