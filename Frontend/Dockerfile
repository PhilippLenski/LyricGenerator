# Basis-Image für Node.js
FROM node:18

# Setze Arbeitsverzeichnis
WORKDIR /app

# Kopiere die package.json und package-lock.json (falls vorhanden)
COPY package.json package-lock.json ./

# Installiere Abhängigkeiten
RUN npm install

# Kopiere alle Dateien in den Container
COPY . .

# Baue die React-App
RUN npm run build

# Exponiere Port 3000 und starte die App
EXPOSE 3000
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]