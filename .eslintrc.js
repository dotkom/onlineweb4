module.exports = {
  extends: "airbnb",
  env: {
    browser: true,
    jest: true,
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
    ],
    // Disabled until eslint-plugin-import gets proper support for webpack externals
    // https://github.com/benmosher/eslint-plugin-import/issues/479
    // https://github.com/benmosher/eslint-plugin-import/issues/605
    "import/no-extraneous-dependencies": 0,
    "import/extensions": 0,
  },
  settings: {
    "import/resolver": {
      webpack: {
        config: "webpack.config.js"
      }
    }
  }
}
