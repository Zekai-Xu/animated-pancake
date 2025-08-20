#!/bin/bash

# AI学术论文监控系统 - 启动脚本
# AI Academic Paper Monitoring System - Startup Script

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
AI学术论文监控系统 - 启动脚本

用法:
    ./run.sh [选项] [命令]

命令:
    install     - 安装系统依赖和Python包
    setup       - 初始化系统 (创建目录、配置文件等)
    gui         - 启动Web界面 (默认端口8501)
    cli         - 运行命令行版本
    test        - 运行系统测试
    clean       - 清理临时文件和缓存
    backup      - 备份数据库和配置
    restore     - 恢复数据库备份
    update      - 更新系统到最新版本
    docker      - 使用Docker运行系统
    help        - 显示此帮助信息

选项:
    --port PORT         指定Web界面端口 (默认: 8501)
    --config CONFIG     指定配置文件路径 (默认: config/config.yaml)
    --verbose          详细输出模式
    --no-browser       启动Web界面时不自动打开浏览器
    --dev              开发模式 (启用调试功能)

示例:
    ./run.sh install                    # 安装系统
    ./run.sh gui --port 8080           # 在端口8080启动Web界面
    ./run.sh cli --verbose             # 详细模式运行命令行版本
    ./run.sh test                      # 运行系统测试
    ./run.sh docker                    # 使用Docker运行

更多信息请查看 README.md 文档
EOF
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装Python 3.8+"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python版本过低: $python_version, 需要 $required_version+"
        exit 1
    fi
    
    print_success "Python版本检查通过: $python_version"
}

# 检查Chrome浏览器
check_chrome() {
    print_info "检查Chrome浏览器..."
    
    if command -v google-chrome &> /dev/null; then
        chrome_version=$(google-chrome --version | cut -d' ' -f3)
        print_success "Chrome已安装: $chrome_version"
    elif command -v chromium-browser &> /dev/null; then
        chromium_version=$(chromium-browser --version | cut -d' ' -f2)
        print_success "Chromium已安装: $chromium_version"
    else
        print_warning "Chrome/Chromium未检测到，系统将尝试自动下载ChromeDriver"
    fi
}

# 创建虚拟环境
create_venv() {
    print_info "创建Python虚拟环境..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "虚拟环境创建成功"
    else
        print_info "虚拟环境已存在"
    fi
}

# 激活虚拟环境
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_info "虚拟环境已激活"
    else
        print_error "虚拟环境未找到，请先运行: ./run.sh install"
        exit 1
    fi
}

# 安装Python依赖
install_dependencies() {
    print_info "安装Python依赖包..."
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "依赖包安装完成"
    else
        print_error "requirements.txt 文件未找到"
        exit 1
    fi
}

# 创建必要目录
create_directories() {
    print_info "创建必要目录..."
    
    directories=("logs" "data" "output" "config")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "创建目录: $dir"
        fi
    done
}

# 初始化配置文件
init_config() {
    print_info "初始化配置文件..."
    
    if [ ! -f "config/config.yaml" ]; then
        print_error "配置文件 config/config.yaml 未找到"
        print_info "请确保配置文件存在，或从模板复制"
        exit 1
    else
        print_success "配置文件检查通过"
    fi
}

# 安装系统
install_system() {
    print_info "开始安装AI学术论文监控系统..."
    
    check_python
    check_chrome
    create_venv
    activate_venv
    install_dependencies
    create_directories
    init_config
    
    print_success "系统安装完成！"
    print_info "运行 './run.sh gui' 启动Web界面"
    print_info "运行 './run.sh cli --help' 查看命令行选项"
}

# 系统设置
setup_system() {
    print_info "初始化系统设置..."
    
    create_directories
    init_config
    
    # 创建示例环境变量文件
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# AI学术论文监控系统环境变量
# 数据库配置
DATABASE_PATH=data/papers.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/paper_monitor.log

# 代理配置 (如需要)
# HTTP_PROXY=http://127.0.0.1:7890
# HTTPS_PROXY=http://127.0.0.1:7890

# Chrome配置
CHROME_HEADLESS=true
CHROME_NO_SANDBOX=true
EOF
        print_success "创建环境变量文件: .env"
    fi
    
    print_success "系统设置完成"
}

# 启动Web界面
start_gui() {
    local port=${PORT:-8501}
    local no_browser=${NO_BROWSER:-false}
    
    print_info "启动Web界面..."
    print_info "端口: $port"
    
    activate_venv
    
    # 检查端口是否被占用
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        print_warning "端口 $port 已被占用"
        read -p "是否使用其他端口? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            port=$((port + 1))
            print_info "使用端口: $port"
        else
            exit 1
        fi
    fi
    
    # 启动Streamlit
    if [ "$no_browser" = true ]; then
        streamlit run gui.py --server.port=$port --server.headless=true
    else
        streamlit run gui.py --server.port=$port
    fi
}

# 运行命令行版本
run_cli() {
    print_info "启动命令行版本..."
    
    activate_venv
    
    # 传递所有参数给main.py
    python main.py "$@"
}

# 运行测试
run_tests() {
    print_info "运行系统测试..."
    
    activate_venv
    
    # 基础功能测试
    print_info "1. 测试Python环境..."
    python -c "
import sys
print(f'Python版本: {sys.version}')

# 测试关键依赖包
try:
    import requests, beautifulsoup4, selenium, pandas, openpyxl, streamlit, yaml
    print('✓ 所有依赖包导入成功')
except ImportError as e:
    print(f'✗ 依赖包导入失败: {e}')
    sys.exit(1)
"
    
    # 测试数据库连接
    print_info "2. 测试数据库连接..."
    python -c "
try:
    from src.core.database import DatabaseManager
    db = DatabaseManager('data/test.db')
    print('✓ 数据库连接成功')
    db.close()
    import os
    os.remove('data/test.db')
except Exception as e:
    print(f'✗ 数据库连接失败: {e}')
"
    
    # 测试配置文件
    print_info "3. 测试配置文件..."
    python -c "
try:
    import yaml
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print('✓ 配置文件加载成功')
except Exception as e:
    print(f'✗ 配置文件加载失败: {e}')
"
    
    print_success "系统测试完成"
}

# 清理系统
clean_system() {
    print_info "清理系统缓存和临时文件..."
    
    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理日志文件 (保留最近的)
    if [ -d "logs" ]; then
        find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    fi
    
    # 清理pip缓存
    if command -v pip &> /dev/null; then
        pip cache purge 2>/dev/null || true
    fi
    
    print_success "清理完成"
}

# 备份数据
backup_data() {
    print_info "备份系统数据..."
    
    backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份数据库
    if [ -f "data/papers.db" ]; then
        cp "data/papers.db" "$backup_dir/"
        print_success "数据库备份完成"
    fi
    
    # 备份配置文件
    if [ -f "config/config.yaml" ]; then
        cp "config/config.yaml" "$backup_dir/"
        print_success "配置文件备份完成"
    fi
    
    # 备份环境变量
    if [ -f ".env" ]; then
        cp ".env" "$backup_dir/"
        print_success "环境变量备份完成"
    fi
    
    print_success "备份完成: $backup_dir"
}

# 恢复数据
restore_data() {
    print_info "恢复系统数据..."
    
    if [ ! -d "backups" ]; then
        print_error "备份目录不存在"
        exit 1
    fi
    
    # 列出可用备份
    echo "可用备份:"
    ls -1 backups/ | nl
    
    read -p "请选择要恢复的备份编号: " backup_num
    
    backup_name=$(ls -1 backups/ | sed -n "${backup_num}p")
    
    if [ -z "$backup_name" ]; then
        print_error "无效的备份编号"
        exit 1
    fi
    
    backup_path="backups/$backup_name"
    
    # 恢复文件
    if [ -f "$backup_path/papers.db" ]; then
        cp "$backup_path/papers.db" "data/"
        print_success "数据库恢复完成"
    fi
    
    if [ -f "$backup_path/config.yaml" ]; then
        cp "$backup_path/config.yaml" "config/"
        print_success "配置文件恢复完成"
    fi
    
    print_success "数据恢复完成"
}

# 更新系统
update_system() {
    print_info "更新系统到最新版本..."
    
    # 备份当前数据
    backup_data
    
    # 更新代码
    if [ -d ".git" ]; then
        git pull origin main
        print_success "代码更新完成"
    else
        print_warning "非Git仓库，请手动更新代码"
    fi
    
    # 更新依赖
    activate_venv
    pip install -r requirements.txt --upgrade
    print_success "依赖更新完成"
    
    print_success "系统更新完成"
}

# 使用Docker运行
run_docker() {
    print_info "使用Docker运行系统..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 构建镜像
    print_info "构建Docker镜像..."
    docker build -t ai-paper-monitor .
    
    # 运行容器
    print_info "启动Docker容器..."
    docker run -p 8501:8501 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/output:/app/output" \
        -v "$(pwd)/logs:/app/logs" \
        ai-paper-monitor
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --port)
                PORT="$2"
                shift 2
                ;;
            --config)
                CONFIG="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --no-browser)
                NO_BROWSER=true
                shift
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            install)
                install_system
                exit 0
                ;;
            setup)
                setup_system
                exit 0
                ;;
            gui)
                shift
                start_gui "$@"
                exit 0
                ;;
            cli)
                shift
                run_cli "$@"
                exit 0
                ;;
            test)
                run_tests
                exit 0
                ;;
            clean)
                clean_system
                exit 0
                ;;
            backup)
                backup_data
                exit 0
                ;;
            restore)
                restore_data
                exit 0
                ;;
            update)
                update_system
                exit 0
                ;;
            docker)
                run_docker
                exit 0
                ;;
            help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定命令，显示帮助
    show_help
}

# 运行主函数
main "$@"