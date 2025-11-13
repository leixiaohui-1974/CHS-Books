"""
邮件服务
支持发送各类邮件：验证码、重置密码、通知等
"""

from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容（可选）
        
        Returns:
            是否发送成功
        """
        try:
            # 创建邮件
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            message['Subject'] = Header(subject, 'utf-8')
            
            # 添加文本内容
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                message.attach(part1)
            
            # 添加HTML内容
            part2 = MIMEText(html_content, 'html', 'utf-8')
            message.attach(part2)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_verification_code(
        self,
        to_email: str,
        code: str,
        expires_in: int = 300
    ) -> bool:
        """
        发送验证码邮件
        
        Args:
            to_email: 收件人邮箱
            code: 验证码
            expires_in: 有效期（秒）
        """
        subject = f"{settings.APP_NAME} - 验证码"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .code-box {{
                    background-color: #fff;
                    border: 2px dashed #4CAF50;
                    border-radius: 5px;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4CAF50;
                    letter-spacing: 5px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{settings.APP_NAME}</h1>
                    <p>您的验证码</p>
                </div>
                
                <p>您好！</p>
                <p>您正在进行身份验证，验证码为：</p>
                
                <div class="code-box">
                    <div class="code">{code}</div>
                </div>
                
                <p>此验证码将在 <strong>{expires_in // 60} 分钟</strong>后失效。</p>
                <p>如果这不是您的操作，请忽略此邮件。</p>
                
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复。</p>
                    <p>&copy; 2025 {settings.APP_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        {settings.APP_NAME} - 验证码
        
        您好！
        
        您正在进行身份验证，验证码为：{code}
        
        此验证码将在 {expires_in // 60} 分钟后失效。
        如果这不是您的操作，请忽略此邮件。
        
        ----
        此邮件由系统自动发送，请勿回复。
        © 2025 {settings.APP_NAME}. All rights reserved.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_welcome_email(
        self,
        to_email: str,
        username: str
    ) -> bool:
        """发送欢迎邮件"""
        subject = f"欢迎加入 {settings.APP_NAME}！"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    padding: 30px;
                    color: white;
                }}
                .content {{
                    background-color: white;
                    color: #333;
                    border-radius: 5px;
                    padding: 30px;
                    margin-top: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 style="text-align: center;">🎉 欢迎加入！</h1>
                <div class="content">
                    <h2>你好，{username}！</h2>
                    <p>欢迎加入 <strong>{settings.APP_NAME}</strong>！</p>
                    <p>我们很高兴您能成为我们学习社区的一员。</p>
                    
                    <h3>开始您的学习之旅：</h3>
                    <ul>
                        <li>📚 浏览海量优质教材</li>
                        <li>💻 在线运行代码练习</li>
                        <li>🤖 AI助手随时答疑</li>
                        <li>📊 跟踪学习进度</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="{settings.APP_URL}" class="button">立即开始学习</a>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        如果您有任何问题，请随时联系我们的支持团队。
                    </p>
                </div>
                <p style="text-align: center; margin-top: 20px; font-size: 14px;">
                    © 2025 {settings.APP_NAME}. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str
    ) -> bool:
        """发送密码重置邮件"""
        reset_url = f"{settings.APP_URL}/reset-password?token={reset_token}"
        subject = f"{settings.APP_NAME} - 重置密码"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #f44336;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{settings.APP_NAME}</h1>
                <h2>重置密码</h2>
                
                <p>您好！</p>
                <p>我们收到了您的密码重置请求。点击下面的按钮重置密码：</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">重置密码</a>
                </div>
                
                <p>或者复制以下链接到浏览器：</p>
                <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                    {reset_url}
                </p>
                
                <div class="warning">
                    <strong>⚠️ 安全提示：</strong>
                    <ul>
                        <li>此链接将在 30 分钟后失效</li>
                        <li>如果这不是您的操作，请立即修改密码</li>
                        <li>切勿将此链接分享给他人</li>
                    </ul>
                </div>
                
                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    此邮件由系统自动发送，请勿回复。<br>
                    © 2025 {settings.APP_NAME}. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)


# 创建全局实例
email_service = EmailService()
