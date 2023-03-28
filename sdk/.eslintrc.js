module.exports = {
    env: {
        browser: false,
        es6: true,
        node: true,
    },
    parser: "@typescript-eslint/parser",
    rules: {
        "prettier/prettier": "error",
    },
    plugins: ["prettier", "@typescript-eslint"],
    extends: ["eslint:recommended", "plugin:prettier/recommended"],
}
