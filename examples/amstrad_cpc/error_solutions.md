# Soluciones a Errores Comunes en el Desarrollo para Amstrad CPC

Este documento contiene soluciones a los errores más comunes que pueden surgir al desarrollar para Amstrad CPC usando CPCtelera y SDCC.

## Errores de Sintaxis

### Error: `syntax error: token -> 'u8'`

**Problema**: El compilador no reconoce el tipo de dato `u8`.

**Solución**: 
- Asegúrate de incluir `<cpctelera.h>` al principio de tu archivo.
- Este header define los tipos `u8`, `u16`, `u32`, etc.

```c
#include <cpctelera.h>

// Ahora puedes usar u8, u16, etc.
u8 myVariable = 42;
```

### Error: `syntax error: token -> '0x0400'`

**Problema**: SDCC puede tener problemas con algunas constantes hexadecimales, especialmente cuando se usan en expresiones complejas.

**Solución**:
- Usa paréntesis alrededor de las expresiones con constantes hexadecimales.
- Define constantes con nombres significativos.

```c
// Mal
cpct_drawSolidBox(0xC000 + 0x0400, 1, 40, 40);

// Bien - Usando paréntesis
cpct_drawSolidBox((void*)(0xC000 + 0x0400), 1, 40, 40);

// Mejor - Usando constantes definidas
#define SCREEN_START 0xC000
#define OFFSET_LINE_50 0x0400
cpct_drawSolidBox((void*)(SCREEN_START + OFFSET_LINE_50), 1, 40, 40);
```

### Error: `syntax error: token -> 'Node'` o `syntax error: token -> 'char'`

**Problema**: El compilador no reconoce un tipo de dato personalizado o hay un error en la declaración de estructuras.

**Solución**:
- Asegúrate de definir las estructuras antes de usarlas.
- En SDCC para Z80, las declaraciones de estructuras deben seguir un formato específico.
- Usa `typedef` para simplificar el uso de estructuras.

```c
// Definición correcta de una estructura
typedef struct {
    u8 x;
    u8 y;
    u8 color;
} Sprite;

// Ahora puedes usar el tipo Sprite
Sprite player;
player.x = 10;
```

## Errores de Variables

### Error: `Undefined identifier 'palette'`

**Problema**: Estás usando una variable que no ha sido definida.

**Solución**:
- Define todas las variables antes de usarlas.
- Para paletas, usa arrays de tamaño fijo.

```c
// Definición correcta de paleta
const u8 g_palette[16] = {0, 3, 6, 9, 12, 15, 18, 21, 24, 26, 28, 30, 31, 22, 14, 6};

// Ahora puedes usar g_palette
cpct_setPalette(g_palette, 16);
```

### Error: `Undefined identifier 'response'` o `Undefined identifier 'root'`

**Problema**: Estás usando variables que no han sido definidas en el ámbito actual.

**Solución**:
- Declara todas las variables antes de usarlas.
- Verifica el ámbito (scope) de las variables.
- Asegúrate de que los nombres de variables sean consistentes (mayúsculas/minúsculas).

```c
// Declaración correcta de variables
char response[20];
Node* root = NULL;

// Ahora puedes usar estas variables
strcpy(response, "OK");
if (root == NULL) {
    // ...
}
```

### Error: `Undefined identifier 'animal'`, `Undefined identifier 'vegetal'`, `Undefined identifier 'mineral'`

**Problema**: Estás usando variables que no han sido definidas en el ámbito actual.

**Solución**:
- Declara todas las variables antes de usarlas.
- Si son punteros a estructuras, asegúrate de que las estructuras estén definidas.
- Inicializa los punteros antes de usarlos.

```c
// Definición de la estructura
typedef struct Node {
    u8 value;
    struct Node* next;
} Node;

// Declaración correcta de variables
Node* animal = NULL;
Node* vegetal = NULL;
Node* mineral = NULL;

// Inicialización usando un pool de nodos
animal = &nodes_pool[0];
vegetal = &nodes_pool[1];
mineral = &nodes_pool[2];
```

## Errores de Tipos

### Error: `converting integral to pointer without a cast`

**Problema**: Estás intentando usar un número como si fuera un puntero sin hacer un casting explícito.

**Solución**:
- Usa casting explícito cuando conviertas entre tipos, especialmente con punteros.

```c
// Mal
cpct_drawSolidBox(0xC000, 1, 40, 40);

// Bien
cpct_drawSolidBox((void*)0xC000, 1, 40, 40);
// o
cpct_drawSolidBox((u8*)0xC000, 1, 40, 40);
```

### Error: `incompatible types`

**Problema**: Estás intentando asignar un valor de un tipo a una variable de otro tipo incompatible.

**Solución**:
- Asegúrate de que los tipos coincidan en asignaciones y parámetros de funciones.
- Usa casting cuando sea necesario.

```c
// Mal
u8* ptr = 0xC000;

// Bien
u8* ptr = (u8*)0xC000;
```

### Error: `incompatible types from type 'void' to type 'signed-char generic* fixed'`

**Problema**: Estás intentando asignar un valor de tipo `void` a un puntero a `char`.

**Solución**:
- Usa casting explícito para convertir entre tipos de punteros.
- Asegúrate de que la asignación tenga sentido semánticamente.

```c
// Mal
char* text = malloc(10);  // No hay malloc en Z80/CPCtelera

// Bien - Usando un array estático
char text_buffer[10];
char* text = text_buffer;

// O si necesitas asignar desde un puntero void
void* generic_ptr = (void*)0xC000;
char* text = (char*)generic_ptr;
```

### Error: `indirections to different types assignment`

**Problema**: Estás intentando asignar un puntero de un tipo a un puntero de otro tipo incompatible.

**Solución**:
- Asegúrate de que los tipos de punteros sean compatibles.
- Usa casting explícito cuando sea necesario.
- Verifica que estás usando el tipo correcto para las estructuras.

```c
// Mal
void* generic_ptr = malloc(10);
MyStruct* specific_ptr = generic_ptr;

// Bien
void* generic_ptr = malloc(10);
MyStruct* specific_ptr = (MyStruct*)generic_ptr;
```

### Error: `Pointer required`

**Problema**: Estás intentando acceder a un miembro de una estructura usando una variable que no es un puntero.

**Solución**:
- Asegúrate de que la variable sea un puntero válido antes de usar el operador `->`.
- Inicializa los punteros antes de usarlos.

```c
// Mal
Node root;
root->value = 10; // Error: Pointer required

// Bien
Node* root = &nodes_pool[0];
root->value = 10; // Correcto

// Alternativa usando notación de punto para variables no puntero
Node root;
root.value = 10; // Correcto
```

## Errores de Arrays

### Error: `array size missing`

**Problema**: No has especificado el tamaño de un array.

**Solución**:
- Declara los arrays con tamaño fijo.

```c
// Mal
u8 my_array[];

// Bien
u8 my_array[10];
```

## Errores de Funciones

### Error: `function 'malloc' implicit declaration`

**Problema**: Estás usando una función que no ha sido declarada.

**Solución**:
- En CPCtelera/SDCC para Z80, **no hay malloc ni memoria dinámica**.
- Usa arrays estáticos en su lugar.
- Si necesitas estructuras de datos dinámicas, implementa tu propio gestor de memoria.

```c
// Mal - No hay malloc en Z80/CPCtelera
Node* new_node = malloc(sizeof(Node));

// Bien - Usa arrays estáticos
#define MAX_NODES 10
Node nodes_pool[MAX_NODES];
u8 next_free_node = 0;

// Función para "asignar" un nodo
Node* allocate_node() {
    if (next_free_node < MAX_NODES) {
        return &nodes_pool[next_free_node++];
    }
    return NULL; // No hay más nodos disponibles
}
```

### Error: `too many parameters`

**Problema**: Estás llamando a una función con más parámetros de los que acepta.

**Solución**:
- Verifica la firma correcta de la función.
- Consulta la documentación de CPCtelera para conocer los parámetros correctos.

```c
// Ejemplo correcto para cpct_drawSprite
cpct_drawSprite(sprite_data, (void*)0xC000, sprite_width, sprite_height);
```

## Estructuras de Datos Enlazadas

### Implementación de Listas Enlazadas

**Problema**: Intentar implementar listas enlazadas usando `malloc` y punteros como en C estándar.

**Solución**:
- Usa un array estático de nodos (pool) y un índice para el siguiente nodo libre.
- Implementa funciones para "asignar" y "liberar" nodos del pool.

```c
// Definición de la estructura Node
typedef struct Node {
    u8 value;
    struct Node* next;
} Node;

// Pool de nodos
#define MAX_NODES 20
Node nodes_pool[MAX_NODES];
u8 next_free_node = 0;

// Inicializar el pool
void init_nodes_pool() {
    next_free_node = 0;
    for (u8 i = 0; i < MAX_NODES; i++) {
        nodes_pool[i].value = 0;
        nodes_pool[i].next = NULL;
    }
}

// "Asignar" un nodo
Node* allocate_node() {
    if (next_free_node < MAX_NODES) {
        return &nodes_pool[next_free_node++];
    }
    return NULL;
}

// Ejemplo de uso para crear una lista enlazada
void create_linked_list() {
    // Inicializar el pool
    init_nodes_pool();
    
    // Crear el nodo raíz
    Node* root = allocate_node();
    if (root != NULL) {
        root->value = 10;
        
        // Añadir más nodos
        Node* current = root;
        for (u8 i = 1; i < 5; i++) {
            Node* new_node = allocate_node();
            if (new_node != NULL) {
                new_node->value = i * 10;
                current->next = new_node;
                current = new_node;
            }
        }
    }
}
```

### Implementación de Árboles

**Problema**: Intentar implementar árboles binarios u otras estructuras jerárquicas.

**Solución**:
- Usa el mismo enfoque de pool que para las listas enlazadas.
- Define la estructura con punteros a los nodos hijos.

```c
// Definición de un nodo de árbol binario
typedef struct TreeNode {
    u8 value;
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

// Pool de nodos de árbol
#define MAX_TREE_NODES 15
TreeNode tree_nodes_pool[MAX_TREE_NODES];
u8 next_free_tree_node = 0;

// Inicializar el pool
void init_tree_pool() {
    next_free_tree_node = 0;
    for (u8 i = 0; i < MAX_TREE_NODES; i++) {
        tree_nodes_pool[i].value = 0;
        tree_nodes_pool[i].left = NULL;
        tree_nodes_pool[i].right = NULL;
    }
}

// "Asignar" un nodo de árbol
TreeNode* allocate_tree_node() {
    if (next_free_tree_node < MAX_TREE_NODES) {
        return &tree_nodes_pool[next_free_tree_node++];
    }
    return NULL;
}

// Ejemplo de uso para crear un árbol binario simple
void create_binary_tree() {
    // Inicializar el pool
    init_tree_pool();
    
    // Crear el nodo raíz
    TreeNode* root = allocate_tree_node();
    if (root != NULL) {
        root->value = 50;
        
        // Crear nodos hijos
        TreeNode* left = allocate_tree_node();
        if (left != NULL) {
            left->value = 25;
            root->left = left;
        }
        
        TreeNode* right = allocate_tree_node();
        if (right != NULL) {
            right->value = 75;
            root->right = right;
        }
    }
}
```

## Ejemplo de Juego Anivemin (Adivinanza de Animal, Vegetal o Mineral)

**Problema**: Implementar un juego de adivinanzas con árboles de decisión.

**Solución**:
- Usa un árbol binario con un pool de nodos.
- Define claramente la estructura del nodo con los campos necesarios.
- Inicializa todas las variables antes de usarlas.

```c
#include <cpctelera.h>
#include <string.h>

// Definición de la estructura del nodo para el árbol de decisión
typedef struct Node {
    char question[40];           // Pregunta o respuesta
    struct Node* yes;            // Puntero al nodo si la respuesta es "sí"
    struct Node* no;             // Puntero al nodo si la respuesta es "no"
    u8 is_answer;                // 1 si es una respuesta final, 0 si es una pregunta
} Node;

// Pool de nodos para simular memoria dinámica
#define MAX_NODES 30
Node nodes_pool[MAX_NODES];
u8 next_free_node = 0;

// Variables globales para las categorías
Node* animal = NULL;
Node* vegetal = NULL;
Node* mineral = NULL;
Node* current_node = NULL;

// Inicializar el pool de nodos
void init_nodes_pool() {
    next_free_node = 0;
    for (u8 i = 0; i < MAX_NODES; i++) {
        nodes_pool[i].question[0] = '\0';
        nodes_pool[i].yes = NULL;
        nodes_pool[i].no = NULL;
        nodes_pool[i].is_answer = 0;
    }
}

// "Asignar" un nodo del pool
Node* allocate_node() {
    if (next_free_node < MAX_NODES) {
        return &nodes_pool[next_free_node++];
    }
    return NULL;
}

// Inicializar el árbol de decisión
void init_decision_tree() {
    // Inicializar el pool
    init_nodes_pool();
    
    // Crear nodos para las categorías principales
    animal = allocate_node();
    vegetal = allocate_node();
    mineral = allocate_node();
    
    // Configurar nodos de categorías
    if (animal) {
        strcpy(animal->question, "Es un perro?");
        animal->is_answer = 1;
    }
    
    if (vegetal) {
        strcpy(vegetal->question, "Es un arbol?");
        vegetal->is_answer = 1;
    }
    
    if (mineral) {
        strcpy(mineral->question, "Es una piedra?");
        mineral->is_answer = 1;
    }
    
    // Conectar los nodos
    if (animal && vegetal) {
        animal->no = vegetal;
    }
}

void main(void) {
    // Variables locales
    char response[20];
    
    // Desactivar firmware
    cpct_disableFirmware();
    
    // Establecer modo de vídeo
    cpct_setVideoMode(1);
    
    // Inicializar el árbol de decisión
    init_decision_tree();
    
    // Establecer el nodo actual
    current_node = animal;
    
    // Bucle principal
    while(1) {
        // Escanear teclado
        cpct_scanKeyboard();
        
        // Comprobar si se pulsa la tecla ESC
        if (cpct_isKeyPressed(Key_Esc)) {
            break;
        }
    }
}
```

## Ejemplo Completo Correcto

```c
#include <cpctelera.h>

// Definición correcta de constantes
#define SCREEN_START 0xC000
#define OFFSET_LINE_50 0x0400

// Definición correcta de paleta
const u8 g_palette[16] = {0, 3, 6, 9, 12, 15, 18, 21, 24, 26, 28, 30, 31, 22, 14, 6};

// Definición correcta de una estructura
typedef struct {
    u8 x;
    u8 y;
    u8 color;
} Sprite;

// Pool de sprites para simular memoria dinámica
#define MAX_SPRITES 10
Sprite sprites_pool[MAX_SPRITES];
u8 next_free_sprite = 0;

// Función para "asignar" un sprite
Sprite* allocate_sprite() {
    if (next_free_sprite < MAX_SPRITES) {
        return &sprites_pool[next_free_sprite++];
    }
    return NULL; // No hay más sprites disponibles
}

void main(void) {
    // Desactivar firmware
    cpct_disableFirmware();
    
    // Establecer modo de vídeo (1 = 320x200, 4 colores)
    cpct_setVideoMode(1);
    
    // Establecer paleta de colores
    cpct_setPalette(g_palette, 16);
    
    // Crear un sprite usando nuestro pool
    Sprite* player = allocate_sprite();
    if (player != NULL) {
        player->x = 40;
        player->y = 100;
        player->color = 1;
    }
    
    // Dibujar un rectángulo sólido (con casting correcto)
    cpct_drawSolidBox((void*)SCREEN_START, 1, 40, 40);
    
    // Bucle principal
    while(1) {
        // Escanear teclado
        cpct_scanKeyboard();
        
        // Comprobar si se pulsa la tecla ESC
        if (cpct_isKeyPressed(Key_Esc)) {
            break;
        }
    }
}
```

## Recursos Adicionales

- [Documentación oficial de CPCtelera](https://lronaldo.github.io/cpctelera/)
- [Wiki de CPCtelera](https://github.com/lronaldo/cpctelera/wiki)
- [Foro de CPCtelera](https://github.com/lronaldo/cpctelera/discussions) 