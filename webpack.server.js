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

const HTTPS = process.env.WEBPACK_DEV_HTTPS || false;
const IP = process.env.WEBPACK_DEV_IP || '0.0.0.0';
const PUBLIC_IP = process.env.WEBPACK_DEV_PUBLIC_IP || IP;
const PORT = process.env.WEBPACK_DEV_PORT || 3000;
const PUBLIC_PORT = process.env.WEBPACK_DEV_PUBLIC_PORT || PORT;
const HOST = `${PUBLIC_IP}:${PORT}`;
const PROTOCOL = HTTPS ? 'https' : 'http';

// Remove [hash] since webpack-dev-server stores all generated copies in memory based on filename
config.output.filename = '[name].js';
// Entries will be served from a seperate http server instead of from filesystem
config.output.publicPath = process.env.WEBPACK_DEV_GITPOD === 'true' ? `${PROTOCOL}://${PUBLIC_IP}/static/` :
    `${PROTOCOL}://${PUBLIC_IP}:${PUBLIC_PORT}/static/`;

console.log(config.output.publicPath);


config.devServer = {
  // Enables Hot Module Reloading (only CSS and React atm)
  hot: true,
  // Allow CORS
  headers: { 'Access-Control-Allow-Origin': '*' },
}
