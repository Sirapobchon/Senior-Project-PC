#define F_CPU 8000000UL  // 8MHz
#include <avr/io.h>
#include <util/delay.h>

void task(void) {
    DDRB |= (1 << PB0);      // Set PB0 as output
    while (1) {
        PORTB ^= (1 << PB0); // Toggle PB0
        _delay_ms(500);
    }
}

