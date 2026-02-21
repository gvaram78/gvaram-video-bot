const express = require('express');
const {
  upsertProfile,
  addService,
  uploadPhotos,
  uploadVerificationDocs,
  listProviders,
  getProviderById,
  listProviderUsers,
} = require('../controllers/providerController');
const { authRequired, authorizeRoles } = require('../middleware/auth');
const { ROLES } = require('../config/constants');
const { photoUpload, idDocUpload } = require('../middleware/upload');

const router = express.Router();

router.get('/', listProviders);
router.get('/users/providers', authRequired, authorizeRoles(ROLES.ADMIN), listProviderUsers);
router.get('/:id', getProviderById);

router.post('/me/profile', authRequired, authorizeRoles(ROLES.PROVIDER), upsertProfile);
router.post('/me/services', authRequired, authorizeRoles(ROLES.PROVIDER), addService);
router.post('/me/photos', authRequired, authorizeRoles(ROLES.PROVIDER), photoUpload.array('photos', 6), uploadPhotos);
router.post('/me/verification-docs', authRequired, authorizeRoles(ROLES.PROVIDER), idDocUpload.array('docs', 4), uploadVerificationDocs);

module.exports = router;
