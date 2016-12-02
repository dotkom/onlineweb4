var config = require('./webpack.config.js');
var webpack = require('webpack');
var WebpackDevServer = require('webpack-dev-server');

var ip = '0.0.0.0';
var port = 3000;
var host = ip + ':' + String(port);

// Add hot reloading to all entries
for (var entry in config.entry) {
  if (config.entry.hasOwnProperty(entry) && entry !== 'vendor') {
    config.entry[entry].unshift(
      'webpack-dev-server/client?http://' + host,
      'webpack/hot/dev-server'
    );
  }
}

// config.entry.dev = ;

config.output.publicPath = 'http://' + host + '/assets/bundles/';

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
}).listen(port, ip, function (err, result) {
  if (err) {
    console.error(err);
  }

  console.log('Listening at ' + host);
});
