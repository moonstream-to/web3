/*
  Pass this is default metatags that will be added to your pages if you dont specify others in page component
  See more in /pages_templates directory for examples
  title: browser title
  description: SEO description of the page
  keywords: SEO keywords,
  url: URL of your page
  image: URL of image to display on page preview in search engines and link shares
*/
export const DEFAULT_METATAGS = {
  title: "Moonstream Engine",
  description: "Building blocks for your blockchain game",
  keywords: "web3, smart contracts, terminus, nfts",
  url: "https://engine.moonstream.io",
  image: `https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/lender.png`,
};

/*
 Key value pairs that will define categories for links in the footer
*/
export const FOOTER_COLUMNS = {
  // NEWS: "News",
  // COMPANY: "Company",
  // PRODUCT: "Product",
};

/*
 Navigation pathes visible for all site visitors (no matter if they are logged in or not)
 Title: Name of the path to appear in link buttons
 Path: path to the page (it has to be availible in /pages directory or will show 404)
*/
export const ALL_NAV_PATHES = [
  // {
  //   title: "Product",
  //   path: "/product",
  //   footerCategory: FOOTER_COLUMNS.PRODUCT,
  // },
];

/*
 Navigation pathes visible only to authenticated users
 Title: Name of the path to appear in link buttons
 Path: path to the page (it has to be availible in /pages directory or will show 404)
*/
export const USER_NAV_PATHES = [
  // {
  //   title: "Learn how to use Moonstream",
  //   path: "/welcome",
  // },
];

/*
 Social links list to be used in the website
*/
export const SOCIAL_LINKS = [
  // {
  //   label: "Discord",
  //   url: "discord/link/here",
  // },
  // {
  //   label: "Twitter",
  //   url: "twitter/link/here",
  // },
  // {
  //   label: "Github",
  //   url: "Github/link/here",
  // },
];

/*
Default pagination size to load paginated stream events
*/
export const PAGE_SIZE = 20;

/*
AWS assets path where you store images. It will be preconnected to speed up. Preloading images will work by defining those in assets array
and getStaticProps of the page (see /pages_templates for examples)
*/
export const AWS_ASSETS_PATH = `https://s3.amazonaws.com/static.simiotics.com/moonstream/assets`;

/*
White Logo with text URL (.png)
*/
export const WHITE_LOGO_W_TEXT_URL = `https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/moon-logo%2Btext-white.png`;

/*
White Logo URL (.svg)
*/
export const WHITE_LOGO_SVG = `https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/moon-logo%2Btext-white.png`;

export const TIME_RANGE_SECONDS = {
  day: 86400,
  week: 86400 * 7,
  month: 86400 * 28,
};

/*
If true app will require user to be authenticated in order to see anything that is wrapped whithin /src/layouts/AppLayout.js
*/
export const IS_AUTHENTICATION_REQUIRED = false;

/*
This will appear in copyright text
*/
export const COPYRIGHT_NAME = "moonstream.to";

/*
If you define this constant with some page path, it will bring App button in non app layouts. Pressing button will follow that path.
*/
export const APP_ENTRY_POINT = undefined;

/*
Suppport email address
*/
export const SUPPORT_EMAIL = "support@moonstream.to";

/*
App name that will show in titles, modals etc
*/
export const APP_NAME = "Engine";
