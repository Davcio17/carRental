import axios from 'axios';

const API_CATALOG = 'http://localhost:8000';
const API_RENTAL = 'http://localhost:8001';

export const catalogApi = axios.create({ baseURL: API_CATALOG });
export const bookingApi = axios.create({ baseURL: API_RENTAL });