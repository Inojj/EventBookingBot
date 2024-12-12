# Используем базовый образ Node.js
FROM node:16

# Устанавливаем рабочую директорию в контейнере
WORKDIR /frontend

# Копируем package.json и package-lock.json
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальные файлы проекта
COPY . .

# Запускаем сборку приложения
RUN npm run build

# Устанавливаем базовый сервер для статики
RUN npm install -g serve

# Открываем порт для работы приложения
EXPOSE 3000

# Команда запуска React-приложения
CMD ["serve", "-s", "build", "-l", "3000"]
