// TODO: rename to icon, gigignored from parent .gitignore file
// TODO: review if this component makes sense at all, logo must be used from WHITE_LOGO_W_TEXT_URL but it's png
import React from "react";
import { WHITE_LOGO_SVG } from "../core/constants";

const Icon = ({ className, style, icon, width, height, onClick }) => {
  const iconSrc = icon === "logo" ? { WHITE_LOGO_SVG } : `/icons/${icon}.svg`;
  return (
    <img
      onClick={onClick ? onClick : () => {}}
      style={{ style, width: width, height: height }}
      src={iconSrc}
      alt={`icon-${icon}-${height}`}
      className={className}
    />
  );
};

export default Icon;
