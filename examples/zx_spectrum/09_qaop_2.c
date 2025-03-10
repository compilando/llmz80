#include <arch/zx.h>
#include <input.h>
#include <stdio.h>

// Implementación de plot() para dibujar un pixel en la pantalla del ZX Spectrum.
void plot(uint8_t x, uint8_t y)
{
    uint16_t offset = ((y & 0xC0) << 5) | ((y & 0x07) << 8) | ((y & 0x38) << 2) | (x >> 3);
    uint8_t bit = 0x80 >> (x & 7);
    uint8_t *screen = (uint8_t *)0x4000;
    screen[offset] |= bit;
}

void unplot(uint8_t x, uint8_t y)
{
    uint16_t offset = ((y & 0xC0) << 5) | ((y & 0x07) << 8) | ((y & 0x38) << 2) | (x >> 3);
    uint8_t bit = 0x80 >> (x & 7);
    uint8_t *screen = (uint8_t *)0x4000;
    screen[offset] &= ~bit;
}

void main(void)
{
    uint8_t x = 128; // Posición inicial X del pixel
    uint8_t y = 96;  // Posición inicial Y del pixel

    // Limpiar la pantalla usando un único parámetro combinado
    zx_cls(PAPER_BLACK | INK_WHITE);

    printf("Usa QAOP para mover el pixel");

    while (1)
    {
        // Borrar el pixel en su posición actual
        unplot(x, y);

        // Leer teclas para mover el pixel
        if (in_key_pressed(IN_KEY_SCANCODE_q) && y > 0)
            y--; // Q - Arriba
        if (in_key_pressed(IN_KEY_SCANCODE_a) && y < 191)
            y++; // A - Abajo
        if (in_key_pressed(IN_KEY_SCANCODE_o) && x > 0)
            x--; // O - Izquierda
        if (in_key_pressed(IN_KEY_SCANCODE_p) && x < 255)
            x++; // P - Derecha

        // Dibujar el pixel en la nueva posición
        plot(x, y);

        // Pequeña pausa
        for (uint16_t i = 0; i < 1000; i++)
            ; // Espera
    }
}