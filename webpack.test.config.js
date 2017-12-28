const config = require('./webpack.config.js');


/*
  View tests that use templates require a valid webpack-stats.json file, so instead
  of running a full build we just run a minimum build that generates this file.
*/
config.module.rules = [
  {
    test: /\.js$/,
    loader: 'null-loader',
  },
];

module.exports = config;
