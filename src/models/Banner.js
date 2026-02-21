const mongoose = require('mongoose');

const bannerSchema = new mongoose.Schema(
  {
    title: { type: String, required: true, trim: true },
    imageUrl: { type: String, required: true, trim: true },
    targetUrl: { type: String, trim: true },
    isActive: { type: Boolean, default: true },
    startDate: { type: Date },
    endDate: { type: Date },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Banner', bannerSchema);
