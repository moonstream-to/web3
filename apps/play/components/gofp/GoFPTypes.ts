export type GoFPMetadata = {
  title: string;
  imageUrl: string;
  lore: string;
};

export type PathMetadata = GoFPMetadata & {};

export type StageMetadata = GoFPMetadata & {
  paths: PathMetadata[];
};

export type SessionMetadata = GoFPMetadata & {
  stages: StageMetadata[];
};

export enum PathStatus {
  correct,
  incorrect,
  undecided,
}

export type ChoosePathData = {
  path: number;
  tokenIds: number[];
};
