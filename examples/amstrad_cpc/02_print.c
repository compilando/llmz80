/*
   Ejemplo que muestra cómo imprimir texto en la pantalla del Amstrad CPC
   usando CPCtelera.
*/

#include <cpctelera.h>

void main(void)
{
    // Desactivar el firmware para tener control total
    cpct_disableFirmware();

    // Establecer el modo de vídeo 1 (320x200, 4 colores)
    cpct_setVideoMode(1);

    // Cambiar el color del borde a azul (color 1)
    cpct_setBorder(1);

    // Definir colores para el texto (tinta y papel)
    cpct_setDrawCharM1(3, 0); // Tinta blanca (3) sobre fondo negro (0)

    // Imprimir texto en diferentes posiciones
    cpct_drawStringM1("Hola Mundo en Amstrad CPC!", (u8 *)0xC000);
    cpct_drawStringM1("Usando CPCtelera", (u8 *)0xC050);
    cpct_drawStringM1("Generado con LLM", (u8 *)0xC0A0);

    // Bucle infinito para mantener el programa en ejecución
    while (1)
    {
        // No hacemos nada más, solo mostramos el texto
    }
}