#include "WifiModule.hpp"

WifiModule::WifiModule(char* ssid, char* password)
{
    this->ssid = ssid;
    this->password = password;
    this->isConnected = false;
}

void WifiModule::start()
{
    int tryNumber = 1;
    WiFi.begin(this->ssid, this->password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
        if (++tryNumber > 20)
        {
            Serial.println();
            Serial.println("Pas de connexion, abandon");
            return;
        }
    }

    Serial.println();
    Serial.print("Connecté ! Adresse IP : ");
    Serial.println(WiFi.localIP());
    this->isConnected = true;
}