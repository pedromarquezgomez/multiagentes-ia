#!/bin/bash
# railway-commands.sh - Comandos útiles para Railway

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para instalar Railway CLI
install_railway_cli() {
    print_header "Instalando Railway CLI"
    
    if command -v railway &> /dev/null; then
        print_warning "Railway CLI ya está instalado"
        railway --version
        return 0
    fi
    
    if command -v npm &> /dev/null; then
        npm install -g @railway/cli
        print_success "Railway CLI instalado exitosamente"
    else
        print_error "npm no está instalado. Instálalo primero."
        echo "Alternativamente, descarga desde: https://railway.app/cli"
        return 1
    fi
}

# Función para login en Railway
railway_login() {
    print_header "Login en Railway"
    railway login
    print_success "Login completado"
}

# Función para inicializar proyecto
init_project() {
    print_header "Inicializando proyecto en Railway"
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "railway.toml" ]; then
        print_error "No se encontró railway.toml. ¿Estás en el directorio correcto?"
        return 1
    fi
    
    railway link
    print_success "Proyecto vinculado con Railway"
}

# Función para desplegar
deploy() {
    print_header "Desplegando en Railway"
    
    # Verificar archivos necesarios
    if [ ! -f "Dockerfile.railway" ]; then
        print_error "No se encontró Dockerfile.railway"
        return 1
    fi
    
    if [ ! -f "start-railway.sh" ]; then
        print_error "No se encontró start-railway.sh"
        return 1
    fi
    
    print_warning "Asegúrate de haber configurado las variables de entorno:"
    echo "  - OPENAI_API_KEY"
    echo "  - OPENAI_BASE_URL"
    echo "  - OPENAI_MODEL"
    
    read -p "¿Continuar con el despliegue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        railway up
        print_success "Despliegue iniciado"
        
        # Mostrar logs en tiempo real
        echo "Presiona Ctrl+C para dejar de ver los logs"
        sleep 2
        railway logs
    else
        print_warning "Despliegue cancelado"
    fi
}

# Función para configurar variables de entorno
setup_env_vars() {
    print_header "Configurando Variables de Entorno"
    
    echo "Configuremos las variables principales:"
    
    # API Keys
    read -p "Ingresa tu OPENAI_API_KEY: " openai_key
    if [ -n "$openai_key" ]; then
        railway variables --set "OPENAI_API_KEY=$openai_key"
        print_success "API Key configurada"
    fi
    
    # URLs base
    railway variables --set "OPENAI_BASE_URL=https://api.openai.com/v1"
    railway variables --set "OPENAI_MODEL=gpt-4o-mini"
    railway variables --set "ENVIRONMENT=production"
    
    print_success "Variables básicas configuradas"
    
    # Mostrar variables actuales
    echo -e "\n${BLUE}Variables actuales:${NC}"
    railway variables
}

# Función para ver logs
view_logs() {
    print_header "Viendo Logs"
    railway logs --follow
}

# Función para ver estado
check_status() {
    print_header "Estado del Proyecto"
    railway status
    echo
    railway ps
}

# Función para abrir en navegador
open_app() {
    print_header "Abriendo aplicación"
    railway open
}

# Función para conectar a servicios
connect_services() {
    print_header "Conectar a Servicios"
    
    echo "Servicios disponibles:"
    echo "1. Redis"
    echo "2. Base de datos principal"
    
    read -p "¿A cuál quieres conectarte? (1-2): " service_choice
    
    case $service_choice in
        1)
            railway connect redis
            ;;
        2)
            railway shell
            ;;
        *)
            print_error "Opción inválida"
            ;;
    esac
}

# Función para restart
restart_app() {
    print_header "Reiniciando Aplicación"
    railway restart
    print_success "Aplicación reiniciada"
}

# Función para backup
backup_data() {
    print_header "Backup de Datos"
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    # Backup de configuración
    cp railway.toml "$backup_dir/"
    cp Dockerfile.railway "$backup_dir/"
    cp start-railway.sh "$backup_dir/"
    cp railway-env.example "$backup_dir/"
    
    print_success "Backup creado en $backup_dir"
}

# Función para mostrar URLs
show_urls() {
    print_header "URLs del Proyecto"
    
    domain=$(railway domain)
    
    if [ -n "$domain" ]; then
        echo -e "${GREEN}🌐 Aplicación Principal:${NC} https://$domain"
        echo -e "${GREEN}📖 Documentación API:${NC} https://$domain/docs"
        echo -e "${GREEN}🔍 Health Check:${NC} https://$domain/health"
        echo -e "${GREEN}📊 Estadísticas:${NC} https://$domain/stats"
    else
        print_warning "No se pudo obtener el dominio. ¿Está desplegado?"
    fi
}

# Función para troubleshooting
troubleshoot() {
    print_header "Diagnóstico de Problemas"
    
    echo "Verificando configuración..."
    
    # Verificar archivos locales
    files=("railway.toml" "Dockerfile.railway" "start-railway.sh")
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_success "$file existe"
        else
            print_error "$file no encontrado"
        fi
    done
    
    # Verificar variables de entorno
    echo -e "\n${BLUE}Variables de entorno críticas:${NC}"
    railway variables | grep -E "(OPENAI|ENVIRONMENT)" || print_warning "No se encontraron variables críticas"
    
    # Verificar logs recientes
    echo -e "\n${BLUE}Logs recientes:${NC}"
    railway logs --tail 10
}

# Menú principal
show_menu() {
    clear
    print_header "🚀 Sistema de Deployment Railway"
    echo "Proyecto: Sistema Sumiller Virtual"
    echo
    echo "1.  Instalar Railway CLI"
    echo "2.  Login en Railway"
    echo "3.  Inicializar proyecto"
    echo "4.  Configurar variables de entorno"
    echo "5.  Desplegar aplicación"
    echo "6.  Ver logs"
    echo "7.  Verificar estado"
    echo "8.  Abrir aplicación"
    echo "9.  Conectar a servicios"
    echo "10. Reiniciar aplicación"
    echo "11. Crear backup"
    echo "12. Mostrar URLs"
    echo "13. Diagnóstico de problemas"
    echo "0.  Salir"
    echo
    read -p "Selecciona una opción (0-13): " choice
    
    case $choice in
        1) install_railway_cli ;;
        2) railway_login ;;
        3) init_project ;;
        4) setup_env_vars ;;
        5) deploy ;;
        6) view_logs ;;
        7) check_status ;;
        8) open_app ;;
        9) connect_services ;;
        10) restart_app ;;
        11) backup_data ;;
        12) show_urls ;;
        13) troubleshoot ;;
        0) exit 0 ;;
        *) print_error "Opción inválida" ;;
    esac
    
    echo
    read -p "Presiona Enter para continuar..."
    show_menu
}

# Si se ejecuta sin argumentos, mostrar menú
if [ $# -eq 0 ]; then
    show_menu
else
    # Ejecutar función específica si se pasa como argumento
    case $1 in
        install) install_railway_cli ;;
        login) railway_login ;;
        init) init_project ;;
        env) setup_env_vars ;;
        deploy) deploy ;;
        logs) view_logs ;;
        status) check_status ;;
        open) open_app ;;
        restart) restart_app ;;
        backup) backup_data ;;
        urls) show_urls ;;
        troubleshoot) troubleshoot ;;
        *) echo "Función no reconocida: $1" ;;
    esac
fi 