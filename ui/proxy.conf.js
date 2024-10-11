const PROXY_CONFIG = {
    "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
        secure: false,
    },
};

module.exports = PROXY_CONFIG;
