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
    articleDetails: [
      './assets/article/details/index',
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
    dashboardAuthentication: [
      './assets/dashboard/authentication/index',
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
    eventsDetails: [
      './assets/events/details/index',
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
    google: 'google',
    urls: 'Urls',
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        // Somehow babel fucks up jqplot
        exclude: /(node_modules|jqplot\.\w+\.js)/,
        loaders: ['babel'],
      },
      {
        // Hack for modules that depend on global jQuery
        test: /(node_modules\/bootstrap\/.+|jquery.jqplot|jqplot\.\w+)\.js$/,
        loader: 'imports?jQuery=jquery,$=jquery,this=>window',
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
        test: /\.(png|gif|jpe?g)$/,
        loader: 'url-loader?limit=10000',
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2)(\?[a-z0-9=&.]+)?$/,
        loader: 'url-loader?limit=10000',
      },
    ],
  },
  plugins: [
    new CommonsChunkPlugin({
      names: ['common'],
      minChunks: 2,
    }),
    new BundleTracker({ filename: './webpack-stats.json' }),
  ],
};
