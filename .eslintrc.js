module.exports = {
  extends: "airbnb",
  globals: {
    Urls: true
  },
  env: {
    browser: true,
    jest: true,
    jquery: true,
  },
  rules: {
    "react/jsx-filename-extension": [
      1,
      {
        extensions: [
          ".js",
          ".jsx"
        ]
      }
    ]
  },
  settings: {
    "import/resolver": {
      webpack: {
        config: "webpack.config.js"
      }
    }
  }
}
