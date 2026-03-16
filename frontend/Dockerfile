FROM node:20-alpine

WORKDIR /app

# Dependencies
COPY package.json ./
RUN npm install

# App code
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
