var config = require('./webpack.config.js');
var webpack = require('webpack');
var WebpackDevServer = require('webpack-dev-server');

var port = 3000;

// Add hot reloading to all entries
for (var entry in config.entry) {
  if (config.entry.hasOwnProperty(entry)) {
    config.entry[entry].push('webpack/hot/dev-server');
  }
}

config.entry.dev = 'webpack-dev-server/client?http://0.0.0.0:' + String(port);

config.output.publicPath = 'http://localhost:' + String(port) + '/assets/bundles/';

config.plugins.unshift(new webpack.NoErrorsPlugin()); // don't reload if there is an error
config.plugins.unshift(new webpack.HotModuleReplacementPlugin());

var compiler =  webpack(config);

new WebpackDevServer(compiler, {
  publicPath: config.output.publicPath,
  hot: true,
  inline: true,
  historyApiFallback: true,
  headers: { "Access-Control-Allow-Origin": "*" },
  stats: {
    chunks: false
  }
}).listen(3000, '0.0.0.0', function (err, result) {
  if (err) {
    console.error(err);
  }

  console.log('Listening at 0.0.0.0:3000');
});
