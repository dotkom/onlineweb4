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

const ip = '0.0.0.0';
const port = 3000;
const host = `${ip}:${port}`;
// Add hot reloading to all entries
Object.keys(config.entry).forEach((entry) => {
  if ({}.hasOwnProperty.call(config.entry, entry)) {
    config.entry[entry].unshift(
      `webpack-dev-server/client?http://${host}`,
      'webpack/hot/dev-server'
    );
  }
});

// Remove [hash] since webpack-dev-server stores all generated copies in memory based on filename
config.output.filename = '[name].js';
config.output.publicPath = `http://${host}/static/`;

// Don't reload if there is an error
config.plugins.unshift(new webpack.NoErrorsPlugin());
config.plugins.unshift(new webpack.HotModuleReplacementPlugin());

// Add react-hot-loader to js loader
Object.keys(config.module.loaders).forEach((key) => {
  if ({}.hasOwnProperty.call(config.module.loaders, key)) {
    const loader = config.module.loaders[key];
    if ('.js'.match(loader.test)) {
      loader.loaders.unshift('react-hot');
    }
  }
});


const compiler = webpack(config);

new WebpackDevServer(compiler, {
  publicPath: config.output.publicPath,
  hot: true,
  inline: true,
  historyApiFallback: true,
  headers: { 'Access-Control-Allow-Origin': '*' },
  stats: {
    chunks: false,
    colors: true,
  },
}).listen(port, ip, (err) => {
  if (err) {
    console.error(err);
  }
  console.log(`Listening at ${host}`);
});
