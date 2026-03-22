const mongoose = require('mongoose');
const { BOOKING_STATUSES, FIXED_DEPOSIT_GEL } = require('../config/constants');

const bookedServiceSchema = new mongoose.Schema(
  {
    serviceId: { type: mongoose.Schema.Types.ObjectId, required: true },
    name: { type: String, required: true },
    durationMin: { type: Number, required: true },
    priceGel: { type: Number, required: true },
  },
  { _id: false }
);

const bookingSchema = new mongoose.Schema(
  {
    client: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    provider: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    providerProfile: { type: mongoose.Schema.Types.ObjectId, ref: 'ProviderProfile', required: true },
    services: { type: [bookedServiceSchema], validate: [(v) => v.length > 0, 'At least one service required'] },
    city: { type: String, required: true },
    serviceDate: { type: String, required: true },
    startTime: { type: String, required: true },
    endTime: { type: String, required: true },
    status: { type: String, enum: BOOKING_STATUSES, default: 'pending' },
    depositGel: { type: Number, default: FIXED_DEPOSIT_GEL },
    paymentStatus: { type: String, enum: ['pending', 'paid', 'failed', 'refunded'], default: 'pending' },
    paymentMethod: { type: String, default: 'mock' },
    notes: { type: String, trim: true },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Booking', bookingSchema);
