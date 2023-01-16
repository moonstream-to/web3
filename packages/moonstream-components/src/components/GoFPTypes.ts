export type GoFPMetadata = {
  imageUrl: string;
  lore: string;
};

export type PathMetadata = GoFPMetadata & { characters: string[] };

export type StageMetadata = GoFPMetadata & {
  paths: PathMetadata[];
  isCurrent: boolean;
};

export type SessionMetadata = GoFPMetadata & {
  stages: StageMetadata[];
};
