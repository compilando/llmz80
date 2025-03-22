CC=zcc
CFLAGS=+zx -vn -O3 -clib=sdcc_iy -I.
LDFLAGS=-create-app
SUBTYPE=--subtype=tap

TARGET=program
SOURCES=main.c
OBJECTS=$(SOURCES:.c=.o)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(OBJECTS) -o $@ $(LDFLAGS) $(SUBTYPE)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET) $(TARGET).tap
