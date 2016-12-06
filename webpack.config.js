var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var BundleTracker = require('webpack-bundle-tracker');
var CommonsChunkPlugin = require("webpack/lib/optimize/CommonsChunkPlugin");

module.exports = {
  context: __dirname,
  devtool: 'eval-source-map',
  entry: {
    // Used to extract common libraries
    vendor: [
      'classnames', 'es6-promise', 'isomorphic-fetch',
      'moment', 'react', 'react-bootstrap', 'react-dom'
    ],
    frontpageEvents: [
      './assets/js/frontpage/events/index'
    ],
    frontpageArticles: [
      './assets/js/frontpage/articles/index'
    ]
  },
  resolve: {
    root: path.resolve(__dirname, './assets/'),
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
    new CommonsChunkPlugin({
      names: ['vendor'],
      minChunks: Infinity
    }),
    new BundleTracker({filename: './webpack-stats.json'})
  ]
};
