#!/bin/bash
# 15本考研书系列 - 快速更新脚本

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   🔄 15本考研书系列 - 快速更新"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查是否是git仓库
if [ ! -d ".git" ]; then
    echo "❌ 当前目录不是git仓库"
    echo "💡 提示：如果这是首次使用，请先执行："
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

echo "🔍 检查更新..."
echo ""

# 检查远程仓库
REMOTE=$(git remote -v | grep fetch | awk '{print $2}')

if [ -z "$REMOTE" ]; then
    echo "⚠️ 未配置远程仓库"
    echo ""
    read -p "是否现在配置？(y/n): " CONFIG_REMOTE
    
    if [ "$CONFIG_REMOTE" = "y" ]; then
        echo ""
        echo "请输入远程仓库地址（如：https://github.com/username/repo.git）："
        read REMOTE_URL
        
        if [ ! -z "$REMOTE_URL" ]; then
            git remote add origin "$REMOTE_URL"
            echo "✅ 远程仓库已配置"
        fi
    fi
    exit 0
fi

echo "📡 远程仓库: $REMOTE"
echo ""

# 拉取最新代码
echo "⬇️ 正在拉取最新代码..."
git fetch origin

# 检查是否有更新
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ 已是最新版本"
elif [ "$LOCAL" = "$BASE" ]; then
    echo "🆕 发现新版本，正在更新..."
    
    # 保存本地修改
    if [[ -n $(git status -s) ]]; then
        echo "💾 检测到本地修改，正在保存..."
        git stash
        STASHED=1
    fi
    
    # 拉取更新
    git pull origin main || git pull origin master
    
    # 恢复本地修改
    if [ "$STASHED" = "1" ]; then
        echo "📂 恢复本地修改..."
        git stash pop
    fi
    
    echo ""
    echo "✅ 更新完成！"
    echo ""
    
    # 显示更新日志
    echo "📋 最近的更新："
    git log --oneline -5
    
elif [ "$REMOTE" = "$BASE" ]; then
    echo "⚠️ 本地版本较新，可能需要推送"
else
    echo "⚠️ 本地和远程版本有分歧"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✨ 更新检查完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
