const express = require('express');
const {
  reviewProvider,
  getAdminDashboard,
  listUsers,
  updateUserStatus,
  listBookingsAdmin,
  createBanner,
  listBanners,
  deleteBanner,
} = require('../controllers/adminController');
const { authRequired, authorizeRoles } = require('../middleware/auth');
const { ROLES } = require('../config/constants');

const router = express.Router();

router.use(authRequired, authorizeRoles(ROLES.ADMIN));

router.get('/dashboard', getAdminDashboard);
router.patch('/providers/:id/review', reviewProvider);
router.get('/users', listUsers);
router.patch('/users/:id/status', updateUserStatus);
router.get('/bookings', listBookingsAdmin);
router.post('/banners', createBanner);
router.get('/banners', listBanners);
router.delete('/banners/:id', deleteBanner);

module.exports = router;
