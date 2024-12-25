# Compiler and flags
CC = gcc
CFLAGS = -Wall -g
LDFLAGS = -lreadline

# Source files
SRC = socket.c rl.c
OBJ = $(SRC:.c=.o)

# Target executable
TARGET = player

# Rules
all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)
