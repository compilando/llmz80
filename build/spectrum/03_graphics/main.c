#include <arch/zx.h>
#include <stdio.h>
#include <stdint.h>

/*
 * Ejemplo 3: Gráficos básicos para ZX Spectrum con z88dk
 *
 * Este ejemplo muestra cómo dibujar gráficos básicos en la pantalla del ZX Spectrum.
 * Se implementan funciones básicas de dibujo:
 *   - plot: Dibuja un pixel en (x, y)
 *   - zx_line: Dibuja una línea entre dos puntos usando el algoritmo de Bresenham
 *
 * Nota: La pantalla del ZX Spectrum comienza en la dirección 0x4000 y su disposición es no lineal.
 */

// Implementación de plot: Dibuja un pixel en (x, y)
void plot(uint8_t x, uint8_t y)
{
    // Cálculo del offset de memoria según la disposición del ZX Spectrum
    uint16_t offset = ((y & 0xC0) << 5) | ((y & 0x07) << 8) | ((y & 0x38) << 2) | (x >> 3);
    uint8_t bit = 0x80 >> (x & 7);
    uint8_t *screen = (uint8_t *)0x4000;
    screen[offset] |= bit;
}

// Implementación de zx_line: Dibuja una línea desde (x0, y0) hasta (x1, y1)
// utilizando el algoritmo de Bresenham
void zx_line(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1)
{
    int dx = (int)x1 - (int)x0;
    int dy = (int)y1 - (int)y0;
    int abs_dx = dx < 0 ? -dx : dx;
    int abs_dy = dy < 0 ? -dy : dy;
    int sx = dx < 0 ? -1 : 1;
    int sy = dy < 0 ? -1 : 1;
    int err = (abs_dx > abs_dy ? abs_dx : -abs_dy) / 2;
    int e2;

    while (1)
    {
        plot(x0, y0);
        if (x0 == x1 && y0 == y1)
            break;
        e2 = err;
        if (e2 > -abs_dx)
        {
            err -= abs_dy;
            x0 += sx;
        }
        if (e2 < abs_dy)
        {
            err += abs_dx;
            y0 += sy;
        }
    }
}

/* Variables globales para almacenar la posición actual de dibujo */
uint8_t current_x = 0;
uint8_t current_y = 0;

/* Función draw: Mueve el "cursor" de dibujo a la posición (x, y) */
void draw(uint8_t x, uint8_t y)
{
    current_x = x;
    current_y = y;
}

/* Función drawr: Dibuja una línea desde la posición actual hasta (current_x+dx, current_y+dy)
   y actualiza la posición actual. Se recibe un parámetro "color" que no se utiliza, pues zx_line no lo requiere. */
void drawr(int8_t dx, int8_t dy, uint8_t color)
{
    (void)color; // No se utiliza el parámetro color
    uint8_t x1 = current_x + dx;
    uint8_t y1 = current_y + dy;
    zx_line(current_x, current_y, x1, y1);
    current_x = x1;
    current_y = y1;
}

void main(void)
{
    // Limpiar la pantalla y establecer colores (zx_cls recibe un parámetro combinando PAPER e INK)
    zx_cls(PAPER_BLACK | INK_WHITE);

    // Dibujar un rectángulo
    draw(10, 10);     // Mover a la posición inicial
    drawr(40, 0, 1);  // Línea horizontal superior
    drawr(0, 20, 1);  // Línea vertical derecha
    drawr(-40, 0, 1); // Línea horizontal inferior
    drawr(0, -20, 1); // Línea vertical izquierda

    // Dibujar una línea diagonal
    draw(0, 0);
    drawr(100, 75, 1); // Línea diagonal

    // Dibujar un punto en la posición central
    plot(128, 96);

    // Mostrar un mensaje en pantalla
    printf("Graficos ZX Spectrum");

    while (1)
        ; // Bucle infinito para mantener los gráficos en pantalla
}
