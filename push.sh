#!/bin/bash
# 推送脚本 - Push to GitHub

echo "=========================================="
echo "Vidur Simulator - 推送到GitHub"
echo "=========================================="
echo ""
echo "准备推送以下提交到GitHub:"
echo ""

# 显示待推送的提交
git log origin/Sai_speculative_decode..HEAD --oneline

echo ""
echo "分支: Sai_speculative_decode"
echo "仓库: https://github.com/Nemo0412/Sai_speculative_vidur"
echo ""
echo "正在推送..."
echo ""

# 执行推送
git push origin Sai_speculative_decode

# 检查推送结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "查看你的更改:"
    echo "https://github.com/Nemo0412/Sai_speculative_vidur/tree/Sai_speculative_decode"
    echo ""
else
    echo ""
    echo "❌ 推送失败！"
    echo ""
    echo "可能的原因:"
    echo "1. 需要GitHub认证 - 请设置Personal Access Token"
    echo "2. 网络问题"
    echo "3. 权限问题"
    echo ""
    echo "详细说明请查看: PUSH_TO_GITHUB.md"
    echo ""
fi

