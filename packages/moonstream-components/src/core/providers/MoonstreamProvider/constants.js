const defaultTimeRanges = {
  day: 86400,
  week: 86400 * 7,
  month: 86400 * 28,
};

const deaultMetatags = {
  title: "change me",
  description: "change me",
  keywords: "change me",
  url: "change me",
  image: `change me`,
};
const defaultCopyright = "moonstream.to";
const defaultSupportEmail = "support@moonstream.to";
const defaultAppname = "moonstream app";

export const defaultConstants = {
  TIME_RANGE_SECONDS: { ...defaultTimeRanges },
  DEFAULT_METATAGS: { ...deaultMetatags },
  COPYRIGHT_NAME: defaultCopyright,
  SUPPORT_EMAIL: defaultSupportEmail,
  APP_NAME: defaultAppname,
};
