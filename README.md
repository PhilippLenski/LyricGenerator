# LyricGenerator
 
## 1 Installieren
Der Einsatz von Docker ist vorgesehen:
```
cd PATH_TO_FOLDER/LyricGenerator
docker-compose build
docker-compose up -d
```

Da die einzelnen Modelle zu groß für GitHub sind, müssen diese manuell runtergeladen und in Docker bereitgestellt werden.
Hierfür verfügt das Backend über ein Volumen "/app/models/", worauf während der Laufzeit zugegriffen werden kann.

Ordner mit Modellen können komplett importiert werden:
```
docker cp PATH_TO_MODELFOLDER/. lyricgenerator-backend-1:/app/models/
```

Die verfügbaren Modelle werden im Backend in der mode.py definiert:
```
MODEL_STACK = [
    ModelInfo("Gemma3 - 7B", "models/gemma-7b.safetensors"),
    ModelInfo("Gemma3 - 7B - Q5", "/app/models/gemma3-7b-Q5/gemma-7b.Q5_K_M.gguf"),
    ModelInfo("Mistral 7B Q5", "/app/models/Mistral-7b/Mistral-7B-Instruct-v0.3.Q5_K_M.gguf")
    ]
```

Entsprechend der in Docker geladenen Modelle bitte anpassen.

## 2 Ausführen
Die Oberfläche ist unter dem Port 8000 erreichbar
http://localhost:8000/

![image](https://github.com/user-attachments/assets/0384d00e-6f84-449a-8cc4-cc2dea5bf5fa)
