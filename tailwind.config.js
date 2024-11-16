/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"./templates/*.html",
		"./templates/partials/*.html",
		"./static/js/*.js",
		"./static/css/*.css",
	],
	theme: {
		extend: {},
	},
	plugins: [require("daisyui")],
};
