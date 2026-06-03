from functools import wraps
import os
import secrets
import threading
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_user_by_email, save_user
from .email_service import send_otp_email, send_welcome_email

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    if not any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~" for c in password):
        return False, "Password must contain at least one special character."
    return True, ""

auth_bp = Blueprint("auth", __name__)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view



@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please complete every field.", "error")
            return render_template("register.html")

        ok, err_msg = validate_password_strength(password)
        if not ok:
            flash(err_msg, "error")
            return render_template("register.html")

        if get_user_by_email(email):
            flash("A user with this email already exists.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        save_user(name, email, password_hash)
        threading.Thread(target=send_welcome_email, args=(email, name), daemon=True).start()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session.clear()
        session["temp_user_id"] = user["id"]
        session.permanent = True
        
        otp_code = f"{secrets.SystemRandom().randint(100000, 999999)}"
        session["otp_code"] = otp_code
        email_sent = send_otp_email(user["email"], otp_code)
        session["otp_email_sent"] = email_sent
        
        if email_sent:
            flash("Please verify your account with the OTP sent to your email.", "info")
        else:
            flash("Failed to send SMTP email. Running in demo mode.", "warning")
        return redirect(url_for("auth.verify_otp"))

    return render_template("login.html")

@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "temp_user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
        
    otp_code = session.get("otp_code")
    email_sent = session.get("otp_email_sent", False)
    demo_otp = None if email_sent else otp_code

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        expected_otp = otp_code
        
        if not entered_otp or entered_otp != expected_otp:
            flash("Invalid OTP. Please check your console log or mail.", "error")
            return render_template("verify_otp.html", demo_otp=demo_otp)
            
        session["user_id"] = session.pop("temp_user_id")
        session.pop("otp_code", None)
        flash("OTP Verification successful!", "success")
        return redirect(url_for("routes.dashboard"))
        
    return render_template("verify_otp.html", demo_otp=demo_otp)

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
