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
            test: /\.(png|woff|woff2|eot|ttf|svg)$/,
            loader: 'url-loader?limit=100000'
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
