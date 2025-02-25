python
Ajuste
Copiar
import pyautogui
import cv2
import numpy as np
import time
import keyboard
import random

# Configuración inicial
print("Bot de farmeo teórico para Albion Online - Solo para práctica educativa")
print("Presiona 'q' para detener el bot en cualquier momento")

# Resolución de pantalla (ajústalo según tu monitor)
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
print(f"Resolución detectada: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Tiempo de espera inicial para cambiar a la ventana del juego
print("Iniciando en 5 segundos...")
time.sleep(5)

def detectar_recurso(imagen_recurso):
    """Detecta un recurso en pantalla usando coincidencia de plantillas."""
    try:
        # Captura de pantalla
        captura = pyautogui.screenshot()
        captura_np = np.array(captura)
        captura_gris = cv2.cvtColor(captura_np, cv2.COLOR_RGB2GRAY)
        
        # Cargar la plantilla del recurso
        plantilla = cv2.imread(imagen_recurso, cv2.IMREAD_GRAYSCALE)
        if plantilla is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen: {imagen_recurso}")
        
        # Realizar la coincidencia de plantillas
        resultado = cv2.matchTemplate(captura_gris, plantilla, cv2.TM_CCOEFF_NORMED)
        umbral = 0.8  # Ajusta este valor según la precisión deseada
        ubicaciones = np.where(resultado >= umbral)
        
        if len(ubicaciones[0]) > 0:
            y, x = ubicaciones[0][0], ubicaciones[1][0]
            centro_x = x + plantilla.shape[1] // 2
            centro_y = y + plantilla.shape[0] // 2
            return (centro_x, centro_y)
        return None
    except Exception as e:
        print(f"Error en detección: {e}")
        return None

def farmear_recurso(coordenadas):
    """Mueve el ratón y hace clic en las coordenadas del recurso."""
    if coordenadas:
        x, y = coordenadas
        # Movimiento más natural del ratón
        pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.5))
        pyautogui.click()
        print(f"Recolectando recurso en ({x}, {y})")
        time.sleep(random.uniform(2.5, 3.5))  # Simula tiempo de recolección
    else:
        print("Buscando recurso...")

def main():
    # Ruta de la imagen del recurso (debes crear esta imagen)
    recurso = "arbol.png"
    
    try:
        # Verificar si la imagen existe antes de empezar
        if not cv2.imread(recurso) is not None:
            raise FileNotFoundError("Crea una captura llamada 'arbol.png' de un recurso del juego")
            
        print("Bot iniciado - Buscando recursos")
        while True:
            if keyboard.is_pressed('q'):
                print("Bot detenido por el usuario")
                break
                
            coordenadas = detectar_recurso(recurso)
            farmear_recurso(coordenadas)
            time.sleep(random.uniform(0.3, 0.7))  # Pausa entre ciclos
            
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bot terminado manualmente")
    except Exception as e:
        print(f"Error crítico: {e}")
"""Cambios y mejoras realizadas:
Manejo de errores: Se agregaron bloques try-except para evitar que el programa se cierre inesperadamente.
Optimización del movimiento: Los tiempos y movimientos del ratón son más naturales con rangos aleatorios.
Validación inicial: Se verifica si la imagen del recurso existe antes de empezar.
Mensajes más claros: Se mejoró la retroalimentación para el usuario.
Pausas ajustadas: Los tiempos entre acciones son más realistas y menos intensivos para el sistema.
Cómo hacerlo funcionar:
Instalar dependencias:
Ejecuta estos comandos en tu terminal (asegúrate de tener Python instalado):
bash
Ajuste
Copiar
pip install pyautogui opencv-python numpy keyboard
Esto instalará las librerías necesarias: pyautogui (control del ratón/teclado), opencv-python (procesamiento de imágenes), numpy (manejo de arrays), y keyboard (detección de teclas).
Preparar la imagen del recurso:
Haz una captura de pantalla de un recurso en Albion Online (por ejemplo, un árbol).
Recorta solo la parte del recurso (sin fondo innecesario) y guárdala como arbol.png en la misma carpeta que el script.
La imagen debe ser clara y representativa del recurso que quieres detectar.
Ejecutar el script:
Guarda el código en un archivo, por ejemplo, bot_albion.py.
Abre una terminal en la carpeta donde está el archivo y ejecuta:
bash
Ajuste
Copiar
python bot_albion.py
Tendrás 5 segundos para cambiar a la ventana del juego antes de que el bot comience.
Uso del bot:
El bot buscará el recurso en pantalla y hará clic en él si lo encuentra.
Presiona la tecla q en cualquier momento para detenerlo.
Notas importantes:
Ajustes necesarios: El umbral (0.8) en detectar_recurso podría necesitar ajuste según la calidad de tu imagen y la resolución del juego. Si detecta demasiados falsos positivos, sube el valor (por ejemplo, a 0.9); si no detecta nada, bájalo (por ejemplo, a 0.7).
Legalidad: Este es un ejercicio educativo. Usar bots en juegos como Albion Online puede violar sus términos de servicio y resultar en una expulsión. Úsalo solo en un entorno controlado para practicar programación.
Requisitos: Debes tener el juego en pantalla completa o ventana sin bordes para que pyautogui capture correctamente.
Si tienes problemas o quieres ajustar algo (como tiempos o sensibilidad), ¡dímelo y te ayudo!"""