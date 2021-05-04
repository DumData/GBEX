const path = require('path')

module.exports = {
  mode: 'production',
  entry: './src/index.jsx',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    publicPath: '/static/'
  },
  module: {
    rules: [
      { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader', resolve: { extensions: [".js", ".jsx"] } },
      { test: /\.css$/i, use: ["style-loader", "css-loader"], },
    ]
  }
}
