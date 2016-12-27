const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const CommonsChunkPlugin = require('webpack/lib/optimize/CommonsChunkPlugin');
const fs = require('fs');

const extraResolveFile = 'webpack-extra-resolve.json';
let resolvePaths = [];
if (fs.existsSync(extraResolveFile)) {
  resolvePaths = JSON.parse(fs.readFileSync(extraResolveFile, 'utf-8')).paths;
} else {
  console.error('Start the django web server before running webpack'); // eslint-disable-line no-console
  process.exit(1);
}

module.exports = {
  context: __dirname,
  devtool: 'eval-source-map',
  entry: {
    // Used to extract common libraries
    vendor: [
      'classnames', 'es6-promise', 'whatwg-fetch',
      'moment', 'react', 'react-bootstrap', 'react-dom',
    ],
    articleArchive: [
      './assets/article/archive/index',
    ],
    authentication: [
      './assets/authentication/index',
    ],
    core: [
      './assets/core/index',
    ],
    dashboard: [
      './assets/dashboard/core/index',
    ],
    dashboard_approval: [
      './assets/dashboard/approval/index',
    ],
    dashboardArticle: [
      './assets/dashboard/article/index',
    ],
    dashboardCareeropportunity: [
      './assets/dashboard/careeropportunity/index',
    ],
    dashboardChunks: [
      './assets/dashboard/chunks/index',
    ],
    dashboardEvents: [
      './assets/dashboard/events/index',
    ],
    dashboardGallery: [
      './assets/dashboard/gallery/index',
    ],
    dashboardGroups: [
      './assets/dashboard/groups/index',
    ],
    dashboardInventory: [
      './assets/dashboard/inventory/index',
    ],
    dashboardMarks: [
      './assets/dashboard/marks/index',
    ],
    dashboardPosters: [
      './assets/dashboard/posters/index',
    ],
    dashboardWebshop: [
      './assets/dashboard/webshop/index',
    ],
    events_archive: [
      './assets/events/archive/index',
    ],
    feedback: [
      './assets/feedback/index',
    ],
    frontpage: [
      './assets/frontpage/index',
    ],
    genfors: [
      './assets/genfors/index',
    ],
    mailinglists: [
      './assets/mailinglists/index',
    ],
    offline: [
      './assets/offline/index',
    ],
    profiles: [
      './assets/profiles/index',
    ],
    sso: [
      './assets/sso/index',
    ],
    resourcecenter: [
      './assets/resourcecenter/index',
    ],
    webshop: [
      './assets/webshop/index',
    ],
    wiki: [
      './assets/wiki/index',
    ],
  },
  resolve: {
    root: path.resolve(__dirname, './assets/'),
    fallback: resolvePaths,
  },
  output: {
    path: path.resolve('./bundles/webpack/'),
    filename: '[name]-[hash].js',
  },
  externals: {
    jquery: 'jQuery',
    urls: 'Urls',
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loaders: ['babel'],
      },
      {
        test: /\.css$/,
        loader:
          'style-loader!' +
          'css-loader?sourceMap!',
      },
      {
        test: /\.less$/,
        loader:
          'style-loader!' +
          'css-loader?sourceMap!' +
          'less-loader?sourceMap',
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2)(\?[a-z0-9=&.]+)?$/,
        loader: 'url-loader?limit=10000',
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
