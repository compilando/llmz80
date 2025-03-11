/*
   Ejemplo que muestra cómo usar el sonido en Amstrad CPC
   usando CPCtelera.
*/

#include <cpctelera.h>

// Definiciones de teclas (matriz de teclado del Amstrad CPC)
#define Key_1 (cpct_keyID_t)0x8004
#define Key_2 (cpct_keyID_t)0x8008
#define Key_3 (cpct_keyID_t)0x8010
#define Key_4 (cpct_keyID_t)0x8020
#define Key_5 (cpct_keyID_t)0x8040

void main(void)
{
    // Desactivar el firmware para tener control total
    cpct_disableFirmware();

    // Establecer el modo de vídeo 1 (320x200, 4 colores)
    cpct_setVideoMode(1);

    // Cambiar el color del borde a negro (color 0)
    cpct_setBorder(0);

    // Limpiar la pantalla con color negro (0)
    cpct_memset((void *)0xC000, 0, 0x4000);

    // Definir colores para el texto (tinta y papel)
    cpct_setDrawCharM1(3, 0); // Tinta blanca (3) sobre fondo negro (0)

    // Imprimir instrucciones
    cpct_drawStringM1("SONIDOS EN AMSTRAD CPC", (u8 *)0xC000);
    cpct_drawStringM1("Pulsa teclas 1-5 para diferentes sonidos", (u8 *)0xC050);
    cpct_drawStringM1("1 - Nota baja", (u8 *)0xC0A0);
    cpct_drawStringM1("2 - Nota media", (u8 *)0xC0F0);
    cpct_drawStringM1("3 - Nota alta", (u8 *)0xC140);
    cpct_drawStringM1("4 - Efecto de explosión", (u8 *)0xC190);
    cpct_drawStringM1("5 - Efecto de salto", (u8 *)0xC1E0);

    // Bucle principal
    while (1)
    {
        // Escanear el teclado
        cpct_scanKeyboard();

        // Comprobar teclas y reproducir sonidos
        if (cpct_isKeyPressed(Key_1))
        {
            // Nota baja (canal A, tono bajo, volumen alto)
            cpct_akp_SFXPlay(1, 15, 0, 60, 0, 0);
            cpct_setBorder(1); // Cambiar borde a azul
        }
        else if (cpct_isKeyPressed(Key_2))
        {
            // Nota media (canal B, tono medio, volumen alto)
            cpct_akp_SFXPlay(2, 15, 1, 40, 0, 0);
            cpct_setBorder(2); // Cambiar borde a verde
        }
        else if (cpct_isKeyPressed(Key_3))
        {
            // Nota alta (canal C, tono alto, volumen alto)
            cpct_akp_SFXPlay(3, 15, 2, 20, 0, 0);
            cpct_setBorder(3); // Cambiar borde a rojo
        }
        else if (cpct_isKeyPressed(Key_4))
        {
            // Efecto de explosión (canal A, volumen decreciente)
            cpct_akp_SFXPlay(4, 15, 0, 10, 15, 50);
            cpct_setBorder(6); // Cambiar borde a amarillo
        }
        else if (cpct_isKeyPressed(Key_5))
        {
            // Efecto de salto (canal B, tono ascendente)
            cpct_akp_SFXPlay(5, 15, 1, 60, 20, 0);
            cpct_setBorder(5); // Cambiar borde a magenta
        }
        else
        {
            cpct_setBorder(0); // Restaurar borde a negro
        }

        // Pequeña pausa para evitar lecturas demasiado rápidas
        cpct_waitVSYNC();
    }
}