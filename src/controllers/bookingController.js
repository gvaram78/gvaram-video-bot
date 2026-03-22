const Booking = require('../models/Booking');
const ProviderProfile = require('../models/ProviderProfile');
const { ROLES, FIXED_DEPOSIT_GEL } = require('../config/constants');
const { hhmmToMinutes } = require('../utils/validators');

const createBooking = async (req, res) => {
  if (req.user.role !== ROLES.CLIENT) return res.status(403).json({ message: 'Only clients can book services' });

  const { providerProfileId, serviceIds, serviceDate, startTime, notes } = req.body;
  const profile = await ProviderProfile.findById(providerProfileId).populate('user', '_id');
  if (!profile || !profile.approvedByAdmin) {
    return res.status(404).json({ message: 'Provider unavailable for booking' });
  }

  const selectedServices = profile.services.filter((service) => serviceIds.includes(service._id.toString()));
  if (!selectedServices.length) return res.status(400).json({ message: 'No valid services selected' });

  const totalDuration = selectedServices.reduce((sum, item) => sum + item.durationMin, 0);
  const endMinutes = hhmmToMinutes(startTime) + totalDuration;
  const endTime = `${String(Math.floor(endMinutes / 60)).padStart(2, '0')}:${String(endMinutes % 60).padStart(2, '0')}`;

  const booking = await Booking.create({
    client: req.user._id,
    provider: profile.user._id,
    providerProfile: profile._id,
    services: selectedServices.map((service) => ({
      serviceId: service._id,
      name: service.name,
      durationMin: service.durationMin,
      priceGel: service.priceGel,
    })),
    city: profile.city,
    serviceDate,
    startTime,
    endTime,
    depositGel: FIXED_DEPOSIT_GEL,
    paymentStatus: 'paid',
    notes,
  });

  return res.status(201).json(booking);
};

const listBookings = async (req, res) => {
  let filter = {};
  if (req.user.role === ROLES.CLIENT) filter.client = req.user._id;
  if (req.user.role === ROLES.PROVIDER) filter.provider = req.user._id;

  const bookings = await Booking.find(filter)
    .populate('client', 'name email')
    .populate('provider', 'name email')
    .populate('providerProfile', 'city');

  return res.json(bookings);
};

const updateBookingStatus = async (req, res) => {
  const { status } = req.body;
  const booking = await Booking.findById(req.params.id);
  if (!booking) return res.status(404).json({ message: 'Booking not found' });

  const isProviderOwner = req.user.role === ROLES.PROVIDER && booking.provider.toString() === req.user._id.toString();
  const isAdmin = req.user.role === ROLES.ADMIN;
  if (!isProviderOwner && !isAdmin) return res.status(403).json({ message: 'Forbidden' });

  booking.status = status;
  await booking.save();
  return res.json(booking);
};

module.exports = { createBooking, listBookings, updateBookingStatus };
