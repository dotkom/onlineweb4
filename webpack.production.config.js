// Breaks for some reason
/* eslint comma-dangle: ["error", {"functions":
  "arrays": "always-multiline",
  "objects": "always-multiline",
  "imports": "always-multiline",
  "exports": "always-multiline",
  "functions": "ignore",
}] */

const config = require('./webpack.config.js');
const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

// Full source map
config.devtool = 'source-map';

// Set environment to production
// Some libraries use this to turn off some dev features
config.plugins.push(new webpack.DefinePlugin({
  'process.env': {
    NODE_ENV: JSON.stringify('production'),
  },
}));

// We want to include CSS and JS seperately:
// Remove style loader
Object.keys(config.module.rules).forEach((key) => {
  if ({}.hasOwnProperty.call(config.module.rules, key)) {
    const loader = config.module.rules[key];
    if ('.less'.match(loader.test)) {
      loader.loader = ExtractTextPlugin.extract(
        'css-loader?sourceMap!' +
        'less-loader?sourceMap'
      );
    }
    if ('.css'.match(loader.test)) {
      loader.loader = ExtractTextPlugin.extract(
        'css-loader?sourceMap'
      );
    }
  }
});
// Add extract text plugin to extract css to .css files
config.plugins.push(new ExtractTextPlugin('[name]-[hash].css'));


// Uglify js
config.plugins.push(new webpack.optimize.UglifyJsPlugin({
  compress: {
    warnings: false,
    screw_ie8: true,
  },
  sourceMap: true,
  comments: false,
}));

module.exports = config;
