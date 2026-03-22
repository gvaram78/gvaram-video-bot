const ROLES = {
  CLIENT: 'client',
  PROVIDER: 'provider',
  ADMIN: 'admin',
};

const CITIES = ['Tbilisi', 'Rustavi', 'Batumi', 'Kutaisi'];
const LANGUAGES = ['ka', 'ru', 'en'];
const SERVICE_LOCATIONS = ['salon', 'home_visit', 'own_home'];
const BOOKING_STATUSES = ['pending', 'confirmed', 'completed', 'cancelled'];

module.exports = {
  ROLES,
  CITIES,
  LANGUAGES,
  SERVICE_LOCATIONS,
  BOOKING_STATUSES,
  FIXED_DEPOSIT_GEL: 10,
};
