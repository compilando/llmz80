// Description: Displays and animates an 8x8 pixel sprite moving diagonally across the ZX Spectrum screen by plotting and unplotting pixels in a loop.
#include <arch/zx.h>
#include <stdint.h>
#include <stdio.h>

/*
 * Ejemplo 5: Sprites básicos
 *
 * Este ejemplo muestra cómo crear y mover un sprite simple
 * usando un array de bytes para definir su forma.
 */

// Definición del sprite (8x8 píxeles)
const uint8_t sprite[] = {
    0b00111100, // ..XXXX..
    0b01111110, // .XXXXXX.
    0b11111111, // XXXXXXXX
    0b11111111, // XXXXXXXX
    0b11111111, // XXXXXXXX
    0b01111110, // .XXXXXX.
    0b00111100, // ..XXXX..
    0b00011000  // ...XX...
};

/* Variable para almacenar la posición actual (opcional) */
uint8_t current_x = 0, current_y = 0;

/* Función draw: Actualiza la posición actual de dibujo */
void draw(uint8_t x, uint8_t y)
{
    current_x = x;
    current_y = y;
}

/*
 * Función plot: Dibuja un pixel en (x, y)
 * Se calcula el offset en memoria según la disposición típica del ZX Spectrum.
 */
void plot(uint8_t x, uint8_t y)
{
    uint16_t offset = ((y & 0xC0) << 5) | ((y & 0x07) << 8) | ((y & 0x38) << 2) | (x >> 3);
    uint8_t bit = 0x80 >> (x & 7);
    uint8_t *screen = (uint8_t *)0x4000;
    screen[offset] |= bit;
}

/*
 * Función unplot: Borra un pixel en (x, y)
 * Se limpia el bit correspondiente en la memoria de pantalla.
 */
void unplot(uint8_t x, uint8_t y)
{
    uint16_t offset = ((y & 0xC0) << 5) | ((y & 0x07) << 8) | ((y & 0x38) << 2) | (x >> 3);
    uint8_t bit = 0x80 >> (x & 7);
    uint8_t *screen = (uint8_t *)0x4000;
    screen[offset] &= ~bit;
}

void main(void)
{
    uint8_t x = 128; // Posición inicial X
    uint8_t y = 96;  // Posición inicial Y

    // Limpiar la pantalla usando zx_cls con un único parámetro combinado
    zx_cls(PAPER_BLACK | INK_WHITE);

    while (1)
    {
        // Borrar el sprite en la posición anterior
        draw(x, y);
        for (uint8_t i = 0; i < 8; i++)
        {
            for (uint8_t j = 0; j < 8; j++)
            {
                if (sprite[i] & (0x80 >> j))
                {
                    unplot(x + j, y + i);
                }
            }
        }

        // Mover el sprite en diagonal
        x = (x + 1) & 255; // Wrap-around en 256 para X
        y = (y + 1) % 192; // Wrap-around en la altura de pantalla (192 píxeles)

        // Dibujar el sprite en la nueva posición
        draw(x, y);
        for (uint8_t i = 0; i < 8; i++)
        {
            for (uint8_t j = 0; j < 8; j++)
            {
                if (sprite[i] & (0x80 >> j))
                {
                    plot(x + j, y + i);
                }
            }
        }

        // Pequeña pausa
        for (uint16_t i = 0; i < 500; i++)
            ; // Espera
    }
}
