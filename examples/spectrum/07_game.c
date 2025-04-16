// Description: Implements a number guessing game on the ZX Spectrum where the player has five attempts to guess a randomly chosen number between 1 and 20, with input debouncing and feedback after each guess.
#include <arch/zx.h>
#include <input.h>
#include <stdlib.h>
#include <stdio.h>

// Función de "debounce": espera un breve periodo
void debounce_delay(void)
{
    for (volatile int i = 0; i < 5000; i++)
    {
        ; // Bucle vacío para retardar
    }
}

// Función para obtener un número aleatorio en un rango
uint8_t random_range(uint8_t min, uint8_t max)
{
    return min + (rand() % (max - min + 1));
}

// Función para leer un número entero del usuario con debounce
uint8_t read_number(void)
{
    uint8_t number = 0;
    char key;

    while (1)
    {
        // Espera activa hasta que se pulse alguna tecla
        while ((key = in_inkey()) == 0)
            ;

        // Aplicar debounce para estabilizar la lectura
        debounce_delay();

        // Si se pulsa ENTER (puede ser '\n' o CR (13)), finaliza la lectura
        if (key == '\n' || key == 13)
        {
            // Espera a que se suelte la tecla
            while (in_inkey() != 0)
                ;
            break;
        }

        // Si es un dígito, se procesa
        if (key >= '0' && key <= '9')
        {
            printf("%c", key);
            number = number * 10 + (key - '0');
            // Espera a que se suelte la tecla para evitar repeticiones
            while (in_inkey() != 0)
                ;
        }
    }

    return number;
}

int main(void)
{
    // En ZX Spectrum usamos una semilla fija, pues no hay reloj real
    srand(1);
    uint8_t secret = random_range(1, 20);
    uint8_t guess;
    uint8_t attempts = 5;

    zx_cls(PAPER_BLACK | INK_WHITE);

    printf("Adivina el numero (1-20)\n");
    printf("Tienes 5 intentos\n");

    do
    {
        printf("Ingresa tu intento: ");
        guess = read_number();
        attempts--;

        if (guess < secret)
        {
            printf("Mayor\n");
        }
        else if (guess > secret)
        {
            printf("Menor\n");
        }

        if (guess == secret)
        {
            printf("Felicidades! Has adivinado el numero\n");
            break;
        }
        else if (attempts > 0)
        {
            printf("Te quedan %d intentos\n", attempts);
        }
        else
        {
            printf("Lo siento, no has adivinado. El numero era %d\n", secret);
        }
    } while (attempts > 0);

    while (1)
        ; // Mantener texto en pantalla

    return 0;
}
