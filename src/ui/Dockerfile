# ---------- build stage ----------
FROM node:18-alpine AS build

WORKDIR /app

COPY src/ui/package*.json ./
#-jc NOTE: npm ci fails because package-lock.json is out of sync with package.json.
#-jc Proper fix: regenerate and commit a consistent lockfile.
#-jc TEMPORARY: using npm install to allow build to proceed for PoC/demo purposes.
#-jc RUN npm ci
RUN npm install

COPY src/ui/ ./
#-jc Angular 12 / webpack incompatibility with Node ≥17 causes ERR_OSSL_EVP_UNSUPPORTED.
#-jc Proper fix: upgrade Angular toolchain or pin Node to 16.
#-jc TEMPORARY workaround: enable legacy OpenSSL provider for PoC build stability.
ENV NODE_OPTIONS=--openssl-legacy-provider
RUN npm run build

# ---------- runtime stage ----------
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# SPA routing support
COPY src/ui/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

