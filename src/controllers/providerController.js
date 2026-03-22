const ProviderProfile = require('../models/ProviderProfile');
const User = require('../models/User');
const { ROLES } = require('../config/constants');

const upsertProfile = async (req, res) => {
  if (req.user.role !== ROLES.PROVIDER) {
    return res.status(403).json({ message: 'Only providers can create profile' });
  }

  const payload = {
    user: req.user._id,
    bio: req.body.bio,
    city: req.body.city,
    serviceLocations: req.body.serviceLocations || [],
    availability: req.body.availability || [],
  };

  const profile = await ProviderProfile.findOneAndUpdate({ user: req.user._id }, payload, {
    new: true,
    upsert: true,
    runValidators: true,
    setDefaultsOnInsert: true,
  });

  return res.json(profile);
};

const addService = async (req, res) => {
  const profile = await ProviderProfile.findOne({ user: req.user._id });
  if (!profile) return res.status(404).json({ message: 'Provider profile not found' });

  profile.services.push(req.body);
  await profile.save();
  return res.status(201).json(profile.services);
};

const uploadPhotos = async (req, res) => {
  const profile = await ProviderProfile.findOne({ user: req.user._id });
  if (!profile) return res.status(404).json({ message: 'Provider profile not found' });

  const paths = (req.files || []).map((f) => `/uploads/provider-photos/${f.filename}`);
  profile.photos = [...profile.photos, ...paths].slice(0, 6);
  await profile.save();

  return res.json({ photos: profile.photos });
};

const uploadVerificationDocs = async (req, res) => {
  const profile = await ProviderProfile.findOne({ user: req.user._id });
  if (!profile) return res.status(404).json({ message: 'Provider profile not found' });

  const docPaths = (req.files || []).map((f) => `/uploads/id-documents/${f.filename}`);
  if (!docPaths.length) return res.status(400).json({ message: 'Please upload at least one document' });

  profile.verificationDocs = [...profile.verificationDocs, ...docPaths];
  profile.verificationStatus = 'pending';
  profile.verificationComment = 'Awaiting admin review';
  await profile.save();

  return res.json({ verificationStatus: profile.verificationStatus, verificationDocs: profile.verificationDocs });
};

const listProviders = async (req, res) => {
  const { city, serviceType } = req.query;
  const filter = { approvedByAdmin: true };
  if (city) filter.city = city;

  const providers = await ProviderProfile.find(filter)
    .populate('user', 'name email city')
    .lean();

  const filtered = serviceType
    ? providers.filter((p) => p.services.some((s) => s.category.toLowerCase() === serviceType.toLowerCase()))
    : providers;

  return res.json(filtered);
};

const getProviderById = async (req, res) => {
  const provider = await ProviderProfile.findById(req.params.id).populate('user', 'name email city');
  if (!provider) return res.status(404).json({ message: 'Provider profile not found' });
  return res.json(provider);
};

const listProviderUsers = async (req, res) => {
  const providers = await User.find({ role: ROLES.PROVIDER }).select('name email city createdAt');
  return res.json(providers);
};

module.exports = {
  upsertProfile,
  addService,
  uploadPhotos,
  uploadVerificationDocs,
  listProviders,
  getProviderById,
  listProviderUsers,
};
