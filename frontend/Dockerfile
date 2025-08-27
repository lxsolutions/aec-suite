






# Use official Node.js image
FROM node:20-alpine

WORKDIR /app

# Copy package.json and yarn.lock first for cache efficiency
COPY package.json ./

# Install dependencies
RUN npm install --production=false

# Copy the rest of the application code
COPY . .

# Build the React app
RUN npm run build

# Use a lightweight base image for production
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Install only production dependencies
COPY package.json ./
RUN npm install --only=production

# Copy built assets from previous stage
COPY --from=builder /app/dist ./dist

# Expose the port and start the server
EXPOSE 3000
CMD ["npm", "start"]



