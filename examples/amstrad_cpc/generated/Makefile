CPCT_PATH := $(CPCT_PATH)
CPCT_SHARED_PATH := $(CPCT_PATH)/tools/img2tileset
SRC := src
OBJ := obj

TARGET := generated
OUT := $(TARGET).dsk

SRCS := $(wildcard $(SRC)/*.c)
OBJS := $(SRCS:$(SRC)/%.c=$(OBJ)/%.o)

CCFLAGS := -mz80 -I$(CPCT_PATH)/src
CCFLAGS += -O2 -Wall
LDFLAGS := -mz80 --no-std-crt0 --code-loc 0x0400
LDFLAGS += -Wl -b_CODE=0x0400
LDFLAGS += -l$(CPCT_PATH)/cpctelera.lib

.PHONY: all clean

all: $(OUT)

$(OUT): $(TARGET)
	$(CPCT_PATH)/tools/hex2bin/2cdt.exe -n $(TARGET) -r $(TARGET) $(TARGET).bin $(OUT)

$(TARGET): $(OBJS)
	sdcc $(LDFLAGS) -o $(TARGET).ihx $(OBJS)
	hex2bin -p 00 $(TARGET).ihx

$(OBJ)/%.o: $(SRC)/%.c
	$(CC) $(CCFLAGS) -c $< -o $@

clean:
	$(RM) $(TARGET) $(OUT) $(OBJS) $(TARGET).ihx $(TARGET).bin
