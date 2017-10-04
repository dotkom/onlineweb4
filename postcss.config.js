module.exports = ({ file, options, env }) => {
  return {
  plugins: {
    'autoprefixer': {},
    'cssnano': env === 'production' ? {
      preset: 'default',
    } : false,
  },
}};
