CXX = g++
CXXFLAGS = -shared -fPIC -O2 -Wall
TARGET = libgamelogic.so
SRC = game_logic.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)

test: $(TARGET)
	python3 test_cpp_logic.py

.PHONY: all clean test
