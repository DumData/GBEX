var path = require('path');
var webpack = require('webpack');

module.exports = {
  mode: "development",
  entry: ["./src/index.jsx"],
  output: { filename: 'bundle.js', path: path.resolve(__dirname, 'dist'), publicPath: '/static/' },
  module: {
    rules: [
      { test: /\.jsx?$/, exclude: /node_modules/, loader: "babel-loader" },
      { test: /\.s?css$/, loader: ["style-loader", "css-loader"]}
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  },
};
