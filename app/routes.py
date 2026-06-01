from flask import Blueprint, redirect, render_template, session, url_for
from .auth import login_required
from .db import get_user_by_id

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("routes.dashboard"))
    return redirect(url_for("auth.login"))

@routes_bp.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    if not user:
        return redirect(url_for("auth.logout"))
    
    # We pass completed status so template knows whether to show recommendations
    return render_template("dashboard.html", user=user)

@routes_bp.route("/profile")
@login_required
def profile():
    user = get_user_by_id(session["user_id"])
    if not user:
        return redirect(url_for("auth.logout"))
    return render_template("profile.html", user=user)
