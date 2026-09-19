#include "Dock.hpp"


Dock::Dock(int nbButtons)
{
    this->nbButtons = nbButtons;
    this->buttons = malloc(nbButtons*sizeof(Button));
    if(this->buttons == NULL)
    {
        Serial.println("Erreur malloc dans Dock()");
    }
}

void Dock::handle()
{
    while(true)
    {
        for(Button b : this->buttons)
        {
            
        }
    }
}