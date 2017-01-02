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

config.devtool = 'cheap-source-map';

// Set environment to production
config.plugins.push(new webpack.DefinePlugin({
  'process.env': {
    NODE_ENV: JSON.stringify('production'),
  },
}));

// Extract css to file

// Remove style loader
Object.keys(config.module.loaders).forEach((key) => {
  if ({}.hasOwnProperty.call(config.module.loaders, key)) {
    const loader = config.module.loaders[key];
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
// Add extract text plugin
config.plugins.push(new ExtractTextPlugin('[name]-[hash].css'));


// Uglify js
config.plugins.push(new webpack.optimize.UglifyJsPlugin({
  compress: {
    warnings: false,
    screw_ie8: true,
  },
  comments: false,
}));

module.exports = config;
