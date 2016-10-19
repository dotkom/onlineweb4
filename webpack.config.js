var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,
  entry: {
    frontpageEvents: [
      './assets/js/frontpage/events/index'
    ]
  },
  output: {
    path: path.resolve('./assets/webpack_bundles/'),
    filename: '[name]-[hash].js'
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      },
      {
        test: /\.less$/,
        loader: ExtractTextPlugin.extract('style', 'css!less'),
      }
    ]
  },
  lessLoader: {
    includePath: [path.resolve(__dirname, './styles')]
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'})
  ]
};
