import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------

def dispatch(name: str, args: dict) -> dict:
    """Route a VAPI tool call to the correct tool function."""
    try:
        if name == "get_client":
            from tools.get_client import get_client
            return get_client(**args)
        elif name == "create_client":
            from tools.create_client import create_client
            return create_client(**args)
        elif name == "get_availability":
            from tools.get_availability import get_availability
            return get_availability(**args)
        elif name == "create_reservation":
            from tools.create_reservation import create_reservation
            return create_reservation(**args)
        elif name == "send_sms":
            from tools.send_sms import send_sms
            return send_sms(**args)
        else:
            return {"status": "error", "message": f"Unknown tool: {name}"}
    except TypeError as e:
        return {"status": "error", "message": f"Invalid arguments for {name}: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Tool {name} failed: {e}"}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/tools", methods=["POST"])
def handle_tools():
    """
    Receives VAPI tool call webhooks.

    VAPI payload format:
    {
      "message": {
        "type": "tool-calls",
        "toolCalls": [{"id": "...", "function": {"name": "...", "arguments": "..."}}]
      }
    }
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON payload"}), 400

    tool_calls = payload.get("message", {}).get("toolCalls", [])
    if not tool_calls:
        return jsonify({"error": "No tool calls found"}), 400

    results = []
    for call in tool_calls:
        call_id = call.get("id", "unknown")
        function = call.get("function", {})
        name = function.get("name", "")
        raw_args = function.get("arguments", "{}")

        try:
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except json.JSONDecodeError:
            args = {}

        result = dispatch(name, args)
        results.append({
            "toolCallId": call_id,
            "result": json.dumps(result, ensure_ascii=False),
        })

    return jsonify({"results": results})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("ENVIRONMENT", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
