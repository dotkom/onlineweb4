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
    core: [
      './assets/js/core/index',
    ],
    dashboard: [
      './assets/js/dashboard/core/index',
    ],
    dashboard_approval: [
      './assets/js/dashboard/approval/index',
    ],
    dashboardArticle: [
      './assets/js/dashboard/article/index',
    ],
    dashboardCareeropportunity: [
      './assets/js/dashboard/careeropportunity/index',
    ],
    dashboardEvents: [
      './assets/js/dashboard/events/index',
    ],
    dashboardGallery: [
      './assets/js/dashboard/gallery/index',
    ],
    dashboardGroups: [
      './assets/js/dashboard/groups/index',
    ],
    dashboardMarks: [
      './assets/js/dashboard/marks/index',
    ],
    dashboardPosters: [
      './assets/js/dashboard/posters/index',
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
    mailinglists: [
      './assets/js/mailinglists/index',
    ],
    profiles: [
      './assets/js/profiles/index',
    ],
    sso: [
      './assets/js/sso/index',
    ],
    resourcecenter: [
      './assets/js/resourcecenter/index',
    ],
    webshop: [
      './assets/js/webshop/index',
    ],
    wiki: [
      './assets/js/wiki/index',
    ],
  },
  resolve: {
    root: path.resolve(__dirname, './assets/'),
    fallback: resolvePaths,
  },
  output: {
    path: path.resolve('./assets/webpack_bundles/'),
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
