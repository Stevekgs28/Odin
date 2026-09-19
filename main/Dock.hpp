#ifndef DOCK_HPP
#define DOCK_HPP

#include "Button.hpp"


class Dock
{
    private :
        int nbButtons;
        Button* buttons;
    
    public :
        Dock(int nbButtons);
        void handle();
};


#endif