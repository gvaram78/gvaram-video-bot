const mongoose = require('mongoose');
const { CITIES, SERVICE_LOCATIONS } = require('../config/constants');

const serviceSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true },
    category: { type: String, required: true, trim: true },
    durationMin: { type: Number, required: true, min: 10 },
    priceGel: { type: Number, required: true, min: 1 },
    isActive: { type: Boolean, default: true },
  },
  { _id: true }
);

const availabilitySchema = new mongoose.Schema(
  {
    dayOfWeek: { type: Number, min: 0, max: 6, required: true },
    startTime: { type: String, required: true },
    endTime: { type: String, required: true },
    isAvailable: { type: Boolean, default: true },
  },
  { _id: false }
);

const providerProfileSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, unique: true },
    bio: { type: String, trim: true },
    city: { type: String, enum: CITIES, required: true },
    serviceLocations: [{ type: String, enum: SERVICE_LOCATIONS, required: true }],
    photos: {
      type: [String],
      validate: {
        validator(value) {
          return value.length <= 6;
        },
        message: 'Provider can upload up to 6 photos only.',
      },
      default: [],
    },
    services: { type: [serviceSchema], default: [] },
    availability: { type: [availabilitySchema], default: [] },
    ratingAverage: { type: Number, default: 0, min: 0, max: 5 },
    ratingCount: { type: Number, default: 0, min: 0 },
    verificationDocs: { type: [String], default: [] },
    verificationStatus: { type: String, enum: ['pending', 'approved', 'rejected'], default: 'pending' },
    verificationComment: { type: String, trim: true },
    approvedByAdmin: { type: Boolean, default: false },
  },
  { timestamps: true }
);

module.exports = mongoose.model('ProviderProfile', providerProfileSchema);
