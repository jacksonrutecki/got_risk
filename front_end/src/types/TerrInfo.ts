// terr info type - contains number of armies and respective color on a territory

export type TerrInfo = {
    num_armies: number;
    color: string;
    is_ter_from: boolean;
    is_ter_to: boolean;
};

export const INTIIAL_USER: TerrInfo = {
  num_armies: 0,
  color: "black",
  is_ter_from: false,
  is_ter_to: false
};