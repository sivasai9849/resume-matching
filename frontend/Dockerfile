FROM node:18-alpine

WORKDIR /app

# Install Python and other dependencies
RUN apk add --no-cache python3 make g++ gcc

COPY package.json .

# Install dependencies
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD npm start
