from functools import wraps
import os
import random
import smtplib
from email.mime.text import MIMEText
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_user_by_email, save_user

auth_bp = Blueprint("auth", __name__)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view

def send_otp_email(to_email, otp_code):
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_EMAIL")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    
    body = f"Hello!\n\nYour One-Time Password (OTP) is: {otp_code}\n\nValid for session login."
    
    if smtp_server and smtp_port and smtp_user and smtp_pass:
        try:
            msg = MIMEText(body)
            msg["Subject"] = "Your Career Guidance OTP Code"
            msg["From"] = smtp_user
            msg["To"] = to_email
            
            port = int(smtp_port)
            if port == 465:
                server = smtplib.SMTP_SSL(smtp_server, port, timeout=10)
                server.login(smtp_user, smtp_pass)
            else:
                server = smtplib.SMTP(smtp_server, port, timeout=10)
                server.starttls()
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            print(f"[SMTP] Sent OTP to {to_email}")
            return True
        except Exception as e:
            print(f"[SMTP ERROR] {e}")
            
    print("\n" + "="*40)
    print("📢 EMAIL OTP FALLBACK ACTIVE")
    print(f"To: {to_email} | OTP: {otp_code}")
    print("="*40 + "\n")
    return False

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please complete every field.", "error")
            return render_template("register.html")

        if get_user_by_email(email):
            flash("A user with this email already exists.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        save_user(name, email, password_hash)
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
        
        otp_code = f"{random.randint(100000, 999999)}"
        session["otp_code"] = otp_code
        send_otp_email(user["email"], otp_code)
        
        flash("Please verify your account with the OTP sent to your email.", "info")
        return redirect(url_for("auth.verify_otp"))

    return render_template("login.html")

@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "temp_user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
        
    otp_code = session.get("otp_code")
    smtp_active = os.environ.get("SMTP_SERVER") is not None
    demo_otp = None if smtp_active else otp_code

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
