import axios from "axios";

// Устанавливаем базовый URL для всех запросов (замените на ваш URL)
axios.defaults.baseURL = process.env.REACT_APP_API_URL;

// Добавление токена авторизации в каждый запрос
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Обработка ошибок
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Удаляем токен и перенаправляем на страницу входа
      localStorage.removeItem("authToken");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default axios;
