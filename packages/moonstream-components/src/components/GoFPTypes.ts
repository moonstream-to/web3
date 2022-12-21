export type GoFPMetadata = {
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
