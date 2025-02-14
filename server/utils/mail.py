from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from server.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


def get_signup_otp_template(otp, username: str):
    # return f"""<div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
    #             <div style="margin:20px auto;width:1000px;padding:20px 0">
    #                 <div style="border-bottom:1px solid #eee">
    #                 <a href="" style="font-size:1.5rem;color: #00466a;text-decoration:none;font-weight:600">Stock Market</a>
    #                 </div>
    #                 <p style="font-size:1.1em">Hi there,</p>
    #                 <p>Thank you for choosing Stock Market. Use the following OTP to complete your Sign Up process. OTP is valid for 10 minutes</p>
    #                 <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{otp}</h2>
    #                 <p style="font-size:0.9em;">Regards,<br />Stock Market</p>
    #                 <hr style="border:none;border-top:1px solid #eee" />
    #                 <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
    #                 <p>Stock Market. Inc</p>
    #                 <p>1600 Amphitheatre Parkway</p>
    #                 <p>California</p>
    #                 </div>
    #             </div>
    #             </div>
    #         """
    return (
        f"""
    <div>
        <div style="margin-top: 10px;">Hi <span style="font-weight: bold;">{username.title()}</span>,</div>
        
        <div style="margin-top: 15px;">Thank you for choosing <span style="font-weight: bold;">Dhanarthi</span>!</div>
        
        <div style="margin-top: 15px;">To complete your sign-up process, please use the One-Time Password (OTP) below:</div>
        
        <div style="margin-top: 10px; font-size: 22px; font-weight: bold; color: #333;">{otp}</div>
        
        <div style="margin-top: 15px;">This OTP is valid for <span style="font-weight: bold;">10 minutes</span>. For security reasons, please do not share it with anyone.</div>
        
        <div style="margin-top: 15px;">If you did not request this verification, you can safely ignore this email.</div>
        
        <div style="margin-top: 15px;">If you need any assistance, feel free to contact our support team.</div>
        
        <div style="margin-top: 20px; font-weight: bold;">Best regards,</div>
        <div style="font-weight: bold;">Dhanarthi Team</div>
    </div>

    """,
        "Your OTP for Email Verification – Dhanarthi",
    )


def get_signup_link_template(link, username: str):
    return f"""
        <div>
            <p style="font-size:1.1em">Hi {username.title()},</p>
            <p>We received a request to reset your password for your Dhanarthi account. Click the link below to set a new password. This link is valid for 10 minutes.</p>
            <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 10px;color: #fff;border-radius: 4px;">
                <a href="{link}" style="color: #fff; text-decoration: none;">Reset Password</a>
            </h2>
            <p>If you did not request this, you can safely ignore this email.</p>
            <p style="font-size:0.9em;">Best regards,<br />Dhanarthi Team</p>
            <hr style="border:none;border-top:1px solid #eee" />
            <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
        </div>
    """, "Your Verification link for Email Verification – Dhanarthi"


async def send_email(email, otp=None, link=None, username=None):
    body, subject = get_signup_link_template(link, username) if link else get_signup_otp_template(otp, username)
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return True
