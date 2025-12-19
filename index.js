/**
 * Archivo Orquestador Principal del Bot de Trading
 * Punto de entrada que conecta todos los módulos Python
 */

const { spawn } = require('child_process');
const path = require('path');

class TradingBotOrchestrator {
    constructor() {
        this.pythonProcess = null;
        this.isRunning = false;
        this.restartAttempts = 0;
        this.maxRestartAttempts = 5;
        this.restartDelay = 30000; // 30 segundos
    }

    /**
     * Inicia el bot de trading
     */
    async start() {
        console.log('🤖 Iniciando Bot de Trading - Breakout + Reentry');
        console.log('=' * 60);

        try {
            // Verificar que el archivo Python principal existe
            const pythonMainPath = path.join(__dirname, 'src', 'main.py');
            console.log(`📁 Ruta del archivo principal: ${pythonMainPath}`);

            // Iniciar proceso Python
            await this.startPythonProcess();
            
            // Configurar manejo de señales del sistema
            this.setupSignalHandlers();
            
            console.log('✅ Bot de trading iniciado correctamente');
            
        } catch (error) {
            console.error('❌ Error iniciando el bot:', error);
            process.exit(1);
        }
    }

    /**
     * Inicia el proceso Python
     */
    startPythonProcess() {
        return new Promise((resolve, reject) => {
            try {
                console.log('🐍 Iniciando proceso Python...');

                const pythonPath = process.env.PYTHON_PATH || 'python3';
                const scriptPath = path.join(__dirname, 'src', 'main.py');

                const options = {
                    stdio: ['pipe', 'pipe', 'pipe'],
                    cwd: __dirname,
                    env: {
                        ...process.env,
                        PYTHONPATH: path.join(__dirname, 'src')
                    }
                };

                this.pythonProcess = spawn(pythonPath, [scriptPath], options);

                // Manejar salida del proceso
                this.pythonProcess.stdout.on('data', (data) => {
                    const output = data.toString();
                    console.log('📤 PYTHON OUTPUT:', output.trim());
                });

                this.pythonProcess.stderr.on('data', (data) => {
                    const error = data.toString();
                    console.error('❌ PYTHON ERROR:', error.trim());
                });

                this.pythonProcess.on('close', (code) => {
                    console.log(`🐍 Proceso Python terminó con código: ${code}`);
                    this.isRunning = false;
                    
                    if (code !== 0 && this.restartAttempts < this.maxRestartAttempts) {
                        this.restartAttempts++;
                        console.log(`🔄 Reiniciando bot (intento ${this.restartAttempts}/${this.maxRestartAttempts})...`);
                        
                        setTimeout(() => {
                            this.startPythonProcess().then(resolve).catch(reject);
                        }, this.restartDelay);
                    } else if (code !== 0) {
                        reject(new Error(`Proceso Python terminó con código ${code} después de ${this.restartAttempts} intentos`));
                    }
                });

                this.pythonProcess.on('error', (error) => {
                    console.error('❌ Error en proceso Python:', error);
                    reject(error);
                });

                this.isRunning = true;
                resolve();

            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Configura manejo de señales del sistema
     */
    setupSignalHandlers() {
        // Manejar cierre graceful
        process.on('SIGTERM', () => {
            console.log('📨 Recibida señal SIGTERM, cerrando bot...');
            this.shutdown();
        });

        process.on('SIGINT', () => {
            console.log('📨 Recibida señal SIGINT, cerrando bot...');
            this.shutdown();
        });

        // Manejar errores no capturados
        process.on('uncaughtException', (error) => {
            console.error('💥 Excepción no capturada:', error);
            this.shutdown();
        });

        process.on('unhandledRejection', (reason, promise) => {
            console.error('💥 Promise rechazada no manejada:', reason);
            this.shutdown();
        });
    }

    /**
     * Cierra el bot de trading
     */
    shutdown() {
        console.log('🛑 Cerrando bot de trading...');

        if (this.pythonProcess) {
            console.log('🐍 Terminando proceso Python...');
            this.pythonProcess.kill('SIGTERM');
            
            // Forzar cierre después de 10 segundos
            setTimeout(() => {
                if (this.pythonProcess && !this.pythonProcess.killed) {
                    console.log('⚡ Forzando cierre del proceso Python...');
                    this.pythonProcess.kill('SIGKILL');
                }
            }, 10000);
        }

        console.log('👋 Bot de trading cerrado');
        process.exit(0);
    }

    /**
     * Obtiene el estado del bot
     */
    getStatus() {
        return {
            running: this.isRunning,
            restartAttempts: this.restartAttempts,
            maxRestartAttempts: this.maxRestartAttempts,
            pythonProcessRunning: this.pythonProcess && !this.pythonProcess.killed
        };
    }
}

/**
 * Función principal
 */
async function main() {
    const orchestrator = new TradingBotOrchestrator();
    
    try {
        await orchestrator.start();
        
        // Mantener el proceso vivo
        console.log('🔄 Bot de trading ejecutándose...');
        console.log('📊 Endpoints disponibles:');
        console.log(`   Health Check: http://localhost:5000/health`);
        console.log(`   Status: http://localhost:5000/status`);
        console.log(`   Ready: http://localhost:5000/ready`);
        
        // Monitorear estado cada 30 segundos
        setInterval(() => {
            const status = orchestrator.getStatus();
            console.log(`📈 Estado: ${status.running ? '🟢 Activo' : '🔴 Inactivo'}`);
        }, 30000);
        
    } catch (error) {
        console.error('❌ Error en main:', error);
        process.exit(1);
    }
}

// Ejecutar si es el archivo principal
if (require.main === module) {
    main().catch(console.error);
}

module.exports = TradingBotOrchestrator;