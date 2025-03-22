# Makefile template for Amstrad CPC examples
# This file should be copied to each example directory and modified as needed

# Project name
PROJECT_NAME = generated

# Source files
SRCS = src/main.c

# Object files
OBJS = $(SRCS:.c=.o)

# Compiler and flags
CC = sdcc
CFLAGS = -mz80 --opt-code-size -I$(CPCT_PATH)/include
LDFLAGS = -mz80 --no-std-crt0 -Wl-z80 -D__AMSTRAD_CAP32__

# CPCtelera tools
CPCT_BIN = $(CPCT_PATH)/bin
CPCT_2CDT = $(CPCT_BIN)/2cdt
CPCT_BIN2DSK = $(CPCT_BIN)/bin2dsk

# Default target
all: $(PROJECT_NAME).dsk

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Link object files
$(PROJECT_NAME).ihx: $(OBJS)
	$(CC) $(LDFLAGS) $(OBJS) -o $@

# Convert to binary
$(PROJECT_NAME).bin: $(PROJECT_NAME).ihx
	$(CPCT_BIN)/ihx2bin $< $@

# Create DSK file
$(PROJECT_NAME).dsk: $(PROJECT_NAME).bin
	$(CPCT_BIN2DSK) $@ $<

# Clean
clean:
	rm -f $(OBJS) $(PROJECT_NAME).ihx $(PROJECT_NAME).bin $(PROJECT_NAME).dsk

.PHONY: all clean 