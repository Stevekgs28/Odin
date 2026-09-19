#include "Button.hpp"

Button::Button(int pin)
{
    this->pin = pin;
    pinMode(pin, INPUT_PULLUP);
}

bool Button::isPressed()
{
    return digitalRead(this->pin) == LOW;
}