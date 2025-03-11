/*
   Ejemplo que muestra cómo leer el teclado en Amstrad CPC
   usando CPCtelera.
*/

#include <cpctelera.h>

// Definiciones de teclas (matriz de teclado del Amstrad CPC)
#define Key_Q (cpct_keyID_t)0x4402
#define Key_A (cpct_keyID_t)0x4108
#define Key_O (cpct_keyID_t)0x4102
#define Key_P (cpct_keyID_t)0x4101
#define Key_Space (cpct_keyID_t)0x8005

void main(void)
{
    u8 border_color = 0;

    // Desactivar el firmware para tener control total
    cpct_disableFirmware();

    // Establecer el modo de vídeo 1 (320x200, 4 colores)
    cpct_setVideoMode(1);

    // Cambiar el color del borde a negro (color 0)
    cpct_setBorder(border_color);

    // Limpiar la pantalla con color negro (0)
    cpct_memset((void *)0xC000, 0, 0x4000);

    // Definir colores para el texto (tinta y papel)
    cpct_setDrawCharM1(3, 0); // Tinta blanca (3) sobre fondo negro (0)

    // Imprimir instrucciones
    cpct_drawStringM1("CONTROLES:", (u8 *)0xC000);
    cpct_drawStringM1("Q - Cambiar borde a azul", (u8 *)0xC050);
    cpct_drawStringM1("A - Cambiar borde a rojo", (u8 *)0xC0A0);
    cpct_drawStringM1("O - Cambiar borde a verde", (u8 *)0xC0F0);
    cpct_drawStringM1("P - Cambiar borde a amarillo", (u8 *)0xC140);
    cpct_drawStringM1("ESPACIO - Cambiar borde a negro", (u8 *)0xC190);

    // Bucle principal
    while (1)
    {
        // Escanear el teclado
        cpct_scanKeyboard();

        // Comprobar teclas y cambiar el color del borde
        if (cpct_isKeyPressed(Key_Q))
        {
            border_color = 1; // Azul
        }
        else if (cpct_isKeyPressed(Key_A))
        {
            border_color = 3; // Rojo
        }
        else if (cpct_isKeyPressed(Key_O))
        {
            border_color = 2; // Verde
        }
        else if (cpct_isKeyPressed(Key_P))
        {
            border_color = 6; // Amarillo
        }
        else if (cpct_isKeyPressed(Key_Space))
        {
            border_color = 0; // Negro
        }

        // Actualizar el color del borde
        cpct_setBorder(border_color);

        // Pequeña pausa para evitar lecturas demasiado rápidas
        cpct_waitVSYNC();
    }
}