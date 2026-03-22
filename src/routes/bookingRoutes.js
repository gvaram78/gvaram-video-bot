const express = require('express');
const { createBooking, listBookings, updateBookingStatus } = require('../controllers/bookingController');
const { authRequired } = require('../middleware/auth');

const router = express.Router();

router.use(authRequired);
router.post('/', createBooking);
router.get('/', listBookings);
router.patch('/:id/status', updateBookingStatus);

module.exports = router;
