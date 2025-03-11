/**
 * @file anivemin_example.c
 * @brief Ejemplo ultra minimalista para Amstrad CPC
 */

#include <cpctelera.h>

// Paleta de colores
const u8 g_palette[16] = {
    0, 3, 6, 9, 12, 15, 18, 21,
    24, 26, 28, 30, 31, 22, 14, 6};

// Estado del juego
u8 border_color = 1;

/**
 * @brief Función principal
 */
void main(void)
{
    // Desactivar firmware
    cpct_disableFirmware();

    // Establecer modo de vídeo (0 = 160x200, 16 colores)
    cpct_setVideoMode(0);

    // Establecer paleta de colores
    cpct_setPalette(g_palette, 16);

    // Limpiar la pantalla
    cpct_clearScreen(0);

    // Dibujar un borde
    cpct_drawSolidBox((void *)0xC000, border_color, 40, 200);
    cpct_drawSolidBox((void *)(0xC000 + 40 * 4 - 4), border_color, 4, 200);
    cpct_drawSolidBox((void *)0xC000, border_color, 40 * 4, 8);
    cpct_drawSolidBox((void *)(0xC000 + 80 * 24), border_color, 40 * 4, 8);

    // Bucle principal
    while (1)
    {
        // Escanear teclado
        cpct_scanKeyboard();

        // Cambiar color del borde al pulsar espacio
        if (cpct_isKeyPressed(Key_Space))
        {
            border_color = (border_color + 1) % 16;

            // Redibujar el borde con el nuevo color
            cpct_drawSolidBox((void *)0xC000, border_color, 40, 200);
            cpct_drawSolidBox((void *)(0xC000 + 40 * 4 - 4), border_color, 4, 200);
            cpct_drawSolidBox((void *)0xC000, border_color, 40 * 4, 8);
            cpct_drawSolidBox((void *)(0xC000 + 80 * 24), border_color, 40 * 4, 8);

            // Esperar a que se suelte la tecla
            while (cpct_isKeyPressed(Key_Space))
            {
                cpct_scanKeyboard();
                cpct_waitVSYNC();
            }
        }

        // Pequeña pausa para estabilizar el sistema
        cpct_waitVSYNC();
    }
}