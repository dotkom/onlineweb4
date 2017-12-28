const config = require('./webpack.config.js');
const BundleTracker = require('webpack-bundle-tracker');
const CommonsChunkPlugin = require('webpack/lib/optimize/CommonsChunkPlugin');


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

config.plugins = [
  // Needed because otherwise the common entry is not created
  new CommonsChunkPlugin({ names: ['common'] }),
  new BundleTracker({ filename: './webpack-stats-test.json' }),
]

module.exports = config;
