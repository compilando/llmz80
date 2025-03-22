#include <arch/zx.h>
#include <stdio.h>

void main(void)
{
    // Limpiar la pantalla con atributo (papel y tinta)
    zx_cls(PAPER_BLACK | INK_WHITE); // ✔️ Usa un parámetro

    // Imprimir mensajes
    printf("Hola ZX Spectrum!\n");
    printf("Este es un ejemplo de\n");
    printf("como imprimir texto.\n");

    while (1)
        ; // Mantener texto en pantalla
}