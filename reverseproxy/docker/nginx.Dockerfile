FROM nginx:1.21.1-alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy our complete nginx.conf to replace the main configuration
COPY /config/nginx.conf /etc/nginx/nginx.conf
