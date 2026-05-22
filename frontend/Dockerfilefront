
FROM node:20-alpine AS build

RUN apk update && apk upgrade --no-cache

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM nginx:1.29-alpine


RUN apk update && apk upgrade --no-cache && \
    apk del curl nghttp2-libs nghttp2

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]