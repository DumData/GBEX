module.exports = {
    "extends": ["eslint:recommended", "plugin:react/recommended"],
    "plugins": ["react", "import", "flowtype"],
    "rules": {"no-console": "off", "strict": 0, "flowtype/define-flow-type": 1, "flowtype/use-flow-type": 1},
    "env": {"browser": true, es6: true},
    "parser": "babel-eslint",
    "parserOptions": {"ecmaVersion": 2020, "sourceType": "module", "ecmaFeatures": {"jsx": true}}
};
