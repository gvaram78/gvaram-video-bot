const express = require('express');
const authRoutes = require('./authRoutes');
const providerRoutes = require('./providerRoutes');
const bookingRoutes = require('./bookingRoutes');
const adminRoutes = require('./adminRoutes');

const router = express.Router();

router.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'STYLIO API' });
});

router.use('/auth', authRoutes);
router.use('/providers', providerRoutes);
router.use('/bookings', bookingRoutes);
router.use('/admin', adminRoutes);

module.exports = router;
