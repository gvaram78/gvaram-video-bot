const mongoose = require('mongoose');

const connectDB = async () => {
  const mongoUri = process.env.MONGODB_URI;
  if (!mongoUri) {
    throw new Error('MONGODB_URI is required in environment');
  }

  await mongoose.connect(mongoUri);
  // eslint-disable-next-line no-console
  console.log('MongoDB connected');
};

module.exports = connectDB;
