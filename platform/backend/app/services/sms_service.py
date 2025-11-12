"""
短信服务
提供短信验证码发送、短信通知等功能
支持阿里云SMS
"""

import json
import secrets
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest

from app.core.config import settings
from app.models.auth import VerificationCode, VerificationType


class SMSService:
    """短信服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = None
        
        # 初始化阿里云客户端
        if settings.ALIYUN_ACCESS_KEY and settings.ALIYUN_ACCESS_SECRET:
            self.client = AcsClient(
                settings.ALIYUN_ACCESS_KEY,
                settings.ALIYUN_ACCESS_SECRET,
                'cn-hangzhou'  # 地域
            )
    
    # ========================================
    # 验证码发送
    # ========================================
    
    async def send_verification_code(
        self,
        phone: str,
        code_type: VerificationType,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送验证码短信
        
        Args:
            phone: 手机号
            code_type: 验证码类型
            user_id: 用户ID（可选）
            
        Returns:
            发送结果
        """
        # 1. 检查发送频率（1分钟内只能发送一次）
        await self._check_send_frequency(phone, code_type)
        
        # 2. 生成验证码
        code = self._generate_code()
        
        # 3. 发送短信
        if settings.APP_ENV == 'development':
            # 开发环境：打印到控制台
            print(f"\n{'='*50}")
            print(f"📱 SMS验证码 (开发模式)")
            print(f"{'='*50}")
            print(f"手机号: {phone}")
            print(f"验证码: {code}")
            print(f"类型: {code_type}")
            print(f"有效期: 5分钟")
            print(f"{'='*50}\n")
            
            result = {
                'success': True,
                'message': '验证码已发送（开发模式）',
                'request_id': 'DEV_' + secrets.token_hex(16)
            }
        else:
            # 生产环境：调用阿里云SMS
            result = await self._send_sms_aliyun(phone, code, code_type)
        
        # 4. 保存验证码记录
        if result['success']:
            await self._save_verification_code(
                phone=phone,
                code=code,
                code_type=code_type,
                user_id=user_id
            )
        
        return {
            'success': result['success'],
            'message': result['message'],
            'expires_in': 300  # 5分钟
        }
    
    async def _send_sms_aliyun(
        self,
        phone: str,
        code: str,
        code_type: VerificationType
    ) -> Dict[str, Any]:
        """
        通过阿里云发送短信
        
        Args:
            phone: 手机号
            code: 验证码
            code_type: 类型
            
        Returns:
            发送结果
        """
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="短信服务未配置"
            )
        
        try:
            # 创建请求
            request = SendSmsRequest.SendSmsRequest()
            request.set_accept_format('json')
            
            # 设置参数
            request.set_PhoneNumbers(phone)
            request.set_SignName(settings.SMS_SIGN_NAME)
            request.set_TemplateCode(self._get_template_code(code_type))
            request.set_TemplateParam(json.dumps({'code': code}))
            
            # 发送请求
            response = self.client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))
            
            if result.get('Code') == 'OK':
                return {
                    'success': True,
                    'message': '短信发送成功',
                    'request_id': result.get('RequestId')
                }
            else:
                error_msg = result.get('Message', '短信发送失败')
                return {
                    'success': False,
                    'message': error_msg,
                    'request_id': result.get('RequestId')
                }
        
        except Exception as e:
            print(f"短信发送异常: {str(e)}")
            return {
                'success': False,
                'message': '短信发送失败，请稍后重试',
                'request_id': None
            }
    
    def _get_template_code(self, code_type: VerificationType) -> str:
        """
        获取短信模板代码
        
        Args:
            code_type: 验证码类型
            
        Returns:
            模板代码
        """
        # 这里需要根据实际申请的阿里云短信模板填写
        templates = {
            VerificationType.REGISTER: settings.SMS_TEMPLATE_CODE or 'SMS_123456789',
            VerificationType.LOGIN: settings.SMS_TEMPLATE_CODE or 'SMS_123456789',
            VerificationType.RESET_PASSWORD: settings.SMS_TEMPLATE_CODE or 'SMS_123456789',
            VerificationType.CHANGE_PHONE: settings.SMS_TEMPLATE_CODE or 'SMS_123456789',
            VerificationType.TWO_FACTOR: settings.SMS_TEMPLATE_CODE or 'SMS_123456789',
        }
        return templates.get(code_type, settings.SMS_TEMPLATE_CODE or 'SMS_123456789')
    
    # ========================================
    # 验证码验证
    # ========================================
    
    async def verify_code(
        self,
        phone: str,
        code: str,
        code_type: VerificationType,
        delete_after_verify: bool = True
    ) -> bool:
        """
        验证短信验证码
        
        Args:
            phone: 手机号
            code: 验证码
            code_type: 类型
            delete_after_verify: 验证后是否删除
            
        Returns:
            是否验证成功
        """
        # 1. 查找验证码记录
        query = select(VerificationCode).where(
            and_(
                VerificationCode.recipient == phone,
                VerificationCode.type == code_type,
                VerificationCode.is_used == False,
                VerificationCode.expires_at > datetime.utcnow()
            )
        ).order_by(VerificationCode.created_at.desc())
        
        result = await self.db.execute(query)
        verification = result.scalar_one_or_none()
        
        if not verification:
            return False
        
        # 2. 验证码是否正确
        if verification.code != code:
            return False
        
        # 3. 标记为已使用或删除
        if delete_after_verify:
            await self.db.delete(verification)
        else:
            verification.is_used = True
        
        await self.db.commit()
        return True
    
    # ========================================
    # 辅助方法
    # ========================================
    
    def _generate_code(self, length: int = 6) -> str:
        """
        生成数字验证码
        
        Args:
            length: 长度
            
        Returns:
            验证码
        """
        code = ''.join([str(secrets.randbelow(10)) for _ in range(length)])
        return code
    
    async def _check_send_frequency(
        self,
        phone: str,
        code_type: VerificationType
    ) -> None:
        """
        检查发送频率
        
        Args:
            phone: 手机号
            code_type: 类型
            
        Raises:
            HTTPException: 如果发送过于频繁
        """
        # 查找最近1分钟内的记录
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        
        query = select(VerificationCode).where(
            and_(
                VerificationCode.recipient == phone,
                VerificationCode.type == code_type,
                VerificationCode.created_at > one_minute_ago
            )
        )
        
        result = await self.db.execute(query)
        recent_code = result.scalar_one_or_none()
        
        if recent_code:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="发送过于频繁，请1分钟后重试"
            )
    
    async def _save_verification_code(
        self,
        phone: str,
        code: str,
        code_type: VerificationType,
        user_id: Optional[int] = None
    ) -> VerificationCode:
        """
        保存验证码记录
        
        Args:
            phone: 手机号
            code: 验证码
            code_type: 类型
            user_id: 用户ID
            
        Returns:
            VerificationCode对象
        """
        verification = VerificationCode(
            user_id=user_id,
            type=code_type,
            recipient=phone,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            is_used=False
        )
        
        self.db.add(verification)
        await self.db.commit()
        await self.db.refresh(verification)
        
        return verification
    
    # ========================================
    # 短信通知（非验证码）
    # ========================================
    
    async def send_notification(
        self,
        phone: str,
        template_code: str,
        params: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        发送短信通知
        
        Args:
            phone: 手机号
            template_code: 模板代码
            params: 模板参数
            
        Returns:
            发送结果
        """
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="短信服务未配置"
            )
        
        try:
            request = SendSmsRequest.SendSmsRequest()
            request.set_accept_format('json')
            request.set_PhoneNumbers(phone)
            request.set_SignName(settings.SMS_SIGN_NAME)
            request.set_TemplateCode(template_code)
            request.set_TemplateParam(json.dumps(params))
            
            response = self.client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))
            
            if result.get('Code') == 'OK':
                return {
                    'success': True,
                    'message': '短信发送成功',
                    'request_id': result.get('RequestId')
                }
            else:
                return {
                    'success': False,
                    'message': result.get('Message', '短信发送失败'),
                    'request_id': result.get('RequestId')
                }
        
        except Exception as e:
            print(f"短信发送异常: {str(e)}")
            return {
                'success': False,
                'message': '短信发送失败',
                'request_id': None
            }
    
    # ========================================
    # 统计和管理
    # ========================================
    
    async def get_send_count(
        self,
        phone: str,
        start_time: datetime,
        end_time: datetime
    ) -> int:
        """
        获取指定时间段内的发送次数
        
        Args:
            phone: 手机号
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            发送次数
        """
        query = select(VerificationCode).where(
            and_(
                VerificationCode.recipient == phone,
                VerificationCode.created_at >= start_time,
                VerificationCode.created_at <= end_time
            )
        )
        
        result = await self.db.execute(query)
        codes = result.scalars().all()
        
        return len(codes)
    
    async def cleanup_expired_codes(self) -> int:
        """
        清理过期的验证码
        
        Returns:
            清理数量
        """
        from sqlalchemy import delete
        
        query = delete(VerificationCode).where(
            VerificationCode.expires_at < datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount
