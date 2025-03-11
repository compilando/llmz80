/*
   Ejemplo básico que muestra cómo cambiar el color del borde en Amstrad CPC
   usando CPCtelera.
*/

#include <cpctelera.h>

void main(void)
{
    // Desactivar el firmware para tener control total
    cpct_disableFirmware();

    // Establecer el modo de vídeo 1 (320x200, 4 colores)
    cpct_setVideoMode(1);

    // Cambiar el color del borde a rojo (color 3)
    cpct_setBorder(3);

    // Bucle infinito para mantener el programa en ejecución
    while (1)
    {
        // No hacemos nada más, solo mostramos el borde
    }
}