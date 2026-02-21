const ProviderProfile = require('../models/ProviderProfile');
const Booking = require('../models/Booking');
const User = require('../models/User');
const Banner = require('../models/Banner');

const reviewProvider = async (req, res) => {
  const { decision, comment } = req.body;
  const profile = await ProviderProfile.findById(req.params.id);
  if (!profile) return res.status(404).json({ message: 'Provider profile not found' });

  profile.verificationStatus = decision;
  profile.approvedByAdmin = decision === 'approved';
  profile.verificationComment = comment || '';
  await profile.save();

  return res.json(profile);
};

const getAdminDashboard = async (req, res) => {
  const [usersCount, providersPending, bookingsCount, bannersCount] = await Promise.all([
    User.countDocuments(),
    ProviderProfile.countDocuments({ verificationStatus: 'pending' }),
    Booking.countDocuments(),
    Banner.countDocuments(),
  ]);

  return res.json({ usersCount, providersPending, bookingsCount, bannersCount });
};

const listUsers = async (req, res) => {
  const users = await User.find().select('name email role city isActive createdAt');
  return res.json(users);
};

const updateUserStatus = async (req, res) => {
  const user = await User.findByIdAndUpdate(req.params.id, { isActive: req.body.isActive }, { new: true });
  if (!user) return res.status(404).json({ message: 'User not found' });
  return res.json(user);
};

const listBookingsAdmin = async (req, res) => {
  const bookings = await Booking.find().populate('client provider', 'name email').sort({ createdAt: -1 });
  return res.json(bookings);
};

const createBanner = async (req, res) => {
  const banner = await Banner.create(req.body);
  return res.status(201).json(banner);
};

const listBanners = async (req, res) => {
  const banners = await Banner.find().sort({ createdAt: -1 });
  return res.json(banners);
};

const deleteBanner = async (req, res) => {
  await Banner.findByIdAndDelete(req.params.id);
  return res.status(204).send();
};

module.exports = {
  reviewProvider,
  getAdminDashboard,
  listUsers,
  updateUserStatus,
  listBookingsAdmin,
  createBanner,
  listBanners,
  deleteBanner,
};
