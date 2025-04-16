// Description: Changes the ZX Spectrum screen border color to red and keeps it that way indefinitely.
#include <arch/zx.h>

/*
 * Ejemplo 1: Cambiar el color del borde
 *
 * Este ejemplo muestra cómo cambiar el color del borde
 * de la pantalla del ZX Spectrum usando la función
 * zx_border().
 */

void main(void)
{
    // Cambiar el color del borde a rojo
    zx_border(INK_RED);

    while (1)
        ; // Bucle infinito para mantener el color
}