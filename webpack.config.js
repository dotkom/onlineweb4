const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const CommonsChunkPlugin = require('webpack/lib/optimize/CommonsChunkPlugin');

module.exports = {
  context: __dirname,
  devtool: 'eval-source-map',
  entry: {
    // Used to extract common libraries
    vendor: [
      'classnames', 'es6-promise', 'whatwg-fetch',
      'moment', 'react', 'react-bootstrap', 'react-dom',
    ],
    core: [
      './assets/js/core/index',
    ],
    dashboard_approval: [
      './assets/js/dashboard/approval/index',
    ],
    events_archive: [
      './assets/js/events/archive/index',
    ],
    frontpageEvents: [
      './assets/js/frontpage/events/index',
    ],
    frontpageArticles: [
      './assets/js/frontpage/articles/index',
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
    filename: '[name]-[hash].js',
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
      },
      {
        test: /\.less$/,
        // loader: ExtractTextPlugin.extract(
        loader:
          'style-loader!' +
          'css-loader?sourceMap!' +
          'less-loader?sourceMap',
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2)$/,
        loader: 'file-loader?name=fonts/[name].[ext]&publicPath=/static/fonts/',
      },
    ],
  },
  plugins: [
    new CommonsChunkPlugin({
      names: ['vendor'],
      minChunks: Infinity,
    }),
    new BundleTracker({ filename: './webpack-stats.json' }),
  ],
};
