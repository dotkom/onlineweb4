// Breaks for some reason
/* eslint comma-dangle: ["error", {"functions":
  "arrays": "always-multiline",
  "objects": "always-multiline",
  "imports": "always-multiline",
  "exports": "always-multiline",
  "functions": "ignore",
}] */

const config = require('./webpack.config.js');

// Full source map
config.devtool = 'source-map';
config.mode = "production";
config.hot = false;

module.exports = config;
