import logging
import json
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import csrf
from app.forms import AIForm

logger = logging.getLogger(__name__)
ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/", methods=["GET"])
@login_required
def assistant():
    form = AIForm()
    return render_template("ai/assistant.html", form=form)


@ai_bp.route("/generate-task", methods=["POST"])
@csrf.exempt
@login_required
def generate_task():
    from app.extensions import db
    from app.models import Task
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        from openai import OpenAI, Timeout
        client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"],
                        base_url=current_app.config["OPENAI_BASE_URL"],
                        timeout=Timeout(60.0, connect=10.0))
        response = client.chat.completions.create(
            model=current_app.config["OPENAI_MODEL"],
            messages=[
                {"role": "system", "content": "You are a task management assistant. Given a task title, generate a description, estimated hours (number), priority (low/medium/high/critical), and up to 3 tags. Return raw JSON only."},
                {"role": "user", "content": f"Task title: {title}"}
            ],
            temperature=0.3,
            max_tokens=300,
        )
        result = json.loads(response.choices[0].message.content)
        return jsonify({
            "description": result.get("description", ""),
            "estimated_hours": result.get("estimated_hours", None),
            "priority": result.get("priority", "medium"),
            "tags": result.get("tags", []),
        })
    except Exception as e:
        logger.error("AI generation failed: %s", str(e))
        return jsonify({"error": "AI generation failed. Check your API key."}), 500


@ai_bp.route("/chat", methods=["POST"])
@csrf.exempt
@login_required
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:

        from openai import OpenAI, Timeout
        client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"],
                        base_url=current_app.config["OPENAI_BASE_URL"],
                        timeout=Timeout(60.0, connect=10.0))
        from app.models import Task
        tasks = Task.query.filter(
            (Task.assignee_id == current_user.id) | (Task.created_by == current_user.id)
        ).order_by(Task.created_at.desc()).limit(20).all()
        context = "\n".join([f"- [{t.status}] {t.title} (priority: {t.priority})" for t in tasks])
        system = f"You are a task management AI assistant. Here are the user's recent tasks:\n{context}\nAnswer questions helpfully and concisely."

        response = client.chat.completions.create(
            model=current_app.config["OPENAI_MODEL"],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=200,
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        logger.error("AI chat failed: %s", str(e))
        return jsonify({"error": "AI chat failed. Check your API key."}), 500


from flask import current_app
