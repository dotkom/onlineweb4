// Not relevant for nodejs
/* eslint no-console: 0 */
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
const WebpackDevServer = require('webpack-dev-server');

const IP = process.env.WEBPACK_DEV_IP || '0.0.0.0';
const PUBLIC_IP = process.env.WEBPACK_DEV_PUBLIC_IP || IP;
const PORT = process.env.WEBPACK_DEV_PORT || 3000;
const HOST = `${PUBLIC_IP}:${PORT}`;

// Add hot reloading to all entries
// https://webpack.js.org/concepts/hot-module-replacement/
Object.keys(config.entry).forEach((entry) => {
  if ({}.hasOwnProperty.call(config.entry, entry)) {
    config.entry[entry].unshift(
      `webpack-dev-server/client?http://${HOST}`,
      'webpack/hot/dev-server'
    );
  }
});

// Remove [hash] since webpack-dev-server stores all generated copies in memory based on filename
config.output.filename = '[name].js';
// Entries will be served from a seperate http server instead of from filesystem
config.output.publicPath = `http://${HOST}/static/`;

// Don't reload if there is an error
config.plugins.unshift(new webpack.NoErrorsPlugin());
// HMR
config.plugins.unshift(new webpack.HotModuleReplacementPlugin());

// Add react-hot-loader to js loader
Object.keys(config.module.loaders).forEach((key) => {
  if ({}.hasOwnProperty.call(config.module.loaders, key)) {
    const loader = config.module.loaders[key];
    /*
      TODO: This check might match more than necessary in the future.
      It should only match babel loader rule
    */
    if ('.js'.match(loader.test)) {
      loader.loaders.unshift('react-hot');
    }
  }
});


const compiler = webpack(config);

new WebpackDevServer(compiler, {
  publicPath: config.output.publicPath,
  // Enables Hot Module Reloading (only CSS and React atm)
  hot: true,
  // Adds some code that refreshes the page if the code changes
  inline: true,
  // TODO: Not sure if this is actually needed
  historyApiFallback: true,
  // Allow CORS
  headers: { 'Access-Control-Allow-Origin': '*' },
  stats: {
    // Hide some 'useless' info
    chunks: false,
    // Enables color output
    colors: true,
  },
}).listen(PORT, IP, (err) => {
  if (err) {
    console.error(err);
  }
  console.log(`Listening at ${HOST}`);
});
