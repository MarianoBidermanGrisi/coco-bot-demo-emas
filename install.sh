#!/bin/bash

# Script de Instalación Automática del Bot de Trading
# Autor: MiniMax Agent

echo "🤖 INSTALADOR DEL BOT DE TRADING BREAKOUT + REENTRY"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para print con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Python está instalado
check_python() {
    print_status "Verificando Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        print_success "Python encontrado: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        print_success "Python encontrado: $PYTHON_VERSION"
    else
        print_error "Python no está instalado"
        print_status "Instalando Python 3..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        else
            print_error "No se pudo instalar Python automáticamente"
            exit 1
        fi
    fi
}

# Verificar si Node.js está instalado
check_nodejs() {
    print_status "Verificando Node.js..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js encontrado: $NODE_VERSION"
    else
        print_warning "Node.js no está instalado"
        print_status "Instalando Node.js..."
        if command -v apt-get &> /dev/null; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif command -v yum &> /dev/null; then
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo yum install -y nodejs
        else
            print_error "No se pudo instalar Node.js automáticamente"
            print_status "Por favor instala Node.js manualmente desde https://nodejs.org/"
            exit 1
        fi
    fi
}

# Instalar dependencias Python
install_python_deps() {
    print_status "Instalando dependencias Python..."
    if command -v python3 &> /dev/null; then
        python3 -m pip install --user --upgrade pip
        python3 -m pip install -r requirements.txt
        print_success "Dependencias Python instaladas"
    else
        python -m pip install --user --upgrade pip
        python -m pip install -r requirements.txt
        print_success "Dependencias Python instaladas"
    fi
}

# Instalar dependencias Node.js
install_nodejs_deps() {
    print_status "Instalando dependencias Node.js..."
    npm install
    print_success "Dependencias Node.js instaladas"
}

# Crear archivo .env si no existe
setup_env_file() {
    print_status "Configurando archivo de entorno..."
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Archivo .env creado"
        print_warning "IMPORTANTE: Edita el archivo .env con tus configuraciones"
        print_warning "   - TELEGRAM_TOKEN: Token de tu bot de Telegram"
        print_warning "   - TELEGRAM_CHAT_ID: ID de tu chat de Telegram"
        print_warning "   - RENDER_EXTERNAL_URL: URL de tu app en Render"
    else
        print_warning "El archivo .env ya existe"
    fi
}

# Crear directorios necesarios
create_directories() {
    print_status "Creando directorios necesarios..."
    mkdir -p logs data
    print_success "Directorios creados"
}

# Verificar instalación
verify_installation() {
    print_status "Verificando instalación..."
    
    # Verificar Python
    if python3 -c "import requests, pandas, numpy, matplotlib, flask" 2>/dev/null; then
        print_success "Dependencias Python OK"
    else
        print_error "Algunas dependencias Python fallaron"
        return 1
    fi
    
    # Verificar Node.js
    if [ -f "node_modules/.bin/node" ] || command -v node &> /dev/null; then
        print_success "Node.js OK"
    else
        print_error "Node.js no está disponible"
        return 1
    fi
    
    # Verificar estructura de archivos
    if [ -f "src/main.py" ] && [ -f "index.js" ]; then
        print_success "Estructura de archivos OK"
    else
        print_error "Estructura de archivos incompleta"
        return 1
    fi
    
    return 0
}

# Mostrar resumen final
show_summary() {
    echo ""
    echo "🎉 INSTALACIÓN COMPLETADA"
    echo "========================"
    echo ""
    echo "📋 PRÓXIMOS PASOS:"
    echo "1. Edita el archivo .env con tus configuraciones"
    echo "2. Configura tu bot de Telegram con @BotFather"
    echo "3. Obtén tu Chat ID con @userinfobot"
    echo "4. Despliega en Render.com"
    echo ""
    echo "🚀 PARA EJECUTAR LOCALMENTE:"
    echo "   node index.js"
    echo "   # o"
    echo "   python src/main.py"
    echo ""
    echo "📊 ENDPOINTS DISPONIBLES:"
    echo "   Health Check: http://localhost:5000/health"
    echo "   Status: http://localhost:5000/status"
    echo ""
    echo "📖 DOCUMENTACIÓN:"
    echo "   Lee el archivo README.md para más detalles"
    echo ""
}

# Función principal
main() {
    echo ""
    print_status "Iniciando instalación del Bot de Trading..."
    echo ""
    
    # Verificaciones del sistema
    check_python
    check_nodejs
    
    # Instalación de dependencias
    install_python_deps
    install_nodejs_deps
    
    # Configuración
    setup_env_file
    create_directories
    
    # Verificación final
    if verify_installation; then
        show_summary
        print_success "¡Instalación exitosa!"
    else
        print_error "La instalación tuvo problemas"
        print_status "Revisa los errores anteriores e intenta nuevamente"
        exit 1
    fi
}

# Verificar si se ejecuta como script principal
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi