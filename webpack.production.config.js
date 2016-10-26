var config = require('./webpack.config.js');
var webpack = require('webpack');

config.devtool = 'cheap-module-source-map';

// Set environment to production
config.plugins.push(new webpack.DefinePlugin({
  'process.env': {
    'NODE_ENV': JSON.stringify('production')
  }
}));

// Uglify js
config.plugins.push(new webpack.optimize.UglifyJsPlugin({
  compress: {
    warnings: false,
    screw_ie8: true
  },
  comments: false,
  sourceMap: false
}));

module.exports = config;
