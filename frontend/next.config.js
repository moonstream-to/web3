module.exports = {
  reactStrictMode: true,
  target: "serverless",
  trailingSlash: true,
  presets: [require.resolve("next/babel")],
  webpack: (config, { isServer, webpack }) => {
    // Fixes npm packages that depend on `fs` module
    if (!isServer) {
      // config.node = { fs: 'empty' };
      config.resolve.fallback.fs = false;
      config.resolve.fallback.electron = false;
    }
    config.plugins.push(
      new webpack.IgnorePlugin({
        resourceRegExp: /^electron$/,
      })
    );

    return config;
  },
};
