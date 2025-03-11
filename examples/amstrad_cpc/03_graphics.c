/*
   Ejemplo que muestra cómo dibujar gráficos básicos en Amstrad CPC
   usando CPCtelera.
*/

#include <cpctelera.h>

void main(void)
{
    u8 i;

    // Desactivar el firmware para tener control total
    cpct_disableFirmware();

    // Establecer el modo de vídeo 0 (160x200, 16 colores)
    cpct_setVideoMode(0);

    // Cambiar el color del borde a negro (color 0)
    cpct_setBorder(0);

    // Limpiar la pantalla con color negro (0)
    cpct_memset((void *)0xC000, 0, 0x4000);

    // Dibujar un rectángulo rojo (color 3) en el centro de la pantalla
    cpct_drawSolidBox((void *)(0xC000 + 40 * 80 + 35), 3, 30, 40);

    // Dibujar un rectángulo azul (color 1) en la esquina superior izquierda
    cpct_drawSolidBox((void *)(0xC000), 1, 20, 30);

    // Dibujar un rectángulo verde (color 2) en la esquina inferior derecha
    cpct_drawSolidBox((void *)(0xC000 + 170 * 80 + 60), 2, 20, 30);

    // Dibujar líneas de diferentes colores
    for (i = 0; i < 16; i++)
    {
        // Dibujar línea horizontal con diferentes colores
        cpct_drawSolidBox((void *)(0xC000 + (100 + i) * 80), i, 80, 1);

        // Dibujar línea vertical con diferentes colores
        cpct_drawSolidBox((void *)(0xC000 + i * 80 + 40), 15 - i, 1, 80);
    }

    // Bucle infinito para mantener el programa en ejecución
    while (1)
    {
        // No hacemos nada más, solo mostramos los gráficos
    }
}