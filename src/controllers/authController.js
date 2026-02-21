const User = require('../models/User');
const { ROLES } = require('../config/constants');
const { signToken } = require('../utils/jwt');

const register = async (req, res) => {
  const { name, email, password, phone, role, city, preferredLanguage } = req.body;

  const allowedRoles = [ROLES.CLIENT, ROLES.PROVIDER];
  const normalizedRole = allowedRoles.includes(role) ? role : ROLES.CLIENT;

  const existing = await User.findOne({ email });
  if (existing) return res.status(409).json({ message: 'Email already in use' });

  const user = await User.create({ name, email, password, phone, role: normalizedRole, city, preferredLanguage });
  const token = signToken(user);

  return res.status(201).json({ token, user: { id: user._id, name: user.name, role: user.role, email: user.email } });
};

const login = async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email }).select('+password');
  if (!user) return res.status(401).json({ message: 'Invalid credentials' });

  const valid = await user.comparePassword(password);
  if (!valid) return res.status(401).json({ message: 'Invalid credentials' });

  const token = signToken(user);
  return res.json({ token, user: { id: user._id, name: user.name, role: user.role, email: user.email } });
};

const me = async (req, res) => res.json({ user: req.user });

module.exports = { register, login, me };
