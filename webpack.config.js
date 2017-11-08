var webpack = require('webpack');

var production = (process.env.NODE_ENV === 'production');

const ExtractTextPlugin = require("extract-text-webpack-plugin");
const extractSass = new ExtractTextPlugin({ filename: '../css/[name].css' });

module.exports = {  
    entry: {
        main: [
            __dirname + '/website/assets/js/main.js',
            __dirname + '/website/assets/scss/main.scss'
        ],
        dashboard: [
            __dirname + '/website/assets/js/dashboard.js',
            __dirname + '/website/assets/scss/dashboard.scss'
        ],
        kitconfig: [
            __dirname + '/website/assets/scss/kitconfig.scss'
        ],
        sensors: [
            __dirname + '/website/assets/scss/sensors.scss'
        ]
    },
    devtool: 'source-map',
    output: {
        path: __dirname + '/website/static/website/js/',
        filename: '[name].js',
    },
  
    module: {
        rules: [{
            test: /\.scss$/,
            use: extractSass.extract({
                use: [{
                    loader: "css-loader", options: {
                        sourceMap: true
                    }
                }, {
                    loader: "sass-loader", options: {
                        sourceMap: true
                    }
                }]
            })
        }, {
            test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
            loader: "url-loader?name=../files/[hash].[ext]&limit=10000&mimetype=application/font-woff"
        }, {
            test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
            loader: "url-loader?name=../files/[hash].[ext]&limit=10000&mimetype=application/font-woff"
        }, {
            test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
            loader: "url-loader?name=../files/[hash].[ext]&limit=10000&mimetype=application/octet-stream"
        }, {
            test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
            loader: "file-loader?name=../files/[hash].[ext]"
        }, {
            test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
            loader: "url-loader?name=../files/[hash].[ext]&limit=10000&mimetype=image/svg+xml"
        }, {
            test: /\.png(\?v=\d+\.\d+\.\d+)?$/,
            loader: 'url-loader?name=../files/[hash].[ext]&limit=100000&mimetype=image/png'
        }, {
            test: require.resolve('jquery'),
            use: [{
                loader: 'expose-loader',
                options: '$'
            }, {
                loader: 'expose-loader',
                options: 'jQuery'
            }]
        }]
    },

    plugins: [
        extractSass
    ].concat(production ? [
        new webpack.optimize.UglifyJsPlugin({
            compress: { warnings: false }
        }),
        extractSass
    ] : [])
}
