FROM node:20-alpine

WORKDIR /app

# Khởi tạo một package.json tối giản nếu chưa có để Docker cài đặt
RUN echo '{"name": "lottery-frontend", "private": true, "version": "0.0.0", "type": "module", "scripts": {"dev": "vite --host"}, "dependencies": {"react": "^19.0.0", "react-dom": "^19.0.0"}, "devDependencies": {"vite": "^5.0.0"}}' > package.json

RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]