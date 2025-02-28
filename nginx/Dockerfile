FROM nginx:1.27.4-alpine-slim

RUN rm /etc/nginx/conf.d/default.conf
COPY selftest-cert.crt /etc/nginx/ssl/selftest-cert.crt
COPY selftest-cert.key /etc/nginx/ssl/selftest-cert.key
COPY nginx.conf /etc/nginx/conf.d