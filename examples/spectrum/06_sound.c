// Description: Generates a simple melody on the ZX Spectrum by playing a sequence of musical notes with specified frequencies and durations using the beeper.
#include <arch/zx.h>
#include <sound.h>
#include <stdint.h>

/*
 * Ejemplo 6: Sonido básico
 *
 * Este ejemplo muestra cómo generar sonidos usando
 * el beeper del ZX Spectrum. Reproduce una pequeña
 * melodía usando diferentes frecuencias.
 */

// Notas musicales (frecuencias aproximadas)
#define NOTE_C4 262
#define NOTE_D4 294
#define NOTE_E4 330
#define NOTE_F4 349
#define NOTE_G4 392

void play_note(int freq, int duration)
{
    bit_beep(duration * 50, freq); // Multiplicamos la duración para hacerla más notable
}

void main(void)
{
    // Limpiar la pantalla usando zx_cls con un único parámetro combinado
    zx_cls(PAPER_BLACK | INK_WHITE);

    // Se elimina la llamada a zx_colour, ya que no está definida o acepta parámetros
    // zx_colour(PAPER_BLACK | INK_WHITE);

    while (1)
    {
        // Reproducir una secuencia simple
        play_note(NOTE_C4, 3);
        play_note(NOTE_E4, 3);
        play_note(NOTE_G4, 3);
        play_note(NOTE_F4, 2);
        play_note(NOTE_D4, 5);

        // Pausa entre repeticiones
        for (uint16_t i = 0; i < 30000; i++)
            ; // Espera
    }
}
