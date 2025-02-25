# Define the builder stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM node:18-alpine AS production

WORKDIR /app

COPY --from=builder /app ./

RUN npm ci --only=production

EXPOSE 3000

CMD ["npm", "start"]
