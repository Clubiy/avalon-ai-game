#!/bin/bash

# Git 配置和 GitHub 发布脚本
# 使用方法：./setup_git_and_push.sh

echo "============================================================"
echo "Avalon AI Game - Git 配置和 GitHub 发布脚本"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否已配置 Git
if ! git config user.name > /dev/null 2>&1; then
    echo -e "${YELLOW}需要配置 Git 用户信息${NC}"
    echo ""
    
    # 获取用户输入
    read -p "请输入你的 GitHub 用户名或昵称: " GIT_USER_NAME
    read -p "请输入你的 GitHub 注册邮箱: " GIT_USER_EMAIL
    
    # 配置 Git（仅在当前仓库）
    git config user.name "$GIT_USER_NAME"
    git config user.email "$GIT_USER_EMAIL"
    
    echo -e "${GREEN}✓ Git 用户信息配置完成${NC}"
    echo ""
else
    echo -e "${GREEN}✓ Git 用户信息已配置${NC}"
    echo "  用户名：$(git config user.name)"
    echo "  邮箱：$(git config user.email)"
    echo ""
fi

# 检查是否有远程仓库
if ! git remote get-url origin > /dev/null 2>&1; then
    echo -e "${YELLOW}需要添加远程仓库${NC}"
    echo ""
    
    # 获取 GitHub 用户名
    GITHUB_USERNAME=$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    read -p "请输入你的 GitHub 用户名 (默认：$GITHUB_USERNAME): " INPUT_USERNAME
    GITHUB_USERNAME=${INPUT_USERNAME:-$GITHUB_USERNAME}
    
    # 询问仓库名称
    read -p "请输入仓库名称 (默认：avalon-ai-game): " REPO_NAME
    REPO_NAME=${REPO_NAME:-avalon-ai-game}
    
    # 询问是公开还是私有仓库
    echo ""
    echo "选择仓库类型:"
    echo "1) 公开仓库 (Public) - 推荐"
    echo "2) 私有仓库 (Private)"
    read -p "请选择 (1/2): " REPO_TYPE
    
    if [ "$REPO_TYPE" = "1" ]; then
        VISIBILITY="public"
    else
        VISIBILITY="private"
    fi
    
    echo ""
    echo -e "${YELLOW}请按照以下步骤操作:${NC}"
    echo ""
    echo "1. 访问 https://github.com/new"
    echo "2. 输入仓库名称：$REPO_NAME"
    echo "3. 选择 $VISIBILITY"
    echo "4. 不要勾选 'Initialize this repository with a README'"
    echo "5. 点击 'Create repository'"
    echo ""
    
    read -p "创建完成后，按回车键继续..."
    
    # 添加远程仓库
    REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    git remote add origin "$REMOTE_URL"
    
    echo -e "${GREEN}✓ 远程仓库已添加${NC}"
    echo "  地址：$REMOTE_URL"
    echo ""
    
    # 推送代码
    echo -e "${YELLOW}准备推送到 GitHub...${NC}"
    echo ""
    
    read -p "是否现在推送代码到 GitHub? (y/n): " PUSH_NOW
    
    if [ "$PUSH_NOW" = "y" ] || [ "$PUSH_NOW" = "Y" ]; then
        echo "推送到 GitHub..."
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}============================================${NC}"
            echo -e "${GREEN}✓ 成功推送到 GitHub!${NC}"
            echo -e "${GREEN}============================================${NC}"
            echo ""
            echo "🎉 你的项目已成功发布！"
            echo ""
            echo "访问地址：https://github.com/$GITHUB_USERNAME/$REPO_NAME"
            echo ""
            echo "下一步建议:"
            echo "1. 在 GitHub 上查看你的仓库"
            echo "2. 更新 README.md 添加徽章和简介"
            echo "3. 在社交媒体分享你的项目"
            echo "4. 考虑添加更多功能和文档"
            echo ""
        else
            echo ""
            echo -e "${RED}推送失败，请检查网络连接和仓库配置${NC}"
            exit 1
        fi
    else
        echo ""
        echo -e "${YELLOW}稍后手动推送：git push -u origin main${NC}"
        echo ""
    fi
else
    echo -e "${GREEN}✓ 远程仓库已配置${NC}"
    echo "  地址：$(git remote get-url origin)"
    echo ""
    
    # 直接推送
    read -p "是否推送到远程仓库？(y/n): " PUSH_NOW
    
    if [ "$PUSH_NOW" = "y" ] || [ "$PUSH_NOW" = "Y" ]; then
        git push -u origin main
        echo -e "${GREEN}✓ 推送成功${NC}"
    fi
fi

echo "============================================================"
echo "配置完成！"
echo "============================================================"
