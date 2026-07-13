import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class EmailService:
    RESEND_API_URL = "https://api.resend.com/emails"

    def send_password_reset(self, to_email: str, reset_link: str, user_name: str = ""):
        from core.config import settings

        if not settings.RESEND_API_KEY:
            logger.info(f"[DEV] Enlace de recuperación para {to_email}: {reset_link}")
            return

        payload = {
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "Recupera tu contraseña · ExamIA",
            "html": self._build_html(reset_link, user_name),
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.RESEND_API_URL,
            data=data,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "resend-python/1.0.0",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as response:
                logger.info(f"Email enviado a {to_email}, status: {response.status}")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            logger.error(f"Error al enviar email: {e.code} {e.reason} — {body}")
            raise

    def _build_html(self, reset_link: str, user_name: str) -> str:
        name = user_name.split()[0] if user_name else "docente"
        return f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:480px;margin:40px auto;padding:0 16px;">
    <div style="background:white;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0;">
      <div style="background:linear-gradient(135deg,#0ea5e9,#0284c7);padding:28px 32px;">
        <span style="font-size:22px;font-weight:800;color:white;letter-spacing:-0.5px;">Exam<span style="color:#bae6fd;">IA</span></span>
      </div>
      <div style="padding:32px;">
        <h2 style="margin:0 0 8px;color:#0f172a;font-size:20px;">Recupera tu contraseña</h2>
        <p style="margin:0 0 16px;color:#64748b;font-size:14px;line-height:1.6;">Hola {name},</p>
        <p style="margin:0 0 24px;color:#64748b;font-size:14px;line-height:1.6;">
          Recibimos una solicitud para restablecer la contraseña de tu cuenta.
          Haz clic en el botón para crear una nueva contraseña:
        </p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{reset_link}"
             style="display:inline-block;background:linear-gradient(135deg,#0ea5e9,#0284c7);
                    color:white;text-decoration:none;padding:13px 36px;border-radius:10px;
                    font-weight:600;font-size:15px;">
            Restablecer contraseña
          </a>
        </div>
        <p style="margin:0;color:#94a3b8;font-size:12px;line-height:1.6;">
          Este enlace expira en <strong>10 minutos</strong>.<br>
          Si no solicitaste el cambio, puedes ignorar este correo.
        </p>
      </div>
    </div>
    <p style="text-align:center;color:#cbd5e1;font-size:11px;margin-top:16px;">
      © 2025 ExamIA · Para educación media colombiana
    </p>
  </div>
</body>
</html>
        """


email_service = EmailService()
