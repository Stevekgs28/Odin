#ifndef WIFIMODULE_CPP
#define WIFIMODULE_CPP

#include <ESP8266WiFi.h>


class WifiModule
{
    private :
        char* ssid;
        char* password;
        bool isConnected;
    public:
        WifiModule(char* ssid, char* password);
        void start();
        

};


#endif
