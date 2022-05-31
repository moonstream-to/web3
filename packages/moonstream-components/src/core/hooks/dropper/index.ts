import useClaim from "./useClaim";
import useClaims from "./useClaims";
import useDrop from "./useDrop";
import useDrops from "./useDrops";
import useDropperContract from "./useDropper.sol";

export { default as useDrop } from "./useDrop";
export { default as useDrops } from "./useDrops";
export { default as useClaim } from "./useClaim";
export { default as useClaims } from "./useClaims";
export { default as useDropperContract } from "./useDropper.sol";
const dropper = {
  useClaim,
  useDrops,
  useDrop,
  useClaims,
  useDropperContract,
};
export default dropper;
