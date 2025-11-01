"""
邮件发送工具
支持用户注册、密码重置、通知等邮件
"""

import os
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from jinja2 import Template
from loguru import logger
from app.core.config import settings


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        """初始化邮件服务"""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", settings.APP_NAME)
        
        self.enabled = bool(self.smtp_user and self.smtp_password)
        
        if not self.enabled:
            logger.warning("⚠️  Email service not configured")
    
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
        if not self.enabled:
            logger.warning(f"Email service disabled, skipping email to {to_email}")
            return False
        
        try:
            # 创建邮件
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # 添加文本内容
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"✅ Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    async def send_welcome_email(self, to_email: str, username: str) -> bool:
        """发送欢迎邮件"""
        subject = f"欢迎加入{settings.APP_NAME}！"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                          color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 欢迎加入！</h1>
                </div>
                <div class="content">
                    <p>亲爱的 <strong>{username}</strong>，</p>
                    <p>感谢您注册{settings.APP_NAME}！我们很高兴您能加入我们的学习社区。</p>
                    
                    <h3>🚀 开始您的学习之旅</h3>
                    <ul>
                        <li>浏览我们的课程库</li>
                        <li>使用交互式工具进行实践</li>
                        <li>追踪您的学习进度</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="{settings.APP_URL}" class="button">立即开始学习</a>
                    </div>
                    
                    <p>如果您有任何问题，请随时联系我们的支持团队。</p>
                    <p>祝学习愉快！<br>
                    {settings.APP_NAME} 团队</p>
                </div>
                <div class="footer">
                    <p>这是一封自动发送的邮件，请勿回复。</p>
                    <p>&copy; 2025 {settings.APP_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_password_reset_email(
        self, 
        to_email: str, 
        reset_token: str,
        username: str
    ) -> bool:
        """发送密码重置邮件"""
        subject = "重置您的密码"
        reset_url = f"{settings.APP_URL}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f44336; color: white; padding: 30px; 
                          text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f44336; 
                          color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; 
                           padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 密码重置请求</h1>
                </div>
                <div class="content">
                    <p>您好 <strong>{username}</strong>，</p>
                    <p>我们收到了重置您账户密码的请求。</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">重置密码</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️  安全提示：</strong>
                        <ul>
                            <li>此链接将在 <strong>1小时</strong> 后过期</li>
                            <li>如果不是您本人操作，请忽略此邮件</li>
                            <li>切勿将此链接分享给他人</li>
                        </ul>
                    </div>
                    
                    <p>如果您没有请求重置密码，请联系我们的支持团队。</p>
                    <p>祝好！<br>
                    {settings.APP_NAME} 安全团队</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_course_completion_email(
        self,
        to_email: str,
        username: str,
        book_title: str,
        completion_percentage: float
    ) -> bool:
        """发送课程完成通知邮件"""
        subject = f"🎉 恭喜完成《{book_title}》！"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                          color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .achievement {{ text-align: center; padding: 30px; background: white; 
                               border-radius: 10px; margin: 20px 0; }}
                .progress {{ width: 100%; height: 30px; background: #e0e0e0; 
                            border-radius: 15px; overflow: hidden; margin: 20px 0; }}
                .progress-bar {{ height: 100%; background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); 
                                text-align: center; line-height: 30px; color: white; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 课程完成！</h1>
                </div>
                <div class="content">
                    <p>亲爱的 <strong>{username}</strong>，</p>
                    
                    <div class="achievement">
                        <h2>🏆 恭喜您完成课程！</h2>
                        <h3>《{book_title}》</h3>
                        <div class="progress">
                            <div class="progress-bar" style="width: {completion_percentage}%">
                                {completion_percentage:.1f}%
                            </div>
                        </div>
                        <p style="font-size: 48px; margin: 20px 0;">🎓</p>
                    </div>
                    
                    <p>通过不懈的努力和坚持，您已经完成了这门课程的学习。这是一个了不起的成就！</p>
                    
                    <h3>🚀 继续学习</h3>
                    <p>探索更多课程，继续提升您的技能：</p>
                    <ul>
                        <li>浏览推荐课程</li>
                        <li>挑战进阶内容</li>
                        <li>获取学习证书</li>
                    </ul>
                    
                    <p>再次恭喜您！<br>
                    {settings.APP_NAME} 团队</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)


# 全局实例
email_service = EmailService()


# 便捷函数
async def send_welcome_email(to_email: str, username: str) -> bool:
    """发送欢迎邮件"""
    return await email_service.send_welcome_email(to_email, username)


async def send_password_reset_email(to_email: str, reset_token: str, username: str) -> bool:
    """发送密码重置邮件"""
    return await email_service.send_password_reset_email(to_email, reset_token, username)


async def send_course_completion_email(
    to_email: str,
    username: str,
    book_title: str,
    completion_percentage: float
) -> bool:
    """发送课程完成通知"""
    return await email_service.send_course_completion_email(
        to_email, username, book_title, completion_percentage
    )
