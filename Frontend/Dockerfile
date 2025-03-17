# Basis-Image für Node.js
FROM node:18
WORKDIR /app

COPY package.json ./

RUN npm install --include=dev
RUN npm install tailwindcss @tailwindcss/vite

COPY . .

RUN [ ! -f tailwind.config.js ] && npx tailwindcss init -p || echo "Tailwind bereits initialisiert"

RUN  npm run build

EXPOSE 3000
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]