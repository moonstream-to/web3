export interface MetatagsInterface {
  title: string;
  description: string;
  keywords: string;
  url: string;
  image: string;
}

export type TimeRanges = {
  day: number;
  week: number;
  month: number;
};

export const PAGETYPE = {
  EMPTY: 0,
  CONTENT: 1,
  EXTERNAL: 2,
};

export interface SiteItem {
  title: string;
  path: string;
  type: typeof PAGETYPE;
  children?: Array<SiteItem>;
}

export interface ConstantsInterface {
  DEFAULT_METATAGS: MetatagsInterface;
  TIME_RANGE_SECONDS: TimeRanges;
  COPYRIGHT_NAME: string;
  SUPPORT_EMAIL: string;
  APP_NAME: string;
  WHITE_LOGO_W_TEXT_URL: string;
  AWS_ASSETS_PATH: string;
  SITEMAP: Array<SiteItem>;
}
