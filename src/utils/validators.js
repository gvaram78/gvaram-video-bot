const { CITIES } = require('../config/constants');

const isValidCity = (city) => CITIES.includes(city);

const hhmmToMinutes = (timeText) => {
  const [hh, mm] = timeText.split(':').map(Number);
  return hh * 60 + mm;
};

module.exports = {
  isValidCity,
  hhmmToMinutes,
};
