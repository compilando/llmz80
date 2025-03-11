/*
   Ejemplo que muestra cómo usar sprites en Amstrad CPC
   usando CPCtelera.
*/

#include <cpctelera.h>

// Definición de un sprite de 8x8 píxeles (modo 0, 16 colores)
// Cada byte representa 2 píxeles (4 bits por píxel en modo 0)
const u8 g_sprite[8 * 4] = {
    0x30, 0x30, 0x30, 0x30, // ··██····██····██····██··
    0x30, 0xF0, 0xF0, 0x30, // ··██··████████··██··
    0x33, 0xFF, 0xFF, 0x33, // ██████████████████
    0x3F, 0xFF, 0xFF, 0xF3, // ██████████████████
    0x3F, 0xFF, 0xFF, 0xF3, // ██████████████████
    0x33, 0xFF, 0xFF, 0x33, // ██████████████████
    0x30, 0xF3, 0x3F, 0x30, // ··██████····██████··
    0x30, 0x33, 0x33, 0x30  // ··████████████··
};

// Definiciones de teclas (matriz de teclado del Amstrad CPC)
#define Key_Q (cpct_keyID_t)0x4402 // Arriba
#define Key_A (cpct_keyID_t)0x4108 // Abajo
#define Key_O (cpct_keyID_t)0x4102 // Izquierda
#define Key_P (cpct_keyID_t)0x4101 // Derecha

void main(void)
{
    // Posición inicial del sprite
    u8 x = 40;
    u8 y = 100;
    u8 old_x, old_y;

    // Desactivar el firmware para tener control total
    cpct_disableFirmware();

    // Establecer el modo de vídeo 0 (160x200, 16 colores)
    cpct_setVideoMode(0);

    // Cambiar el color del borde a negro (color 0)
    cpct_setBorder(0);

    // Limpiar la pantalla con color negro (0)
    cpct_memset((void *)0xC000, 0, 0x4000);

    // Bucle principal
    while (1)
    {
        // Guardar posición anterior
        old_x = x;
        old_y = y;

        // Escanear el teclado
        cpct_scanKeyboard();

        // Mover el sprite según las teclas presionadas
        if (cpct_isKeyPressed(Key_Q) && y > 0)
        {
            y--; // Mover arriba
        }
        if (cpct_isKeyPressed(Key_A) && y < 192)
        {
            y++; // Mover abajo
        }
        if (cpct_isKeyPressed(Key_O) && x > 0)
        {
            x--; // Mover izquierda
        }
        if (cpct_isKeyPressed(Key_P) && x < 152)
        {
            x++; // Mover derecha
        }

        // Si la posición ha cambiado
        if (x != old_x || y != old_y)
        {
            // Borrar el sprite en la posición anterior
            cpct_drawSolidBox((void *)(0xC000 + old_y * 80 + old_x / 2), 0, 4, 8);

            // Dibujar el sprite en la nueva posición
            cpct_drawSprite(g_sprite, (void *)(0xC000 + y * 80 + x / 2), 4, 8);
        }

        // Pequeña pausa para controlar la velocidad
        cpct_waitVSYNC();
    }
}