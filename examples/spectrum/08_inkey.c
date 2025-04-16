// Description: Calculates and displays the product, larger, and smaller of two user-input numbers between 0 and 99 on a ZX Spectrum, with a flashing border effect until the space key is pressed to exit.
#include <arch/zx.h> // Funciones específicas del Spectrum
#include <stdio.h>
#include <stdint.h>
#include <input.h> // Para in_Inkey()
#include <im2.h>   // Para im2_pause()

// Función simple de retardo
void delay(uint16_t ms)
{
    uint16_t i;
    while (ms--)
        for (i = 0; i < 250; i++)
        {
        } // Aproximadamente 1ms en un Z80 a 3.5MHz
}

uint8_t read_number(void)
{
    uint8_t number = 0;
    uint8_t digits = 0;
    int key, last_key = 0;

    printf("(0-99, ENTER=ok, DEL=borrar): ");

    while (1)
    {
        key = in_inkey();

        // Solo procesa la tecla si es diferente a la anterior
        if (key != 0 && key != last_key)
        {
            if (key == 13) // ENTER
            {
                if (digits > 0) // Solo acepta si hay al menos un dígito
                    break;
            }
            else if (key == 12) // DELETE (tecla BREAK en Spectrum)
            {
                if (digits > 0)
                {
                    number /= 10;
                    digits--;
                    printf("\b \b"); // Borra último carácter
                }
            }
            else if (key >= '0' && key <= '9' && digits < 2) // Máximo 2 dígitos
            {
                uint8_t new_number = number * 10 + (key - '0');
                if (new_number <= 99) // Asegura que no pase de 99
                {
                    putchar(key);
                    number = new_number;
                    digits++;
                }
            }
        }

        last_key = key;
        delay(50); // Aumentamos el delay para mejor debounce
    }

    return number;
}

int main()
{
    uint8_t num1, num2;

    zx_cls(PAPER_BLACK | INK_WHITE);

    printf("Primer numero ");
    num1 = read_number();

    printf("\nSegundo numero ");
    num2 = read_number();

    printf("\n\nResultados:");
    printf("\nProducto: %u", (uint16_t)num1 * num2);
    printf("\nMayor: %u", (num1 > num2) ? num1 : num2);
    printf("\nMenor: %u", (num1 < num2) ? num1 : num2);

    printf("\n\nPulsa BREAK para salir");

    while (!in_key_pressed(IN_KEY_SCANCODE_SPACE))
    {
        zx_border(INK_RED);
        delay(200);
        zx_border(INK_BLACK);
        delay(200);
    }
}