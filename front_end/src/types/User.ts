// user type - contains a username and corresponding sid

export type User = {
  username: string;
  roomID: string;
  points: number;
  color: string;
};

export const INTIIAL_USER: User = {
  username: "",
  roomID: "",
  points: -1,
  color: ""
};