import logging
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services import get_dashboard_stats

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    from flask import redirect, url_for
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    stats = get_dashboard_stats(current_user.id)
    return render_template("dashboard/index.html", stats=stats)
