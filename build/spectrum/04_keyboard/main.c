// Description: Allows a user to move a cursor around the ZX Spectrum screen using the QAOP keys, drawing a pixel at the cursor's position.
#include <arch/zx.h>
#include <input.h>
#include <stdio.h>
#include <stdint.h>

/*
 * Ejemplo 4: Entrada de teclado
 *
 * Este ejemplo muestra cómo leer la entrada del teclado
 * y responder a las teclas presionadas.
 *
 * Se incluye una implementación básica de plot() para dibujar un pixel.
 */

// Implementación de plot() para dibujar un pixel en la pantalla del ZX Spectrum.
void plot(uint8_t x, uint8_t y)
{
    uint16_t offset = ((y & 0xC0) << 5) | ((y & 0x07) << 8) | ((y & 0x38) << 2) | (x >> 3);
    uint8_t bit = 0x80 >> (x & 7);
    uint8_t *screen = (uint8_t *)0x4000;
    screen[offset] |= bit;
}

void main(void)
{
    uint8_t x = 128; // Posición X del cursor
    uint8_t y = 96;  // Posición Y del cursor

    // Limpiar la pantalla usando un único parámetro combinado
    zx_cls(PAPER_BLACK | INK_WHITE);

    printf("Use las teclas QAOP para mover\n");
    printf("el cursor por la pantalla\n");

    while (1)
    {
        // Leer teclas
        if (in_key_pressed(IN_KEY_SCANCODE_q))
            y--; // Q - Arriba
        if (in_key_pressed(IN_KEY_SCANCODE_a))
            y++; // A - Abajo
        if (in_key_pressed(IN_KEY_SCANCODE_o))
            x--; // O - Izquierda
        if (in_key_pressed(IN_KEY_SCANCODE_p))
            x++; // P - Derecha

        // Dibujar cursor
        plot(x, y);

        // Pequeña pausa
        for (uint16_t i = 0; i < 1000; i++)
            ; // Espera
    }
}
