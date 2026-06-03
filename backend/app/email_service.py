import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception:
        pass

def send_html_email(to_email, subject, html_content, fallback_plain=""):
    if SMTP_SERVER and SMTP_PORT and SMTP_EMAIL and SMTP_PASSWORD:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"], msg["From"], msg["To"] = subject, SMTP_EMAIL, to_email
            msg.attach(MIMEText(fallback_plain or "Please view in HTML.", "plain"))
            msg.attach(MIMEText(html_content, "html"))
            port = int(SMTP_PORT)
            server = smtplib.SMTP_SSL(SMTP_SERVER, port, timeout=10) if port == 465 else smtplib.SMTP(SMTP_SERVER, port, timeout=10)
            server.ehlo()
            if port != 465:
                server.starttls()
                server.ehlo()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            safe_print(f"[SMTP] Email '{subject}' successfully sent to {to_email}")
            return True
        except Exception as e:
            safe_print(f"[SMTP ERROR] Failed to send email to {to_email}: {e}")
            
    # Fallback output
    safe_print(f"\n[EMAIL FALLBACK]\nTo: {to_email}\nSubject: {subject}\n{'-'*30}\n{fallback_plain}\n{'-'*30}\n")
    return False

def send_otp_email(to_email, otp_code):
    subject, fallback = "Your Career Guidance OTP Code", f"Your OTP: {otp_code}"
    html = f"""<html><body style="font-family:'Segoe UI',sans-serif;background-color:#0f172a;color:#f1f5f9;padding:20px;">
    <div style="max-width:500px;margin:0 auto;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.5);">
      <div style="text-align:center;margin-bottom:20px;"><h2 style="color:#6366f1;margin:0;">Smart Career Guidance</h2><p style="color:#94a3b8;font-size:14px;margin:5px 0 0 0;">Two-Step Verification</p></div>
      <hr style="border:0;border-top:1px solid #334155;margin-bottom:20px;"/><p>Hello,</p><p>To verify your identity and access your dashboard, please use the following OTP:</p>
      <div style="text-align:center;margin:30px 0;"><div style="display:inline-block;background:#312e81;border:1px solid #4338ca;color:#e0e7ff;font-size:32px;font-weight:bold;letter-spacing:5px;padding:15px 30px;border-radius:8px;">{otp_code}</div></div>
      <p style="color:#94a3b8;font-size:14px;">This code is valid for session login.</p><hr style="border:0;border-top:1px solid #334155;margin:20px 0;"/>
      <p style="color:#64748b;font-size:12px;text-align:center;margin:0;">&copy; 2026 Smart Career Guidance Platform. All rights reserved.</p>
    </div></body></html>"""
    return send_html_email(to_email, subject, html, fallback)

def send_welcome_email(to_email, name):
    subject, fallback = "Welcome to Smart Career Guidance Platform!", f"Welcome, {name}!"
    html = f"""<html><body style="font-family:'Segoe UI',sans-serif;background-color:#0f172a;color:#f1f5f9;padding:20px;">
    <div style="max-width:550px;margin:0 auto;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.5);">
      <div style="text-align:center;margin-bottom:20px;"><h2 style="color:#6366f1;margin:0;">Smart Career Guidance</h2><p style="color:#94a3b8;font-size:14px;margin:5px 0 0 0;">Your Personalized Internship Matchmaker</p></div>
      <hr style="border:0;border-top:1px solid #334155;margin-bottom:20px;"/><p>Hi {name.split()[0]},</p>
      <p>Welcome! We are excited to help you find the best internship opportunities tailored to your career goal and preferences.</p>
      <p><strong>Next steps:</strong></p>
      <ul style="padding-left:20px;line-height:1.6;">
        <li>Complete your profile with target cities, domains, and preferred companies.</li>
        <li>Upload your resume in PDF format for automated skill extraction.</li>
        <li>Review matched recommendations on the dashboard.</li>
      </ul><hr style="border:0;border-top:1px solid #334155;margin:20px 0;"/>
      <p style="color:#64748b;font-size:12px;text-align:center;margin:0;">&copy; 2026 Smart Career Guidance Platform. All rights reserved.</p>
    </div></body></html>"""
    return send_html_email(to_email, subject, html, fallback)

def send_profile_matches_email(to_email, name, preferred_company, top_matches):
    subject = "Your Top Internship Recommendations Are Ready!"
    fallback = f"Hello {name},\n\nYour profile has been updated. Preferred Company: {preferred_company or 'Any'}\n\n" + "\n".join([f"{i+1}. {x['title']} at {x['company']} (Match: {x['score']}% - Loc: {x['location']})" for i, x in enumerate(top_matches)])
    match_cards_html = ""
    for item in top_matches:
        is_pref = preferred_company and preferred_company.strip().lower() != "any" and preferred_company.strip().lower() in item['company'].lower()
        pref_badge = f'<span style="background:#065f46;color:#34d399;font-size:11px;padding:2px 8px;border-radius:12px;margin-left:10px;font-weight:bold;">Preferred Company Match</span>' if is_pref else ""
        skills_badges = " ".join([f'<span style="background:#1e293b;color:#94a3b8;font-size:11px;padding:2px 6px;border-radius:4px;margin-right:4px;display:inline-block;margin-bottom:4px;">{s}</span>' for s in item['skills'][:4]])
        match_cards_html += f"""
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:15px;margin-bottom:15px;">
          <table style="width:100%;border-collapse:collapse;"><tr>
            <td><h4 style="margin:0 0 4px 0;color:#f8fafc;font-size:16px;">{item['title']}</h4><p style="margin:0 0 8px 0;color:#94a3b8;font-size:13px;">{item['company']} {pref_badge}</p></td>
            <td style="text-align:right;vertical-align:top;width:60px;"><span style="color:#38bdf8;font-size:18px;font-weight:bold;">{item['score']}%</span></td>
          </tr></table>
          <div style="color:#64748b;font-size:12px;margin-bottom:8px;">📍 Location: {item['location']} &bull; 💰 Stipend: {item['stipend'] or 'Not specified'} &bull; ⏱️ Duration: {item['duration']}</div>
          <div style="margin-top:8px;">{skills_badges}</div>
        </div>"""
    html = f"""<html><body style="font-family:'Segoe UI',sans-serif;background-color:#0f172a;color:#f1f5f9;padding:20px;">
    <div style="max-width:600px;margin:0 auto;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.5);">
      <div style="text-align:center;margin-bottom:20px;"><h2 style="color:#6366f1;margin:0;">Smart Career Guidance</h2><p style="color:#94a3b8;font-size:14px;margin:5px 0 0 0;">Profile Update & Recommendations</p></div>
      <hr style="border:0;border-top:1px solid #334155;margin-bottom:20px;"/><p>Hi {name.split()[0]},</p><p>Your profile was successfully updated. Based on your preferences, we've recalculated your compatibility matches.</p>
      <p style="margin-bottom:15px;"><strong>Your Top Internship Recommendations:</strong></p>
      {match_cards_html}
      <hr style="border:0;border-top:1px solid #334155;margin:20px 0;"/>
      <p style="color:#64748b;font-size:12px;text-align:center;margin:0;">&copy; 2026 Smart Career Guidance Platform. All rights reserved.</p>
    </div></body></html>"""
    return send_html_email(to_email, subject, html, fallback)
