const errorHandler = (err, req, res, next) => {
  if (err.name === 'ValidationError') {
    return res.status(400).json({ message: err.message });
  }
  if (err.code === 11000) {
    return res.status(409).json({ message: 'Duplicate record detected' });
  }
  return res.status(500).json({ message: err.message || 'Unexpected server error' });
};

module.exports = errorHandler;
