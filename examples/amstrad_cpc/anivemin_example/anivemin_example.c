/**
 * @file anivemin_example.c
 * @brief Ejemplo de juego de adivinanzas Animal, Vegetal o Mineral para Amstrad CPC
 *
 * Este ejemplo muestra cómo implementar un juego de adivinanzas con árboles de decisión
 * sin usar malloc, utilizando un pool de nodos preasignados.
 */

#include <cpctelera.h>
#include <string.h>

// Definición de la estructura del nodo para el árbol de decisión
typedef struct Node
{
    char question[40]; // Pregunta o respuesta
    struct Node *yes;  // Puntero al nodo si la respuesta es "sí"
    struct Node *no;   // Puntero al nodo si la respuesta es "no"
    u8 is_answer;      // 1 si es una respuesta final, 0 si es una pregunta
    u8 category;       // 0=animal, 1=vegetal, 2=mineral
} Node;

// Pool de nodos para simular memoria dinámica
#define MAX_NODES 30
Node nodes_pool[MAX_NODES];
u8 next_free_node = 0;

// Paleta de colores
const u8 g_palette[16] = {
    0, 3, 6, 9, 12, 15, 18, 21,
    24, 26, 28, 30, 31, 22, 14, 6};

// Variables globales para las categorías
Node *animal = NULL;
Node *vegetal = NULL;
Node *mineral = NULL;
Node *current_node = NULL;
Node *root = NULL; // Nodo raíz

// Estado del juego
u8 waiting_for_answer = 0;
u8 game_over = 0;
char user_input[40];
u8 input_pos = 0;

/**
 * @brief Inicializa el pool de nodos
 */
void init_nodes_pool()
{
    next_free_node = 0;
    for (u8 i = 0; i < MAX_NODES; i++)
    {
        nodes_pool[i].question[0] = '\0';
        nodes_pool[i].yes = NULL;
        nodes_pool[i].no = NULL;
        nodes_pool[i].is_answer = 0;
        nodes_pool[i].category = 0;
    }
}

/**
 * @brief "Asigna" un nodo del pool
 * @return Puntero al nodo asignado o NULL si no hay nodos disponibles
 */
Node *allocate_node()
{
    if (next_free_node < MAX_NODES)
    {
        return &nodes_pool[next_free_node++];
    }
    return NULL; // No hay más nodos disponibles
}

/**
 * @brief Inicializa el árbol de decisión
 */
void init_decision_tree()
{
    // Inicializar el pool
    init_nodes_pool();

    // Crear nodos para las categorías principales
    root = allocate_node();
    animal = allocate_node();
    vegetal = allocate_node();
    mineral = allocate_node();

    // Configurar nodo raíz
    if (root)
    {
        strcpy(root->question, "Es un ser vivo?");
        root->is_answer = 0;
        root->yes = animal;
        root->no = mineral;
    }

    // Configurar nodos de categorías
    if (animal)
    {
        strcpy(animal->question, "Se mueve por si mismo?");
        animal->is_answer = 0;
        animal->yes = allocate_node();
        animal->no = vegetal;
        animal->category = 0;

        if (animal->yes)
        {
            strcpy(animal->yes->question, "Es un perro");
            animal->yes->is_answer = 1;
            animal->yes->category = 0;
        }
    }

    if (vegetal)
    {
        strcpy(vegetal->question, "Es un arbol?");
        vegetal->is_answer = 0;
        vegetal->yes = allocate_node();
        vegetal->category = 1;

        if (vegetal->yes)
        {
            strcpy(vegetal->yes->question, "Es un roble");
            vegetal->yes->is_answer = 1;
            vegetal->yes->category = 1;
        }
    }

    if (mineral)
    {
        strcpy(mineral->question, "Es duro?");
        mineral->is_answer = 0;
        mineral->yes = allocate_node();
        mineral->category = 2;

        if (mineral->yes)
        {
            strcpy(mineral->yes->question, "Es una piedra");
            mineral->yes->is_answer = 1;
            mineral->yes->category = 2;
        }
    }

    // Establecer el nodo actual
    current_node = root;
}

/**
 * @brief Dibuja texto en la pantalla
 * @param text Texto a dibujar
 * @param x Posición X
 * @param y Posición Y
 * @param color Color del texto
 */
void draw_text(const char *text, u8 x, u8 y, u8 color)
{
    // Calcular la dirección de memoria
    u8 *screen_pos = (u8 *)(0xC000 + y * 80 + x);

    // Dibujar cada carácter
    while (*text)
    {
        // Dibujar un carácter simple (un rectángulo)
        cpct_drawSolidBox(screen_pos, color, 8, 8);

        // Avanzar a la siguiente posición
        screen_pos += 1;
        text++;
    }
}

/**
 * @brief Dibuja la interfaz del juego
 */
void draw_interface()
{
    // Limpiar la pantalla
    cpct_memset((void *)0xC000, 0, 0x4000);

    // Dibujar título
    draw_text("ANIVEMIN - ANIMAL, VEGETAL O MINERAL", 10, 10, 3);

    // Dibujar pregunta actual
    if (current_node)
    {
        draw_text(current_node->question, 10, 30, 1);

        if (!current_node->is_answer)
        {
            draw_text("Si (S) / No (N)", 10, 40, 2);
        }
        else
        {
            draw_text("He adivinado! Jugar de nuevo (J)", 10, 40, 2);
            game_over = 1;
        }
    }

    // Dibujar entrada del usuario si estamos esperando
    if (waiting_for_answer)
    {
        draw_text("Nueva pregunta:", 10, 60, 1);
        draw_text(user_input, 10, 70, 2);
    }
}

/**
 * @brief Procesa la entrada del usuario
 */
void process_input()
{
    Node *new_node; // Declarar new_node al inicio de la función

    // Si el juego ha terminado, solo aceptamos 'J' para jugar de nuevo
    if (game_over)
    {
        if (cpct_isKeyPressed(Key_J))
        {
            init_decision_tree();
            game_over = 0;
            draw_interface();
        }
        return;
    }

    // Si estamos esperando una respuesta de texto
    if (waiting_for_answer)
    {
        // Procesar teclas para entrada de texto
        // (Simplificado para este ejemplo)
        if (cpct_isKeyPressed(Key_Return))
        {
            // Finalizar entrada
            user_input[input_pos] = '\0';

            // Crear un nuevo nodo con la respuesta
            new_node = allocate_node();
            if (new_node)
            {
                strcpy(new_node->question, user_input);
                new_node->is_answer = 1;
                new_node->category = current_node->category;

                // Conectar el nuevo nodo
                if (current_node->yes == NULL)
                {
                    current_node->yes = new_node;
                }
                else if (current_node->no == NULL)
                {
                    current_node->no = new_node;
                }
            }

            // Reiniciar estado
            waiting_for_answer = 0;
            input_pos = 0;
            user_input[0] = '\0';

            // Volver al inicio
            init_decision_tree();
            draw_interface();
        }
        else
        {
            // Simplificado: solo añadimos 'X' para simular entrada de texto
            if (cpct_isKeyPressed(Key_X) && input_pos < 39)
            {
                user_input[input_pos++] = 'X';
                user_input[input_pos] = '\0';
                draw_interface();
            }
        }
        return;
    }

    // Procesar respuestas Sí/No
    if (!current_node->is_answer)
    {
        if (cpct_isKeyPressed(Key_S))
        {
            // Respuesta Sí
            if (current_node->yes)
            {
                current_node = current_node->yes;
            }
            else
            {
                // Pedir nueva respuesta
                waiting_for_answer = 1;
            }
            draw_interface();
        }
        else if (cpct_isKeyPressed(Key_N))
        {
            // Respuesta No
            if (current_node->no)
            {
                current_node = current_node->no;
            }
            else
            {
                // Pedir nueva respuesta
                waiting_for_answer = 1;
            }
            draw_interface();
        }
    }
}

/**
 * @brief Función principal
 */
void main(void)
{
    // Desactivar firmware
    cpct_disableFirmware();

    // Establecer modo de vídeo (1 = 320x200, 4 colores)
    cpct_setVideoMode(1);

    // Establecer paleta de colores
    cpct_setPalette(g_palette, 16);

    // Inicializar árbol de decisión
    init_decision_tree();

    // Dibujar interfaz inicial
    draw_interface();

    // Bucle principal
    while (1)
    {
        // Escanear teclado
        cpct_scanKeyboard();

        // Procesar entrada
        process_input();

        // Pequeña pausa para evitar múltiples pulsaciones
        for (u16 i = 0; i < 1000; i++)
            ;
    }
}