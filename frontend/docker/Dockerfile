# ============================================
# Multi-Stage Build for Frontend Application
# ============================================

# ============================================
# Stage 1: Builder - Compile Frontend Assets
# ============================================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
# Separate layer for better caching
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application source code
COPY . ./

# Build production-ready static assets
# Vite will output to dist/ directory
RUN npm run build

# ============================================
# Stage 2: Production - Nginx Server
# ============================================
FROM nginx:alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY ./docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy entrypoint script for htpasswd generation
COPY ./docker/entrypoint.sh /entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /entrypoint.sh

# Install apache2-utils for htpasswd command
RUN apk add --no-cache apache2-utils

# Create directory for htpasswd file
RUN mkdir -p /etc/nginx/auth
