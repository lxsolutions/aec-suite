











# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

# Build the Next.js application
RUN yarn build

# Runtime stage
FROM node:20-alpine AS runtime

WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/package.json /app/yarn.lock /app/.next /app/public /app/src /app/tsconfig.json ./

EXPOSE 3000

CMD ["yarn", "start"]











