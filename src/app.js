const path = require('path');
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const routes = require('./routes');
const errorHandler = require('./middleware/errorHandler');

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev'));

app.use('/uploads', express.static(path.join(process.cwd(), 'src/uploads')));
app.use(express.static(path.join(process.cwd(), 'src/public')));

app.use('/api', routes);

app.use(errorHandler);

module.exports = app;
