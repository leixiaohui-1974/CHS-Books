"""
积分系统服务
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from loguru import logger

from app.models.points import (
    PointsAccount, PointsTransaction, PointsProduct, PointsRedemption, PointsRule,
    TransactionType, PointsReason, ProductType
)


class PointsService:
    """积分系统服务"""
    
    async def get_or_create_account(
        self,
        db: AsyncSession,
        user_id: int
    ) -> PointsAccount:
        """获取或创建积分账户"""
        try:
            result = await db.execute(
                select(PointsAccount).where(PointsAccount.user_id == user_id)
            )
            account = result.scalar_one_or_none()
            
            if not account:
                account = PointsAccount(
                    user_id=user_id,
                    balance=0,
                    total_earned=0,
                    total_spent=0,
                    frozen=0
                )
                db.add(account)
                await db.commit()
                await db.refresh(account)
                logger.info(f"Created points account for user {user_id}")
            
            return account
            
        except Exception as e:
            logger.error(f"Failed to get/create points account: {str(e)}")
            await db.rollback()
            raise
    
    async def earn_points(
        self,
        db: AsyncSession,
        user_id: int,
        reason: PointsReason,
        amount: Optional[int] = None,
        description: Optional[str] = None,
        related_type: Optional[str] = None,
        related_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获得积分"""
        try:
            account = await self.get_or_create_account(db, user_id)
            
            # 如果没有指定积分数，从规则中获取
            if amount is None:
                rule = await self._get_rule(db, reason)
                if not rule:
                    raise ValueError(f"找不到积分规则: {reason}")
                amount = rule.points
            
            # 检查今日限制
            if not await self._check_daily_limit(db, account.id, reason):
                raise ValueError(f"今日{reason.value}积分获取次数已达上限")
            
            # 创建交易记录
            balance_before = account.balance
            account.balance += amount
            account.total_earned += amount
            balance_after = account.balance
            
            transaction = PointsTransaction(
                account_id=account.id,
                transaction_type=TransactionType.EARN,
                amount=amount,
                reason=reason,
                description=description or f"获得积分: {reason.value}",
                balance_before=balance_before,
                balance_after=balance_after,
                related_type=related_type,
                related_id=related_id
            )
            db.add(transaction)
            
            await db.commit()
            await db.refresh(account)
            
            logger.info(f"User {user_id} earned {amount} points for {reason.value}")
            
            return {
                "success": True,
                "amount": amount,
                "balance": account.balance,
                "reason": reason.value,
                "transaction_id": transaction.id
            }
            
        except Exception as e:
            logger.error(f"Failed to earn points: {str(e)}")
            await db.rollback()
            raise
    
    async def spend_points(
        self,
        db: AsyncSession,
        user_id: int,
        amount: int,
        reason: PointsReason,
        description: Optional[str] = None,
        related_type: Optional[str] = None,
        related_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """消费积分"""
        try:
            account = await self.get_or_create_account(db, user_id)
            
            # 检查余额
            if account.balance < amount:
                raise ValueError(f"积分余额不足，当前余额: {account.balance}")
            
            # 创建交易记录
            balance_before = account.balance
            account.balance -= amount
            account.total_spent += amount
            balance_after = account.balance
            
            transaction = PointsTransaction(
                account_id=account.id,
                transaction_type=TransactionType.SPEND,
                amount=amount,
                reason=reason,
                description=description or f"消费积分: {reason.value}",
                balance_before=balance_before,
                balance_after=balance_after,
                related_type=related_type,
                related_id=related_id
            )
            db.add(transaction)
            
            await db.commit()
            await db.refresh(account)
            
            logger.info(f"User {user_id} spent {amount} points for {reason.value}")
            
            return {
                "success": True,
                "amount": amount,
                "balance": account.balance,
                "reason": reason.value,
                "transaction_id": transaction.id
            }
            
        except Exception as e:
            logger.error(f"Failed to spend points: {str(e)}")
            await db.rollback()
            raise
    
    async def get_account_info(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """获取积分账户信息"""
        try:
            account = await self.get_or_create_account(db, user_id)
            
            return {
                "user_id": user_id,
                "balance": account.balance,
                "total_earned": account.total_earned,
                "total_spent": account.total_spent,
                "frozen": account.frozen,
                "available": account.balance - account.frozen,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            raise
    
    async def get_transactions(
        self,
        db: AsyncSession,
        user_id: int,
        transaction_type: Optional[TransactionType] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取积分交易记录"""
        try:
            account = await self.get_or_create_account(db, user_id)
            
            query = select(PointsTransaction).where(
                PointsTransaction.account_id == account.id
            )
            
            if transaction_type:
                query = query.where(PointsTransaction.transaction_type == transaction_type)
            
            query = query.order_by(PointsTransaction.created_at.desc()).limit(limit).offset(offset)
            
            result = await db.execute(query)
            transactions = result.scalars().all()
            
            return [
                {
                    "id": t.id,
                    "type": t.transaction_type.value,
                    "amount": t.amount,
                    "reason": t.reason.value,
                    "description": t.description,
                    "balance_before": t.balance_before,
                    "balance_after": t.balance_after,
                    "created_at": t.created_at.isoformat()
                }
                for t in transactions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get transactions: {str(e)}")
            raise
    
    async def get_products(
        self,
        db: AsyncSession,
        product_type: Optional[ProductType] = None,
        is_active: bool = True
    ) -> List[Dict[str, Any]]:
        """获取积分商品列表"""
        try:
            query = select(PointsProduct)
            
            if product_type:
                query = query.where(PointsProduct.product_type == product_type)
            
            if is_active:
                query = query.where(PointsProduct.is_active == True)
            
            query = query.order_by(PointsProduct.sort_order, PointsProduct.id)
            
            result = await db.execute(query)
            products = result.scalars().all()
            
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "type": p.product_type.value,
                    "points_cost": p.points_cost,
                    "stock": p.stock,
                    "sold_count": p.sold_count,
                    "max_per_user": p.max_per_user,
                    "requires_level": p.requires_level,
                    "image_url": p.image_url,
                    "is_active": p.is_active
                }
                for p in products
            ]
            
        except Exception as e:
            logger.error(f"Failed to get products: {str(e)}")
            raise
    
    async def redeem_product(
        self,
        db: AsyncSession,
        user_id: int,
        product_id: int,
        quantity: int = 1,
        shipping_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """兑换积分商品"""
        try:
            account = await self.get_or_create_account(db, user_id)
            
            # 获取商品信息
            product = await db.get(PointsProduct, product_id)
            if not product or not product.is_active:
                raise ValueError("商品不存在或已下架")
            
            # 检查库存
            if product.stock is not None and product.stock < quantity:
                raise ValueError(f"库存不足，当前库存: {product.stock}")
            
            # 检查每人限购
            if product.max_per_user:
                result = await db.execute(
                    select(func.sum(PointsRedemption.quantity))
                    .where(
                        and_(
                            PointsRedemption.user_id == user_id,
                            PointsRedemption.product_id == product_id,
                            PointsRedemption.status == "completed"
                        )
                    )
                )
                purchased = result.scalar() or 0
                if purchased + quantity > product.max_per_user:
                    raise ValueError(f"超过限购数量，每人限购{product.max_per_user}件")
            
            # 计算总积分
            total_cost = product.points_cost * quantity
            
            # 消费积分
            spend_result = await self.spend_points(
                db=db,
                user_id=user_id,
                amount=total_cost,
                reason=PointsReason.REDEEM_COUPON if product.product_type == ProductType.COUPON
                       else PointsReason.REDEEM_COURSE if product.product_type == ProductType.COURSE
                       else PointsReason.REDEEM_MEMBERSHIP if product.product_type == ProductType.MEMBERSHIP
                       else PointsReason.REDEEM_GIFT,
                description=f"兑换商品: {product.name}",
                related_type="product",
                related_id=product_id
            )
            
            # 创建兑换记录
            redemption = PointsRedemption(
                user_id=user_id,
                product_id=product_id,
                points_cost=total_cost,
                quantity=quantity,
                status="pending",
                shipping_info=shipping_info
            )
            db.add(redemption)
            
            # 更新商品库存和销量
            if product.stock is not None:
                product.stock -= quantity
            product.sold_count += quantity
            
            await db.commit()
            await db.refresh(redemption)
            
            logger.info(f"User {user_id} redeemed product {product_id} x{quantity}")
            
            return {
                "success": True,
                "redemption_id": redemption.id,
                "product_name": product.name,
                "quantity": quantity,
                "points_cost": total_cost,
                "balance": spend_result["balance"],  # 使用消费后的实际余额
                "status": redemption.status
            }
            
        except Exception as e:
            logger.error(f"Failed to redeem product: {str(e)}")
            await db.rollback()
            raise
    
    async def _get_rule(
        self,
        db: AsyncSession,
        reason: PointsReason
    ) -> Optional[PointsRule]:
        """获取积分规则"""
        result = await db.execute(
            select(PointsRule).where(
                and_(
                    PointsRule.reason == reason,
                    PointsRule.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def _check_daily_limit(
        self,
        db: AsyncSession,
        account_id: int,
        reason: PointsReason
    ) -> bool:
        """检查每日限制"""
        rule = await self._get_rule(db, reason)
        if not rule or not rule.daily_limit:
            return True
        
        # 查询今日已获取次数
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = await db.execute(
            select(func.count(PointsTransaction.id))
            .where(
                and_(
                    PointsTransaction.account_id == account_id,
                    PointsTransaction.reason == reason,
                    PointsTransaction.transaction_type == TransactionType.EARN,
                    PointsTransaction.created_at >= today_start
                )
            )
        )
        count = result.scalar() or 0
        
        return count < rule.daily_limit


# 创建全局实例
points_service = PointsService()
