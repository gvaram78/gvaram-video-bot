const path = require('path');
const multer = require('multer');

const createStorage = (folder) =>
  multer.diskStorage({
    destination: (req, file, cb) => cb(null, path.join(process.cwd(), 'src/uploads', folder)),
    filename: (req, file, cb) => cb(null, `${Date.now()}-${file.originalname.replace(/\s+/g, '-')}`),
  });

const imageOnly = (req, file, cb) => {
  if (file.mimetype.startsWith('image/')) {
    cb(null, true);
  } else {
    cb(new Error('Only image files are allowed'));
  }
};

const photoUpload = multer({ storage: createStorage('provider-photos'), fileFilter: imageOnly });
const idDocUpload = multer({ storage: createStorage('id-documents') });

module.exports = { photoUpload, idDocUpload };
