var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var BundleTracker = require('webpack-bundle-tracker');
var CommonsChunkPlugin = require("webpack/lib/optimize/CommonsChunkPlugin");

module.exports = {
  context: __dirname,
  devtool: 'inline-source-map',
  entry: {
    // Used to extract common libraries
    vendor: [
      'classnames', 'es6-promise', 'isomorphic-fetch',
      'moment', 'react', 'react-bootstrap', 'react-dom'
    ],
    core: [
      './assets/js/core/index',
    ],
    dashboard_approval: [
      './assets/js/dashboard/approval/index',
    ],
    events_archive: [
      './assets/js/events/archive/index'
    ],
    frontpageEvents: [
      './assets/js/frontpage/events/index'
    ],
    frontpageArticles: [
      './assets/js/frontpage/articles/index'
    ],
    webshop: [
      './assets/js/webshop/index',
    ],
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
        loader: ExtractTextPlugin.extract(
          'css-loader?sourceMap!' +
          'less-loader?sourceMap'),
      }
    ]
  },
  plugins: [
    new CommonsChunkPlugin({
      names: ['vendor'],
      minChunks: Infinity
    }),
    new ExtractTextPlugin('[name]-[hash].css'),
    new BundleTracker({filename: './webpack-stats.json'})
  ]
};
