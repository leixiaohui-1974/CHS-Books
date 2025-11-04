#!/usr/bin/env python3
"""
配置向导
引导用户完成平台的初始配置
"""

import os
import sys
from pathlib import Path
import json
import random
import string


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SetupWizard:
    """配置向导"""
    
    def __init__(self):
        self.config = {}
        self.env_file = Path(__file__).parent / ".env"
    
    def print_header(self, text: str):
        """打印标题"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    def print_step(self, step: int, total: int, text: str):
        """打印步骤"""
        print(f"\n{Colors.CYAN}[{step}/{total}] {text}{Colors.END}")
    
    def print_success(self, text: str):
        """打印成功信息"""
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")
    
    def print_warning(self, text: str):
        """打印警告信息"""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")
    
    def print_error(self, text: str):
        """打印错误信息"""
        print(f"{Colors.RED}✗ {text}{Colors.END}")
    
    def generate_secret_key(self, length: int = 32) -> str:
        """生成密钥"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def ask_question(self, question: str, default: str = None, required: bool = True) -> str:
        """询问问题"""
        if default:
            prompt = f"{question} [{default}]: "
        else:
            prompt = f"{question}: "
        
        while True:
            answer = input(prompt).strip()
            
            if answer:
                return answer
            elif default:
                return default
            elif not required:
                return ""
            else:
                self.print_warning("此项为必填项，请输入")
    
    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """询问是/否问题"""
        default_str = "Y/n" if default else "y/N"
        answer = input(f"{question} [{default_str}]: ").strip().lower()
        
        if not answer:
            return default
        
        return answer in ['y', 'yes', '是']
    
    def step_welcome(self):
        """欢迎步骤"""
        self.print_header("智能知识平台 V2.1 - 配置向导")
        
        print("欢迎使用智能知识平台！\n")
        print("本向导将引导您完成平台的初始配置。")
        print("这个过程大约需要 5 分钟。\n")
        
        if self.env_file.exists():
            self.print_warning(f"发现已存在的配置文件: {self.env_file}")
            if not self.ask_yes_no("是否覆盖现有配置？", default=False):
                print("\n配置已取消。")
                sys.exit(0)
        
        input("\n按回车键继续...")
    
    def step_database(self):
        """数据库配置"""
        self.print_step(1, 7, "数据库配置")
        
        print("\n配置PostgreSQL数据库连接")
        print("提示: 如果使用Docker部署，可以使用默认值\n")
        
        self.config['DB_HOST'] = self.ask_question(
            "数据库主机",
            default="localhost"
        )
        
        self.config['DB_PORT'] = self.ask_question(
            "数据库端口",
            default="5432"
        )
        
        self.config['DB_NAME'] = self.ask_question(
            "数据库名称",
            default="platform_db"
        )
        
        self.config['DB_USER'] = self.ask_question(
            "数据库用户",
            default="platform_user"
        )
        
        self.config['DB_PASSWORD'] = self.ask_question(
            "数据库密码",
            default=self.generate_secret_key(16)
        )
        
        self.print_success("数据库配置完成")
    
    def step_redis(self):
        """Redis配置"""
        self.print_step(2, 7, "Redis配置")
        
        print("\n配置Redis缓存服务器\n")
        
        self.config['REDIS_HOST'] = self.ask_question(
            "Redis主机",
            default="localhost"
        )
        
        self.config['REDIS_PORT'] = self.ask_question(
            "Redis端口",
            default="6379"
        )
        
        self.config['REDIS_PASSWORD'] = self.ask_question(
            "Redis密码 (留空表示无密码)",
            default="",
            required=False
        )
        
        self.print_success("Redis配置完成")
    
    def step_mongodb(self):
        """MongoDB配置"""
        self.print_step(3, 7, "MongoDB配置")
        
        print("\n配置MongoDB数据库\n")
        
        use_mongodb = self.ask_yes_no("是否使用MongoDB？", default=True)
        
        if use_mongodb:
            self.config['MONGODB_HOST'] = self.ask_question(
                "MongoDB主机",
                default="localhost"
            )
            
            self.config['MONGODB_PORT'] = self.ask_question(
                "MongoDB端口",
                default="27017"
            )
            
            self.config['MONGODB_DB'] = self.ask_question(
                "MongoDB数据库名",
                default="platform_db"
            )
            
            self.print_success("MongoDB配置完成")
        else:
            self.print_warning("跳过MongoDB配置")
            self.config['MONGODB_HOST'] = ""
    
    def step_ai(self):
        """AI服务配置"""
        self.print_step(4, 7, "AI服务配置")
        
        print("\n配置AI服务密钥")
        print("提示: 需要至少配置一个AI服务\n")
        
        # OpenAI
        use_openai = self.ask_yes_no("是否使用OpenAI？", default=True)
        if use_openai:
            self.config['OPENAI_API_KEY'] = self.ask_question(
                "OpenAI API密钥",
                required=True
            )
            
            self.config['OPENAI_MODEL'] = self.ask_question(
                "OpenAI模型",
                default="gpt-4"
            )
            
            self.print_success("OpenAI配置完成")
        else:
            self.config['OPENAI_API_KEY'] = ""
        
        # Anthropic
        use_anthropic = self.ask_yes_no("是否使用Anthropic Claude？", default=False)
        if use_anthropic:
            self.config['ANTHROPIC_API_KEY'] = self.ask_question(
                "Anthropic API密钥",
                required=True
            )
            
            self.print_success("Anthropic配置完成")
        else:
            self.config['ANTHROPIC_API_KEY'] = ""
    
    def step_security(self):
        """安全配置"""
        self.print_step(5, 7, "安全配置")
        
        print("\n配置安全密钥\n")
        
        self.config['SECRET_KEY'] = self.generate_secret_key(64)
        self.print_success(f"生成SECRET_KEY: {self.config['SECRET_KEY'][:20]}...")
        
        self.config['JWT_SECRET'] = self.generate_secret_key(64)
        self.print_success(f"生成JWT_SECRET: {self.config['JWT_SECRET'][:20]}...")
        
        self.config['JWT_ALGORITHM'] = "HS256"
        self.config['JWT_EXPIRE_MINUTES'] = "30"
        
        self.print_success("安全配置完成")
    
    def step_app(self):
        """应用配置"""
        self.print_step(6, 7, "应用配置")
        
        print("\n配置应用基本信息\n")
        
        self.config['APP_NAME'] = self.ask_question(
            "应用名称",
            default="智能知识平台"
        )
        
        self.config['APP_VERSION'] = self.ask_question(
            "应用版本",
            default="2.1.0"
        )
        
        self.config['API_HOST'] = self.ask_question(
            "API主机",
            default="0.0.0.0"
        )
        
        self.config['API_PORT'] = self.ask_question(
            "API端口",
            default="8000"
        )
        
        self.config['DEBUG'] = "True" if self.ask_yes_no(
            "是否启用调试模式？",
            default=True
        ) else "False"
        
        self.print_success("应用配置完成")
    
    def step_optional(self):
        """可选配置"""
        self.print_step(7, 7, "可选配置")
        
        print("\n配置可选功能\n")
        
        # 对象存储
        use_minio = self.ask_yes_no("是否使用MinIO对象存储？", default=False)
        if use_minio:
            self.config['MINIO_ENDPOINT'] = self.ask_question(
                "MinIO地址",
                default="localhost:9000"
            )
            self.config['MINIO_ACCESS_KEY'] = self.ask_question("MinIO Access Key")
            self.config['MINIO_SECRET_KEY'] = self.ask_question("MinIO Secret Key")
        else:
            self.config['MINIO_ENDPOINT'] = ""
        
        # 邮件服务
        use_email = self.ask_yes_no("是否启用邮件服务？", default=False)
        if use_email:
            self.config['MAIL_SERVER'] = self.ask_question("SMTP服务器")
            self.config['MAIL_PORT'] = self.ask_question("SMTP端口", default="587")
            self.config['MAIL_USERNAME'] = self.ask_question("邮箱地址")
            self.config['MAIL_PASSWORD'] = self.ask_question("邮箱密码")
        else:
            self.config['MAIL_SERVER'] = ""
        
        # Sentry监控
        use_sentry = self.ask_yes_no("是否启用Sentry错误监控？", default=False)
        if use_sentry:
            self.config['SENTRY_DSN'] = self.ask_question("Sentry DSN")
        else:
            self.config['SENTRY_DSN'] = ""
        
        self.print_success("可选配置完成")
    
    def generate_env_file(self):
        """生成.env文件"""
        self.print_header("生成配置文件")
        
        env_content = []
        env_content.append("# ========================================")
        env_content.append("# 智能知识平台 V2.1 - 环境配置")
        env_content.append(f"# 生成时间: {os.popen('date').read().strip()}")
        env_content.append("# ========================================")
        env_content.append("")
        
        # 应用配置
        env_content.append("# ----------------------------------------")
        env_content.append("# 应用配置")
        env_content.append("# ----------------------------------------")
        env_content.append(f"APP_NAME={self.config['APP_NAME']}")
        env_content.append(f"APP_VERSION={self.config['APP_VERSION']}")
        env_content.append(f"API_HOST={self.config['API_HOST']}")
        env_content.append(f"API_PORT={self.config['API_PORT']}")
        env_content.append(f"DEBUG={self.config['DEBUG']}")
        env_content.append("")
        
        # 数据库配置
        env_content.append("# ----------------------------------------")
        env_content.append("# 数据库配置")
        env_content.append("# ----------------------------------------")
        env_content.append(f"DB_HOST={self.config['DB_HOST']}")
        env_content.append(f"DB_PORT={self.config['DB_PORT']}")
        env_content.append(f"DB_NAME={self.config['DB_NAME']}")
        env_content.append(f"DB_USER={self.config['DB_USER']}")
        env_content.append(f"DB_PASSWORD={self.config['DB_PASSWORD']}")
        env_content.append("")
        
        # Redis配置
        env_content.append("# ----------------------------------------")
        env_content.append("# Redis配置")
        env_content.append("# ----------------------------------------")
        env_content.append(f"REDIS_HOST={self.config['REDIS_HOST']}")
        env_content.append(f"REDIS_PORT={self.config['REDIS_PORT']}")
        if self.config['REDIS_PASSWORD']:
            env_content.append(f"REDIS_PASSWORD={self.config['REDIS_PASSWORD']}")
        env_content.append("")
        
        # MongoDB配置
        if self.config['MONGODB_HOST']:
            env_content.append("# ----------------------------------------")
            env_content.append("# MongoDB配置")
            env_content.append("# ----------------------------------------")
            env_content.append(f"MONGODB_HOST={self.config['MONGODB_HOST']}")
            env_content.append(f"MONGODB_PORT={self.config['MONGODB_PORT']}")
            env_content.append(f"MONGODB_DB={self.config['MONGODB_DB']}")
            env_content.append("")
        
        # AI配置
        env_content.append("# ----------------------------------------")
        env_content.append("# AI服务配置")
        env_content.append("# ----------------------------------------")
        if self.config['OPENAI_API_KEY']:
            env_content.append(f"OPENAI_API_KEY={self.config['OPENAI_API_KEY']}")
            env_content.append(f"OPENAI_MODEL={self.config['OPENAI_MODEL']}")
        if self.config['ANTHROPIC_API_KEY']:
            env_content.append(f"ANTHROPIC_API_KEY={self.config['ANTHROPIC_API_KEY']}")
        env_content.append("")
        
        # 安全配置
        env_content.append("# ----------------------------------------")
        env_content.append("# 安全配置")
        env_content.append("# ----------------------------------------")
        env_content.append(f"SECRET_KEY={self.config['SECRET_KEY']}")
        env_content.append(f"JWT_SECRET={self.config['JWT_SECRET']}")
        env_content.append(f"JWT_ALGORITHM={self.config['JWT_ALGORITHM']}")
        env_content.append(f"JWT_EXPIRE_MINUTES={self.config['JWT_EXPIRE_MINUTES']}")
        env_content.append("")
        
        # 可选配置
        if self.config.get('MINIO_ENDPOINT'):
            env_content.append("# ----------------------------------------")
            env_content.append("# 对象存储配置")
            env_content.append("# ----------------------------------------")
            env_content.append(f"MINIO_ENDPOINT={self.config['MINIO_ENDPOINT']}")
            env_content.append(f"MINIO_ACCESS_KEY={self.config['MINIO_ACCESS_KEY']}")
            env_content.append(f"MINIO_SECRET_KEY={self.config['MINIO_SECRET_KEY']}")
            env_content.append("")
        
        if self.config.get('MAIL_SERVER'):
            env_content.append("# ----------------------------------------")
            env_content.append("# 邮件服务配置")
            env_content.append("# ----------------------------------------")
            env_content.append(f"MAIL_SERVER={self.config['MAIL_SERVER']}")
            env_content.append(f"MAIL_PORT={self.config['MAIL_PORT']}")
            env_content.append(f"MAIL_USERNAME={self.config['MAIL_USERNAME']}")
            env_content.append(f"MAIL_PASSWORD={self.config['MAIL_PASSWORD']}")
            env_content.append("")
        
        if self.config.get('SENTRY_DSN'):
            env_content.append("# ----------------------------------------")
            env_content.append("# 监控配置")
            env_content.append("# ----------------------------------------")
            env_content.append(f"SENTRY_DSN={self.config['SENTRY_DSN']}")
            env_content.append("")
        
        # 写入文件
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(env_content))
        
        self.print_success(f"配置文件已生成: {self.env_file}")
        
        # 设置权限
        os.chmod(self.env_file, 0o600)
        self.print_success("已设置文件权限为 600 (仅所有者可读写)")
    
    def show_summary(self):
        """显示总结"""
        self.print_header("配置完成")
        
        print("✓ 所有配置已完成！\n")
        print(f"配置文件: {self.env_file}\n")
        
        print(f"{Colors.BOLD}下一步操作:{Colors.END}\n")
        print("1. 启动平台:")
        print(f"   {Colors.CYAN}python3 deploy.py{Colors.END}")
        print()
        print("2. 或手动启动:")
        print(f"   {Colors.CYAN}cd backend{Colors.END}")
        print(f"   {Colors.CYAN}./manage.py server start --reload{Colors.END}")
        print()
        print("3. 访问平台:")
        print(f"   API文档: {Colors.CYAN}http://localhost:{self.config['API_PORT']}/docs{Colors.END}")
        print()
        
        print(f"\n{Colors.BOLD}重要提示:{Colors.END}")
        print(f"• 请妥善保管配置文件 {self.env_file}")
        print(f"• 不要将配置文件提交到版本控制系统")
        print(f"• 定期备份配置文件")
        print()
    
    def run(self):
        """运行向导"""
        try:
            self.step_welcome()
            self.step_database()
            self.step_redis()
            self.step_mongodb()
            self.step_ai()
            self.step_security()
            self.step_app()
            self.step_optional()
            self.generate_env_file()
            self.show_summary()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n配置已取消。")
            return False
        except Exception as e:
            self.print_error(f"发生错误: {e}")
            return False


def main():
    """主函数"""
    wizard = SetupWizard()
    success = wizard.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
