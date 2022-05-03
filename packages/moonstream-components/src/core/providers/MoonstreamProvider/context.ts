import { createContext } from "react";
import { ConstantsInterface } from "../../../../../../types/Site";
const defaultTimeRanges = {
  day: 86400,
  week: 86400 * 7,
  month: 86400 * 28,
};

export const DEFAULT_METATAGS = {
  title: "change me",
  description: "change me",
  keywords: "change me",
  url: "change me",
  image: `change me`,
};
const defaultCopyright = "moonstream.to";
const defaultSupportEmail = "support@moonstream.to";
const defaultAppname = "moonstream app";
const WHITE_LOGO_W_TEXT_URL = `https://s3.amazonaws.com/static.simiotics.com/moonstream/assets`;
const defaultLogoWURLSvg = `https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/moon-logo%2Btext-white.png`;

export const defaultConstants = {
  TIME_RANGE_SECONDS: { ...defaultTimeRanges },
  DEFAULT_METATAGS: { ...DEFAULT_METATAGS },
  COPYRIGHT_NAME: defaultCopyright,
  SUPPORT_EMAIL: defaultSupportEmail,
  APP_NAME: defaultAppname,
  WHITE_LOGO_W_TEXT_URL: defaultLogoWURLSvg,
  AWS_ASSETS_PATH: WHITE_LOGO_W_TEXT_URL,
  SITEMAP: [],
};
const MoonstreamContext = createContext<ConstantsInterface>({
  ...defaultConstants,
});

export default MoonstreamContext;
