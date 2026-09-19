#ifndef BUTTON_HPP
#define BUTTON_HPP


class Button
{
    private :
        int pin;
    
    public :
        Button(int pin);
        bool isPressed();
};

#endif