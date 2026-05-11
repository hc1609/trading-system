#!/bin/bash
# 初始化所有Django app的基础结构

cd apps

# 创建所有app目录
apps=("market" "strategy" "position" "box" "daytrade" "risk" "config" "sync")

for app in "${apps[@]}"; do
    echo "Creating app: $app"
    mkdir -p "$app/services"
    touch "$app/__init__.py"
    touch "$app/admin.py"
    touch "$app/apps.py"
    touch "$app/models.py"
    touch "$app/serializers.py"
    touch "$app/views.py"
    touch "$app/urls.py"
    touch "$app/tasks.py"
    touch "$app/services/__init__.py"
done

echo "All apps initialized!"
