const config = require('./webpack.config.js');
const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

config.devtool = 'cheap-module-source-map';

// Set environment to production
config.plugins.push(new webpack.DefinePlugin({
  'process.env': {
    NODE_ENV: JSON.stringify('production'),
  },
}));

// Extract css to file

// Replace less loader
Object.keys(config.module.loaders).forEach((key) => {
  const loader = config.module.loaders[key];
  if (loader.test.match(/\.less$/)) {
    loader.loader = ExtractTextPlugin.extract(
      'css-loader?sourceMap!' +
      'less-loader?sourceMap',
    );
  }
});
// Add extract text plugin
config.plugins.push(new ExtractTextPlugin('[name]-[hash].css'));


// Uglify js
config.plugins.push(new webpack.optimize.UglifyJsPlugin({
  compress: {
    warnings: false,
    screw_ie8: true,
  },
  comments: false,
  sourceMap: false,
}));

module.exports = config;
