var config = require('./webpack.config.js');
var webpack = require('webpack');
var WebpackDevServer = require('webpack-dev-server');

config.entry.dev = [
  'webpack-dev-server/client?http://localhost:3000/',
  'webpack/hot/dev-server'
];

config.plugins.push(new webpack.HotModuleReplacementPlugin())

var compiler =  webpack(config);

var server = new WebpackDevServer(compiler, {
  publicPath: config.output.publicPath,
  hot: true
});

server.listen(3000);
