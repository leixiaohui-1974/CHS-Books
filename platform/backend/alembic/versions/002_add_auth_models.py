"""Add authentication models

Revision ID: 002
Revises: 001
Create Date: 2025-11-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema"""
    
    # 1. 修改users表 - 添加新字段
    op.add_column('users', sa.Column('status', sa.String(20), nullable=False, server_default='active'))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default='false'))
    
    # 修改email和phone为可空
    op.alter_column('users', 'email', existing_type=sa.String(255), nullable=True)
    op.alter_column('users', 'phone', existing_type=sa.String(20), nullable=True)
    op.alter_column('users', 'hashed_password', existing_type=sa.String(255), nullable=True)
    
    # 添加索引
    op.create_index('ix_users_status', 'users', ['status'])
    
    # 2. 创建user_profiles表
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('real_name', sa.String(50), nullable=True),
        sa.Column('gender', sa.String(10), nullable=True),
        sa.Column('birthday', sa.DateTime(timezone=True), nullable=True),
        sa.Column('school', sa.String(100), nullable=True),
        sa.Column('major', sa.String(100), nullable=True),
        sa.Column('grade', sa.String(20), nullable=True),
        sa.Column('student_id', sa.String(50), nullable=True),
        sa.Column('wechat', sa.String(50), nullable=True),
        sa.Column('qq', sa.String(20), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('signature', sa.String(200), nullable=True),
        sa.Column('country', sa.String(50), nullable=True),
        sa.Column('province', sa.String(50), nullable=True),
        sa.Column('city', sa.String(50), nullable=True),
        sa.Column('address', sa.String(200), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('privacy_settings', sa.JSON(), nullable=True),
        sa.Column('social_links', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'])
    
    # 3. 创建oauth_accounts表
    op.create_table(
        'oauth_accounts',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('provider_user_id', sa.String(100), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('provider_username', sa.String(100), nullable=True),
        sa.Column('provider_email', sa.String(255), nullable=True),
        sa.Column('provider_avatar', sa.String(500), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_oauth_accounts_user_id', 'oauth_accounts', ['user_id'])
    op.create_index('ix_oauth_accounts_provider', 'oauth_accounts', ['provider', 'provider_user_id'])
    
    # 4. 创建two_factor_auth表
    op.create_table(
        'two_factor_auth',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('method', sa.String(20), nullable=False),
        sa.Column('secret', sa.String(100), nullable=True),
        sa.Column('backup_codes', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_two_factor_auth_user_id', 'two_factor_auth', ['user_id'])
    
    # 5. 创建user_tokens表
    op.create_table(
        'user_tokens',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('token_type', sa.String(20), nullable=False),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.Column('device_name', sa.String(100), nullable=True),
        sa.Column('device_type', sa.String(20), nullable=True),
        sa.Column('device_info', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_user_tokens_user_id', 'user_tokens', ['user_id'])
    op.create_index('ix_user_tokens_token', 'user_tokens', ['token'])
    op.create_index('ix_user_tokens_expires_at', 'user_tokens', ['expires_at'])
    
    # 6. 创建login_history表
    op.create_table(
        'login_history',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('username', sa.String(50), nullable=True),
        sa.Column('login_method', sa.String(20), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_type', sa.String(20), nullable=True),
        sa.Column('browser', sa.String(50), nullable=True),
        sa.Column('os', sa.String(50), nullable=True),
        sa.Column('country', sa.String(50), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('ix_login_history_user_id', 'login_history', ['user_id'])
    op.create_index('ix_login_history_ip_address', 'login_history', ['ip_address'])
    op.create_index('ix_login_history_success', 'login_history', ['success'])
    op.create_index('ix_login_history_created_at', 'login_history', ['created_at'])
    
    # 7. 创建verification_codes表
    op.create_table(
        'verification_codes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('code_type', sa.String(20), nullable=False),
        sa.Column('recipient', sa.String(100), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_verification_codes_recipient', 'verification_codes', ['recipient', 'code_type'])
    op.create_index('ix_verification_codes_expires_at', 'verification_codes', ['expires_at'])


def downgrade() -> None:
    """Downgrade database schema"""
    
    # 删除表（逆序）
    op.drop_table('verification_codes')
    op.drop_table('login_history')
    op.drop_table('user_tokens')
    op.drop_table('two_factor_auth')
    op.drop_table('oauth_accounts')
    op.drop_table('user_profiles')
    
    # 恢复users表字段
    op.drop_index('ix_users_status', 'users')
    op.drop_column('users', 'phone_verified')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'status')
    
    # 恢复NOT NULL约束
    op.alter_column('users', 'hashed_password', existing_type=sa.String(255), nullable=False)
    op.alter_column('users', 'phone', existing_type=sa.String(20), nullable=False)
    op.alter_column('users', 'email', existing_type=sa.String(255), nullable=False)
